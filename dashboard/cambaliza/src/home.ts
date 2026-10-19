// Landing page: what this is, the main findings as tiles (each opens its Insights card), and how to use the dashboards.
import * as d3 from "d3";
import { wkey, type Data } from "./data";
import { el, ratio, slug } from "./insights";

export function renderHome(root: HTMLElement, data: Data, name: string) {
  if (root.childElementCount) return;
  const hero = el("section", "home-hero", "", root);
  el("h1", "", name, hero);
  el("p", "home-lede", "Cambaliza & Saloma (2000) rebuilt from its equations, then taken from low to high NA, in air and in water.", hero);

  const hl = el("section", "home-section", "", root);
  el("h2", "home-h", "Main findings", hl);
  const cta = el("a", "home-cta", "Start with Insights →", hl) as HTMLAnchorElement;
  cta.href = "#v=insights";
  const list = el("div", "home-highlights", "", hl);

  const W = (s: "2PE" | "2CE", a: "x" | "z", t: "0" | "pi2" | "pi", m: "vector" | "scalar", p: "circ" | "ann", i: "uni" | "gau", med: "air" | "water") =>
    wkey(s, a, t, m, p, i, med);
  const at = (pts: [number, number][], na: number) => pts.find((q) => Math.abs(q[0] - na) < 1e-6)?.[1] ?? NaN;
  const dofAir = ratio(data, W("2CE", "z", "0", "scalar", "circ", "uni", "air"), W("2CE", "z", "0", "vector", "circ", "uni", "air"));
  const dofWater = ratio(data, W("2CE", "z", "0", "scalar", "circ", "uni", "water"), W("2CE", "z", "0", "vector", "circ", "uni", "water"));
  const ann = data.widths[W("2CE", "z", "0", "vector", "ann", "uni", "air")] ?? [];
  const circ = data.widths[W("2CE", "z", "0", "vector", "circ", "uni", "air")] ?? [];
  const cmp = ratio(data, W("2CE", "x", "pi2", "vector", "circ", "uni", "air"), W("2PE", "x", "pi2", "vector", "circ", "uni", "air"));

  type Tile = { stat: string; title: string; text: string; card: string; mini?: [number, number][][]; img?: string };
  const tiles: Tile[] = [
    { stat: "NA 0.5", title: "2PE and 2CE profiles recomputed from Eqs. 1–6", img: "cw2b",
      text: "Circular and annular pupils at NA 0.5; current work agrees with the published curves.", card: "Circular pupils: 2PE and 2CE profiles recomputed from Eqs. 1–6" },
    { stat: `+${Math.round((at(dofAir, 0.9) - 1) * 100)}%`, title: "The paraxial depth of focus is too long at high NA", mini: [dofAir, dofWater],
      text: `Scalar over vector at NA 0.9 in air; ${Math.round((at(dofWater, 0.9) - 1) * 100)}% in water.`, card: "The paraxial depth of focus is too long at high NA" },
    { stat: `${at(cmp, 0.5).toFixed(1)}× → ${at(cmp, 0.7).toFixed(1)}×`, title: "2CE–2PE comparisons hold at high NA", mini: [cmp],
      text: "2CE over 2PE spot at θ = π/2, NA 0.5 to 0.7; scalar and vector within 4%.", card: "2CE–2PE comparisons hold at high NA" },
    { stat: `${Math.round(at(ann, 0.5) / at(circ, 0.5))}×`, title: "Annular pupils: a long, thin focus", mini: [ann, circ],
      text: "Depth of focus over the circular one at NA 0.5, with a spot 0.70× as wide.", card: "Annular pupils: a long, thin focus" },
  ];
  for (const t of tiles) {
    const a = el("a", "home-highlight", "", list) as HTMLAnchorElement;
    a.href = "#v=insights";
    a.addEventListener("click", () => setTimeout(() => {
      const c = document.getElementById(slug(t.card));
      c?.scrollIntoView({ behavior: "smooth", block: "start" });
      c?.classList.add("flash");
      setTimeout(() => c?.classList.remove("flash"), 1500);
    }, 60));
    if (t.img) {
      const img = el("img", "home-mini home-img", "", a) as HTMLImageElement;
      img.src = `./img/${t.img}.png`; img.alt = "";
    } else if (t.mini) {
      const svg = d3.select(a).append("svg").attr("class", "home-mini").attr("viewBox", "0 0 200 54").attr("preserveAspectRatio", "none");
      const all = t.mini.flat();
      const x = d3.scaleLog().domain(d3.extent(all, (p) => p[0]) as [number, number]).range([2, 198]);
      const y = d3.scaleLog().domain(d3.extent(all, (p) => p[1]) as [number, number]).range([51, 4]);
      t.mini.forEach((pts, i) => svg.append("path").attr("class", `home-line home-line-sm${i ? " home-line-soft" : ""}`)
        .attr("d", d3.line<[number, number]>().x((p) => x(p[0])).y((p) => y(p[1]))(pts)));
    }
    el("b", "", t.stat, a);
    el("strong", "", t.title, a);
    el("span", "", t.text, a);
  }

  const how = el("section", "home-section", "", root);
  el("h2", "home-h", "Explore", how);
  const entries = el("div", "home-highlights", "", how);
  for (const [title, text, href] of [
    ["Profiles", "The 2PE and 2CE responses across and along the axis at one NA, for the three angles between the lenses.",
      "#v=profiles&m=air&na=0.5&s=2CE&a=x&mo=both&p=circ&i=uni&th=0.pi2.pi"],
    ["Widths", "Width across the axis and depth of focus against NA, from 0.2 to 0.95 in air and to 1.25 in water.",
      "#v=widths&m=air&na=0.5&s=2CE&a=z&mo=both&p=circ&i=uni&th=0.pi2.pi"],
  ]) {
    const a = el("a", "home-highlight", "", entries) as HTMLAnchorElement;
    a.href = href;
    el("strong", "", `${title} →`, a);
    el("span", "", text, a);
  }
  el("p", "home-sub home-how-note",
    "Options sit in the side panel; the URL keeps your view, so links are shareable. Solid lines are the vector focus, dashed the paraxial scalar model (Eqs. 1–6).",
    how);
}
