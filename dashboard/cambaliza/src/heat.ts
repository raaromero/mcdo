// 2D map of a PSF in the x–z plane (x to the right, z downwards, as in the setup diagram), with the two cuts drawn.
// heat map: inferno with a colorbar and the half-maximum contour in white.
// contour:  black contour lines at 1, 10, 20, 40, 60, 80% of the peak, each labelled on the line, as in the contour figures of
//           the two-color scripts (fig_lim2002.py: LEVELS, colors='k', clabel); the 50% contour in orange.
// Both: the cuts as dashed lines (across at z = z₀, along at x = x₀); drag on the map to move them, the button resets them.
import * as d3 from "d3";

export const LEVELS = [1, 10, 20, 40, 60, 80];                            // % of the peak
const HALF = "#ff7f0e";

/** Indices (fractional) where y falls to half of its maximum on both sides of the maximum; null if it never does. */
export function halfPoints(y: ArrayLike<number>): [number, number] | null {
  let c = 0;
  for (let i = 1; i < y.length; i++) if (y[i] > y[c]) c = i;
  const h = 0.5 * y[c];
  let r = c, l = c;
  while (r < y.length - 1 && y[r] >= h) r++;
  while (l > 0 && y[l] >= h) l--;
  if (y[r] >= h || y[l] >= h || y[c] <= 0) return null;
  return [l + (h - y[l]) / (y[l + 1] - y[l]), r - 1 + (y[r - 1] - h) / (y[r - 1] - y[r])];
}

export class Heat {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private cv = document.createElement("canvas");
  private id = `h${Math.random().toString(36).slice(2, 9)}`;
  onCut: ((x: number, z: number) => void) | null = null;
  /** Height over width of the plot area; null: the same µm per pixel along x and z (the default). */
  shape: number | null = null;
  private last: Parameters<Heat["draw"]> | null = null;
  private reset: HTMLButtonElement;

  constructor(host: HTMLElement, public title: string) {
    host.classList.add("heat");
    this.svg = d3.select(host).append("svg");
    let w = "";                                                           // redraw when the panel is stretched (width, or a set height)
    new ResizeObserver(() => { const now = `${host.clientWidth}|${host.style.height}`; if (now !== w && this.last) { w = now; this.draw(...this.last); } w = now; }).observe(host);
    this.reset = document.createElement("button");
    this.reset.type = "button"; this.reset.className = "map-reset"; this.reset.textContent = "Cuts back to the focus"; this.reset.hidden = true;
    this.reset.onclick = () => this.onCut?.(0, 0);
    host.append(this.reset);
    const defs = this.svg.append("defs");
    defs.append("clipPath").attr("id", `${this.id}c`).append("rect");
    const grad = defs.append("linearGradient").attr("id", `${this.id}g`).attr("x1", 0).attr("x2", 0).attr("y1", 1).attr("y2", 0);
    for (let k = 0; k <= 10; k++) grad.append("stop").attr("offset", k / 10).attr("stop-color", d3.interpolateInferno(k / 10));
    for (const [n, c] of [["w", "#fff"], ["o", HALF]]) {
      defs.append("marker").attr("id", `${this.id}${n}`).attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5)
        .attr("markerWidth", 7).attr("markerHeight", 7).attr("orient", "auto-start-reverse")
        .append("path").attr("d", "M0,0 L10,5 L0,10 z").style("fill", c);
    }
  }

  /** v: the map normalized to its own peak. scale: f multiplies v (1, or 1/total energy), vmax is the top of the colorbar. */
  draw(v: ArrayLike<number>, nx: number, nz: number, xr: [number, number], zr: [number, number], style: "heat" | "contour" = "heat",
    cut: { x: number; z: number } = { x: 0, z: 0 }, scale: { f: number; vmax: number; unit: string } = { f: 1, vmax: 1, unit: "of peak" }) {
    const k = scale.f / scale.vmax;                                          // v → fraction of the colorbar
    this.last = [v, nx, nz, xr, zr, style, cut, scale];
    const heat = style === "heat";
    const box = this.svg.node()!.parentElement!;
    const m = { t: 24, r: heat ? 50 : 10, b: 40, l: 46 };
    const st = getComputedStyle(box), fit = box.style.height ? box.clientHeight - parseFloat(st.paddingTop) - parseFloat(st.paddingBottom) : Infinity;              // a stretched panel: the map fits its height
    const aspect = this.shape ?? (zr[1] - zr[0]) / (xr[1] - xr[0]);
    const W = Math.max(200, Math.min(box.clientWidth, (fit - m.t - m.b) / aspect + m.l + m.r));
    const H = (W - m.l - m.r) * aspect + m.t + m.b;                           // same µm per pixel along x and z
    this.svg.node()!.style.width = box.style.height ? `${W}px` : "";
    this.svg.attr("viewBox", `0 0 ${W} ${H}`);
    const x = d3.scaleLinear().domain(xr).range([m.l, W - m.r]);
    const z = d3.scaleLinear().domain(zr).range([m.t, H - m.b]);           // z grows downwards
    const root = this.svg.selectAll<SVGGElement, number>("g.root").data([0]).join("g").attr("class", `root ${style}`);
    const L = root.selectAll<SVGGElement, string>("g.lay").data(["map", "iso", "top"]).join("g").attr("class", "lay");   // fixed drawing order
    const [gm, gi, g] = [0, 1, 2].map((i) => d3.select(L.nodes()[i]));

    // heat map image
    if (heat) {
      this.cv.width = nx; this.cv.height = nz;
      const ctx = this.cv.getContext("2d")!, img = ctx.createImageData(nx, nz);
      for (let i = 0; i < nx * nz; i++) {
        const c = d3.rgb(d3.interpolateInferno(Math.min(1, Math.max(0, k * v[i]))));
        img.data[4 * i] = c.r; img.data[4 * i + 1] = c.g; img.data[4 * i + 2] = c.b; img.data[4 * i + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
    }
    gm.selectAll("image").data(heat ? [0] : []).join("image").attr("preserveAspectRatio", "none")
      .attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b).attr("href", () => this.cv.toDataURL());
    gm.selectAll("rect.frame").data(heat ? [] : [0]).join("rect").attr("class", "frame")
      .attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b);

    // contours: a ring of zeros closes them just outside the window and the clip hides it, so cut contours end at the frame;
    // grid point (i, j) of the padded grid sits at (i + 0.5, j + 0.5) in d3.contours coordinates
    // levels in % of the colorbar top; the half-maximum contour is at half of this map's own peak (k·50)
    const halfLv = 100 * k * 0.5, lv = heat ? [halfLv] : [...LEVELS, halfLv].sort((a, b) => a - b);
    const Pd = new Float64Array((nx + 2) * (nz + 2));
    for (let i = 0; i < nz; i++) for (let j = 0; j < nx; j++) Pd[(i + 1) * (nx + 2) + j + 1] = 100 * k * v[i * nx + j];
    const cs = d3.contours().size([nx + 2, nz + 2]).thresholds(lv)(Array.from(Pd));
    const isHalf = (c: { value: number }) => Math.abs(c.value - halfLv) < 1e-9;
    const fmtLv = (c: { value: number }) => (isHalf(c) ? "½ peak" : scale.f === 1 && scale.vmax === 1 ? String(c.value) : d3.format(".2~g")((c.value / 100) * scale.vmax));
    const gx = (c: number) => x(xr[0] + ((c - 1.5) * (xr[1] - xr[0])) / (nx - 1)), gz = (c: number) => z(zr[0] + ((c - 1.5) * (zr[1] - zr[0])) / (nz - 1));
    this.svg.select(`#${this.id}c rect`).attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b);
    gi.attr("clip-path", `url(#${this.id}c)`);
    const path = d3.geoPath(d3.geoTransform({ point(px, py) { this.stream.point(gx(px), gz(py)); } }));
    gi.selectAll<SVGPathElement, d3.ContourMultiPolygon>("path.iso").data(cs).join("path")
      .attr("class", (c) => `iso${isHalf(c) ? " half" : ""}`).attr("d", (c) => path(c));

    // labels on the contour lines (contour view): one per ring big enough, at its upper-right point, inside the frame
    const labs: { v: number; t: string; half: boolean; p: [number, number] }[] = [];
    if (!heat) for (const c of cs) for (const poly of c.coordinates) {
      const ring = poly[0].map(([a, b]) => [gx(a), gz(b)] as [number, number])
        .filter(([a, b]) => a > m.l + 10 && a < W - m.r - 10 && b > m.t + 8 && b < H - m.b - 8);
      if (ring.length < 8) continue;
      const ex = d3.extent(ring, (p) => p[0]) as [number, number], ez = d3.extent(ring, (p) => p[1]) as [number, number];
      if (ex[1] - ex[0] < 22 && ez[1] - ez[0] < 22) continue;
      const q = ring.reduce((a, b) => (b[0] - b[1] > a[0] - a[1] ? b : a));
      if (labs.every((l) => Math.hypot(l.p[0] - q[0], l.p[1] - q[1]) > 18)) labs.push({ v: c.value, t: fmtLv(c), half: isHalf(c), p: q });   // no overlapping labels
    }
    gi.selectAll<SVGTextElement, (typeof labs)[number]>("text.clab").data(labs).join("text")
      .attr("class", (d) => `clab${d.half ? " half" : ""}`).attr("x", (d) => d.p[0]).attr("y", (d) => d.p[1] + 3.5)
      .attr("text-anchor", "middle").text((d) => d.t);

    // the cuts, at the grid row and column nearest to (x₀, z₀), and the FWHM on each
    const dx = (xr[1] - xr[0]) / (nx - 1), dz = (zr[1] - zr[0]) / (nz - 1);
    const jc = Math.max(0, Math.min(nx - 1, Math.round((cut.x - xr[0]) / dx))), kc = Math.max(0, Math.min(nz - 1, Math.round((cut.z - zr[0]) / dz)));
    const z0 = z(zr[0] + kc * dz), x0 = x(xr[0] + jc * dx);
    g.selectAll("line.cut-x").data([0]).join("line").attr("class", "cut cut-x").attr("x1", m.l).attr("x2", W - m.r).attr("y1", z0).attr("y2", z0);
    g.selectAll("line.cut-z").data([0]).join("line").attr("class", "cut cut-z").attr("x1", x0).attr("x2", x0).attr("y1", m.t).attr("y2", H - m.b);
    g.selectAll("line.fw").remove();
    // back to the focus, on the map itself, once the cuts have moved
    this.reset.hidden = !cut.x && !cut.z;

    // colorbar (heat map)
    const cb = g.selectAll<SVGGElement, number>("g.cbar").data(heat ? [0] : []).join("g").attr("class", "cbar")
      .attr("transform", `translate(${W - m.r + 10},0)`);
    cb.selectAll("rect").data([0]).join("rect").attr("x", 0).attr("y", m.t).attr("width", 10).attr("height", H - m.t - m.b)
      .style("fill", `url(#${this.id}g)`);
    cb.selectAll<SVGGElement, number>("g.cax").data([0]).join("g").attr("class", "cax gy").attr("transform", "translate(10,0)")
      .call(d3.axisRight(d3.scaleLinear().domain([0, scale.vmax]).range([H - m.b, m.t])).tickValues([0, scale.vmax / 2, scale.vmax]).tickFormat(d3.format(".2~g")).tickSize(3));
    cb.selectAll("text.cl").data([scale.unit]).join("text").attr("class", "lab cl").attr("x", -2).attr("y", m.t - 6).text((d) => d);

    // axes and labels
    g.selectAll<SVGGElement, number>("g.ax").data([0]).join("g").attr("class", "ax gx").attr("transform", `translate(0,${H - m.b})`)
      .call(d3.axisBottom(x).ticks(5, "~g"));
    g.selectAll<SVGGElement, number>("g.az").data([0]).join("g").attr("class", "az gy").attr("transform", `translate(${m.l},0)`)
      .call(d3.axisLeft(z).ticks(6, "~g"));
    g.selectAll("text.t").data([this.title]).join("text").attr("class", "t").attr("x", m.l).attr("y", 16).text((d) => d);
    g.selectAll("text.lx").data(["x (µm)"]).join("text").attr("class", "lab lx").attr("x", W - m.r).attr("y", H - 6).attr("text-anchor", "end").text((d) => d);
    g.selectAll("text.lz").data(["z (µm)"]).join("text").attr("class", "lab lz").attr("x", 4).attr("y", H - 6).text((d) => d);

    // drag (or click) on the map to move the cuts
    const zone = g.selectAll<SVGRectElement, number>("rect.drag").data([0]).join("rect").attr("class", "drag")
      .attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b);
    const at = (e: PointerEvent) => { const [px, py] = d3.pointer(e, this.svg.node()); return [x.invert(px), z.invert(py)]; };   // viewBox units
    zone.on("pointerdown", (e: PointerEvent) => { (e.target as Element).setPointerCapture(e.pointerId); const [a, b] = at(e); this.onCut?.(a, b); })
      .on("pointermove", (e: PointerEvent) => { if (e.buttons) { const [a, b] = at(e); this.onCut?.(a, b); } });
  }
}
