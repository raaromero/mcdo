// Setup drawing that follows the controls: lens L1 on the z axis, lens L2 turned by θ about the focus O,
// x to the right and z downwards (as the maps). Biconvex lenses; the collimated beams meet the lens rims; arrows on every beam.
import * as d3 from "d3";

const F = 3, IN = 1.6;                  // lens distance, length of the collimated part (drawing units)

export class Setup {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  constructor(host: HTMLElement) {
    host.classList.add("setup");
    this.svg = d3.select(host).append("svg").attr("viewBox", "-6.4 -5.6 12.8 11.2");
    const defs = this.svg.append("defs");
    for (const [id, c] of [["a1", "var(--b1)"], ["a2", "var(--b2)"]]) {
      defs.append("marker").attr("id", id).attr("viewBox", "0 0 10 10").attr("refX", 5).attr("refY", 5)
        .attr("markerWidth", 5).attr("markerHeight", 5).attr("orient", "auto-start-reverse")
        .append("path").attr("d", "M0,0 L10,5 L0,10 z").style("fill", c);
    }
    defs.append("marker").attr("id", "ax").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5)
      .attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto")
      .append("path").attr("d", "M0,1 L10,5 L0,9").style("fill", "none").style("stroke", "var(--muted)").attr("stroke-width", 1.4);
    const g = this.svg.append("g").attr("class", "axes");
    g.append("line").attr("x1", -5).attr("x2", 5).attr("y1", 0).attr("y2", 0).attr("marker-end", "url(#ax)");
    g.append("line").attr("x1", 0).attr("x2", 0).attr("y1", -5).attr("y2", 5).attr("marker-end", "url(#ax)");
    g.append("text").attr("x", 5).attr("y", -0.3).attr("text-anchor", "end").text("x");
    g.append("text").attr("x", 0.3).attr("y", 5).text("z");
    this.svg.append("g").attr("class", "b2");
    this.svg.append("g").attr("class", "b1");
    this.svg.append("path").attr("class", "arc");
    this.svg.append("text").attr("class", "thl");
    this.svg.append("circle").attr("r", 0.14).attr("class", "o");
    this.svg.append("text").attr("x", -0.25).attr("y", -0.25).attr("text-anchor", "end").attr("class", "lab").text("O");
  }

  /** theta in rad, measured from +z towards +x; beam 2 arrives along (sinθ, cosθ)·(−1) from its lens. */
  draw(theta: number, na: number, eps: number, l1: number, l2: number) {
    const half = Math.asin(Math.min(0.999, na));       // true cone angle: a wider cone brings the lens closer to O
    const a = Math.min(2.2, F * Math.tan(half)), f = a / Math.tan(half);
    this.beam(this.svg.select("g.b1"), 0, a, eps, "L1", `λ₁ ${Math.round(l1 * 1000)} nm`, 1, f);
    this.beam(this.svg.select("g.b2"), theta, a, eps, "L2", `λ₂ ${Math.round(l2 * 1000)} nm`, 2, f);
    const r = 1.1, n = 40, pts = d3.range(n + 1).map((i) => { const t = (theta * i) / n; return [-r * Math.sin(t), -r * Math.cos(t)]; });
    this.svg.select("path.arc").attr("d", d3.line()(pts as [number, number][]));
    const m = theta / 2;
    this.svg.select("text.thl").attr("x", -1.55 * Math.sin(m)).attr("y", -1.55 * Math.cos(m) + 0.15).attr("text-anchor", "middle")
      .text(theta > 0.05 ? "θ" : "");
  }

  private beam(g: d3.Selection<any, unknown, null, undefined>, th: number, a: number, eps: number, lens: string, lab: string, k: 1 | 2, f = F) {
    const d: [number, number] = [Math.sin(th), Math.cos(th)];            // propagation in (x, z)
    const p: [number, number] = [d[1], -d[0]];                           // across the beam
    const c: [number, number] = [-f * d[0], -f * d[1]];                  // lens centre (focus at O)
    const at = (s: number, t: number): [number, number] => [c[0] + s * a * p[0] + t * d[0], c[1] + s * a * p[1] + t * d[1]];
    const col = `var(--b${k})`;
    const cone: [number, number][][] = eps > 0
      ? [[at(1, 0), [0, 0], at(eps, 0)], [at(-1, 0), [0, 0], at(-eps, 0)]]
      : [[at(1, 0), [0, 0], at(-1, 0)]];
    g.selectAll("path.cone").data(cone).join("path").attr("class", "cone").attr("d", (q) => d3.line()(q) + "Z").style("fill", col);
    const rays: [[number, number], [number, number]][] = [];
    for (const s of eps > 0 ? [1, -1, eps, -eps] : [1, -1]) {
      rays.push([at(s, -IN), at(s, 0)]);                                  // collimated, ends at the lens rim
      rays.push([at(s, 0), [0, 0]]);                                      // converging to O
    }
    g.selectAll("line.ray").data(rays).join("line").attr("class", "ray").style("stroke", col)
      .attr("x1", (r) => r[0][0]).attr("y1", (r) => r[0][1]).attr("x2", (r) => r[1][0]).attr("y2", (r) => r[1][1]);
    const mids = rays.map((r): [[number, number], [number, number]] => {
      const f = (t: number): [number, number] => [r[0][0] + t * (r[1][0] - r[0][0]), r[0][1] + t * (r[1][1] - r[0][1])];
      return [f(0.42), f(0.5)];
    });
    g.selectAll("line.arw").data(mids).join("line").attr("class", "arw").style("stroke", "none").attr("marker-end", `url(#a${k})`)
      .attr("x1", (r) => r[0][0]).attr("y1", (r) => r[0][1]).attr("x2", (r) => r[1][0]).attr("y2", (r) => r[1][1]);
    const ts = d3.range(-1, 1.0001, 0.05);
    const face = (sgn: number) => ts.map((t) => at(t, sgn * 0.22 * (1 - t * t)));
    const shape = [...face(1), ...face(-1).reverse()];
    g.selectAll("path.lens").data([shape]).join("path").attr("class", "lens").attr("d", (q) => d3.line()(q) + "Z");
    const lp = at(-1.45, 0), bp = at(1.35, -IN * 0.7);
    g.selectAll("text.lens-l").data([lens]).join("text").attr("class", "lens-l lab").attr("x", lp[0]).attr("y", lp[1] + 0.15)
      .attr("text-anchor", "middle").text((t) => t);
    g.selectAll("text.beam-l").data([lab]).join("text").attr("class", "beam-l").style("fill", col).attr("x", bp[0]).attr("y", bp[1] + 0.15)
      .attr("text-anchor", p[0] * 1.35 >= 0 ? "start" : "end").text((t) => t);
  }
}
