// "How it is measured": the quantity being plotted, drawn on the actual profile at the picked NA, with its equations.
import * as d3 from "d3";
import katex from "katex";
import "katex/dist/katex.min.css";

export type HowData = { s: number[]; vec: number[]; sca?: number[]; axis: "x" | "z"; lamn: number; label: string };

const tex = (t: string) => katex.renderToString(t, { displayMode: true, throwOnError: false });

/** Half-maximum crossings around the centre (s = 0). */
function half(s: number[], y: number[]): [number, number] | null {
  const i0 = s.reduce((a, v, i) => (Math.abs(v) < Math.abs(s[a]) ? i : a), 0), h = 0.5 * y[i0];
  let r = i0, l = i0;
  while (r < y.length - 1 && y[r] >= h) r++;
  while (l > 0 && y[l] >= h) l--;
  if (y[r] >= h || y[l] >= h) return null;
  const at = (a: number, b: number) => s[a] + ((h - y[a]) / (y[b] - y[a])) * (s[b] - s[a]);
  return [at(l, l + 1), at(r, r - 1)];
}
/** First minimum and first side peak at s > 0 (profile normalized at the centre), as in the data scripts. */
function lobe(s: number[], y: number[]): { min: number; s: number; h: number } | null {
  let i = s.reduce((a, v, k) => (Math.abs(v) < Math.abs(s[a]) ? k : a), 0);
  while (i < y.length - 1 && y[i + 1] <= y[i]) i++;
  let j = i;
  while (j < y.length - 1 && y[j + 1] >= y[j]) j++;
  if (j >= y.length - 1 || j === i || y[j] < 1e-3) return null;
  return { min: s[i], s: s[j], h: y[j] };
}
const unit = (y: number[], ds: number) => { const t = y.reduce((a, b) => a + b, 0) * ds; return y.map((v) => v / t); };

const TEXT: Record<string, { what: string; eq: string[] }> = {
  width: { what: "The full width at half maximum of the profile is the spot size (FWHM) across the axis and the depth of focus (DOF) along it.",
    eq: ["I(s_\\pm) = \\tfrac{1}{2}\\, I(0)", "w = s_+ - s_-"] },
  gap: { what: "How much wider the paraxial scalar profile is than the vector one, in percent. The band marks ±5%.",
    eq: ["\\Delta = \\left(\\frac{w_\\text{scalar}}{w_\\text{vector}} - 1\\right) \\times 100\\%"] },
  nrmse: { what: "The difference over the whole profile, with both profiles scaled to unit energy over the window so that side lobes count too; a is the scalar profile and r the vector one.",
    eq: ["\\sum_k a_k\\,\\Delta s = \\sum_k r_k\\,\\Delta s = 1", "\\text{NRMSE} = \\sqrt{\\frac{\\sum_k (a_k - r_k)^2}{\\sum_k r_k^2}} = \\sqrt{1 - F}"] },
  F: { what: "Linfoot's fidelity is one minus the squared difference of the unit-energy profiles, relative to the vector one; it is 1 for identical profiles.",
    eq: ["F = 1 - \\frac{\\sum_k (a_k - r_k)^2}{\\sum_k r_k^2}"] },
  C: { what: "Linfoot's structural content is the energy of the squared scalar profile relative to the vector one. Below 1 when the scalar profile is flatter (a longer focus has a lower peak at the same energy).",
    eq: ["C = \\frac{\\sum_k a_k^2}{\\sum_k r_k^2}"] },
  Q: { what: "Linfoot's correlation quality is the overlap of the two unit-energy profiles relative to the vector one.",
    eq: ["Q = \\frac{\\sum_k a_k\\, r_k}{\\sum_k r_k^2}", "F = 2Q - C"] },
  lobe: { what: "The distance of the first side lobe from the centre, found by walking down from the centre to the first minimum and then up to the next peak, in units of λ/n (λ = 700 nm).",
    eq: ["d = \\frac{s_\\text{lobe}}{\\lambda / n}"] },
  lobeh: { what: "Height of the first side lobe, relative to the central peak (same lobe as the distance).",
    eq: ["h = \\frac{I(s_\\text{lobe})}{I(0)}"] },
  cmp: { what: "Ratio of two widths (FWHM or DOF), each measured as above on its own profile. The star is the number written in the paper, and the cross the same ratio measured on its printed curves.",
    eq: ["\\rho = \\frac{w_a}{w_b}", "\\text{shorter or narrower } 1 - \\rho, \\quad \\text{longer } \\rho - 1"] },
};

export function renderHow(host: HTMLElement, metric: string, d: HowData) {
  host.replaceChildren();
  host.className = "cell how";
  const T = TEXT[metric] ?? TEXT.width;
  const text = document.createElement("div");
  text.className = "how-text";
  text.innerHTML = `<p class="how-what">${T.what}</p>${T.eq.map(tex).join("")}<p class="how-on">Drawn on ${d.label}</p>`;
  const fig = document.createElement("div");
  fig.className = "how-fig";
  host.append(fig, text);

  const W = 460, H = 250, m = { t: 14, r: 14, b: 34, l: 40 };
  const svg = d3.select(fig).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  const ds = d.s[1] - d.s[0];
  const energy = ["nrmse", "F", "C", "Q"].includes(metric);
  const vec = energy ? unit(d.vec, ds) : d.vec, sca = d.sca ? (energy ? unit(d.sca, ds) : d.sca) : undefined;
  // window: a few widths around the centre (wider for side lobes)
  const hv = half(d.s, d.vec), w = hv ? hv[1] - hv[0] : (d.s[d.s.length - 1] - d.s[0]) / 4;
  const smax = d.s[d.s.length - 1];
  const L0 = lobe(d.s, d.vec.map((v) => v / Math.max(...d.vec)));
  const lim = energy ? smax                                                  // the sums run over the whole window
    : metric.startsWith("lobe") ? Math.min(smax, Math.max(2.6 * w, L0 ? 1.5 * L0.s : 0)) : Math.min(smax, 1.6 * w);
  const keep = d.s.map((v, i) => [v, i] as const).filter(([v]) => Math.abs(v) <= lim).map(([, i]) => i);
  const top = Math.max(...keep.map((i) => vec[i]), ...(sca ? keep.map((i) => sca[i]) : [0])) * 1.08;
  const x = d3.scaleLinear().domain([-lim, lim]).range([m.l, W - m.r]), y = d3.scaleLinear().domain([0, top]).range([H - m.b, m.t]);
  svg.append("g").attr("class", "gx").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5, "~g"));
  svg.append("g").attr("class", "gy").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4, "~g"));
  svg.append("text").attr("class", "lab").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").text(`${d.axis} (µm)`);
  const line = (yy: number[]) => d3.line<number>().x((i) => x(d.s[i])).y((i) => y(yy[i]))(keep);
  if (sca && energy) {                                                       // the difference, shaded
    const area = d3.area<number>().x((i) => x(d.s[i])).y0((i) => y(vec[i])).y1((i) => y(sca[i]));
    svg.append("path").attr("d", area(keep)).attr("class", "how-diff");
  }
  svg.append("path").attr("d", line(vec)).attr("class", "how-v");
  if (sca && (energy || metric === "gap")) svg.append("path").attr("d", line(sca)).attr("class", "how-s");
  const arrow = (x1: number, y1: number, x2: number, y2: number, label: string, below = false) => {
    svg.append("line").attr("class", "how-arrow").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2)
      .attr("marker-start", "url(#how-a)").attr("marker-end", "url(#how-a)");
    svg.append("text").attr("class", "how-l").attr("x", (x1 + x2) / 2 + (x1 === x2 ? 8 : 0)).attr("y", (y1 + y2) / 2 + (below ? 16 : -6))
      .attr("text-anchor", x1 === x2 ? "start" : "middle").text(label);
  };
  svg.append("defs").append("marker").attr("id", "how-a").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5)
    .attr("markerWidth", 7).attr("markerHeight", 7).attr("orient", "auto-start-reverse").append("path").attr("d", "M0,0 L10,5 L0,10 z");
  if (["width", "gap", "cmp"].includes(metric) && hv) {
    const i0 = d.s.reduce((a, v, i) => (Math.abs(v) < Math.abs(d.s[a]) ? i : a), 0), hh = 0.5 * vec[i0];
    svg.append("line").attr("class", "how-ref").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(hh)).attr("y2", y(hh));
    svg.append("text").attr("class", "how-l").attr("x", W - m.r).attr("y", y(hh) - 5).attr("text-anchor", "end").text("½ of the peak");
    arrow(x(hv[0]), y(hh), x(hv[1]), y(hh), metric === "gap" ? "w vector" : d.axis === "x" ? "FWHM" : "DOF", true);
    if (metric === "gap" && sca) { const hs = half(d.s, sca); if (hs) arrow(x(hs[0]), y(hh) - 26, x(hs[1]), y(hh) - 26, "w scalar"); }
  }
  if (metric.startsWith("lobe")) {
    const L = lobe(d.s, vec.map((v) => v / vec[d.s.reduce((a, v2, i) => (Math.abs(v2) < Math.abs(d.s[a]) ? i : a), 0)]));
    if (L && L.s <= lim) {
      svg.append("circle").attr("class", "how-pt").attr("cx", x(L.min)).attr("cy", y(0)).attr("r", 4);
      svg.append("text").attr("class", "how-l").attr("x", x(L.min)).attr("y", y(0) - 8).attr("text-anchor", "middle").text("first minimum");
      svg.append("circle").attr("class", "how-pt lobe").attr("cx", x(L.s)).attr("cy", y(L.h)).attr("r", 5);
      if (metric === "lobe") arrow(x(0), y(L.h) - 14, x(L.s), y(L.h) - 14, "d");
      else arrow(x(L.s) + 14, y(0), x(L.s) + 14, y(L.h), "h");
    } else svg.append("text").attr("class", "how-l").attr("x", W / 2).attr("y", m.t + 20).attr("text-anchor", "middle").text("no side lobe in this profile");
  }
  const leg = svg.append("g").attr("transform", `translate(${m.l + 8},${m.t + 6})`);
  const items: [string, string][] = [["how-v", energy ? "vector, unit energy (r)" : "vector"]];
  if (sca && (energy || metric === "gap")) items.push(["how-s", energy ? "scalar, unit energy (a)" : "scalar"]);
  items.forEach(([c, t], k) => {
    leg.append("line").attr("class", c).attr("x1", 0).attr("x2", 18).attr("y1", k * 16).attr("y2", k * 16);
    leg.append("text").attr("class", "how-l").attr("x", 24).attr("y", k * 16 + 4).text(t);
  });
}
