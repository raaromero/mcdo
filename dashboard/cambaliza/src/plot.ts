// One animated line chart: series are keyed, so a change of parameters morphs the curves instead of redrawing them.
// Hover shows the values at the nearest x; a click on a pickable chart reports that x (e.g. the NA to show the PSF at).
import * as d3 from "d3";

export type Series = {
  id: string; label: string; color: string; pts: [number, number][];
  dash?: boolean; dots?: boolean; faint?: boolean; width?: number; dotted?: boolean;   // dotted: a reference curve
};
export type Opts = {
  xlabel: string; ylabel: string; xlog?: boolean; ylog?: boolean;
  xdomain?: [number, number]; ydomain?: [number, number];
  marker?: number | null;            // x of the selected point (vertical rule)
  pickable?: boolean;                // click reports the nearest x
  ref?: number;                      // horizontal reference line
  band?: [number, number];           // shaded y band
  fmt?: (v: number) => string;
  marks?: { x: number; y: number; label: string; shape: "star" | "cross" }[];   // single published values (legend entries too)
};

const T = 450;
type Dot = { id: string; s: Series; p: [number, number] };

export class LineChart {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private g: d3.Selection<SVGGElement, unknown, null, undefined>;
  private legend: HTMLUListElement;
  private tip: HTMLDivElement;
  private last: [Series[], Opts] | null = null;
  onPick: ((x: number) => void) | null = null;
  private hidden = new Set<string>();                            // legend entries switched off (by label, without the value in parentheses)

  constructor(host: HTMLElement) {
    host.classList.add("lc");
    const box = document.createElement("div");
    box.className = "lc-box";
    host.append(box);
    this.svg = d3.select(box).append("svg");
    this.g = this.svg.append("g");
    for (const c of ["band", "gx", "gy", "ref", "lines", "dots", "marks", "marker", "hover"]) this.g.append("g").attr("class", c);
    this.tip = document.createElement("div");
    this.tip.className = "tip";
    this.tip.hidden = true;
    box.append(this.tip);
    this.legend = document.createElement("ul");
    this.legend.className = "legend";
    host.append(this.legend);
    let size = "";
    new ResizeObserver(() => {                                     // redraw only when the box really changes size
      const now = `${box.clientWidth}x${box.clientHeight}`;
      if (now !== size && this.last) { size = now; this.update(this.last[0], this.last[1], false); }
      size = now;
    }).observe(box);
  }

  update(all: Series[], o: Opts, animate = true) {
    this.last = [all, o];
    const key = (lab: string) => lab.replace(/ \([^()]*(µm|–)\)$/, "");      // a legend entry without its value
    const series = all.filter((s) => !this.hidden.has(key(s.label)));
    const allMarks = o.marks;
    o = { ...o, marks: allMarks?.filter((k) => !this.hidden.has(key(k.label))) };
    const box = this.svg.node()!.parentElement!;
    const W = Math.max(280, box.clientWidth), H = Math.max(220, box.clientHeight);
    const m = { t: 22, r: 18, b: 46, l: 60 };
    this.svg.attr("viewBox", `0 0 ${W} ${H}`);
    const ok = (p: [number, number]) => Number.isFinite(p[0]) && Number.isFinite(p[1]) && (!o.ylog || p[1] > 0);
    const pool = [...series.flatMap((s) => s.pts), ...(o.marks ?? []).map((k): [number, number] => [k.x, k.y])].filter(ok);
    const xd = o.xdomain ?? ((pool.length ? d3.extent(pool, (p) => p[0]) : [0, 1]) as [number, number]);
    let yd = o.ydomain;
    if (!yd) {
      let [lo, hi] = (pool.length ? d3.extent(pool, (p) => p[1]) : [0, 1]) as [number, number];
      if (o.ref !== undefined) { lo = Math.min(lo, o.ref); hi = Math.max(hi, o.ref); }
      if (!o.ylog && hi > 0 && (hi - lo) / hi < 0.02) { const mid = (hi + lo) / 2; lo = Math.min(lo, mid * 0.97); hi = Math.max(hi, mid * 1.03); }   // < 2% change: keep a ±3% window
      const pad = (hi - lo) * 0.06 || 0.1;
      yd = o.ylog ? [lo / 1.15, hi * 1.15] : [lo - pad, hi + pad];
    }
    const x = (o.xlog ? d3.scaleLog() : d3.scaleLinear()).domain(xd).range([m.l, W - m.r]);
    const y = (o.ylog ? d3.scaleLog() : d3.scaleLinear()).domain(yd).range([H - m.b, m.t]);
    const tr = (sel: any) => (animate ? sel.transition().duration(T) : sel);

    const ax = d3.axisBottom(x).ticks(Math.max(3, Math.floor(W / 90)), o.xlog ? "~g" : undefined).tickSizeOuter(0);
    const ay = d3.axisLeft(y).ticks(Math.max(3, Math.floor(H / 60)), o.ylog ? "~g" : undefined).tickSize(-(W - m.l - m.r)).tickSizeOuter(0);
    tr(this.g.select<SVGGElement>(".gx").attr("transform", `translate(0,${H - m.b})`)).call(ax);
    tr(this.g.select<SVGGElement>(".gy").attr("transform", `translate(${m.l},0)`)).call(ay);
    this.g.select(".gx").selectAll(".title").data([o.xlabel]).join("text").attr("class", "title")
      .attr("x", W - m.r).attr("y", 38).attr("text-anchor", "end").text((d) => d);
    this.g.select(".gy").selectAll(".title").data([o.ylabel]).join("text").attr("class", "title")
      .attr("x", -m.l + 4).attr("y", m.t - 8).attr("text-anchor", "start").text((d) => d);

    const yc = (v: number) => y(Math.max(yd![0], Math.min(yd![1], v)));
    this.g.select(".band").selectAll("rect").data(o.band ? [o.band] : []).join("rect")
      .attr("x", m.l).attr("width", W - m.l - m.r).attr("y", (b) => yc(b[1])).attr("height", (b) => Math.abs(yc(b[0]) - yc(b[1])));
    this.g.select(".ref").selectAll("line").data(o.ref !== undefined ? [o.ref] : []).join("line")
      .attr("x1", m.l).attr("x2", W - m.r).attr("y1", (v) => y(v)).attr("y2", (v) => y(v));

    const line = d3.line<[number, number]>().defined(ok).x((p) => x(p[0])).y((p) => y(p[1]));
    const paths = this.g.select(".lines").selectAll<SVGPathElement, Series>("path").data(series, (d) => d.id)
      .join((e) => e.append("path").attr("d", (d) => line(d.pts)).attr("opacity", 0), (u) => u,
        (q) => q.transition().duration(200).attr("opacity", 0).remove());
    paths.style("stroke", (d) => d.color).attr("stroke-width", (d) => d.width ?? (d.dash ? 2.2 : 2.6))
      .attr("stroke-dasharray", (d) => (d.dotted ? "2 4" : d.dash ? "7 5" : null));
    tr(paths).attr("d", (d: Series) => line(d.pts)).attr("opacity", (d: Series) => (d.faint ? 0.35 : 1));

    const sel = o.marker ?? null;
    const dots: Dot[] = series.filter((s) => s.dots).flatMap((s) => s.pts.filter(ok).map((p) => ({ id: `${s.id}@${p[0]}`, s, p })));
    const circles = this.g.select(".dots").selectAll<SVGCircleElement, Dot>("circle").data(dots, (d) => d.id)
      .join((e) => e.append("circle").attr("r", 0).attr("cx", (d) => x(d.p[0])).attr("cy", (d) => y(d.p[1])), (u) => u, (q) => q.remove());
    circles.style("fill", (d) => (d.s.dash ? "var(--bg)" : d.s.color)).style("stroke", (d) => d.s.color);
    tr(circles).attr("r", (d: Dot) => (sel !== null && Math.abs(d.p[0] - sel) < 1e-9 ? 6.5 : 3.4))
      .attr("cx", (d: Dot) => x(d.p[0])).attr("cy", (d: Dot) => y(d.p[1]));

    const sym = (k: { shape: string }) => d3.symbol(k.shape === "star" ? d3.symbolStar : d3.symbolTimes, k.shape === "star" ? 260 : 170)()!;
    const mks = this.g.select(".marks").selectAll<SVGPathElement, NonNullable<Opts["marks"]>[number]>("path").data(o.marks ?? [], (k) => k.label)
      .join("path").attr("class", (k) => k.shape).attr("d", sym);
    tr(mks).attr("transform", (k: { x: number; y: number }) => `translate(${x(k.x)},${y(k.y)})`);

    const mk = this.g.select(".marker").selectAll<SVGLineElement, number>("line").data(sel !== null ? [sel] : [])
      .join((e) => e.append("line").attr("x1", (v) => x(v)).attr("x2", (v) => x(v)));
    tr(mk.attr("y1", m.t).attr("y2", H - m.b)).attr("x1", (v: number) => x(v)).attr("x2", (v: number) => x(v));

    // hover and pick
    const xs = [...new Set(series.filter((s) => !s.faint).flatMap((s) => s.pts.filter(ok).map((p) => p[0])))].sort((a, b) => a - b);
    const hv = this.g.select(".hover");
    const rule = hv.selectAll<SVGLineElement, number>("line").data([0]).join("line").attr("y1", m.t).attr("y2", H - m.b).style("display", "none");
    const zone = hv.selectAll<SVGRectElement, number>("rect").data([0]).join("rect").attr("x", m.l).attr("y", m.t)
      .attr("width", W - m.l - m.r).attr("height", H - m.t - m.b).classed("pick", !!o.pickable);
    const fmt = o.fmt ?? ((v: number) => (Math.abs(v) >= 100 ? v.toFixed(0) : v.toPrecision(3)));
    const nearest = (px: number) => xs.reduce((a, b) => (Math.abs(x(b) - px) < Math.abs(x(a) - px) ? b : a), xs[0]);
    const toPx = (e: PointerEvent) => d3.pointer(e, this.svg.node())[0] * (W / box.clientWidth);
    zone.on("pointermove", (e: PointerEvent) => {
      if (!xs.length) return;
      const xv = nearest(toPx(e));
      rule.style("display", null).attr("x1", x(xv)).attr("x2", x(xv));
      const rows = series.filter((s) => !s.faint && s.pts.length).map((s) => {
        const p = s.pts.reduce((a, b) => (Math.abs(b[0] - xv) < Math.abs(a[0] - xv) ? b : a), s.pts[0]);
        return Number.isFinite(p[1]) ? `<div class="tip-row"><i style="background:${s.color}"></i><span>${s.label}</span><b>${fmt(p[1])}</b></div>` : "";
      }).join("");
      this.tip.innerHTML = `<div class="tip-title">${o.xlabel.split(" (")[0]} ${d3.format("~g")(+xv.toPrecision(4))}${o.pickable ? " · click" : ""}</div>${rows}`;
      this.tip.hidden = false;
      const left = (x(xv) / W) * box.clientWidth;
      this.tip.style.left = `${left > box.clientWidth * 0.6 ? left - this.tip.offsetWidth - 12 : left + 12}px`;
      this.tip.style.top = "8px";
    }).on("pointerleave", () => { rule.style("display", "none"); this.tip.hidden = true; })
      .on("click", (e: PointerEvent) => { if (o.pickable && this.onPick && xs.length) this.onPick(nearest(toPx(e))); });

    // legend: click an entry to hide or show its line
    const seen = new Set<string>();
    const toggle = (lab: string) => { const k = key(lab); this.hidden.has(k) ? this.hidden.delete(k) : this.hidden.add(k); this.update(all, { ...o, marks: allMarks }); };
    const item = (lab: string, swatch: string) => {
      const li = document.createElement("li");
      li.innerHTML = swatch;
      li.append(lab);
      li.tabIndex = 0;
      li.setAttribute("role", "button");
      li.setAttribute("aria-pressed", String(!this.hidden.has(key(lab))));
      li.title = "Click to hide or show";
      li.onclick = () => toggle(lab);
      li.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(lab); } };
      return li;
    };
    this.legend.replaceChildren(...all.filter((s) => !s.faint && !seen.has(s.label) && !!seen.add(s.label)).map((s) =>
      item(s.label, `<svg width="24" height="10" aria-hidden="true"><line x1="1" x2="23" y1="5" y2="5" style="stroke:${s.color}" stroke-width="2.6"${s.dotted ? ' stroke-dasharray="2 3"' : s.dash ? ' stroke-dasharray="6 4"' : ""}/></svg>`)),
    ...(allMarks ?? []).map((k) => item(k.label, `<svg width="24" height="16" viewBox="-12 -8 24 16" aria-hidden="true"><path class="${k.shape}" d="${sym(k)}" transform="scale(0.7)"/></svg>`)));
  }
}
