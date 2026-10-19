// Insights tab: one finding per card, each with a small chart from the same data and links into the dashboards.
import * as d3 from "d3";
import { wkey, type Data, type Medium } from "./data";

export const slug = (t: string) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export function el<K extends keyof HTMLElementTagNameMap>(tag: K, cls = "", text = "", parent?: HTMLElement) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  parent?.append(e);
  return e;
}

type Series = { name: string; cls: string; pts: [number, number][] };

/** NA on a log axis, values on y; end-of-line labels; a dashed reference line at y = ref if given. */
function lineChart(parent: HTMLElement, series: Series[], ylab: string, opts: { ref?: number; fmt?: (v: number) => string; logy?: boolean } = {}) {
  const wrap = el("div", "ins-chart", "", parent);
  const W = Math.max(260, wrap.clientWidth || 520), H = 210;
  const m = { t: 26, r: 104, b: 26, l: 44 };
  const svg = d3.select(wrap).append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", ylab);
  const all = series.flatMap((s) => s.pts);
  const x = d3.scaleLog().domain(d3.extent(all, (p) => p[0]) as [number, number]).range([m.l, W - m.r]);
  let [lo, hi] = d3.extent(all, (p) => p[1]) as [number, number];
  if (opts.ref !== undefined) { lo = Math.min(lo, opts.ref); hi = Math.max(hi, opts.ref); }
  const y = (opts.logy ? d3.scaleLog() : d3.scaleLinear()).domain(opts.logy ? [lo / 1.2, hi * 1.2] : [lo - (hi - lo) * 0.08, hi + (hi - lo) * 0.08])
    .range([H - m.b, m.t]);
  const fmt = opts.fmt ?? d3.format("~g");
  const g = svg.append("g");
  g.append("text").attr("class", "ins-axis ins-axis-title").attr("x", 2).attr("y", 11).text(ylab);
  const yt = opts.logy ? [0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000].filter((v) => v >= y.domain()[0] && v <= y.domain()[1]) : (y as d3.ScaleLinear<number, number>).ticks(4);
  for (const t of yt) {
    g.append("line").attr("class", "ins-grid").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(t)).attr("y2", y(t));
    g.append("text").attr("class", "ins-axis").attr("x", m.l - 6).attr("y", y(t)).attr("dy", "0.35em").attr("text-anchor", "end").text(fmt(t));
  }
  for (const t of [0.2, 0.3, 0.5, 0.7, 1].filter((v) => v >= x.domain()[0] - 1e-9 && v <= x.domain()[1] + 1e-9))
    g.append("text").attr("class", "ins-axis").attr("x", x(t)).attr("y", H - 8).attr("text-anchor", "middle").text(t);
  g.append("text").attr("class", "ins-axis ins-axis-title").attr("x", W - m.r).attr("y", H - 8).attr("text-anchor", "start").attr("dx", 8).text("NA");
  if (opts.ref !== undefined)
    g.append("line").attr("class", "ins-marker").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(opts.ref)).attr("y2", y(opts.ref));
  const line = d3.line<[number, number]>().x((p) => x(p[0])).y((p) => y(p[1]));
  const ends = series.map((s) => ({ s, y: y(s.pts[s.pts.length - 1][1]) })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) ends[i].y = Math.max(ends[i].y, ends[i - 1].y + 13);
  const over = ends.length ? ends[ends.length - 1].y - (H - m.b - 14) : 0;   // keep clear of the NA title below
  if (over > 0) for (const e of ends) e.y -= over;
  for (const { s, y: ly } of ends) {
    g.append("path").attr("class", `pline ${s.cls}`).attr("d", line(s.pts));
    g.append("text").attr("class", "ins-axis ins-direct").attr("x", W - m.r + 8).attr("y", ly).attr("dy", "0.35em").text(s.name);
  }
}

/** Ratio a/b of two width series at the NAs they share. */
export function ratio(data: Data, a: string, b: string): [number, number][] {
  const B = new Map((data.widths[b] ?? []).map((p) => [p[0], p[1]]));
  return (data.widths[a] ?? []).filter((p) => B.has(p[0])).map((p) => [p[0], p[1] / B.get(p[0])!]);
}

const W2 = (s: "2PE" | "2CE", a: "x" | "z", t: "0" | "pi2" | "pi", m: "vector" | "scalar", p: "circ" | "ann", i: "uni" | "gau", med: Medium) =>
  wkey(s, a, t, m, p, i, med);
const pct = (v: number) => `${Math.round((v - 1) * 100)}%`;

export function renderInsights(host: HTMLElement, data: Data) {
  if (host.childElementCount) return;
  const nav = el("nav", "ins-nav", "", host);
  const main = el("div", "ins-main", "", host);
  const sections: [string, HTMLElement][] = [];
  const section = (title: string) => {
    const s = el("section", "ins-section", "", main);
    s.id = slug(title);
    el("h2", "ins-section-title", title, s);
    sections.push([title, s]);
    return el("div", "ins-cards", "", s);
  };
  const card = (parent: HTMLElement, title: string, lede: string, links: [string, string][] = []) => {
    const c = el("article", "ins-card", "", parent);
    c.id = slug(title);
    el("h2", "", title, c);
    el("p", "ins-lede", lede, c);
    const ex = el("div", "ins-explores", "", c);
    for (const [label, href] of links) {
      const a = el("a", "ins-explore", `${label} →`, ex) as HTMLAnchorElement;
      a.href = href;
    }
    return c;
  };
  // keys are overlay names ("fig2a") or [file, caption] pairs
  const images = (parent: HTMLElement, keys: (string | [string, string])[], caption: string) => {
    const grid = el("div", "ins-images", "", parent);
    for (const k of keys) {
      const [file, cap] = typeof k === "string" ? [k, `Fig. ${k.slice(3)}`] : k;
      const fig = el("figure", "", "", grid);
      const img = el("img", "", "", fig) as HTMLImageElement;
      img.src = `./img/${file}.png`; img.alt = typeof k === "string" ? `${cap}: current work over the paper` : cap; img.loading = "lazy";
      el("figcaption", "", cap, fig);
    }
    el("p", "ins-footnote", caption, parent);
  };

  // ---------------- Replication ----------------
  const rep = section("Replication at NA 0.5");
  images(card(rep, "Circular pupils come back from the equations",
    "Figs. 2–3 rebuilt from Eqs. 1–6 of the paper (paraxial scalar, NA 0.5, air): current work in color over the printed curves.",
    [["See the profiles", "#v=profiles&m=air&na=0.5&s=2CE&a=x&mo=scalar&p=circ&i=uni&th=0.pi2.pi"]]),
  ["fig2a", "fig2b", "fig3a", "fig3b"], "(a) 2PE, (b) 2CE; Fig. 2 across the axis, Fig. 3 along it.");
  images(card(rep, "Annular pupils: Figs. 6(a) and 7(a) plot the excitation",
    "With annular pupils (ε = 0.99) the 2CE panels match. The printed 2PE curves of Figs. 6(a) and 7(a) are the excitation |U₁ + U₂|², not Eq. 6 (|U₁ + U₂|⁴).",
    [["See the annular profiles", "#v=profiles&m=air&na=0.5&s=2CE&a=z&mo=scalar&p=ann&i=uni&th=0.pi2.pi"]]),
  ["fig6a", "fig6b", "fig7a", "fig7b"], "Orange: |U₁ + U₂|²; blue: Eq. 6.");
  const gap = card(rep, "A wider gap between the two wavelengths",
    "Figs. 4–5: the 2CE focus at θ = π/2 as Δλ = λ₁ − λ₂ grows from 10 to 94 nm. As in the paper, the spot widens by about 6% (p. 30) and the depth of focus shortens, here by about 5%.",
    []);
  gap.classList.add("ins-card-wide");
  images(gap, [["paper4a", "Fig. 4a, paper"], ["paper4b", "Fig. 4b, paper"], ["paper5", "Fig. 5, paper"],
   ["cw4a", "Fig. 4a, current work"], ["cw4b", "Fig. 4b, current work"], ["cw5", "Fig. 5, current work"]],
  "Fig. 4: (a) across the axis, (b) along it. Fig. 5: width across the axis (FWHM) and depth of focus (DOF) against Δλ.");

  // ---------------- High and low NA ----------------
  const hn = section("From low to high NA");
  const dof = (med: Medium, p: "circ" | "ann" = "circ") => ratio(data, W2("2CE", "z", "0", "scalar", p, "uni", med), W2("2CE", "z", "0", "vector", p, "uni", med));
  const at = (pts: [number, number][], na: number) => pts.find((q) => Math.abs(q[0] - na) < 1e-6)?.[1] ?? NaN;
  {
    const air = dof("air"), water = dof("water");
    const c = card(hn, "The paraxial depth of focus is too long at high NA",
      `The scalar model of the paper gives a longer focus than the vector one: ${pct(at(air, 0.5))} at NA 0.5, ${pct(at(air, 0.9))} at NA 0.9 in air. ` +
      `In water the gap at the same NA is smaller (${pct(at(water, 0.9))} at NA 0.9). Across the axis the two agree within 6% to NA 0.9.`,
      [["Depth of focus against NA", "#v=widths&m=air&na=0.9&s=2CE&a=z&mo=both&p=circ&i=uni&th=0.pi2.pi"],
       ["Axial profiles at NA 0.9", "#v=profiles&m=air&na=0.9&s=2CE&a=z&mo=both&p=circ&i=uni&th=0"]]);
    lineChart(c, [{ name: "air", cls: "t0 vector", pts: air }, { name: "water", cls: "t2 vector", pts: water }],
      "Scalar DOF / vector DOF (2CE, θ = 0)", { ref: 1, fmt: d3.format(".2f") });
  }
  {
    const r = (m: "vector" | "scalar", med: Medium) => ratio(data, W2("2CE", "x", "pi2", m, "circ", "uni", med), W2("2PE", "x", "pi2", m, "circ", "uni", med));
    const c = card(hn, "The paper's comparisons hold at high NA",
      `At θ = π/2 the 2CE spot stays wider than the 2PE spot, by less as NA grows: ${at(r("vector", "air"), 0.5).toFixed(1)}× at NA 0.5, ` +
      `${at(r("vector", "air"), 0.7).toFixed(1)}× at NA 0.7. Scalar and vector agree within 4%.`,
      [["Widths across the axis", "#v=widths&m=air&na=0.7&s=2CE&a=x&mo=both&p=circ&i=uni&th=pi2"]]);
    lineChart(c, [{ name: "vector, air", cls: "t1 vector", pts: r("vector", "air") }, { name: "scalar, air", cls: "t1 scalar", pts: r("scalar", "air") },
      { name: "vector, water", cls: "t2 vector", pts: r("vector", "water") }], "2CE width / 2PE width across the axis, θ = π/2");
  }
  {
    const ann = data.widths[W2("2CE", "z", "0", "vector", "ann", "uni", "air")] ?? [];
    const sca = data.widths[W2("2CE", "z", "0", "scalar", "ann", "uni", "air")] ?? [];
    const circ = data.widths[W2("2CE", "z", "0", "vector", "circ", "uni", "air")] ?? [];
    const c = card(hn, "Annular pupils: a long, thin focus",
      `An annular pupil (ε = 0.99) stretches the depth of focus ${Math.round(at(ann, 0.5) / at(circ, 0.5))}× at NA 0.5 and narrows the spot to 0.70× of the circular one. ` +
      `At high NA the paraxial model overestimates the annular focus: ${(at(sca, 0.9) / at(ann, 0.9)).toFixed(1)}× at NA 0.9.`,
      [["Annular depth of focus against NA", "#v=widths&m=air&na=0.9&s=2CE&a=z&mo=both&p=ann&i=uni&th=0.pi2.pi"]]);
    lineChart(c, [{ name: "annular, vector", cls: "t0 vector", pts: ann }, { name: "annular, scalar", cls: "t0 scalar", pts: sca },
      { name: "circular", cls: "t2 vector", pts: circ }], "2CE depth of focus, θ = 0 (µm)", { logy: true });
  }
  {
    const keys: [string, string, string][] = [["air|0.3", "NA 0.3, air", "t0"], ["air|0.7", "NA 0.7, air", "t1"], ["water|0.9", "NA 0.9, water", "t2"]];
    const c = card(hn, "The wavelength gap acts the same at all NA",
      "Figs. 4–5 of the paper: widening the gap Δλ between the two wavelengths widens the 2CE spot at θ = π/2 by about 6% from 10 to 94 nm, " +
      "and shortens its depth of focus by about 5%, at low and high NA alike.");
    const wrap = el("div", "ins-chart", "", c);
    const W = Math.max(260, wrap.clientWidth || 520), H = 200, m = { t: 26, r: 104, b: 26, l: 44 };
    const svg = d3.select(wrap).append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", "relative width against wavelength gap");
    const x = d3.scaleLinear().domain([0, 100]).range([m.l, W - m.r]), y = d3.scaleLinear().domain([0.94, 1.07]).range([H - m.b, m.t]);
    const g = svg.append("g");
    g.append("text").attr("class", "ins-axis ins-axis-title").attr("x", 2).attr("y", 11).text("2CE width / width at Δλ = 10 nm (vector)");
    for (const t of [0.95, 1, 1.05]) {
      g.append("line").attr("class", "ins-grid").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(t)).attr("y2", y(t));
      g.append("text").attr("class", "ins-axis").attr("x", m.l - 6).attr("y", y(t)).attr("dy", "0.35em").attr("text-anchor", "end").text(t.toFixed(2));
    }
    for (const t of [0, 20, 40, 60, 80, 100]) g.append("text").attr("class", "ins-axis").attr("x", x(t)).attr("y", H - 8).attr("text-anchor", "middle").text(t);
    g.append("text").attr("class", "ins-axis ins-axis-title").attr("x", W - m.r).attr("dx", 8).attr("y", H - 8).text("Δλ (nm)");
    for (const [k, name, cls] of keys)
      for (const a of ["x", "z"] as const) {
        const pts = data.dlambda[`${k}|${a}|vector`];
        if (!pts) continue;
        const rel = pts.map((p) => [p[0], p[1] / pts[0][1]] as [number, number]);
        g.append("path").attr("class", `pline ${cls} vector`).attr("d", d3.line<[number, number]>().x((p) => x(p[0])).y((p) => y(p[1]))(rel));
        if (a === "x") g.append("text").attr("class", "ins-axis ins-direct").attr("x", W - m.r + 8)
          .attr("y", y(1.06) + 13 * keys.findIndex((k) => k[2] === cls) - 13).attr("dy", "0.35em").text(name);
      }
    el("p", "ins-footnote", "Upper lines: width across the axis; lower lines: depth of focus. Scalar within 0.3% of vector.", c);
  }
  {
    const g = (s: "2CE", a: "x" | "z", med: Medium) => ratio(data, W2(s, a, "0", "vector", "circ", "gau", med), W2(s, a, "0", "vector", "circ", "uni", med));
    const c = card(hn, "A Gaussian input widens the 2CE response by half",
      `A truncated Gaussian input (α = 4) instead of a uniform one widens the 2CE spot ${at(g("2CE", "x", "air"), 0.5).toFixed(2)}× and its depth of focus ` +
      `${at(g("2CE", "z", "air"), 0.5).toFixed(2)}× at NA 0.5, up to ${at(g("2CE", "z", "air"), 0.9).toFixed(2)}× at NA 0.9 in air.`,
      [["Gaussian input against NA", "#v=widths&m=air&na=0.9&s=2CE&a=z&mo=vector&p=circ&i=gau&th=0.pi2.pi"]]);
    lineChart(c, [{ name: "spot, air", cls: "t0 vector", pts: g("2CE", "x", "air") }, { name: "DOF, air", cls: "t1 vector", pts: g("2CE", "z", "air") },
      { name: "DOF, water", cls: "t2 vector", pts: g("2CE", "z", "water") }], "Gaussian / uniform width (2CE, θ = 0)", { fmt: d3.format(".2f") });
  }

  // ---------------- nav ----------------
  for (const [title, s] of sections) {
    const a = el("a", "ins-nav-link", title, nav) as HTMLAnchorElement;
    a.href = `#v=insights`;
    a.addEventListener("click", (e) => { e.preventDefault(); s.scrollIntoView({ behavior: "smooth" }); });
  }
}
