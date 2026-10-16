import "./style.css";
import { Chart, type State, type View } from "./chart";
import { loadData, THETAS, type Data, type Theta } from "./data";
import { renderHome } from "./home";
import { renderInsights } from "./insights";

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const NAME = "Two-Color Excitation";

async function main() {
  let data: Data;
  try {
    data = await loadData();
  } catch (err) {
    $("status").textContent = `Could not load data (${(err as Error).message}). Run scripts/dashboard_cambaliza_data.py first.`;
    $("explore").hidden = false;
    return;
  }

  const state: State = {
    view: "home", medium: "air", na: 0.5, signal: "2CE", axis: "x", model: "both", pupil: "circ", input: "uni",
    th: { "0": true, pi2: true, pi: true },
  };
  readHash(state, data);

  const progress = $("progress");
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    progress.style.transform = `scaleX(${max > 8 ? Math.min(1, scrollY / max) : 0})`;
  };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);

  const chart = new Chart($("chart"), data, $("legend"), $("status"), $("chartTitle"));
  $("chart").addEventListener("pickna", (e) => { state.na = (e as CustomEvent<number>).detail; update(); });

  // ----- segmented controls (radio groups with roving focus) -----
  const segs = ["view", "medium", "signal", "axis", "model", "pupil", "input"] as const;
  for (const key of segs) {
    const buttons = [...$(key).querySelectorAll<HTMLButtonElement>("button")];
    const pick = (b: HTMLButtonElement) => {
      const value = b.dataset.value!;
      if (state[key] === value) return;
      (state[key] as string) = value;
      if (key === "medium") state.na = nearestNA(data, state.medium, state.na);
      update(key === "view");
    };
    buttons.forEach((b, i) => {
      b.addEventListener("click", () => pick(b));
      b.addEventListener("keydown", (e) => {
        const d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        const next = buttons[(i + d + buttons.length) % buttons.length];
        next.focus();
        pick(next);
      });
    });
  }
  for (const t of THETAS)
    $(`th-${t}`).addEventListener("click", () => { state.th[t] = !state.th[t]; update(); });

  const slider = $<HTMLInputElement>("na");
  slider.addEventListener("input", () => { state.na = data.meta.na[state.medium][+slider.value]; update(); });

  $("exportBtn").addEventListener("click", () => {
    const t = $("chartTitle").textContent ?? "";
    chart.exportPNG(t, `${NAME} · Cambaliza & Saloma, Opt. Commun. 184 (2000) 25–35; current work`,
      `${t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`);
  });

  const setPanel = (open: boolean) => {
    document.body.classList.toggle("panel-hidden", !open);
    $("panelShow").hidden = open;
    try { localStorage.setItem("panelHidden", open ? "0" : "1"); } catch { /* storage unavailable */ }
  };
  $("panelHide").addEventListener("click", () => setPanel(false));
  $("panelShow").addEventListener("click", () => setPanel(true));
  try { if (localStorage.getItem("panelHidden") === "1") setPanel(false); } catch { /* storage unavailable */ }
  const moreBtn = $<HTMLButtonElement>("moreBtn");
  const setMore = (open: boolean) => {
    $("more").hidden = !open;
    moreBtn.setAttribute("aria-expanded", String(open));
    moreBtn.textContent = open ? "Fewer settings" : "More settings";
  };
  moreBtn.addEventListener("click", () => setMore($("more").hidden === true));

  addEventListener("hashchange", () => { readHash(state, data); update(true); });
  new ResizeObserver(() => { if (state.view === "profiles" || state.view === "widths") chart.render(state); }).observe($("chart"));

  function update(scrollTop = false) {
    for (const key of segs)
      for (const b of $(key).querySelectorAll<HTMLButtonElement>("button")) {
        const on = b.dataset.value === String(state[key]);
        b.setAttribute("aria-checked", String(on));
        b.tabIndex = on ? 0 : -1;
      }
    for (const t of THETAS) $(`th-${t}`).setAttribute("aria-pressed", String(state.th[t]));
    const nas = data.meta.na[state.medium];
    slider.min = "0"; slider.max = String(nas.length - 1); slider.step = "1";
    slider.value = String(Math.max(0, nas.indexOf(state.na)));
    $("naOut").textContent = `NA ${state.na} (${state.medium}, n = ${data.meta.n[state.medium]})`;
    if (state.pupil !== "circ" || state.input !== "uni") setMore(true);

    const explore = state.view === "profiles" || state.view === "widths";
    $("home").hidden = state.view !== "home";
    $("insights").hidden = state.view !== "insights";
    $("explore").hidden = !explore;
    document.body.dataset.view = state.view;
    if (state.view === "home") renderHome($("home"), data, NAME);
    if (state.view === "insights") renderInsights($("insights"), data);
    if (explore) chart.render(state);
    writeHash(state);
    if (scrollTop) scrollTo(0, 0);
  }
  update();
}

function nearestNA(data: Data, medium: State["medium"], na: number) {
  return data.meta.na[medium].reduce((a, b) => (Math.abs(b - na) < Math.abs(a - na) ? b : a));
}

/** The URL keeps the view, e.g. #v=profiles&m=water&na=0.9&s=2CE&a=z&mo=both&p=ann&i=uni&th=0.pi */
function writeHash(s: State) {
  const th = THETAS.filter((t) => s.th[t]).join(".") || "none";
  const h = s.view === "home" ? "#v=home" : s.view === "insights" ? "#v=insights" :
    `#v=${s.view}&m=${s.medium}&na=${s.na}&s=${s.signal}&a=${s.axis}&mo=${s.model}&p=${s.pupil}&i=${s.input}&th=${th}`;
  if (location.hash !== h) history.replaceState(null, "", h);
}

function readHash(s: State, data: Data) {
  const q = new URLSearchParams(location.hash.slice(1));
  const pick = <T extends string>(k: string, ok: readonly T[], cur: T): T => (ok.includes(q.get(k) as T) ? (q.get(k) as T) : cur);
  s.view = pick<View>("v", ["home", "insights", "profiles", "widths"], s.view);
  s.medium = pick("m", ["air", "water"] as const, s.medium);
  s.signal = pick("s", ["2PE", "2CE"] as const, s.signal);
  s.axis = pick("a", ["x", "z"] as const, s.axis);
  s.model = pick("mo", ["both", "vector", "scalar"] as const, s.model);
  s.pupil = pick("p", ["circ", "ann"] as const, s.pupil);
  s.input = pick("i", ["uni", "gau"] as const, s.input);
  if (q.get("na")) s.na = nearestNA(data, s.medium, +q.get("na")!);
  if (q.get("th")) for (const t of THETAS) s.th[t as Theta] = q.get("th")!.split(".").includes(t);
}

main();
