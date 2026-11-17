import "./style.css";
import * as d3 from "d3";
import { LineChart, type Series, type Opts } from "./plot";
import { Heat, halfPoints } from "./heat";
import { signals, pair, fwhm, field } from "./paraxial";
import { rwSignals } from "./rw";
import { loadData, loadProfiles, wkey, type Data, type Medium, type Signal, type Axis, type Theta, type Pupil, type Input } from "./data";
import { Setup } from "./setup";
import { renderHow } from "./how";
import { panels } from "./panels";
import { runPulses, pairSpectra, C, type PulseOpts, type PulseRun } from "./pulsetime";
import { HIGHLIGHTS, type Highlight } from "./highlights";

// ---------------------------------------------------------------- state (kept in the URL) ----------------------------------------------
type Mode = "hl" | "na" | "theta" | "dl" | "eps" | "live" | "pulses" | "ptime" | "psum" | "scatter";
const S = {
  mode: "live" as Mode,
  // live (paraxial, computed here)
  lna: 0.5, th: 90, dl: 94, eps: 0, n: 1,
  // against NA (precomputed scalar and vector)
  med: "air" as Medium, sig: "2CE" as Signal, metric: "width", axis: "z" as Axis, model: "both", pupil: "circ" as Pupil,
  input: "uni" as Input, ths: "0.pi2.pi", na: 0.5,
  // pulses, scattering
  pmed: "air" as Medium, psig: "2CE" as Signal, pna: 0.5, h: 100, one: 0,
  // sweeps at one NA (θ, Δλ, pupil); "pk" is the picked value of the swept parameter
  wna: 0.5, wn: 1, wth: 90, wdl: 94, weps: 0, wdir: "x", pk: NaN,
  // 2D maps: heat map or contours; rotation of beam 2 ((x, z) or the (u, v) of Eq. 1); 2PE as Eq. 6 (|U₁+U₂|⁴) or |U₁+U₂|²
  map: "contour", rot: "xz", pe: 4,
  // where the two cuts are taken (µm): across at z = cz, along at x = cx
  cx: 0, cz: 0,
  // model of the replication tabs: paraxial scalar (Eqs. 1–6, NA ≤ 0.5) or vector Richards–Wolf (any NA)
  mdl: "par",
  // pulses: duration τ (fs, 0 = continuous beams) in the replication tabs; θ of the pulses tab (its own default: facing lenses)
  tau: 0, pth: 180, pplot: "width",
  // against NA: which of the paper's comparisons (ratio of two widths)
  cmp: "r2",
  // pulses in time (computed here): signal, θ (deg), τ (fs), delay of pulse 2 (fs), NA, medium
  qsig: "2CE", qth: 180, qtau: 10, qdel: 0, qna: 0.5, qn: 1, qvid: 0,
  // pulse results (precomputed sweep): signal, cut, scatter x and y, log axes, angles, picked τ, angle of the profile
  rsig: "2CE", rcut: "z", rx: "tau", ry: "crest", rlog: "x", rths: "0.90.180", rk: 10, rpth: 180,
  // pulse results, delay (precomputed, along the axis): angle, τ of the profile, picked path difference N (wavelengths of 700 nm)
  rdth: 180, rdt: 20, rdn: 8,
  // pulse results against NA (precomputed): model and medium of the difference against τ, angle of both plots
  nset: "paraxial_air", nth: 180, nm: "diff", nx: "tau", ny: "dof",
  // pulse results, delay against NA (precomputed, Richards–Wolf, air): angle, τ (fs), the NAs drawn (NA × 100, joined by "."),
  // and the NA and polarization (s perpendicular to the plane of the lens axes, p in it) of the chart of all pairs
  xth: 180, xtau: 100, xnas: "10.20.30.50.70.90", xna: 0.5, xpol: "s",
  how: 0,
  hl: "",                                  // the highlight whose preset is open (src/highlights.ts); a banner above the view shows it
  msc: "peak",                             // 2D map scale: of its own peak, or per unit total energy (shared by both maps)                                  // show how the plotted quantity is measured
};
type K = keyof typeof S;
export type State = typeof S;
const DEF = { ...S };

function readHash() {
  const q = new URLSearchParams(location.hash.slice(1));
  for (const k of Object.keys(DEF) as K[]) {
    const v = q.get(k);
    if (v === null) continue;
    (S as Record<K, unknown>)[k] = typeof DEF[k] === "number" ? +v : v;
  }
}
function writeHash() {
  const q = new URLSearchParams();
  for (const k of Object.keys(DEF) as K[]) if (!Object.is(S[k], DEF[k]) || k === "mode") q.set(k, String(S[k]));
  const h = "#" + q.toString();
  if (location.hash !== h) history.replaceState(null, "", h);
}

const $ = (id: string) => document.getElementById(id)!;
const el = <T extends keyof HTMLElementTagNameMap>(tag: T, cls = "", text = "", parent?: HTMLElement) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  parent?.append(e);
  return e;
};
const TH: Record<Theta, { label: string; color: string }> = {
  "0": { label: "θ = 0", color: "var(--t0)" }, pi2: { label: "θ = π/2", color: "var(--t1)" }, pi: { label: "θ = π", color: "var(--t2)" },
};
const SIG = { "2PE": "var(--t0)", "2CE": "#f28e2b" };
const TAU: Record<string, { label: string; color: string }> = {
  cw: { label: "continuous", color: "var(--t0)" }, "100": { label: "τ = 100 fs", color: "#4e79a7" },
  "20": { label: "τ = 20 fs", color: "#f28e2b" }, "10": { label: "τ = 10 fs", color: "#e15759" },
};
const um = (v: number) => (Number.isFinite(v) ? `${v.toFixed(3)} µm` : "–");

// ---------------------------------------------------------------- controls -----------------------------------------------------------
let render: () => void = () => {};
let redraw: () => void = () => {};       // sliders: new values, same controls
function set(k: K, v: unknown) { (S as Record<K, unknown>)[k] = v; render(); }

function seg(parent: HTMLElement, label: string, k: K, opts: [string | number, string][]) {
  const g = el("div", "ctl", "", parent);
  el("span", "ctl-l", label, g);
  const box = el("div", "seg", "", g);
  for (const [v, t] of opts) {
    const b = el("button", "", t, box) as HTMLButtonElement;
    b.type = "button";
    b.setAttribute("aria-pressed", String(S[k] === v));
    b.onclick = () => set(k, v);
  }
}
function multi(parent: HTMLElement, label: string, k: K, opts: [string, string, string?][]) {
  const g = el("div", "ctl", "", parent);
  el("span", "ctl-l", label, g);
  const box = el("div", "seg", "", g);
  const on = new Set(String(S[k]).split(".").filter(Boolean));
  for (const [v, t, c] of opts) {
    const b = el("button", "", "", box) as HTMLButtonElement;
    b.type = "button";
    if (c) el("i", "sw", "", b).style.background = c;
    b.append(t);
    b.setAttribute("aria-pressed", String(on.has(v)));
    b.onclick = () => { on.has(v) ? on.delete(v) : on.add(v); set(k, [...on].join(".")); };
  }
}
function slider(parent: HTMLElement, label: string, k: K, min: number, max: number, step: number, show: (v: number) => string) {
  const g = el("div", "ctl ctl-slider", "", parent);
  el("span", "ctl-l", label, g);
  const r = el("input", "", "", g) as HTMLInputElement;
  r.type = "range"; r.min = String(min); r.max = String(max); r.step = String(step); r.value = String(S[k]);
  const out = el("output", "", show(+S[k]), g);
  r.oninput = () => { (S as Record<K, unknown>)[k] = +r.value; out.textContent = show(+r.value); redraw(); };
}

// ---------------------------------------------------------------- views ---------------------------------------------------------------
let data: Data;
let metrics: Record<string, (number | null)[][]>;
let pulses: { ratio: Record<string, [number, number][]>; profiles: Record<string, Record<string, number[]>> };
let scatter: Record<string, Record<string, number[] | number>>;

const layout = (cls: string) => { const a = $("app"); a.className = `app ${cls}`; a.replaceChildren(); return a; };
const cell = (parent: HTMLElement, cls = "") => el("div", `cell ${cls}`, "", parent);
const note = (parent: HTMLElement, text: string) => el("p", "note", text, parent);

// A click on a published figure opens the view and settings that reproduce it (NA 0.5, air, 750 + 656 nm).
const PAPER0 = { wna: 0.5, wn: 1, wdl: 94, wth: 90, weps: 0, pe: 4, rot: "xz" };
const FIGS: Record<string, Partial<typeof S>> = {
  fig2a: { mode: "theta", wdir: "x", pk: 90 }, fig2b: { mode: "theta", wdir: "x", pk: 90 },
  fig3a: { mode: "theta", wdir: "z", pk: 180 }, fig3b: { mode: "theta", wdir: "z", pk: 90 },
  fig4a: { mode: "dl", wdir: "x", pk: 94 }, fig4b: { mode: "dl", wdir: "z", pk: 94 }, fig5: { mode: "dl", wdir: "xz", pk: 94 },
  fig6a: { mode: "theta", weps: 0.99, wdir: "x", pe: 1, pk: 90 }, fig6b: { mode: "theta", weps: 0.99, wdir: "x", pk: 90 },
  fig7a: { mode: "theta", weps: 0.99, wdir: "z", pe: 1, pk: 90 }, fig7b: { mode: "theta", weps: 0.99, wdir: "z", pk: 90 },
  fig8a: { mode: "scatter", h: 100 }, fig8b: { mode: "scatter", h: 100 },
};
function openFig(f: string) {
  const to = FIGS[f];
  if (!to) return;
  Object.assign(S, to.mode === "scatter" ? {} : PAPER0, to);
  scrollTo(0, 0);
  render();
}
function paperRow(parent: HTMLElement, figs: [string, string][]) {
  const row = el("div", "paper", "", parent);
  el("span", "paper-l", "Figures of Cambaliza & Saloma (2000); click one to open its settings", row);
  const box = el("div", "paper-figs", "", row);
  for (const [f, cap] of figs) {
    const fig = el("figure", "", "", box);
    const img = el("img", "", "", fig) as HTMLImageElement;
    img.src = `./img/paper/${f}.png`; img.alt = cap;
    el("figcaption", "", cap, fig);
    if (FIGS[f]) {
      fig.classList.add("go");
      fig.tabIndex = 0;
      fig.title = "Open the settings of this figure";
      fig.onclick = () => openFig(f);
      fig.onkeydown = (e) => { if (e.key === "Enter") openFig(f); };
    }
  }
}

// controls shared by the views that compute the PSF here
function psfCtl(c: HTMLElement, rotation: boolean, pulses = true) {
  if (pulses) {
    seg(c, "Beams", "tau", [[0, "continuous"], [100, "100-fs pulses"], [20, "20 fs"], [10, "10 fs"]]);
    if (S.tau) el("p", "hint", "With transform-limited pulses at zero delay, each product of the two beams is weighted by how much the pulses overlap in time at that point. The tab Femtosecond pulses has the sweep against τ.", c);
  }
  seg(c, "2D map", "map", [["heat", "heat map"], ["contour", "contours"]]);
  seg(c, "Map scale", "msc", [["peak", "of its own peak"], ["energy", "per unit total energy"]]);
  if (S.msc === "energy") el("p", "hint", "Each map divided by its total energy over the window (µm⁻²); the two maps share one scale, so their peaks compare directly.", c);
  el("p", "hint", S.map === "contour"
    ? "The contours are at 1, 10, 20, 40, 60 and 80% of the peak, labelled on the lines; the orange line is 50%, where the FWHM is measured."
    : "The white line is half of the peak, where the FWHM is measured.", c);
  const g = el("div", "ctl", "", c);
  el("span", "ctl-l", "Cuts", g);
  el("p", "hint", `Across at z = ${S.cz.toFixed(2)} µm, along at x = ${S.cx.toFixed(2)} µm. Drag on a map to move them.`, g).id = "cutpos";
  const b = el("button", "reset", "Back to the focus (0, 0)", g) as HTMLButtonElement;
  b.type = "button"; b.disabled = !S.cx && !S.cz;
  b.onclick = () => { S.cx = 0; S.cz = 0; render(); };
  if (rotation) {
    seg(c, "Rotation of beam 2", "rot", [["xz", "(x, z), a turned lens"], ["uv", "(u, v), as printed in Eq. 1"]]);
    if (S.rot === "uv") el("p", "hint", "Eq. 1 as printed turns the optical coordinates; equal to the real-space turn only at θ = 0 and π. The published Fig. 3b follows (x, z).", c);
  }
  seg(c, "2PE plotted as", "pe", [[4, "|U₁ + U₂|⁴ (Eq. 6)"], [1, "|U₁ + U₂|² (Figs. 6a, 7a)"]]);
}

// cuts at (cx, cz): intensity relative to the peak of the map (the focus), width at half of the cut's own maximum
const width = (s: number[], y: number[]) => { const h = halfPoints(y); return h ? (h[1] - h[0]) * (s[1] - s[0]) : NaN; };
// Paraxial signals are computed here; Richards–Wolf ones in a worker, one request at a time (a newer request replaces a waiting one).
type Opt = Parameters<typeof signals>[2];
type Job = { x: number[]; z: number[]; o: Opt };
type Sig = { c2: number[]; p2: number[] };
// If the worker fails or does not answer within 4 s, everything is computed on the main thread from then on.
let worker: Worker | null = null, dead = new URLSearchParams(location.search).has("noworker"), timer = 0;   // ?noworker: main thread only
function getWorker() {                                    // created on the first vector request
  if (!worker && !dead) {
    try {
      worker = new Worker(new URL("./rw.worker.ts", import.meta.url), { type: "module" });
      worker.onmessage = (e: MessageEvent<{ out: Sig[] }>) => finish(e.data.out);
      worker.onerror = fail;
    } catch { dead = true; }
  }
  return dead ? null : worker;
}
let busy = false, nextReq: { jobs: Job[]; done: (r: Sig[] | null) => void } | null = null, current: { jobs: Job[]; done: (r: Sig[] | null) => void } | null = null;
const local = (jobs: Job[]) => jobs.map((j) => rwSignals(j.x, j.z, j.o));
function finish(out: Sig[]) {
  clearTimeout(timer);
  current?.done(out); current = null; busy = false;
  if (nextReq) { const r = nextReq; nextReq = null; send(r.jobs, r.done); }
}
function fail() { dead = true; worker?.terminate(); if (current) finish(local(current.jobs)); }
function send(jobs: Job[], done: (r: Sig[] | null) => void) {
  const w = getWorker();
  if (!w) { done(local(jobs)); return; }
  busy = true; current = { jobs, done };
  timer = window.setTimeout(fail, 4000);
  w.postMessage({ id: 0, jobs });
}
function compute(jobs: Job[], rw: boolean): Promise<Sig[] | null> {
  if (!rw) return Promise.resolve(jobs.map((j) => signals(j.x, j.z, j.o)));
  return new Promise((done) => { if (busy) { nextReq?.done(null); nextReq = { jobs, done }; } else send(jobs, done); });
}
const useRW = (na: number) => S.mdl === "rw" || na > 0.5 + 1e-9;   // the paraxial model only up to NA 0.5
const modelName = (rw: boolean) => (rw ? "vector (Richards–Wolf), polarized along y" : "paraxial scalar model (Eqs. 1–6)");
// cuts at (cx, cz): the last point of each is the focus, so the profiles come out relative to the peak of the map
function cutJobs(o: Opt, hx: number, hz: number, N: number) {
  const xs = Array.from({ length: N }, (_, i) => -hx + (2 * hx * i) / (N - 1)), zs = Array.from({ length: N }, (_, i) => -hz + (2 * hz * i) / (N - 1));
  return { xs, zs, jobs: [{ x: [...xs, 0], z: [...xs.map(() => S.cz), 0], o }, { x: [...zs.map(() => S.cx), 0], z: [...zs, 0], o }] as Job[] };
}
const atPeak = (r: Sig, N: number) => ({ p2: r.p2.slice(0, N).map((v) => v / r.p2[N]), c2: r.c2.slice(0, N).map((v) => v / r.c2[N]) });
function modelCtl(c: HTMLElement, naKey: "lna" | "wna", nKey: "n" | "wn") {
  const n = S[nKey] as number;
  slider(c, "NA", naKey, 0.1, +(0.95 * n).toFixed(2), 0.05, (v) => v.toFixed(2));
  const na = S[naKey] as number, high = na > 0.5 + 1e-9;
  const g = el("div", "ctl", "", c);
  el("span", "ctl-l", "Model", g);
  const box = el("div", "seg", "", g);
  for (const [v, t] of [["par", "paraxial scalar"], ["rw", "vector (Richards–Wolf)"]]) {
    const b = el("button", "", t, box) as HTMLButtonElement;
    b.type = "button"; b.setAttribute("aria-pressed", String(v === (high ? "rw" : S.mdl)));
    b.disabled = v === "par" && high;
    b.onclick = () => set("mdl", v);
  }
  el("p", "hint", high ? "Above NA 0.5 only the vector model is used (the paraxial model is kept to NA ≤ 0.5)."
    : "The vector model computes the Richards–Wolf focus of each lens, polarized along y, in the browser.", c);
}
/** Scales for the two maps (2PE, 2CE): of the own peak, or per unit total energy with a shared colorbar. */
function mapScales(maps: ArrayLike<number>[], dA: number) {
  if (S.msc !== "energy") return maps.map(() => ({ f: 1, vmax: 1, unit: "of peak" }));
  const f = maps.map((m) => { let t = 0; for (let i = 0; i < m.length; i++) t += m[i]; return 1 / (t * dA); });
  const vmax = Math.max(...f);
  return f.map((fi) => ({ f: fi, vmax, unit: "µm⁻²" }));
}
function onCut(a: number, b: number) {
  S.cx = Math.round(a * 100) / 100; S.cz = Math.round(b * 100) / 100;
  const t = document.getElementById("cutpos");
  if (t) t.textContent = `Across at z = ${S.cz.toFixed(2)} µm, along at x = ${S.cx.toFixed(2)} µm. Drag on a map to move them.`;
  const r = document.querySelector<HTMLButtonElement>("button.reset");
  if (r) r.disabled = !S.cx && !S.cz;
  redraw();
}
const cutLabel = (ax: "x" | "z") => (ax === "x" ? `x (µm), across at z = ${S.cz ? S.cz.toFixed(2) : 0}` : `z (µm), along at x = ${S.cx ? S.cx.toFixed(2) : 0}`);

// ---- live: paraxial PSF computed in the browser ----
let liveState: { setup: Setup; heats: Heat[]; cuts: LineChart[]; paper: HTMLElement; read: HTMLElement } | null = null;
let pending = 0;
function live() {
  const c = $("controls");
  modelCtl(c, "lna", "n");
  slider(c, "Angle θ between the lenses", "th", 0, 180, 5, (v) => `${v}°`);
  slider(c, "Wavelength difference Δλ", "dl", 0, 100, 1, (v) => { const [a, b] = pair(v / 1000); return `${v} nm (${(a * 1000).toFixed(0)} + ${(b * 1000).toFixed(0)})`; });
  seg(c, "Pupil", "eps", [[0, "circular"], [0.5, "ε 0.5"], [0.9, "ε 0.9"], [0.99, "ε 0.99"]]);
  seg(c, "Medium", "n", [[1, "air"], [1.33, "water"]]);
  psfCtl(c, !useRW(S.lna));
  const setup = new Setup(el("div", "setup-side", "", c));                // small sketch of the settings, in the side panel
  if (liveState) liveState.setup = setup;
  if (!liveState) {
    const a = layout("live");
    const maps = el("div", "top", "", a);
    const heats = [new Heat(cell(maps, "map"), "2PE, x–z"), new Heat(cell(maps, "map"), "2CE, x–z")];
    for (const h of heats) h.onCut = onCut;
    const cuts = el("div", "cuts", "", a);
    const lc = [new LineChart(cell(cuts)), new LineChart(cell(cuts))];
    const read = note(a, "");
    const paper = el("div", "", "", a);
    liveState = { setup, heats, cuts: lc, paper, read };
  }
  cancelAnimationFrame(pending);
  pending = requestAnimationFrame(drawLive);
}
let liveGen = 0;
async function drawLive() {
  if (!liveState) return;
  const gen = ++liveGen, st = liveState;
  const na = S.lna, rw = useRW(na), th = -(S.th * Math.PI) / 180, [l1, l2] = pair(S.dl / 1000);   // −θ: L2 on the right, as in the deck
  st.setup.draw(th, Math.min(0.999, na / S.n), S.eps, l1, l2);
  const o: Opt = { na, n: S.n, theta: th, eps: S.eps, l1, l2, lp: 0.7, rot: rw ? "xz" : (S.rot as "xz" | "uv"), pe: S.pe, tau: S.tau };
  const sx = Math.max(0.8, Math.min(8, 2.2 * (0.5 / na) ** 1.5 * S.n)), sz = sx;    // equal scales, so angles in the maps are true
  const NX = 111, NZ = 151, X: number[] = [], Z: number[] = [];
  for (let i = 0; i < NZ; i++) for (let j = 0; j < NX; j++) { X.push(-sx + (2 * sx * j) / (NX - 1)); Z.push(-sz + (2 * sz * i) / (NZ - 1)); }
  const cj = cutJobs(o, sx, sz, 601);
  if (rw) st.read.textContent = "Computing the vector focus…";
  const cj0 = S.tau ? cutJobs({ ...o, tau: 0 }, sx, sz, 601) : null;            // continuous beams, the reference
  const res = await compute([{ x: X, z: Z, o: { ...o, nr: 81 } }, ...cj.jobs, ...(cj0 ? cj0.jobs : [])], rw);
  if (!res || gen !== liveGen || liveState !== st) return;
  const [map, ra, rl] = res, ax = atPeak(ra, 601), al = atPeak(rl, 601), { xs, zs } = cj;
  const cut = { x: S.cx, z: S.cz };
  const sc = mapScales([map.p2, map.c2], ((2 * sx) / (NX - 1)) * ((2 * sz) / (NZ - 1)));
  st.heats[0].draw(map.p2, NX, NZ, [-sx, sx], [-sz, sz], S.map as "heat", cut, sc[0]);
  st.heats[1].draw(map.c2, NX, NZ, [-sx, sx], [-sz, sz], S.map as "heat", cut, sc[1]);
  const ser = (s: number[], y: number[], sig: "2PE" | "2CE"): Series =>
    ({ id: sig, label: `${sig} (FWHM ${um(width(s, y))})`, color: SIG[sig], pts: s.map((v, i) => [v, y[i]] as [number, number]) });
  const ref = (s: number[], r: Sig | undefined): Series[] => (r ? (["2PE", "2CE"] as const).map((sig) => {
    const y = atPeak(r, 601)[sig === "2PE" ? "p2" : "c2"];
    return { id: `cw${sig}`, label: `${sig} continuous (FWHM ${um(width(s, y))})`, color: SIG[sig], dash: true, width: 1.6, pts: s.map((v, i) => [v, y[i]] as [number, number]) };
  }) : []);
  const tl = (y: Series) => (S.tau ? { ...y, label: y.label.replace(/^(2PE|2CE)/, `$1 ${S.tau} fs`) } : y);
  st.cuts[0].update([tl(ser(xs, ax.p2, "2PE")), tl(ser(xs, ax.c2, "2CE")), ...ref(xs, res[3])], { xlabel: cutLabel("x"), ylabel: "Intensity (of the peak)", ydomain: [0, 1.02] });
  st.cuts[1].update([tl(ser(zs, al.p2, "2PE")), tl(ser(zs, al.c2, "2CE")), ...ref(zs, res[4])], { xlabel: cutLabel("z"), ylabel: "Intensity (of the peak)", ydomain: [0, 1.02] });
  const overlap = S.th > 0 && S.th < 180 && Math.asin(Math.min(1, na / S.n)) > (Math.min(S.th, 180 - S.th) * Math.PI) / 360;
  st.read.textContent = `${modelName(rw)[0].toUpperCase() + modelName(rw).slice(1)}, computed here, NA ${na.toFixed(2)}, 2CE ${(l1 * 1000).toFixed(0)} + ${(l2 * 1000).toFixed(0)} nm, 2PE 700 nm${S.pe === 1 ? " plotted as |U₁ + U₂|²" : ""}; beam 2 is turned by θ in ${o.rot === "uv" ? "(u, v), as Eq. 1 is printed" : "(x, z)"}${overlap ? ". At this NA and θ the two cones overlap, so real lenses would not fit" : ""}`;
  st.paper.replaceChildren();
  const pub = !rw && Math.abs(na - 0.5) < 1e-9 && S.n === 1 && S.dl === 94 && [0, 90, 180].includes(S.th) && (S.eps === 0 || S.eps === 0.99);
  if (pub) {
    const [a, b] = S.eps ? ["6", "7"] : ["2", "3"];
    paperRow(st.paper, [[`fig${a}a`, `Fig. ${a}a, 2PE across`], [`fig${a}b`, `Fig. ${a}b, 2CE across`],
      [`fig${b}a`, `Fig. ${b}a, 2PE along`], [`fig${b}b`, `Fig. ${b}b, 2CE along`]]);
    if (S.eps) note(st.paper, "Published 2PE curves in Figs. 6a and 7a are |U₁ + U₂|², not Eq. 6: set “2PE plotted as” to |U₁ + U₂|² to match them.");
  }
}

// ---- against NA: precomputed scalar and vector, click a point for the PSF ----
// The paper's comparisons (ratios of two widths), with the value stated in the text (star) and the same ratio measured on the
// published curves at NA 0.5 (cross), as on the deck's comparison slides.
type Side = [Signal, Axis, Theta, Pupil];
const CMP: Record<string, { label: string; a: Side; b: Side; tr?: "less" | "more"; star?: number; cross?: number }> = {
  r1: { label: "2PE spot, θ = π/2 over θ = 0 (p. 28)", a: ["2PE", "x", "pi2", "circ"], b: ["2PE", "x", "0", "circ"], star: 0.67, cross: 0.49 },
  r2: { label: "2CE spot over 2PE spot, θ = π/2 (p. 29)", a: ["2CE", "x", "pi2", "circ"], b: ["2PE", "x", "pi2", "circ"], star: 1.58, cross: 2.98 },
  r3: { label: "2CE DOF over 2PE DOF, θ = π/2", a: ["2CE", "z", "pi2", "circ"], b: ["2PE", "z", "pi2", "circ"] },
  a1: { label: "Annular 2CE spot, θ = 0 over θ = π/2 (Fig. 6b, p. 31)", a: ["2CE", "x", "0", "ann"], b: ["2CE", "x", "pi2", "ann"], star: 0.82, cross: 0.673 },
  a2: { label: "Annular, θ = π/2: 2PE spot narrower than 2CE, 1 − ratio (p. 31)", a: ["2PE", "x", "pi2", "ann"], b: ["2CE", "x", "pi2", "ann"], tr: "less", star: 0.35, cross: 0.34 },
  a3: { label: "θ = π/2: 2CE DOF shorter, annular than circular, 1 − ratio (p. 32)", a: ["2CE", "z", "pi2", "ann"], b: ["2CE", "z", "pi2", "circ"], tr: "less", star: 0.4, cross: 0.295 },
  a4: { label: "θ = π/2: annular 2CE DOF longer than circular 2PE, ratio − 1 (p. 32)", a: ["2CE", "z", "pi2", "ann"], b: ["2PE", "z", "pi2", "circ"], tr: "more", star: 0.2, cross: 0.848 },
};
const sideLabel = (d: Side) => `${d[0]}, ${TH[d[2]].label}, ${d[3] === "ann" ? "annular" : "circular"}`;
let naCharts: { left: LineChart; x: LineChart; z: LineChart; paper: HTMLElement; title: HTMLElement; how: HTMLElement; heats: Heat[]; mapNote: HTMLElement } | null = null;
function againstNA() {
  const c = $("controls");
  const cmp = S.metric === "cmp";
  seg(c, "Plot", "metric", [["width", "width"], ["cmp", "paper's comparisons"], ["gap", "scalar / vector"], ["nrmse", "NRMSE"], ["F", "Linfoot F (fidelity)"],
    ["C", "Linfoot C (structure)"], ["Q", "Linfoot Q (correlation)"], ["lobe", "side-lobe distance"], ["lobeh", "side-lobe height"]]);
  seg(c, "How it is measured", "how", [[0, "hide"], [1, "show, with equations"]]);
  if (cmp) {
    seg(c, "Comparison", "cmp", Object.entries(CMP).map(([k, v]) => [k, v.label] as [string, string]));
    el("p", "hint", "The star is the value stated in the text, and the cross is the same ratio measured on the published curves (NA 0.5, air).", c);
  } else seg(c, "Signal", "sig", [["2PE", "2PE"], ["2CE", "2CE"]]);
  seg(c, "Medium", "med", [["air", "air"], ["water", "water"]]);
  if (!cmp) multi(c, "Angle", "ths", [["0", "0", "var(--t0)"], ["pi2", "π/2", "var(--t1)"], ["pi", "π", "var(--t2)"]]);
  seg(c, "Model", "model", [["both", "both"], ["vector", "vector"], ["scalar", "scalar"]]);
  if (!cmp) seg(c, "Pupil", "pupil", [["circ", "circular"], ["ann", "annular"]]);
  seg(c, "Input", "input", [["uni", "uniform"], ["gau", "Gaussian"]]);
  if (!cmp) seg(c, "Direction", "axis", [["x", "across"], ["z", "along"]]);
  seg(c, "2D map", "map", [["heat", "heat map"], ["contour", "contours"]]);
  seg(c, "Map scale", "msc", [["peak", "of its own peak"], ["energy", "per unit total energy"]]);
  if (!naCharts) {
    const a = layout("two");
    const how = el("div", "how", "", a);
    const L = cell(el("div", "stack col", "", a), "big");          // left column: a drop zone for panels too
    const R = el("div", "stack", "", a);
    const title = el("h2", "cell-title", "", R);
    const maps = el("div", "stack2", "", R);
    const heats = [new Heat(cell(maps, "map"), ""), new Heat(cell(maps, "map"), "")];
    for (const hm of heats) hm.onCut = onCut;
    const mapNote = note(R, "");
    const cx = cell(R), cz = cell(R);
    cx.id = "c-nax"; cz.id = "c-naz";                                // profiles across and along the axis (a highlight may scroll to them)
    naCharts = { left: new LineChart(L), x: new LineChart(cx), z: new LineChart(cz), paper: el("div", "", "", a), title, how, heats, mapNote };
    naCharts.left.onPick = (v) => set("na", v);
  }
  drawNA();
}
async function drawNA() {
  if (!naCharts) return;
  const ths = S.ths.split(".").filter(Boolean) as Theta[];
  const models = S.model === "both" ? ["vector", "scalar"] : [S.model];
  const sel: Series[] = [];
  const lab = (t: Theta) => (S.sig === "2CE" && t === "0" ? "θ = 0" : TH[t].label);
  const C = CMP[S.metric === "cmp" ? S.cmp : ""];
  if (C) for (const m of models) {
    const wa = new Map((data.widths[wkey(C.a[0], C.a[1], C.a[2], m as "vector", C.a[3], S.input, S.med)] ?? []).map((p) => [p[0], p[1]]));
    const wb = data.widths[wkey(C.b[0], C.b[1], C.b[2], m as "vector", C.b[3], S.input, S.med)] ?? [];
    const f = (r: number) => (C.tr === "less" ? 1 - r : C.tr === "more" ? r - 1 : r);
    sel.push({ id: `cmp${m}`, label: m === "vector" ? "Vector" : "Scalar", color: m === "vector" ? "var(--t2)" : "var(--t1)", dash: m === "scalar", dots: m === "vector",
      pts: wb.filter((p) => wa.has(p[0])).map((p) => [p[0], f(wa.get(p[0])! / p[1])]) });
  }
  for (const t of C ? [] : ths) {
    const w = (m: string) => data.widths[wkey(S.sig, S.axis, t, m as "vector", S.pupil, S.input, S.med)] ?? [];
    const mt = metrics[`${S.sig}|${S.axis}|${t}|${S.pupil}|${S.input}|${S.med}`] ?? [];
    if (S.metric === "width") for (const m of models)
      sel.push({ id: `${t}${m}`, label: `${lab(t)}, ${m}`, color: TH[t].color, dash: m === "scalar", dots: m === "vector", pts: w(m) });
    else if (S.metric === "gap") {
      const v = new Map(w("vector").map((p) => [p[0], p[1]]));
      sel.push({ id: t, label: lab(t), color: TH[t].color, dots: true, pts: w("scalar").filter((p) => v.has(p[0])).map((p) => [p[0], 100 * (p[1] / v.get(p[0])! - 1)]) });
    } else {
      const col = { nrmse: 1, F: 2, C: 3, Q: 4, lobe: 5, lobeh: 6 }[S.metric as "nrmse"];
      sel.push({ id: t, label: lab(t), color: TH[t].color, dots: true, pts: mt.map((r) => [r[0] as number, (r[col] ?? NaN) as number]) });
    }
  }
  const yl = { width: S.axis === "x" ? "FWHM across (µm)" : "Depth of focus (µm)", gap: "Scalar over vector − 1 (%)",
    nrmse: "NRMSE, scalar against vector (%)", F: "Linfoot fidelity F", C: "Linfoot structural content C", Q: "Linfoot correlation quality Q",
    lobe: "First side-lobe distance (λ/n)", lobeh: "First side-lobe height (of the peak)", cmp: C ? C.label : "" }[S.metric]!;
  const marks = C && S.med === "air" && S.input === "uni" ? [
    ...(C.star !== undefined ? [{ x: 0.5, y: C.star, label: "Stated in the text", shape: "star" as const }] : []),
    ...(C.cross !== undefined ? [{ x: 0.5, y: C.cross, label: "On the published curves", shape: "cross" as const }] : [])] : undefined;
  naCharts.left.update(sel, { xlabel: "NA (click a point)", ylabel: yl, ylog: S.metric === "width", marker: S.na, pickable: true, marks,
    ref: S.metric === "gap" ? 0 : "FCQ".includes(S.metric) ? 1 : undefined, band: S.metric === "gap" ? [-5, 5] : undefined });

  const nas = data.meta.na[S.med];
  if (!nas.includes(S.na)) S.na = nas.reduce((a, b) => (Math.abs(b - S.na) < Math.abs(a - S.na) ? b : a));
  const prof = await loadProfiles(S.med, S.na);
  naCharts.title.textContent = C ? `${C.label}: profiles at NA ${S.na} in ${S.med}` : `${S.sig} at NA ${S.na} in ${S.med} (n = ${data.meta.n[S.med]})`;
  for (const ax of ["x", "z"] as Axis[]) {
    const [half, npt] = prof[`grid|${ax}`];
    const s = Array.from({ length: npt }, (_, i) => -half + (2 * half * i) / (npt - 1));
    const cs: Series[] = [];
    if (C) for (const [d, col] of [[C.a, "#f28e2b"], [C.b, "var(--t0)"]] as [Side, string][]) for (const m of models) {
      const y = prof[`${d[0]}|${ax}|${d[2]}|${m}|${d[3]}|${S.input}`];
      if (y) cs.push({ id: `${d.join()}${m}`, label: `${sideLabel(d)}, ${m} (${um(fwhm(s, y))})`, color: col, dash: m === "scalar", pts: s.map((v, i) => [v, y[i]]) });
    }
    else for (const t of ths) for (const m of models) {
      const y = prof[`${S.sig}|${ax}|${t}|${m}|${S.pupil}|${S.input}`];
      if (y) cs.push({ id: `${t}${m}`, label: `${lab(t)}, ${m} (${um(fwhm(s, y))})`, color: TH[t].color, dash: m === "scalar", pts: s.map((v, i) => [v, y[i]]) });
    }
    naCharts[ax].update(cs, { xlabel: ax === "x" ? "x (µm), across at z = 0" : "z (µm), along at x = 0", ylabel: "Intensity", ydomain: [0, 1.02] });
  }
  // 2D maps at the picked NA, computed here: scalar (paraxial) and vector (Richards–Wolf); for a comparison, the two vector maps
  {
    const st = naCharts, n = data.meta.n[S.med], TH0: Record<Theta, number> = { "0": 0, pi2: Math.PI / 2, pi: Math.PI };
    const side: Side = C ? C.a : [S.sig, S.axis, ths[0] ?? "0", S.pupil];
    const opt = (d: Side): Opt => ({ na: S.na, n, theta: -TH0[d[2]], eps: d[3] === "ann" ? 0.99 : 0, l1: 0.75, l2: 0.656, lp: 0.7, pe: 4 });
    const hx = prof["grid|x"][0], hz = prof["grid|z"][0], h = Math.max(hx, Math.min(hz, 2.5 * hx)), NX = 91, X: number[] = [], Z: number[] = [];
    for (let i = 0; i < NX; i++) for (let j = 0; j < NX; j++) { X.push(-h + (2 * h * j) / (NX - 1)); Z.push(-h + (2 * h * i) / (NX - 1)); }
    const pick = (d: Side, r: Sig) => (d[0] === "2PE" ? r.p2 : r.c2);
    const lab = (d: Side) => `${d[0]}, ${TH[d[2]].label}${d[3] === "ann" ? ", annular" : ""}`;
    let maps: [number[], string][] | null = null;
    if (C) {
      const r = await compute([{ x: X, z: Z, o: opt(C.a) }, { x: X, z: Z, o: opt(C.b) }], true);
      if (r) maps = [[pick(C.a, r[0]), `${lab(C.a)}, vector`], [pick(C.b, r[1]), `${lab(C.b)}, vector`]];
    } else {
      const sc = signals(X, Z, { ...opt(side), nr: 101 }), r = await compute([{ x: X, z: Z, o: opt(side) }], true);
      if (r) maps = [[pick(side, sc), `${lab(side)}, scalar`], [pick(side, r[0]), `${lab(side)}, vector`]];
    }
    if (maps && naCharts === st) {
      const sc = mapScales(maps.map((mm) => mm[0]), ((2 * h) / (NX - 1)) ** 2);
      maps.forEach(([v, t], k) => { st.heats[k].title = t; st.heats[k].draw(v, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc[k]); });
      st.mapNote.textContent = (S.input === "gau" ? "The maps use uniform input; the Gaussian input is in the profiles only. " : "") +
        "Maps computed here at the picked NA; 2D map style and scale as on the replication tabs.";
    }
  }
  // how it is measured, drawn on the profile at the picked NA
  naCharts.how.hidden = !S.how;
  if (S.how) {
    const side: Side = C ? C.a : [S.sig, S.axis, ths[0] ?? "0", S.pupil];
    const ax = side[1], [hh, np] = prof[`grid|${ax}`], s = Array.from({ length: np }, (_, i) => -hh + (2 * hh * i) / (np - 1));
    const key = (m: string) => prof[`${side[0]}|${ax}|${side[2]}|${m}|${side[3]}|${S.input}`];
    if (key("vector")) renderHow(naCharts.how, S.metric, { s, vec: key("vector"), sca: key("scalar"), axis: ax, lamn: 0.7 / data.meta.n[S.med],
      label: `${sideLabel(side)}, ${ax === "x" ? "across" : "along"} the axis, NA ${S.na} in ${S.med}` });
  }
  naCharts.paper.replaceChildren();
  if (S.na === 0.5 && S.med === "air" && S.input === "uni" && !C) {
    const [a, b] = S.pupil === "ann" ? ["6", "7"] : ["2", "3"], k = S.sig === "2PE" ? "a" : "b";
    paperRow(naCharts.paper, [[`fig${a}${k}`, `Fig. ${a}${k}, across`], [`fig${b}${k}`, `Fig. ${b}${k}, along`]]);
  }
  writeHash();
}

// ---- sweeps at one NA: width against θ, Δλ or the pupil; click a value for its PSF (paraxial, computed here) ----
type Sweep = "theta" | "dl" | "eps" | "pulses";
const SW: Record<Sweep, { label: string; unit: string; vals: number[]; fmt: (v: number) => string }> = {
  theta: { label: "Angle θ between the lenses", unit: "°", vals: Array.from({ length: 37 }, (_, i) => 5 * i), fmt: (v) => `${v}°` },
  dl: { label: "Wavelength difference Δλ", unit: "nm", vals: [...new Set([...Array.from({ length: 26 }, (_, i) => 4 * i), 10, 39, 94])].sort((x, y) => x - y), fmt: (v) => `${v} nm` },   // + the gaps of Figs. 4a and 4b
  eps: { label: "Obstruction ratio ε of the pupils", unit: "", vals: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 0.99], fmt: (v) => `ε ${v}` },
  pulses: { label: "Pulse duration τ", unit: "fs", vals: [5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500], fmt: (v) => `τ = ${v} fs` },
};
let wState: { kind: Sweep; left: LineChart; heats: Heat[]; cuts: LineChart[]; title: HTMLElement; paper: HTMLElement; hiNA?: LineChart[]; ref?: LineChart } | null = null;
function sweepView(kind: Sweep) {
  const c = $("controls");
  modelCtl(c, "wna", "wn");
  if (kind === "pulses") slider(c, "Angle θ between the lenses", "pth", 0, 180, 5, (v) => `${v}°`);
  else if (kind !== "theta") seg(c, "Angle θ", "wth", [[0, "0"], [90, "π/2"], [180, "π"]]);
  if (kind !== "dl") slider(c, "Wavelength difference Δλ", "wdl", 0, 100, 1, (v) => { const [a, b] = pair(v / 1000); return `${v} nm (${(a * 1000).toFixed(0)} + ${(b * 1000).toFixed(0)})`; });
  if (kind !== "eps") seg(c, "Pupil", "weps", [[0, "circular"], [0.5, "ε 0.5"], [0.9, "ε 0.9"], [0.99, "ε 0.99"]]);
  seg(c, "Medium", "wn", [[1, "air"], [1.33, "water"]]);
  seg(c, "Width", "wdir", [["x", "across (FWHM)"], ["z", "along (DOF)"], ["xz", "both"]]);
  psfCtl(c, kind === "theta" && !useRW(S.wna), kind !== "pulses");
  if (kind === "pulses") seg(c, "Left chart", "pplot", [["width", "widths (µm)"], ["ratio", "pulsed / continuous"]]);
  if (kind === "pulses") el("p", "hint", "The pulses are transform-limited Gaussians at zero delay, computed in closed form from their overlap in time at each point; this is within 5% of the full frequency sum at 10 fs. Dashed lines are continuous beams.", c);
  el("p", "hint", "Computed in the browser. Click a point for the PSF at that value.", c);
  if (!wState || wState.kind !== kind || (wState.heats.length > 2) !== (kind === "pulses" || !!S.tau)) {
    const a = layout("two");
    const L = cell(el("div", "stack col", "", a), "big");          // left column: a drop zone for panels too
    const R = el("div", "stack", "", a);
    const title = el("h2", "cell-title", "", R);
    const maps = el("div", "stack2", "", R);
    const heats = [new Heat(cell(maps, "map"), "2PE, x–z"), new Heat(cell(maps, "map"), "2CE, x–z")];
    if (kind === "pulses" || S.tau) heats.push(new Heat(cell(maps, "map"), "2PE, continuous"), new Heat(cell(maps, "map"), "2CE, continuous"));
    for (const hm of heats) hm.onCut = onCut;
    const cuts = [new LineChart(cell(R)), new LineChart(cell(R))];
    wState = { kind, left: new LineChart(L), heats, cuts, title, paper: el("div", "paper", "", a) };
    if (kind === "pulses") {                                              // the full frequency sum, precomputed (vector), θ = π
      const w = el("div", "wide stack", "", a);
      el("h2", "cell-title", "Depth of focus, pulsed over continuous, against NA at θ = π, from the full frequency sum with the vector model", w);
      wState.ref = new LineChart(cell(w));
    }
    if (kind === "dl") {                                                  // Δλ above NA 0.5: precomputed vector and scalar
      const w = el("div", "wide stack", "", a);
      el("h2", "cell-title", "2CE width at θ = π/2 and higher NA, relative to its value at Δλ = 10 nm", w);
      const g = el("div", "stack2", "", w);
      wState.hiNA = [new LineChart(cell(g)), new LineChart(cell(g))];
    }
    wState.left.onPick = (v) => { S.pk = v; redraw(); };
  }
  cancelAnimationFrame(pending);
  pending = requestAnimationFrame(drawSweep);
}
function sweepOpts(kind: Sweep, v: number) {
  const th = kind === "theta" ? v : kind === "pulses" ? S.pth : S.wth, dl = kind === "dl" ? v : S.wdl, eps = kind === "eps" ? v : S.weps;
  const [l1, l2] = pair(dl / 1000);
  return { na: S.wna, n: S.wn, theta: -(th * Math.PI) / 180, eps, l1, l2, lp: 0.7, rot: (kind === "theta" && !useRW(S.wna) ? S.rot : "xz") as "xz" | "uv", pe: S.pe,
    tau: kind === "pulses" ? v : S.tau };
}
let sweepGen = 0;
async function drawSweep() {
  if (!wState) return;
  const gen = ++sweepGen, ws = wState;
  const kind = ws.kind, sw = SW[kind], rw = useRW(S.wna);
  if (!sw.vals.includes(S.pk)) S.pk = kind === "theta" ? 90 : kind === "dl" ? 94 : kind === "pulses" ? 10 : 0.99;
  const half = (ax: string, o: ReturnType<typeof sweepOpts>) => {
    const along = ax === "z", wide = o.eps > 0.5 && along;
    return Math.min(40, (along ? 4 * (0.5 / o.na) ** 2 : 1.4 * (0.5 / o.na)) * o.n * (wide ? 6 : 1));
  };
  // jobs: widths against the swept value (at the focus), the map and the two cuts at the picked value
  const N = rw ? 401 : 801, dirs = S.wdir === "xz" ? ["x", "z"] : [S.wdir];
  const jobs: Job[] = [], grid: { v: number; ax: string; s: number[] }[] = [];
  for (const v of sw.vals) {
    const o = sweepOpts(kind, v);
    for (const ax of dirs) {
      const h = half(ax, o), sv = Array.from({ length: N }, (_, i) => -h + (2 * h * i) / (N - 1)), zero = sv.map(() => 0);
      jobs.push(ax === "x" ? { x: sv, z: zero, o: { ...o, nr: 101 } } : { x: zero, z: sv, o: { ...o, nr: 101 } });
      grid.push({ v, ax, s: sv });
    }
  }
  const cw: { ax: string; s: number[] }[] = [];
  if (kind === "pulses") for (const ax of dirs) {                     // continuous beams, for reference
    const oc = { ...sweepOpts(kind, 0), tau: 0 }, h = half(ax, oc), sv = Array.from({ length: N }, (_, i) => -h + (2 * h * i) / (N - 1)), zero = sv.map(() => 0);
    jobs.push(ax === "x" ? { x: sv, z: zero, o: { ...oc, nr: 101 } } : { x: zero, z: sv, o: { ...oc, nr: 101 } });
    cw.push({ ax, s: sv });
  }
  const o = sweepOpts(kind, S.pk);
  const perp = Math.abs(Math.sin(o.theta)) > 0.7;                       // crossed beams: a compact spot
  const h = Math.max(0.6, perp ? 1.6 * (0.5 / o.na) * o.n : Math.min(8, Math.max(half("x", o), Math.min(half("z", o), 3 * half("x", o))))), NX = 101;
  const X: number[] = [], Z: number[] = [];
  for (let i = 0; i < NX; i++) for (let j = 0; j < NX; j++) { X.push(-h + (2 * h * j) / (NX - 1)); Z.push(-h + (2 * h * i) / (NX - 1)); }
  const cj = cutJobs(o, half("x", o), half("z", o), N);
  if (rw) ws.title.textContent = "Computing the vector focus…";
  const pulsed = kind === "pulses" || !!S.tau;
  const cj0 = pulsed ? cutJobs({ ...o, tau: 0 }, half("x", o), half("z", o), N) : null;   // continuous beams, the reference
  const res = await compute([...jobs, { x: X, z: Z, o: { ...o, nr: 81 } }, ...cj.jobs, ...(cj0 ? cj0.jobs : []),
    ...(pulsed ? [{ x: X, z: Z, o: { ...o, tau: 0, nr: 81 } }] : [])], rw);
  if (!res || gen !== sweepGen || wState !== ws) return;
  const rows: Record<string, [number, number][]> = {};
  grid.forEach((g, i) => {
    (rows[`2PE${g.ax}`] ??= []).push([g.v, fwhm(g.s, res[i].p2)]);
    (rows[`2CE${g.ax}`] ??= []).push([g.v, fwhm(g.s, res[i].c2)]);
  });
  const cwW: Record<string, number> = {};
  cw.forEach((g, k) => { const r = res[grid.length + k]; cwW[`2PE${g.ax}`] = fwhm(g.s, r.p2); cwW[`2CE${g.ax}`] = fwhm(g.s, r.c2); });
  const m = res[jobs.length], ax = atPeak(res[jobs.length + 1], N), al = atPeak(res[jobs.length + 2], N);
  const dname = (a: string) => (a === "x" ? "FWHM" : "DOF");
  const ser: Series[] = [];
  const ratio = kind === "pulses" && S.pplot === "ratio";
  for (const a of dirs) for (const sig of ["2PE", "2CE"] as const) {
    ser.push({ id: sig + a, label: `${sig} ${dname(a)}`, color: SIG[sig], dash: a === "z" && dirs.length > 1, dots: true,
      pts: ratio ? rows[sig + a].map((p) => [p[0], p[1] / cwW[sig + a]] as [number, number]) : rows[sig + a] });
    if (kind === "pulses" && !ratio) ser.push({ id: `cw${sig}${a}`, label: `${sig} ${dname(a)}, continuous`, color: SIG[sig], dash: true, width: 1.4,
      pts: [[sw.vals[0], cwW[sig + a]], [sw.vals[sw.vals.length - 1], cwW[sig + a]]] });
  }
  ws.left.update(ser, { xlabel: `${sw.label}${sw.unit ? ` (${sw.unit})` : ""}, click a point`, ylabel: ratio ? "Width, pulsed / continuous" : "Width at the focus (µm)",
    ref: ratio ? 1 : undefined,
    ylog: kind === "eps" && dirs.includes("z"), xlog: kind === "pulses", marker: S.pk, pickable: true, fmt: (v) => v.toFixed(3) });
  ws.title.textContent = `PSF at ${sw.fmt(S.pk)}${kind === "pulses" ? `, θ = ${S.pth}°` : ""}${S.tau && kind !== "pulses" ? `, ${S.tau}-fs pulses` : ""}, NA ${S.wna}, ${S.wn === 1 ? "air" : "water"}, ${rw ? "vector (Richards–Wolf)" : "paraxial scalar"}`;
  const sc = mapScales([m.p2, m.c2], ((2 * h) / (NX - 1)) ** 2);
  ws.heats[0].draw(m.p2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc[0]);
  ws.heats[1].draw(m.c2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc[1]);
  if (pulsed && ws.heats.length > 2) {                                 // the continuous maps, same scale rule, for comparison
    const m0 = res[res.length - 1], sc0 = mapScales([m0.p2, m0.c2], ((2 * h) / (NX - 1)) ** 2);
    ws.heats[0].title = `2PE, ${kind === "pulses" ? S.pk : S.tau} fs`; ws.heats[1].title = `2CE, ${kind === "pulses" ? S.pk : S.tau} fs`;
    ws.heats[2].draw(m0.p2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc0[0]);
    ws.heats[3].draw(m0.c2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc0[1]);
    ws.heats[0].draw(m.p2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc[0]);
    ws.heats[1].draw(m.c2, NX, NX, [-h, h], [-h, h], S.map as "heat", { x: S.cx, z: S.cz }, sc[1]);
  }
  for (const [k, a] of (["x", "z"] as const).entries()) {
    const sv = a === "x" ? cj.xs : cj.zs, r = a === "x" ? ax : al, r0 = cj0 ? atPeak(res[jobs.length + 3 + k], N) : null;
    const tauOf = kind === "pulses" ? S.pk : S.tau;
    ws.cuts[k].update((["2PE", "2CE"] as const).flatMap((sig) => {
      const y = sig === "2PE" ? r.p2 : r.c2, out: Series[] = [{ id: sig, label: `${sig}${pulsed ? ` ${tauOf} fs` : ""} (${dname(a)} ${um(width(sv, y))})`, color: SIG[sig], pts: sv.map((v, i) => [v, y[i]] as [number, number]) }];
      if (r0) { const y0 = sig === "2PE" ? r0.p2 : r0.c2; out.push({ id: `cw${sig}`, label: `${sig} continuous (${dname(a)} ${um(width(sv, y0))})`, color: SIG[sig], dash: true, width: 1.6, pts: sv.map((v, i) => [v, y0[i]] as [number, number]) }); }
      return out;
    }), { xlabel: cutLabel(a), ylabel: "Intensity (of the peak)", ydomain: [0, 1.02] });
  }
  if (ws.ref) {
    const med = S.wn === 1 ? "air" : "water", sr: Series[] = [];
    for (const sig of ["2PE", "2CE"] as const) for (const t of ["20", "10"])
      sr.push({ id: sig + t, label: `${sig}, ${TAU[t].label}`, color: t === "10" ? "#e15759" : "#f28e2b", dash: sig === "2PE", dots: true,
        pts: pulses.ratio[`${sig}|${med}|${t}`] ?? [] });
    ws.ref.update(sr, { xlabel: `NA (${med})`, ylabel: "Depth of focus, pulsed / continuous", ref: 1, fmt: (v) => v.toFixed(3) });
  }
  if (ws.hiNA) for (const [k, ax] of (["x", "z"] as const).entries()) {
    const NC: [string, string][] = [["air|0.3", "#9467bd"], ["air|0.5", "var(--t0)"], ["air|0.7", "#1f77b4"], ["water|0.5", "#ff7f0e"], ["water|0.7", "#2ca02c"], ["water|0.9", "#d62728"]];
    const ser: Series[] = [];
    for (const [mn, col] of NC) for (const model of ["vector", "scalar"]) {
      const d = data.dlambda[`${mn}|${ax}|${model}`];
      if (!d) continue;
      const [med, na] = mn.split("|");
      ser.push({ id: mn + model, label: `NA ${na} ${med}${model === "scalar" ? ", scalar" : ""}`, color: col, dash: model === "scalar", dots: model === "vector",
        pts: d.map((p) => [p[0], p[1] / d[0][1]] as [number, number]) });
    }
    ws.hiNA[k].update(ser, { xlabel: "Wavelength difference Δλ (nm)", ylabel: ax === "x" ? "FWHM / value at 10 nm" : "DOF / value at 10 nm", ref: 1, fmt: (v) => v.toFixed(4) });
  }
  // the published figures at the paper's settings
  ws.paper.replaceChildren();
  if (S.wna === 0.5 && S.wn === 1 && !rw && !S.tau && kind !== "pulses") {
    if (kind === "dl" && S.wth === 90 && S.weps === 0) paperRow(ws.paper, [["fig4a", "Fig. 4a, 2CE across"], ["fig4b", "Fig. 4b, 2CE along"], ["fig5", "Fig. 5, FWHM and DOF against Δλ"]]);
    if (kind === "theta" && S.wdl === 94 && (S.weps === 0 || S.weps === 0.99)) {
      const [a, b] = S.weps ? ["6", "7"] : ["2", "3"];
      paperRow(ws.paper, [[`fig${a}a`, `Fig. ${a}a, 2PE across`], [`fig${a}b`, `Fig. ${a}b, 2CE across`], [`fig${b}a`, `Fig. ${b}a, 2PE along`], [`fig${b}b`, `Fig. ${b}b, 2CE along`]]);
    }
    if (kind === "eps" && S.wdl === 94) paperRow(ws.paper, [["fig2b", "Fig. 2b, circular, across"], ["fig6b", "Fig. 6b, ε 0.99, across"], ["fig3b", "Fig. 3b, circular, along"], ["fig7b", "Fig. 7b, ε 0.99, along"]]);
  }
  writeHash();
}

// ---- scattering (Fig. 8, Monte Carlo) ----
let sCharts: { left: LineChart; right: LineChart; right2: LineChart; title: HTMLElement } | null = null;
function scatterView() {
  const c = $("controls");
  seg(c, "Show", "one", [[0, "mean of 10 runs"], [1, "one run (10⁶ photons)"]]);
  el("p", "hint", "Click an h on the left. Each excitation curve is one beam, normalized to its own peak; legend entries toggle the curves.", c);
  if (!sCharts) {
    const a = layout("two");
    const L = cell(el("div", "stack col", "", a), "big");          // left column: a drop zone for panels too
    const R = el("div", "stack", "", a);
    const title = el("h2", "cell-title", "", R);
    sCharts = { left: new LineChart(L), right: new LineChart(cell(R)), right2: new LineChart(cell(R)), title };
    sCharts.left.onPick = (v) => set("h", v);
    paperRow(a, [["fig8a", "Fig. 8a, 2PE"], ["fig8b", "Fig. 8b, 2CE"]]);
  }
  const hs = Object.keys(scatter).map(Number);
  sCharts.left.update((["2PE", "2CE"] as const).map((s) => ({ id: s, label: s, color: SIG[s], dots: true,
    pts: hs.map((h) => [h, scatter[String(h)][`${s}|bg`] as number] as [number, number]) })),
  { xlabel: "Slab half-thickness h (µm), click a point", ylabel: "Out-of-focus background (|z| > 10 µm)", xlog: true, marker: S.h, pickable: true });
  const D = scatter[String(S.h)], z = D.z as number[], one = S.one ? "|one" : "";
  sCharts.title.textContent = `Along the axis through a scattering slab, θ = π, h = ${S.h} µm`;
  const curve = (key: string): [number, number][] => z.map((v, i) => [v, (D[key] as number[])[i]] as [number, number]);
  for (const [chart, sig, beams] of [[sCharts.right, "2PE", ["Excitation, beam from L1", "Excitation, beam from L2 (θ = π)"]],
    [sCharts.right2, "2CE", ["Excitation, λ₁ (750 nm)", "Excitation, λ₂ (656 nm)"]]] as const) {
    chart.update([
      { id: "e1", label: beams[0], color: "var(--b1)", dash: true, width: 2, pts: curve(`${sig}|e1${one}`) },      // lens L1, as in the setup sketch
      { id: "e2", label: beams[1], color: "var(--b2)", dash: true, width: 2, pts: curve(`${sig}|e2${one}`) },      // lens L2
      { id: "ref", label: "No scattering", color: "var(--muted)", width: 1.6, pts: curve(`${sig}|ref`) },
      { id: "f", label: `${sig} fluorescence`, color: SIG[sig], width: 3, pts: curve(sig + one) },
    ], { xlabel: "z (µm), along at x = 0", ylabel: `${sig} intensity (of the peak)`, ydomain: [0, 1.1] });
  }
  writeHash();
}

// ---- pulses in time: two pulses through the focus, computed here (worker), frame by frame ----
let pWorker: Worker | null = null, pId = 0;
const pWait = new Map<number, (r: PulseRun | null) => void>();
function pulseRun(o: PulseOpts): Promise<PulseRun | null> {
  if (!pWorker) {
    try {
      pWorker = new Worker(new URL("./pulsetime.worker.ts", import.meta.url), { type: "module" });
      pWorker.onmessage = (e: MessageEvent<{ id: number; out: PulseRun }>) => {
        const f = pWait.get(e.data.id); pWait.delete(e.data.id); f?.(e.data.id === pId ? e.data.out : null);
      };
    } catch { pWorker = null; }
  }
  const id = ++pId;
  if (!pWorker) return Promise.resolve(runPulses(o));
  return new Promise((done) => { pWait.set(id, done); pWorker!.postMessage({ id, o }); });
}
const pOpts = (): PulseOpts => {
  const s = 0.5 / S.qna;                                                 // the focus grows as 1/NA across and 1/NA² along
  return { sig: S.qsig as "2CE" | "2PE", tau: S.qtau, theta: -(S.qth * Math.PI) / 180, na: S.qna, n: S.qn, delay: (S.qdel * 0.7) / C,
    xh: 1.5 * s * S.qn, zh: 5 * s * s * S.qn, nx: 41, nz: 201, nl: 801, frames: 160 };
};
type PState = { heats: Heat[]; titles: Record<string, HTMLElement>; vid: HTMLVideoElement; nowP: LineChart; now: LineChart; cum: LineChart; spec: LineChart; build: LineChart; width: LineChart; pairs: LineChart; read: HTMLElement;
  pspec: Float32Array[][] | null;
  run: PulseRun | null; key: string; k: number; timer: number; tmax: Record<string, number>; o: PulseOpts | null;
  stat: { build: Series[]; bo: Opts; width: Series[]; wo: Opts } | null };
let pState: PState | null = null;
const PLAM = Array.from({ length: 281 }, (_, i) => 320 + i * 0.25);    // photon-pair sum wavelengths (nm), 350 on the grid
/** Names of the three kinds of pairs, by the wavelength they add up to (2CE) or by lens (2PE, all at 350 nm): [short, long]. */
function pairNames(run: PulseRun): [string[], string[]] {
  const [a, b] = run.lams.map((l) => Math.round(l * 1000)), sum = (x: number, y: number) => Math.round(1 / (1 / x + 1 / y));
  if (a === b) { const sh = ["350-nm pairs, L1 + L1", "350-nm pairs, L1 + L2", "350-nm pairs, L2 + L2"]; return [sh, sh]; }
  const sh = [`${sum(a, a)}-nm pairs`, `${sum(a, b)}-nm pairs`, `${sum(b, b)}-nm pairs`];
  return [sh, [`${sh[0]} (${a} + ${a} nm)`, `${sh[1]} (${a} + ${b} nm)`, `${sh[2]} (${b} + ${b} nm)`]];
}
const pKey = () => JSON.stringify(pOpts());
function pulseTime() {
  const c = $("controls");
  seg(c, "Signal", "qsig", [["2CE", "2CE (750 + 656 nm)"], ["2PE", "2PE (700 nm)"]]);
  slider(c, "Angle θ between the lenses", "qth", 0, 180, 15, (v) => `${v}°`);
  seg(c, "Pulse width τ", "qtau", [[5, "5 fs"], [10, "10"], [20, "20"], [50, "50"], [100, "100"]]);
  slider(c, "Delay of pulse 2, as a path difference cΔt in wavelengths of 700 nm", "qdel", -20, 20, 1, (v) => `${v} λ (${(v * 0.7 / C).toFixed(1)} fs)`);
  seg(c, "NA", "qna", [[0.3, "0.3"], [0.4, "0.4"], [0.5, "0.5"]]);
  seg(c, "Medium", "qn", [[1, "air"], [1.33, "water"]]);
  seg(c, "2D maps", "map", [["heat", "heat map"], ["contour", "contours"]]);
  const g = el("div", "ctl ctl-slider", "", c);
  el("span", "ctl-l", "Time t", g);
  const r = el("input", "", "", g) as HTMLInputElement;
  r.type = "range"; r.id = "qtime"; r.min = "0"; r.max = String(Math.max(0, (pState?.run?.t.length ?? 1) - 1)); r.step = "1"; r.value = String(pState?.k ?? 0);
  el("output", "", "", g).id = "qtout";
  r.oninput = () => { stopPlay(); showFrame(+r.value); };
  const pb = el("button", "reset", pState?.timer ? "Pause" : "Play", c) as HTMLButtonElement;
  pb.type = "button"; pb.id = "qplay";
  pb.onclick = () => (pState?.timer ? stopPlay() : startPlay());
  const vf = videoFile();
  const vb = el("button", "reset", S.qvid ? "Hide the video" : "Load the video", c) as HTMLButtonElement;
  vb.type = "button"; vb.disabled = !vf && !S.qvid;
  vb.title = vf ? "The rendered video for these settings" : "Videos exist for NA 0.5 in air at zero delay, θ = 0, 90 or 180° and τ = 5, 10, 20 or 100 fs";
  vb.onclick = () => set("qvid", S.qvid ? 0 : 1);
  if (!pState) {                                                       // the layout of the videos: maps; cuts now and accumulated; spectrum
    const a = layout("ptime");
    const vid = el("video", "pvideo", "", cell(a)) as HTMLVideoElement;
    vid.controls = true; vid.loop = true; vid.muted = true; vid.playsInline = true;
    const maps = el("div", "top", "", a);
    const heats = ["I₁", "I₂", "I₁·I₂ now, where the pulses overlap", "2CE accumulated up to t"].map((t) => new Heat(cell(maps, "map"), t));
    for (const h of heats) h.shape = 1.35;                               // as in the videos: maps fill the panel (x stretched)
    const titles: Record<string, HTMLElement> = {};
    const ch = (row: HTMLElement, id: string, cls = "") => {              // a chart with its title above
      const c = cell(row, cls);
      titles[id] = el("h2", "cell-title", "", c);
      return new LineChart(c);
    };
    const r1 = el("div", "mid", "", a), r2 = el("div", "one", "", a);
    const now = ch(r1, "now"), nowP = ch(r1, "nowP"), cum = ch(r1, "cum", "span2"), spec = ch(r2, "spec");
    const read = note(a, "");
    const r3 = el("div", "three", "", a);
    pState = { heats, now, nowP, cum, spec, build: ch(r3, "build"), width: ch(r3, "width"), pairs: ch(r3, "pairs"), vid,
      titles, read, run: null, key: "", k: 0, timer: 0, tmax: {}, o: null, stat: null, pspec: null };
  }
  const v = pState.vid, cellV = v.parentElement!;
  cellV.hidden = !(S.qvid && vf);
  if (S.qvid && vf && !v.src.endsWith(vf)) { v.src = `./video/${vf}`; v.play().catch(() => {}); }
  if (!(S.qvid && vf)) { v.pause(); v.removeAttribute("src"); v.load(); }
  schedulePulses();
  writeHash();
}
/** The rendered video (scripts/cambaliza2000_pulse_video.py) for the current settings, if there is one. */
function videoFile() {
  const th = ({ 0: "0", 90: "pi2", 180: "pi" } as Record<number, string>)[S.qth];
  return th && [5, 10, 20, 100].includes(S.qtau) && !S.qdel && S.qna === 0.5 && S.qn === 1
    ? `pulse_${S.qsig.toLowerCase()}_${th}_tau${S.qtau}.mp4` : "";
}
let pDebounce = 0;
function schedulePulses() {
  if (!pState) return;
  if (pState.key === pKey() && pState.run) { showFrame(pState.k); return; }
  clearTimeout(pDebounce);
  pDebounce = window.setTimeout(computePulses, 250);
}
async function computePulses() {
  const st = pState;
  if (!st) return;
  const key = pKey(), o = pOpts();
  stopPlay();
  st.read.textContent = "Computing the pulses…";
  const run = await pulseRun(o);
  if (!run || pState !== st || key !== pKey()) return;
  st.run = run; st.key = key; st.o = o;
  const mx = (a: Float32Array[]) => a.reduce((m, f) => { for (let i = 0; i < f.length; i++) if (f[i] > m) m = f[i]; return m; }, 0);
  st.tmax = { I1: mx(run.I1), I2: mx(run.I2), P: mx(run.P), all: mx(run.all), lI1: mx(run.lI1), lI2: mx(run.lI2), lP: mx(run.lP) };
  const r = document.getElementById("qtime") as HTMLInputElement | null;
  if (r) r.max = String(run.t.length - 1);
  const k0 = run.t.reduce((a, v, i) => (Math.abs(v) < Math.abs(run.t[a]) ? i : a), 0);
  drawStatic();
  showFrame(k0);
}
const peakOf = (f: ArrayLike<number>) => { let m = 0; for (let i = 0; i < f.length; i++) if (f[i] > m) m = f[i]; return m; };
const widthOf = (s: number[], y: ArrayLike<number>) => { const h = halfPoints(y); return h ? (h[1] - h[0]) * (s[1] - s[0]) : NaN; };
function drawStatic() {                                                  // the curves against time, once per run
  const st = pState!, run = st.run!, t = Array.from(run.t);
  const sig = S.qsig;
  st.pspec = pairSpectra(run, PLAM);
  const i350 = PLAM.indexOf(350), iz = run.zl.reduce((a, v, i) => (Math.abs(v) < Math.abs(run.zl[a]) ? i : a), 0);
  const tot = t.map((_, i) => run.lall[i][iz]), ft = tot[tot.length - 1];
  const [n1, n2] = pairNames(run);
  const build: Series[] = [
    { id: "all", label: `${sig} accumulated up to t`, color: "var(--ink)", width: 2.6, pts: t.map((v, i) => [v, tot[i] / ft] as [number, number]) },
    { id: "one", label: n2[1], color: "#6a3d9a", width: 2, pts: t.map((v, i) => [v, st.pspec![i][1][i350] / ft] as [number, number]) },
    { id: "s1", label: n1[0], color: "var(--b1)", width: 1.6, pts: t.map((v, i) => [v, st.pspec![i][0][i350] / ft] as [number, number]) },
    { id: "s2", label: n1[2], color: "var(--b2)", width: 1.6, pts: t.map((v, i) => [v, st.pspec![i][2][i350] / ft] as [number, number]) },
  ];
  const bo: Opts = { xlabel: "Time t (fs)", ylabel: `At the focus, accumulated up to t (of the total ${sig})`, ydomain: [0, 1.3] };
  const on = (i: number, a: Float32Array[]) => peakOf(a[i]) > 0.05 * peakOf(a[a.length - 1]);
  const pon = (i: number) => peakOf(run.lP[i]) > 0.01 * st.tmax.lP;
  const width: Series[] = [
    { id: "wall", label: `${sig} accumulated up to t`, color: "var(--ink)", width: 2.6, pts: t.flatMap((v, i) => (on(i, run.lall) ? [[v, widthOf(run.zl, run.lall[i])] as [number, number]] : [])) },
    { id: "wone", label: pairNames(run)[0][1], color: "#6a3d9a", width: 1.8, pts: t.flatMap((v, i) => (on(i, run.lone) ? [[v, widthOf(run.zl, run.lone[i])] as [number, number]] : [])) },
    { id: "wp", label: "I₁·I₂ now", color: "#6a3d9a", dash: true, width: 1.8, pts: t.flatMap((v, i) => (pon(i) ? [[v, widthOf(run.zl, run.lP[i])] as [number, number]] : [])) },
    { id: "wcw", label: "continuous beams", color: "var(--muted)", dash: true, width: 1.4, pts: [[t[0], widthOf(run.zl, run.cw)], [t[t.length - 1], widthOf(run.zl, run.cw)]] },
  ];
  st.stat = { build, bo, width, wo: { xlabel: "Time t (fs)", ylabel: "FWHM along the axis (µm), central lobe" } };
}
function showFrame(k: number) {
  const st = pState;
  if (!st?.run || !st.o) return;
  const run = st.run, o = st.o;
  st.k = k = Math.max(0, Math.min(run.t.length - 1, k));
  const r = document.getElementById("qtime") as HTMLInputElement | null, out = document.getElementById("qtout");
  if (r) r.value = String(k);
  if (out) out.textContent = `${run.t[k] >= 0 ? "+" : ""}${run.t[k].toFixed(1)} fs`;
  (["I1", "I2", "P", "all"] as const).forEach((q, j) => {
    const f = run[q][k], pk = peakOf(f), v = pk > 0 ? Float32Array.from(f, (x) => x / pk) : f;
    st.heats[j].draw(v, o.nx, o.nz, [-o.xh, o.xh], [-o.zh, o.zh], S.map as "heat", { x: 0, z: 0 }, { f: pk / st.tmax[q] || 0, vmax: 1, unit: "of max over time" });
  });
  const [l1, l2] = run.lams.map((l) => `${(l * 1000).toFixed(0)} nm`);
  st.heats[0].title = `I₁, ${l1}, L1`; st.heats[1].title = `I₂, ${l2}, L2`;
  st.heats[3].title = `${S.qsig} accumulated up to t`;
  st.heats[2].title = S.qsig === "2CE" ? "I₁·I₂ now, where the pulses overlap" : "|E₁ + E₂|⁴ now";
  const ln = (s: number[], y: ArrayLike<number>, d: number) => s.map((v, i) => [v, y[i] / d] as [number, number]);
  Object.entries({
    now: "I₁, I₂ along the axis, now",
    nowP: S.qsig === "2CE" ? "I₁·I₂ along the axis, now" : "|E₁ + E₂|⁴ along the axis, now",
    cum: `${S.qsig} along the axis, accumulated up to t`,
    spec: "Spectrum arriving at the focus now",
    build: `${S.qsig} at the focus against time, by pair`,
    width: `${S.qsig} width along the axis against time`,
    pairs: "Pair sums at the focus, accumulated up to t",
  }).forEach(([id, txt]) => { if (st.titles[id]) st.titles[id].textContent = txt; });
  st.now.update([
    { id: "i1", label: "I₁", color: "var(--b1)", width: 2.2, pts: ln(run.zl, run.lI1[k], st.tmax.lI1) },
    { id: "i2", label: "I₂", color: "var(--b2)", width: 2.2, pts: ln(run.zl, run.lI2[k], st.tmax.lI2) },
  ], { xlabel: "z (µm), at x = 0", ylabel: "Of its maximum", ydomain: [0, 1.05] }, false);
  st.nowP.update([
    { id: "p", label: S.qsig === "2CE" ? "I₁·I₂" : "|E₁ + E₂|⁴", color: "#6a3d9a", width: 2.6, pts: ln(run.zl, run.lP[k], st.tmax.lP) },
  ], { xlabel: "z (µm), at x = 0", ylabel: "Of its maximum", ydomain: [0, 1.05] }, false);
  const last = run.lall.length - 1, fin = peakOf(run.lall[last]);
  st.cum.update([
    { id: "cw", label: "continuous beams", color: "var(--muted)", dash: true, width: 1.6, pts: ln(run.zl, run.cw, 1) },
    { id: "fin", label: `total ${S.qsig}`, color: "#b0b0b0", width: 1.8, pts: ln(run.zl, run.lall[last], fin) },
    { id: "all", label: `${S.qsig} accumulated up to t`, color: "var(--ink)", width: 2.6, pts: ln(run.zl, run.lall[k], fin) },
  ], { xlabel: "z (µm), along the axis at x = 0", ylabel: `${S.qsig} (peak of the total = 1)`, ydomain: [0, 1.3] }, false);
  const sp = run.spec;
  st.spec.update([
    { id: "f1", label: "full spectrum, beam 1", color: "var(--b1)", dash: true, width: 1, pts: sp.nu1.map((v, i) => [v, sp.s1[i]] as [number, number]) },
    { id: "f2", label: "full spectrum, beam 2", color: "var(--b2)", dash: true, width: 1, pts: sp.nu2.map((v, i) => [v, sp.s2[i]] as [number, number]) },
    { id: "s1", label: `beam 1 (${l1}) at the focus now`, color: "var(--b1)", width: 2.6, pts: sp.nu1.map((v, i) => [v, sp.s1[i] * sp.a1[k]] as [number, number]) },
    { id: "s2", label: `beam 2 (${l2}) at the focus now`, color: "var(--b2)", width: 2.6, pts: sp.nu2.map((v, i) => [v, sp.s2[i] * sp.a2[k]] as [number, number]) },
  ], { xlabel: "Frequency (THz), with a line at 428 THz (700 nm)", ylabel: "Spectrum now", ydomain: [0, 1.05], marker: (C / 0.7) * 1e3 }, false);
  if (st.pspec) {
    const ps = st.pspec, L = ps.length - 1, top = Math.max(...Array.from(ps[L][1])), [, n2] = pairNames(run);
    const cols = ["var(--b1)", "#6a3d9a", "var(--b2)"];
    const ser = (q: number, f: number, fin: boolean): Series => ({ id: `${q}${fin ? "f" : ""}`, label: fin ? `${n2[q]}, total` : `${n2[q]}, up to t`,
      color: cols[q], dash: fin, faint: fin, width: fin ? 1.2 : 2.4,
      pts: PLAM.flatMap((l, i) => (ps[f][q][i] / top > 1e-6 ? [[l, ps[f][q][i] / top] as [number, number]] : [])) });
    st.pairs.update([0, 1, 2].flatMap((q) => [ser(q, L, true), ser(q, k, false)]),
      { xlabel: "Wavelength of the photon-pair sum (nm), with a line at the 350-nm level", ylabel: `At the focus (of the ${pairNames(run)[0][1]} peak)`,
        ylog: true, ydomain: [1e-6, 3], marker: 350 }, false);
  }
  drawMarkers();
  const cw = widthOf(run.zl, run.cw), wf = widthOf(run.zl, run.lall[last]);
  st.read.textContent = `At t = ${run.t[k].toFixed(1)} fs the ${S.qsig} accumulated up to t is ${(100 * peakOf(run.lall[k]) / fin).toFixed(0)}% of the peak of the total. ` +
    `The FWHM of the total along the axis is ${um(wf)}, against ${um(cw)} for continuous beams, at θ = ${S.qth}°, τ = ${S.qtau} fs, a delay of ${S.qdel} λ, NA ${S.qna} in ${S.qn === 1 ? "air" : "water"}.`;
}
function drawMarkers() {                                               // the charts against time: same curves, marker at this frame
  const st = pState!;
  if (!st.run || !st.stat) return;
  const m = st.run.t[st.k];
  st.build.update(st.stat.build, { ...st.stat.bo, marker: m }, false);
  st.width.update(st.stat.width, { ...st.stat.wo, marker: m }, false);
}
function startPlay() {
  const st = pState;
  if (!st?.run) return;
  if (st.k >= st.run.t.length - 1) st.k = 0;
  st.timer = window.setInterval(() => { if (!pState?.run) return stopPlay(); if (pState.k >= pState.run.t.length - 1) return stopPlay(); showFrame(pState.k + 1); }, 70);
  const b = document.getElementById("qplay"); if (b) b.textContent = "Pause";
}
function stopPlay() {
  if (pState?.timer) { clearInterval(pState.timer); pState.timer = 0; }
  const b = document.getElementById("qplay"); if (b) b.textContent = "Play";
}

// ---- pulse results: the τ sweep (precomputed, paraxial NA 0.5, air), widths per angle and any metric against any other ----
type PRow = { sig: string; th: number; cut: string; tau: number; dnu: number; cw: number | null; one: number | null; all: number | null;
  crest: number | null; mean: number | null; rate: number | null; gain: number; same: number; depth: number };
type PSweep = { taus: number[]; z: number[]; x: number[]; rows: PRow[]; prof: Record<string, number[]> };
let psweep: PSweep | null = null;
type PDelay = { ns: number[]; taus: number[]; lam0: number; z: number[];
  met: Record<string, { peak: number[]; centre: (number | null)[]; fwhm: (number | null)[] }>; prof: Record<string, number[]> };
let pdelay: PDelay | null = null;
type PNA = { taus: number[]; met: Record<string, { label: string; unit: string; tol: number }>;
  sets: Record<string, { label: string; nas: number[]; taus?: number[]; val: Record<string, Record<string, Record<string, (number | null)[]>>>; tw: Record<string, Record<string, [number, number | null][]>> }> };
let pna: PNA | null = null;
type PDSweep = { cut: Record<string, string>; dtau: number[]; taus: number[]; nas: Record<string, number[]>; fine_step: number;
  coarse: Record<string, Record<string, Record<string, Record<string, { rel: (number | null)[]; pos: (number | null)[] }>>>>;
  fine: Record<string, Record<string, Record<string, Record<string, { total: (number | null)[]; cross: (number | null)[] }>>>> };
let pdsweep: PDSweep | null = null;
const PTH: Record<number, { label: string; color: string }> = {
  0: { label: "θ = 0", color: "var(--t0)" }, 90: { label: "θ = π/2", color: "var(--t1)" }, 180: { label: "θ = π", color: "var(--t2)" } };
/** Names of the pairs for a signal: across the two pulses, within one pulse. */
const pairWords = (sig: string) => (sig === "2CE" ? ["350-nm pairs (750 + 656 nm)", "375- and 328-nm pairs"] : ["L1 + L2 pairs", "L1 + L1 and L2 + L2 pairs"]);
function metricDefs(sig: string): Record<string, { label: string; get: (r: PRow) => number | null }> {
  const [cross, within] = pairWords(sig);
  return {
    tau: { label: "Pulse width τ (fs)", get: (r) => r.tau },
    dnu: { label: "Spectral bandwidth Δν (THz)", get: (r) => r.dnu },
    cw: { label: "FWHM, continuous beams (µm)", get: (r) => r.cw },
    all: { label: "FWHM, central fringe (µm)", get: (r) => r.all },
    crest: { label: "FWHM through the fringe crests (µm)", get: (r) => r.crest },
    mean: { label: "FWHM, fringes averaged (µm)", get: (r) => r.mean },
    rcrest: { label: "FWHM fringe crests / continuous", get: (r) => (r.crest && r.cw ? r.crest / r.cw : null) },
    gain: { label: `Peak of the total / ${cross}`, get: (r) => r.gain },
    same: { label: `Peak, ${within} / ${cross}`, get: (r) => r.same },
    depth: { label: "Fringe depth", get: (r) => r.depth },
  };
}
function choose(parent: HTMLElement, label: string, k: K, opts: [string, string][]) {
  const g = el("div", "ctl", "", parent);
  el("span", "ctl-l", label, g);
  const s = el("select", "", "", g) as HTMLSelectElement;
  for (const [v, t] of opts) { const o = el("option", "", t, s) as HTMLOptionElement; o.value = v; o.selected = S[k] === v; }
  s.onchange = () => set(k, s.value);
}
let rCharts: Record<string, LineChart> | null = null, rTitles: Record<string, HTMLElement> = {};
let sHeats: Heat[] = [], rHeats: Heat[] = [], sMapKey = "", rMapKey = "";
// x–z maps of the pulse results, computed here at NA 0.5 in air (the grid of the dashboard's pulses in time), kept once computed
const MG = { xh: 1.5, zh: 5, nx: 41, nz: 201 };
const MX = Array.from({ length: MG.nx }, (_, i) => -MG.xh + (2 * MG.xh * i) / (MG.nx - 1));
const MZ = Array.from({ length: MG.nz }, (_, i) => -MG.zh + (2 * MG.zh * i) / (MG.nz - 1));
type RMap = { tot: Float32Array; now: Float32Array; t0: number };
const rMaps = new Map<string, RMap>();
let rQueue: Promise<unknown> = Promise.resolve();
/** Total accumulated as the pulses pass the focus, and the signal at the frame nearest t = 0 (I₁·I₂ or |E₁ + E₂|⁴). */
const mapOpts = (sig: string, tau: number, th: number, n: number): PulseOpts => ({ sig: sig as "2CE" | "2PE", tau,
  theta: -(th * Math.PI) / 180, na: 0.5, n: 1, delay: (n * 0.7) / C, ...MG, nl: 101, frames: 2 });
function pulseMap(sig: string, tau: number, th: number, n: number, still: () => boolean): Promise<RMap | null> {
  const o = mapOpts(sig, tau, th, n);
  const key = JSON.stringify(o), got = rMaps.get(key);
  if (got) return Promise.resolve(got);
  const job = rQueue.then(async () => {                                // one run at a time: a newer run never cancels an older one
    if (!still()) return null;
    const hit = rMaps.get(key);
    if (hit) return hit;
    const run = await pulseRun(o);
    if (!run) return null;
    const k0 = run.t.reduce((a, v, i) => (Math.abs(v) < Math.abs(run.t[a]) ? i : a), 0);
    const m = { tot: run.all[run.all.length - 1], now: run.P[k0], t0: run.t[k0] };
    rMaps.set(key, m);
    return m;
  });
  rQueue = job.catch(() => null);
  return job;
}
const cwMaps = new Map<string, Float32Array>();
function cwMap(sig: string, th: number) {                              // continuous beams: I₁I₂ (2CE) or |U₁ + U₂|⁴ (2PE)
  const key = `${sig}|${th}`, got = cwMaps.get(key);
  if (got) return got;
  const X: number[] = [], Z: number[] = [];
  for (const z of MZ) for (const x of MX) { X.push(x); Z.push(z); }
  const [l1, l2] = sig === "2CE" ? [0.75, 0.656] : [0.7, 0.7];
  const u1 = field(X, Z, l1, 0.5, 1, 0, 0, 101), u2 = field(X, Z, l2, 0.5, 1, -(th * Math.PI) / 180, 0, 101);
  const v = Float32Array.from(X, (_, i) => sig === "2CE" ? (u1.re[i] ** 2 + u1.im[i] ** 2) * (u2.re[i] ** 2 + u2.im[i] ** 2)
    : ((u1.re[i] + u2.re[i]) ** 2 + (u1.im[i] + u2.im[i]) ** 2) ** 2);
  cwMaps.set(key, v);
  return v;
}
const normed = (f: Float32Array) => { const p = peakOf(f); return p > 0 ? Float32Array.from(f, (v) => v / p) : f; };
const across = (f: Float32Array, iz: number) => { const row = Array.from(f.subarray(iz * MG.nx, (iz + 1) * MG.nx)), p = Math.max(...row);
  return row.map((v, i) => [MX[i], p > 0 ? v / p : 0] as [number, number]); };
const drawMap = (h: Heat, v: Float32Array, title: string) => { h.title = title; h.draw(normed(v), MG.nx, MG.nz, [-MG.xh, MG.xh], [-MG.zh, MG.zh], "contour"); };
const nowName = (sig: string) => (sig === "2CE" ? "I₁·I₂" : "|E₁ + E₂|⁴");
async function drawSweepMaps() {                                       // the picked τ and angle, no delay
  const sig = S.rsig, th = S.rpth, tau = S.rk, key = [sig, th, tau].join("|");
  if (key === sMapKey || sHeats.length < 3) return;
  sMapKey = key;
  const cw = cwMap(sig, th), iz = (MG.nz - 1) / 2;
  drawMap(sHeats[0], cw, `${sig}, continuous beams, ${PTH[th].label}`);
  rTitles.sx.textContent = `${sig} across the axis at z = 0, ${PTH[th].label}`;
  const m = await pulseMap(sig, tau, th, 0, () => sMapKey === key);
  if (!m || sMapKey !== key) return;
  drawMap(sHeats[1], m.tot, `Total ${sig}, ${tau}-fs pulses`);
  drawMap(sHeats[2], m.now, `${nowName(sig)} at t = ${m.t0.toFixed(1)} fs, ${tau}-fs pulses`);
  drawProfile();
  rCharts!.sx.update([
    { id: "cw", label: "continuous beams", color: "var(--ink)", dash: true, width: 2, pts: across(cw, iz) },
    { id: "tot", label: `total ${sig}, ${tau} fs`, color: "#d62728", width: 2.2, pts: across(m.tot, iz) },
    { id: "now", label: `${nowName(sig)} at t = 0, ${tau} fs`, color: "#1f77b4", width: 2, pts: across(m.now, iz) },
  ], { xlabel: "x (µm), at z = 0", ylabel: "Of its peak", ydomain: [0, 1.05] });
}
async function drawDelayMaps() {                                       // the delay τ and angle, at N = 0 and the picked N
  const sig = S.rsig, th = S.rdth, tau = S.rdt, n = S.rdn, key = [sig, th, tau, n].join("|");
  if (key === rMapKey || rHeats.length < 2) return;
  rMapKey = key;
  const still = () => rMapKey === key, m0 = await pulseMap(sig, tau, th, 0, still), m = m0 && (await pulseMap(sig, tau, th, n, still));
  if (!m0 || !m || !still()) return;
  drawMap(rHeats[0], m0.tot, `Total ${sig}, ${tau} fs, N = 0`);
  drawMap(rHeats[1], m.tot, `Total ${sig}, ${tau} fs, N = ${n}, peak ${(peakOf(m.tot) / peakOf(m0.tot)).toFixed(2)} of that at N = 0`);
  const top = (f: Float32Array) => { let k = 0; for (let i = 0; i < f.length; i++) if (f[i] > f[k]) k = i; return Math.floor(k / MG.nx); };
  const iz = top(m.tot);
  rTitles.dx.textContent = `Total ${sig} across the axis, at the z of its peak (z = ${MZ[iz].toFixed(2)} µm for N = ${n}), ${PTH[th].label}`;
  rCharts!.dx.update([
    { id: "n0", label: "N = 0, at z = 0", color: "var(--ink)", dash: true, width: 2, pts: across(m0.tot, (MG.nz - 1) / 2) },
    { id: "n", label: `N = ${n}`, color: "#d62728", width: 2.2, pts: across(m.tot, iz) },
  ], { xlabel: "x (µm)", ylabel: "Of its peak", ydomain: [0, 1.05] });
}
async function pulseResults() {
  const c = $("controls");
  seg(c, "Signal", "rsig", [["2CE", "2CE (750 + 656 nm)"], ["2PE", "2PE (700 nm)"]]);
  seg(c, "Direction", "rcut", [["z", "along the axis"], ["x", "across"]]);
  const M = metricDefs(S.rsig), opts = Object.entries(M).map(([k, d]) => [k, d.label] as [string, string]);
  choose(c, "Scatter plot, x axis", "rx", opts);
  choose(c, "Scatter plot, y axis", "ry", opts);
  seg(c, "Scatter axes", "rlog", [["", "linear"], ["x", "log x"], ["y", "log y"], ["xy", "log both"]]);
  multi(c, "Angles", "rths", [["0", "θ = 0", PTH[0].color], ["90", "θ = π/2", PTH[90].color], ["180", "θ = π", PTH[180].color]]);
  seg(c, "Profile at the picked τ", "rpth", [[0, "θ = 0"], [90, "θ = π/2"], [180, "θ = π"]]);
  seg(c, "Angle for the maps and the delay", "rdth", [[0, "θ = 0"], [90, "θ = π/2"], [180, "θ = π"]]);
  seg(c, "τ for the maps and the delay", "rdt", [[10, "10 fs"], [20, "20 fs"], [100, "100 fs"]]);
  seg(c, "Angle for the plots against NA", "nth", [[0, "θ = 0"], [90, "θ = π/2"], [180, "θ = π"]]);
  const SETS: [string, string][] = [];
  for (const [m, ml] of [["rw", "Richards–Wolf"], ["paraxial", "scalar"]]) for (const md of ["air", "water", "oil"]) {
    SETS.push([`${m}_${md}`, `${ml}, ${md}`]);
    for (const ex of ["gauss4", "eps0.5", "eps0.9", "eps0.99"]) SETS.push([`${m}_${md}_${ex}`,
      `${ml}, ${md}, ${ex.startsWith("eps") ? `ε = ${ex.slice(3)}` : "Gaussian input α = 4"}`]);
  }
  choose(c, "Model, medium and pupil of the plot of one measure against another", "nset", SETS);
  const MO: [string, string][] = [["diff", "largest difference"], ["dof", "depth of focus"], ["wx", "width across"], ["side", "side lobe"],
    ["F", "Linfoot F"], ["S", "Linfoot S"], ["Q", "Linfoot Q"]];
  choose(c, "Measure of the pulse width against NA", "nm", MO);
  choose(c, "Plot of one measure against another, x axis", "nx", [["tau", "pulse width τ"], ["na", "NA"], ...MO]);
  choose(c, "Plot of one measure against another, y axis", "ny", MO);
  seg(c, "Angle for the delay against NA", "xth", [[0, "θ = 0"], [90, "θ = π/2"], [180, "θ = π"]]);
  seg(c, "τ for the delay against NA", "xtau", [5, 10, 20, 30, 50, 100].map((t) => [t, `${t} fs`] as [number, string]));
  multi(c, "NAs drawn against the delay", "xnas", XNAS.map((na) => [String(Math.round(na * 100)), `NA ${na}`, naColor(na)] as [string, string, string]));
  seg(c, "NA of the chart of all pairs", "xna", XNAS.map((na) => [na, String(na)] as [number, string]));
  seg(c, "Polarization of the chart of all pairs", "xpol", [["s", "perpendicular to the plane of the lens axes"], ["p", "in the plane of the lens axes"]]);
  if (!rCharts) {
    const a = layout("psum");
    rTitles = {};
    const ch = (row: HTMLElement, id: string) => { const cl = cell(row); cl.id = `c-${id}`; rTitles[id] = el("h2", "cell-title", "", cl); return new LineChart(cl); };
    const m0 = el("div", "top", "", a);
    sHeats = [0, 1, 2].map(() => new Heat(cell(m0, "map"), ""));
    const sx = ch(m0, "sx");
    const r1 = el("div", "three", "", a), r2 = el("div", "cuts", "", a), r3 = el("div", "cuts", "", a);
    const mp = el("div", "top", "", a);
    rHeats = [0, 1].map(() => new Heat(cell(mp, "map"), ""));
    const dc = cell(mp, "span2"); rTitles.dx = el("h2", "cell-title", "", dc); const dx = new LineChart(dc);
    for (const h of [...sHeats, ...rHeats]) h.shape = 1.35;
    sMapKey = rMapKey = "";
    const r4 = el("div", "cuts", "", a), r5 = el("div", "cuts", "", a), r6 = el("div", "cuts", "", a);
    const sec = el("section", "sec", "", a);
    sec.id = "sec-delay-na";
    el("h2", "sec-h", "Delay between the pulses, against NA", sec);
    note(sec, "2CE with the vector (Richards–Wolf) model in air: the 656-nm pulse is delayed by Δt. The peak is taken along the axis with collinear and facing lenses (θ = 0 and π) and across it, along x, with crossed lenses (θ = π/2).");
    const r7 = el("div", "cuts", "", a), r8 = el("div", "cuts", "", a);
    rCharts = { a0: ch(r1, "a0"), a90: ch(r1, "a90"), a180: ch(r1, "a180"), sc: ch(r2, "sc"), pr: ch(r2, "pr"), st: ch(r3, "st"), dp: ch(r3, "dp"),
      dpk: ch(r4, "dpk"), dpr: ch(r4, "dpr"), dce: ch(r5, "dce"), dfw: ch(r5, "dfw"), ntw: ch(r6, "ntw"), ndv: ch(r6, "ndv"), sx, dx,
      xpk: ch(r7, "xpk"), xpos: ch(r7, "xpos"), xpu: ch(r8, "xpu"), xfi: ch(r8, "xfi") };
    for (const k of ["a0", "a90", "a180", "st", "dp"]) rCharts[k].onPick = (v) => set("rk", v);
    for (const k of ["dpk", "dce", "dfw"]) rCharts[k].onPick = (v) => set("rdn", v);
  }
  if (!psweep || !pdelay || !pdsweep) {
    try { [psweep, pdelay, pna, pdsweep] = await Promise.all(["pulse_sweep", "pulse_delay", "pulse_na", "pulse_delay_sweep"].map(async (f) => (await fetch(`./data/${f}.json`)).json())); }
    catch { note($("app"), "Could not load the pulse results."); return; }
    if (S.mode !== "psum") return;
  }
  drawResults();
  writeHash();
}
function drawResults() {
  const D = psweep!, C = rCharts!, sig = S.rsig, cut = S.rcut, M = metricDefs(sig), [cross] = pairWords(sig);
  const rows = (th: number) => D.rows.filter((r) => r.sig === sig && r.cut === cut && r.th === th).sort((p, q) => p.tau - q.tau);
  const dir = cut === "z" ? "along the axis" : "across";
  if (!D.taus.includes(S.rk)) S.rk = 10;
  const pts = (rs: PRow[], f: (r: PRow) => number | null) => rs.flatMap((r) => { const v = f(r); return v == null ? [] : [[r.tau, v] as [number, number]]; });
  for (const th of [0, 90, 180]) {
    const rs = rows(th);
    rTitles[`a${th}`].textContent = `${sig} width ${dir}, ${PTH[th].label}`;
    C[`a${th}`].update([
      { id: "cw", label: "continuous beams", color: "var(--muted)", dash: true, width: 1.6, pts: pts(rs, (r) => r.cw) },
      { id: "crest", label: "through the fringe crests", color: "#f28e2b", width: 2.2, dots: true, pts: pts(rs, (r) => r.crest) },
      { id: "all", label: "central fringe", color: "#e15759", width: 1.6, dots: true, pts: pts(rs, (r) => r.all) },
    ], { xlabel: "Pulse width τ (fs), click a point", ylabel: `FWHM ${dir} (µm)`, xlog: true, marker: S.rk, pickable: true, ydomain: [0, Math.max(0.1, ...rs.map((r) => r.cw ?? 0)) * 1.1] });
  }
  const X = M[S.rx] ?? M.tau, Y = M[S.ry] ?? M.crest, lx = S.rlog.includes("x"), ly = S.rlog.includes("y");
  const ths = String(S.rths).split(".").filter(Boolean).map(Number);
  rTitles.sc.textContent = `${Y.label.replace(/ \(.*\)$/, "")} against ${X.label.replace(/ \(.*\)$/, "")}, ${sig} ${dir}`;
  C.sc.update(ths.map((th) => ({ id: `s${th}`, label: PTH[th].label, color: PTH[th].color, width: 1.4, dots: true,
    pts: rows(th).flatMap((r) => { const x = X.get(r), y = Y.get(r); return x == null || y == null || (lx && x <= 0) || (ly && y <= 0) ? [] : [[x, y] as [number, number]]; }) })),
  { xlabel: X.label, ylabel: Y.label, xlog: lx, ylog: ly });
  drawProfile();
  const rs = rows(180);
  rTitles.st.textContent = `Signal added by the ${pairWords(sig)[1]}`;
  C.st.update([
    { id: "g", label: `total / ${cross} alone − 1`, color: "#e15759", width: 2.2, dots: true, pts: rs.flatMap((r) => (r.gain - 1 > 1e-6 ? [[r.tau, r.gain - 1] as [number, number]] : [])) },
    { id: "s", label: `${pairWords(sig)[1]} / ${cross}`, color: "#f28e2b", width: 2.2, dots: true, pts: rs.flatMap((r) => (r.same > 1e-6 ? [[r.tau, r.same] as [number, number]] : [])) },
  ], { xlabel: "Pulse width τ (fs)", ylabel: "Peak, relative", xlog: true, ylog: true, marker: S.rk, pickable: true });
  rTitles.dp.textContent = "Fringe depth (θ ≠ 0)";
  C.dp.update([{ id: "d", label: "fringe depth", color: "#6a3d9a", width: 2.2, dots: true, pts: rs.map((r) => [r.tau, r.depth] as [number, number]) }],
    { xlabel: "Pulse width τ (fs)", ylabel: "Fringe depth", xlog: true, ydomain: [0, 1.05], marker: S.rk, pickable: true });
  drawDelay();
  drawAgainstNA();
  drawDelayNA();
  void drawSweepMaps();
}
/** The delay sweep against NA: the peak and its position against the delay, the peak at Δt = τ for the pupils, and all pairs against
 *  the 350-nm pairs on the fine grid (pulse_delay_sweep.json, from scripts/export_pulse_delay_sweep_dashboard.py). */
const XNAS = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9];
const naColor = (na: number) => d3.interpolateViridis(Math.min(0.92, (na - 0.1) / 0.85));
const XSET: [string, string, string][] = [["rw_air", "circular pupil", "#1f77b4"], ["rw_air_gauss4", "Gaussian input, α = 4", "#9467bd"],
  ["rw_air_eps0.5", "annular pupil, ε = 0.5", "#ff7f0e"], ["rw_air_eps0.9", "annular pupil, ε = 0.9", "#2ca02c"]];
function drawDelayNA() {
  const D = pdsweep, C = rCharts!;
  if (!D) return;
  const tk = ({ 0: "0", 90: "pi2", 180: "pi" } as Record<number, string>)[S.xth] ?? "pi", ang = PTH[S.xth]?.label ?? "θ = π";
  if (!D.taus.includes(S.xtau)) S.xtau = 100;
  const tau = S.xtau, t = String(tau), xs = D.dtau, where = tk === "pi2" ? "along x" : "along z";
  const line = (ys: (number | null)[], x: (i: number) => number) => ys.flatMap((v, i) => (v == null ? [] : [[x(i), v] as [number, number]]));
  const circ = D.coarse.rw_air?.[tk]?.[t] ?? {};
  const nas = String(S.xnas).split(".").filter(Boolean).map((v) => +v / 100).filter((na) => circ[String(na)]).sort((p, q) => p - q);
  rTitles.xpk.textContent = `2CE peak of the 350-nm pairs against the delay, ${ang}, ${tau} fs`;
  C.xpk.update([...nas.map((na) => ({ id: `n${na}`, label: `NA ${na}`, color: naColor(na), width: 2.2, dots: true, pts: line(circ[String(na)].rel, (i) => xs[i]) })),
    { id: "ov", label: "temporal overlap exp(−2 ln2 (Δt/τ)²)", color: "var(--ink)", width: 2, dotted: true,
      pts: Array.from({ length: 81 }, (_, i) => [i / 40, Math.exp(-2 * Math.LN2 * (i / 40) ** 2)] as [number, number]) }],
  { xlabel: "Delay over the pulse width, Δt/τ", ylabel: "Peak (of its value at Δt = 0)", xdomain: [0, 2], ydomain: [0, 1.05] });
  rTitles.xpos.textContent = `Position of the 2CE peak ${where} against the delay, ${ang}, ${tau} fs`;
  C.xpos.update([...nas.map((na) => ({ id: `n${na}`, label: `NA ${na}`, color: naColor(na), width: 2.2, dots: true, pts: line(circ[String(na)].pos, (i) => xs[i] * tau) })),
    ...(tk === "pi" ? [{ id: "meet", label: "meeting point of the pulses, cΔt/2", color: "var(--ink)", width: 2, dash: true,
      pts: [[0, 0], [2 * tau, 0.299792458 * tau]] as [number, number][] }] : [])],
  { xlabel: "Delay Δt (fs)", ylabel: `Position of the peak ${where} (µm)`, xdomain: [0, 2 * tau] });
  const i1 = xs.findIndex((v) => Math.abs(v - 1) < 1e-9);
  rTitles.xpu.textContent = `2CE peak at Δt = τ against NA, pupils and inputs, ${ang}, ${tau} fs`;
  C.xpu.update([...XSET.map(([set, label, color]) => ({ id: set, label, color, width: 2.2, dots: true,
    pts: (D.nas[set] ?? []).flatMap((na) => { const v = D.coarse[set]?.[tk]?.[t]?.[String(na)]?.rel[i1]; return v == null ? [] : [[na, v] as [number, number]]; }) })),
    { id: "ov", label: "temporal overlap at Δt = τ, 0.25", color: "var(--ink)", width: 2, dotted: true, pts: [[0.1, 0.25], [0.95, 0.25]] }],
  { xlabel: "NA", ylabel: "Peak at Δt = τ (of its value at Δt = 0)", xdomain: [0.05, 1], ydomain: [0, 1.05] });
  const set = S.xpol === "p" ? "rw_air_polp" : "rw_air", f = D.fine[set]?.[tk]?.[t]?.[String(S.xna)];
  const pol = S.xpol === "p" ? "polarization in the plane of the lens axes" : "polarization perpendicular to the plane of the lens axes";
  rTitles.xfi.textContent = f ? `All pairs and the 350-nm pairs against the delay, ${ang}, ${tau} fs, NA ${S.xna}, ${pol}`
    : tau > 20 ? "All pairs against the delay: the fine grid holds 5, 10 and 20 fs; pick one of them."
    : `All pairs against the delay: the ${pol} was computed at NA ${(D.nas[set + "_fine"] ?? []).join(", ")}; pick one of them.`;
  const step = (i: number) => i * D.fine_step;
  C.xfi.update(f ? [
    { id: "tot", label: "all pairs, phase-locked pulses", color: "#4e79a7", width: 2, pts: line(f.total, step) },
    { id: "cross", label: "350-nm pairs", color: "#e15759", width: 2.2, pts: line(f.cross, step) }] : [],
  { xlabel: "Delay Δt (fs)", ylabel: S.xpol === "p" ? "Peak (of all pairs at Δt = 0)" : "Peak (each of its value at Δt = 0)", xdomain: [0, 2 * tau] });
}
/** How long the pulses must be to give the continuous-beam profiles against NA, and any measure against τ, NA or another measure. */
function drawAgainstNA() {
  const D = pna, C = rCharts!, sig = S.rsig, tk = { 0: "0", 90: "pi2", 180: "pi" }[S.nth as 0 | 90 | 180], k = `${sig}|${tk}`;
  if (!D || !D.met) return;
  const MED: Record<string, string> = { air: "#4e79a7", water: "#e15759", oil: "#59a14f" };
  const style = (name: string) => ({ color: MED[name.split("_")[1]] ?? "#888", dash: name.startsWith("paraxial") });
  const main = (name: string) => name.split("_").length === 2;          // circular pupil, uniform input
  const M = D.met, m = M[S.nm] ? S.nm : "diff", tol = (q: string) => (q === "side" ? `${M[q].tol} point` : q === "diff" || q === "dof" || q === "wx" ? `${M[q].tol}%` : `${M[q].tol / 100}`);
  rTitles.ntw.textContent = `Pulse width at which the ${M[m].label.toLowerCase()} of ${sig} comes within ${tol(m)} of continuous beams, ${PTH[S.nth].label}`;
  C.ntw.update(Object.entries(D.sets).filter(([name]) => main(name)).map(([name, d]) => ({ id: name, label: d.label, ...style(name), width: 2.2, dots: true,
    pts: (d.tw[k]?.[m] ?? []).flatMap(([na, t]) => (t == null ? [] : [[na, t] as [number, number]])) })),
  { xlabel: "NA", ylabel: "τ within tolerance of continuous beams (fs)", ylog: true, xdomain: [0, 1.25] });
  const d = D.sets[S.nset], V = d?.val[k] ?? {}, y = M[S.ny] ? S.ny : "dof", x = S.nx;
  const nas = Object.keys(V[y] ?? {}).map(Number).sort((p, q) => p - q), T = d?.taus ?? D.taus;
  const vir = (i: number, n: number) => d3.interpolateViridis(n > 1 ? i / (n - 1) : 0);
  const xl = x === "tau" ? "Pulse width τ (fs)" : x === "na" ? "NA" : `${M[x].label} (${M[x].unit.toLowerCase()})`;
  rTitles.ndv.textContent = `${M[y].label} of ${sig} against ${x === "tau" ? "the pulse width" : x === "na" ? "NA" : M[x].label.toLowerCase()}, ${d ? d.label : "not computed yet"}, ${PTH[S.nth].label}`;
  const series: Series[] = x === "na"
    ? T.map((t, j) => ({ id: `t${t}`, label: `${t} fs`, color: vir(j, T.length), width: 2, dots: true,
        pts: nas.flatMap((na) => { const v = V[y][String(na)][j]; return v == null ? [] : [[na, v] as [number, number]]; }) }))
    : nas.map((na, i) => ({ id: `na${na}`, label: `NA ${na}`, color: vir(i, nas.length), width: 2, dots: true,
        pts: T.flatMap((t, j) => { const xv = x === "tau" ? t : V[x]?.[String(na)][j], v = V[y][String(na)][j];
          return xv == null || v == null ? [] : [[xv, v] as [number, number]]; }) }));
  C.ndv.update(series, { xlabel: xl, ylabel: M[y].unit, xlog: x === "tau", ylog: y === "diff" });
}
/** Profile at the picked τ and angle: continuous beams, the total and, once its map is computed, the signal at t = 0. */
function drawProfile() {
  const D = psweep!, sig = S.rsig, cut = S.rcut, dir = cut === "z" ? "along the axis" : "across";
  const grid = cut === "z" ? D.z : D.x, key = `${sig}|${S.rpth}|${cut}`, kt = `${key}|${S.rk}`;
  const line = (y: number[] | undefined) => (y ?? []).map((v, i) => [grid[i], v] as [number, number]);
  const m = rMaps.get(JSON.stringify(mapOpts(sig, S.rk, S.rpth, 0)));
  const now: Series[] = [];
  if (m) {                                                             // from the map: the column x = 0, or the row z = 0
    const ix = (MG.nx - 1) / 2, iz = (MG.nz - 1) / 2;
    const v = cut === "z" ? MZ.map((z, i) => [z, m.now[i * MG.nx + ix]] as [number, number]) : MX.map((x, i) => [x, m.now[iz * MG.nx + i]] as [number, number]);
    const p = Math.max(...v.map((q) => q[1]));
    now.push({ id: "now", label: `${nowName(sig)} at t = 0`, color: "#1f77b4", width: 2, pts: v.map(([a, b]) => [a, p > 0 ? b / p : 0] as [number, number]) });
  }
  rTitles.pr.textContent = `${sig} ${dir}, τ = ${S.rk} fs, ${PTH[S.rpth].label}`;
  rCharts!.pr.update([
    { id: "cw", label: "continuous beams", color: "var(--muted)", dash: true, width: 1.6, pts: line(D.prof[`${key}|cw`]) },
    { id: "all", label: `total ${sig}, τ = ${S.rk} fs`, color: "#d62728", width: 2.4, pts: line(D.prof[`${kt}|all`]) },
    ...now,
  ], { xlabel: `${cut} (µm), ${cut === "z" ? "at x = 0" : "at z = 0"}`, ylabel: "Of its peak", ydomain: [0, 1.05] });
}
function drawDelay() {                                                 // against the path difference N = cΔt/λ₀, along the axis
  const D = pdelay!, C = rCharts!, sig = S.rsig, th = S.rdth;
  if (!D.ns.includes(S.rdn)) S.rdn = 8;
  if (!D.taus.includes(S.rdt)) S.rdt = 20;
  const xl = "Path difference N (λ₀ = 700 nm), click a point";
  const per = (f: (m: PDelay["met"][string]) => (number | null)[]) => D.taus.map((tau) => {
    const m = D.met[`${sig}|${th}|${tau}|all`];
    return { id: `t${tau}`, label: TAU[String(tau)].label, color: TAU[String(tau)].color, width: 2.2, dots: true,
      pts: f(m).flatMap((v, i) => (v == null ? [] : [[D.ns[i], v] as [number, number]])) };
  });
  rTitles.dpk.textContent = `Peak of the total ${sig} against the delay, ${PTH[th].label}`;
  C.dpk.update(per((m) => m.peak), { xlabel: xl, ylabel: "Peak (of its value at N = 0)", ydomain: [0, 1.05], marker: S.rdn, pickable: true });
  rTitles.dce.textContent = `${sig} centre along the axis against the delay, ${PTH[th].label}`;
  C.dce.update([...per((m) => m.centre), { id: "meet", label: "meeting point Nλ₀/2", color: "var(--ink)", dash: true, width: 1.6,
    pts: D.ns.map((n) => [n, (n * D.lam0) / 2] as [number, number]) }], { xlabel: xl, ylabel: "Centre along z (µm)", marker: S.rdn, pickable: true });
  rTitles.dfw.textContent = `${sig} FWHM along the axis against the delay, ${PTH[th].label}`;
  C.dfw.update(per((m) => m.fwhm), { xlabel: xl, ylabel: "FWHM along the axis (µm)", ydomain: [0, Math.max(...D.taus.flatMap((t) =>
    D.met[`${sig}|${th}|${t}|all`].fwhm.map((v) => v ?? 0))) * 1.1], marker: S.rdn, pickable: true });
  const k = `${sig}|${th}|${S.rdt}`, line = (y: number[] | undefined) => (y ?? []).map((v, i) => [D.z[i], v] as [number, number]);
  rTitles.dpr.textContent = `Total ${sig} along the axis, τ = ${S.rdt} fs, N = ${S.rdn} (Δt = ${((S.rdn * D.lam0) / 0.299792458).toFixed(1)} fs)`;
  C.dpr.update([
    { id: "n0", label: "N = 0", color: "var(--muted)", dash: true, width: 1.6, pts: line(D.prof[`${k}|all|0`]) },
    { id: "all", label: `N = ${S.rdn}`, color: "#d62728", width: 2.4, pts: line(D.prof[`${k}|all|${S.rdn}`]) },
  ], { xlabel: "z (µm), at x = 0", ylabel: "Of the N = 0 peak", ydomain: [0, 1.05] });
  void drawDelayMaps();
}

// ---- highlights: one card per key result; a card is a link to the settings of its view, plus hl=<id> for the banner ----
const hlHash = (h: Highlight) => "#" + new URLSearchParams(Object.entries({ ...h.preset, hl: h.id }).map(([k, v]) => [k, String(v)])).toString();
function highlightsView() {
  el("p", "hint", "Each card is one result of the current work. A click opens the view and the settings that show it, and the banner above the view steps through the results in order.", $("controls"));
  const a = layout("hl");
  for (const g of [...new Set(HIGHLIGHTS.map((h) => h.group))]) {
    const sec = el("section", "hl-group", "", a);
    el("h2", "hl-h", g, sec);
    const box = el("div", "hl-cards", "", sec);
    for (const h of HIGHLIGHTS.filter((x) => x.group === g)) {
      const card = el("a", "hl-card", "", box) as HTMLAnchorElement;
      card.href = hlHash(h);
      el("p", "hl-text", h.text, card);
      el("p", "hl-opens", h.opens, card);
    }
  }
  writeHash();
}
/** The banner of the open highlight: its result, the view it opens, back to the cards, and the previous and next highlights. */
function hlBanner() {
  const b = $("hlbar"), i = HIGHLIGHTS.findIndex((h) => h.id === S.hl);
  b.replaceChildren();
  b.hidden = S.mode === "hl" || i < 0;
  if (b.hidden) return;
  const h = HIGHLIGHTS[i];
  el("p", "hl-text", h.text, b);
  el("p", "hl-opens", h.opens, b);
  const nav = el("div", "hl-nav", "", b);
  const link = (text: string, to: string | null) => {
    const a = el("a", "", text, nav) as HTMLAnchorElement;
    if (to) a.href = to; else a.setAttribute("aria-disabled", "true");
  };
  link("Back to highlights", "#mode=hl");
  link("Previous", i > 0 ? hlHash(HIGHLIGHTS[i - 1]) : null);
  link("Next", i < HIGHLIGHTS.length - 1 ? hlHash(HIGHLIGHTS[i + 1]) : null);
  el("span", "hl-pos", `${i + 1} of ${HIGHLIGHTS.length}`, nav);
}

/** Once the view of an open highlight has drawn, bring the plot it names (highlight.scroll) into view; tries for up to 12 s. */
let hlScrollGen = 0;
function hlScroll() {
  const id = HIGHLIGHTS.find((h) => h.id === S.hl)?.scroll, gen = ++hlScrollGen;
  if (!id || S.mode === "hl") return;
  let tries = 0, seen = 0;
  const go = () => {
    if (gen !== hlScrollGen) return;                                  // another highlight was opened meanwhile
    const e = document.getElementById(id), svg = e?.querySelector("svg path");
    if (e && svg && e.getBoundingClientRect().height > 0) {
      e.scrollIntoView({ block: "center" });
      if (++seen < 2) setTimeout(go, 1500);                           // once more after the charts above have settled
      return;
    }
    if (++tries < 48) setTimeout(go, 250);
  };
  setTimeout(go, 400);
}

// ---------------------------------------------------------------- main -----------------------------------------------------------------
async function main() {
  readHash();
  try {
    const get = async (p: string) => { const r = await fetch(p); if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); };
    [data, metrics, pulses, scatter] = await Promise.all([loadData(), get("./data/metrics.json"),
      get("./data/pulses.json"), get("./data/scattering.json")]);
  } catch (err) {
    $("app").textContent = `Could not load data (${(err as Error).message}).`;
    return;
  }
  let shown: Mode | null = null;
  render = () => {
    if (shown !== S.mode) { stopPlay(); liveState = naCharts = sCharts = wState = pState = null; rCharts = null; shown = S.mode; }
    for (const a of $("nav").querySelectorAll<HTMLAnchorElement>("a")) a.toggleAttribute("aria-current", a.dataset.mode === S.mode);
    $("controls").replaceChildren();
    hlBanner();
    if (S.mode === "hl") { highlightsView(); return; }
    const rb = el("button", "reset reset-all", "Reset parameters", $("controls")) as HTMLButtonElement;
    rb.type = "button"; rb.title = "All parameters back to their defaults (this tab stays open)";
    rb.onclick = () => { const mode = S.mode, hl = S.hl; Object.assign(S, DEF, { mode, hl }); render(); };   // an open highlight keeps its banner
    if (S.mode === "live") { live(); writeHash(); }
    else if (S.mode === "theta" || S.mode === "dl" || S.mode === "eps" || S.mode === "pulses") sweepView(S.mode);
    else if (S.mode === "scatter") scatterView();
    else if (S.mode === "ptime") pulseTime();
    else if (S.mode === "psum") void pulseResults();
    else againstNA();
  };
  redraw = () => {
    if (S.mode === "live") { cancelAnimationFrame(pending); pending = requestAnimationFrame(drawLive); writeHash(); }
    else if (S.mode === "ptime" && pState) { schedulePulses(); writeHash(); }
    else if (S.mode === "psum" && rCharts && psweep) { drawResults(); writeHash(); }
    else if (wState && S.mode === wState.kind) { cancelAnimationFrame(pending); pending = requestAnimationFrame(drawSweep); }
    else render();
  };
  panels($("app"));
  addEventListener("hashchange", () => { const m = S.mode; Object.assign(S, DEF); readHash();   // a link sets every parameter: those it leaves out are the defaults
    if (m !== S.mode) scrollTo(0, 0); render(); hlScroll(); });
  render();
  hlScroll();
}
main();
