// The two dashboards: profiles at one NA, and widths against NA. SVG, themed by CSS classes.
import * as d3 from "d3";
import {
  THETAS, THETA_LABEL, fits, fmtUm, loadProfiles, widthAt, wkey,
  type Axis, type Data, type Input, type Medium, type Model, type Pupil, type Signal, type Theta,
} from "./data";
import { download, svgImage } from "./export";

export type View = "home" | "insights" | "profiles" | "widths";
export type State = {
  view: View;
  medium: Medium;
  na: number;
  signal: Signal;
  axis: Axis;
  model: "both" | Model;
  pupil: Pupil;
  input: Input;
  th: Record<Theta, boolean>;
};

const TCLS: Record<Theta, string> = { "0": "t0", pi2: "t1", pi: "t2" };
const MODELS = (s: State): Model[] => (s.model === "both" ? ["vector", "scalar"] : [s.model]);
const dirWord = (a: Axis) => (a === "x" ? "across the axis" : "along the axis");
const pupilWord = (s: State) => `${s.pupil === "ann" ? "Annular" : "Circular"} pupils, ${s.input === "gau" ? "Gaussian" : "uniform"} input`;

type Curve = { th: Theta; model: Model; xs: number[]; ys: number[]; fwhm?: number };

export class Chart {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private tip: HTMLDivElement;
  private seq = 0;

  constructor(private host: HTMLElement, private data: Data, private legend: HTMLElement, private status: HTMLElement,
    private title: HTMLElement) {
    this.svg = d3.select(host).append("svg").attr("class", "interactive").attr("role", "img");
    this.tip = document.createElement("div");
    this.tip.className = "tip";
    this.tip.hidden = true;
    host.append(this.tip);
  }

  async render(s: State) {
    const id = ++this.seq;
    if (s.view === "profiles") {
      const prof = await loadProfiles(s.medium, s.na);
      if (id !== this.seq) return; // a newer render started while this one loaded
      this.profiles(s, prof);
    } else this.widths(s);
  }

  // ---------------- profiles at one NA ----------------
  private profiles(s: State, prof: Record<string, number[]>) {
    const n = this.data.meta.n[s.medium];
    const [half, npt] = prof[`grid|${s.axis}`];
    const xs = d3.range(npt).map((i) => -half + (2 * half * i) / (npt - 1));
    const curves: Curve[] = [];
    for (const th of THETAS) {
      if (!s.th[th] || !fits(th, s.na, n)) continue;
      for (const model of MODELS(s)) {
        const ys = prof[`${s.signal}|${s.axis}|${th}|${model}|${s.pupil}|${s.input}`];
        if (ys) curves.push({ th, model, xs, ys,
          fwhm: widthAt(this.data.widths, wkey(s.signal, s.axis, th, model, s.pupil, s.input, s.medium), s.na) });
      }
    }
    this.title.textContent = `${s.signal} ${dirWord(s.axis)}, NA ${s.na} in ${s.medium}`;
    this.status.textContent = `${pupilWord(s)}. Each curve is scaled to its own peak.` +
      (s.th.pi2 && !fits("pi2", s.na, n) ? ` Crossed lenses do not fit above NA ${(n * Math.SQRT1_2).toFixed(2)}.` : "");
    const { W, H, m, g } = this.frame();
    const x = d3.scaleLinear().domain([-half, half]).range([m.l, W - m.r]);
    const y = d3.scaleLinear().domain([0, 1.02]).range([H - m.b, m.t]);
    this.gridY(g, y, W, m, [0, 0.25, 0.5, 0.75, 1], d3.format(".2f"));
    this.axisX(g, x, H, m, x.ticks(8), (v) => d3.format("~g")(v));
    this.titles(g, W, H, m, "Intensity (each curve scaled to its peak)", `${s.axis} (µm)`);
    g.append("line").attr("class", "half-rule").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(0.5)).attr("y2", y(0.5));
    const line = d3.line<number>().x((_, i) => x(xs[i])).y((v) => y(v));
    for (const c of curves)
      g.append("path").attr("class", `pline ${TCLS[c.th]} ${c.model}`).attr("d", line(c.ys));
    this.legendItems(curves.map((c) => ({ cls: `${TCLS[c.th]} ${c.model}`,
      text: `${THETA_LABEL[c.th]}, ${c.model}${c.fwhm ? ` · ${s.axis === "z" ? "DOF" : "FWHM"} ${fmtUm(c.fwhm)} µm` : ""}` })));
    this.hover(g, W, H, m, (px) => {
      const xv = x.invert(px);
      const i = Math.max(0, Math.min(npt - 1, Math.round(((xv + half) / (2 * half)) * (npt - 1))));
      return { at: x(xs[i]), head: `${s.axis} = ${xs[i].toFixed(3)} µm`,
        rows: curves.map((c) => ({ cls: `${TCLS[c.th]} ${c.model}`, label: `${THETA_LABEL[c.th]}, ${c.model}`, value: c.ys[i].toFixed(3) })) };
    });
  }

  // ---------------- widths against NA ----------------
  private widths(s: State) {
    const series: { th: Theta; model: Model; pts: [number, number][] }[] = [];
    for (const th of THETAS) {
      if (!s.th[th]) continue;
      for (const model of MODELS(s)) {
        const pts = this.data.widths[wkey(s.signal, s.axis, th, model, s.pupil, s.input, s.medium)];
        if (pts?.length) series.push({ th, model, pts });
      }
    }
    this.title.textContent = `${s.signal} ${s.axis === "z" ? "depth of focus" : "width across the axis"} against NA, ${s.medium}`;
    this.status.textContent = `${pupilWord(s)}. The rule marks NA ${s.na}; drag the NA slider or click the chart to move it.`;
    const { W, H, m, g } = this.frame();
    const all = series.flatMap((d) => d.pts);
    if (!all.length) { this.legendItems([]); return; }
    const nas = this.data.meta.na[s.medium];
    const x = d3.scaleLog().domain([nas[0], nas[nas.length - 1]]).range([m.l, W - m.r]);
    const [lo, hi] = d3.extent(all, (p) => p[1]) as [number, number];
    const y = d3.scaleLog().domain([lo / 1.15, hi * 1.15]).range([H - m.b, m.t]);
    const yt = [0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 500, 1000].filter((v) => v >= y.domain()[0] && v <= y.domain()[1]);
    this.gridY(g, y, W, m, yt, (v) => d3.format("~g")(v));
    this.axisX(g, x, H, m, [0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 1.2].filter((v) => v <= nas[nas.length - 1] + 1e-9), (v) => d3.format("~g")(v));
    this.titles(g, W, H, m, s.axis === "z" ? "Depth of focus (µm)" : "Width across the axis (µm)", "NA");
    g.append("line").attr("class", "na-rule").attr("x1", x(s.na)).attr("x2", x(s.na)).attr("y1", m.t).attr("y2", H - m.b);
    const line = d3.line<[number, number]>().x((p) => x(p[0])).y((p) => y(p[1]));
    for (const d of series) {
      g.append("path").attr("class", `pline ${TCLS[d.th]} ${d.model}`).attr("d", line(d.pts));
      if (d.model === "vector")
        g.selectAll(null).data(d.pts).join("circle").attr("class", `pdot ${TCLS[d.th]}`).attr("r", 2.6)
          .attr("cx", (p) => x(p[0])).attr("cy", (p) => y(p[1]));
    }
    this.legendItems(series.map((d) => {
      const v = d.pts.find((p) => Math.abs(p[0] - s.na) < 1e-6)?.[1];
      return { cls: `${TCLS[d.th]} ${d.model}`, text: `${THETA_LABEL[d.th]}, ${d.model}${v ? ` · ${fmtUm(v)} µm at NA ${s.na}` : ""}` };
    }));
    this.hover(g, W, H, m, (px) => {
      const na = nas.reduce((a, b) => (Math.abs(x(b) - px) < Math.abs(x(a) - px) ? b : a));
      return { at: x(na), head: `NA ${na}`, rows: series.map((d) => {
        const v = d.pts.find((p) => Math.abs(p[0] - na) < 1e-6)?.[1];
        return { cls: `${TCLS[d.th]} ${d.model}`, label: `${THETA_LABEL[d.th]}, ${d.model}`, value: v ? `${fmtUm(v)} µm` : "–" };
      }) };
    }, (px) => {
      const na = nas.reduce((a, b) => (Math.abs(x(b) - px) < Math.abs(x(a) - px) ? b : a));
      this.host.dispatchEvent(new CustomEvent("pickna", { detail: na }));
    });
  }

  // ---------------- shared pieces ----------------
  private frame() {
    const W = Math.max(560, this.host.clientWidth);
    const H = Math.max(320, this.host.clientHeight);
    const m = { t: 30, r: 24, b: 44, l: 56 };
    this.svg.attr("viewBox", `0 0 ${W} ${H}`).selectAll("*").remove();
    this.svg.attr("aria-label", this.title.textContent ?? "");
    return { W, H, m, g: this.svg.append("g") };
  }

  private gridY(g: d3.Selection<SVGGElement, unknown, null, undefined>, y: (v: number) => number, W: number,
    m: { l: number; r: number }, ticks: number[], fmt: (v: number) => string) {
    for (const t of ticks) {
      g.append("line").attr("class", "gridline").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(t)).attr("y2", y(t));
      g.append("text").attr("class", "axis-label").attr("x", m.l - 8).attr("y", y(t)).attr("dy", "0.35em")
        .attr("text-anchor", "end").text(fmt(t));
    }
  }

  private axisX(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: (v: number) => number, H: number,
    m: { b: number }, ticks: number[], fmt: (v: number) => string) {
    for (const t of ticks)
      g.append("text").attr("class", "axis-label").attr("x", x(t)).attr("y", H - m.b + 18).attr("text-anchor", "middle").text(fmt(t));
  }

  private titles(g: d3.Selection<SVGGElement, unknown, null, undefined>, W: number, H: number,
    m: { l: number; r: number; t: number }, yt: string, xt: string) {
    g.append("text").attr("class", "axis-title").attr("x", m.l).attr("y", m.t - 12).text(yt);
    g.append("text").attr("class", "axis-title").attr("x", W - m.r).attr("y", H - 6).attr("text-anchor", "end").text(xt);
  }

  private legendItems(items: { cls: string; text: string }[]) {
    this.legend.replaceChildren(...items.map((it) => {
      const li = document.createElement("li");
      li.innerHTML = `<svg class="key-line" width="26" height="10" aria-hidden="true"><line class="pline ${it.cls}" x1="1" x2="25" y1="5" y2="5"/></svg>`;
      li.append(it.text);
      return li;
    }));
  }

  private hover(g: d3.Selection<SVGGElement, unknown, null, undefined>, W: number, H: number,
    m: { l: number; r: number; t: number; b: number },
    at: (px: number) => { at: number; head: string; rows: { cls: string; label: string; value: string }[] },
    click?: (px: number) => void) {
    const rule = g.append("line").attr("class", "hover-rule").attr("y1", m.t).attr("y2", H - m.b).style("display", "none");
    const zone = g.append("rect").attr("class", "hover-zone").attr("x", m.l).attr("y", m.t)
      .attr("width", W - m.l - m.r).attr("height", H - m.t - m.b);
    const toPx = (e: PointerEvent) => d3.pointer(e, this.svg.node())[0] * (W / this.host.clientWidth);
    zone.on("pointermove", (e: PointerEvent) => {
      const info = at(toPx(e));
      rule.style("display", null).attr("x1", info.at).attr("x2", info.at);
      this.tip.innerHTML = `<div class="tip-title">${info.head}</div>` + info.rows.map((r) =>
        `<div class="tip-row"><span class="${r.cls}">${r.label}</span><b>${r.value}</b></div>`).join("");
      this.tip.hidden = false;
      const left = (info.at / W) * this.host.clientWidth;
      this.tip.style.left = `${left > this.host.clientWidth / 2 ? left - this.tip.offsetWidth - 14 : left + 14}px`;
      this.tip.style.top = `${m.t + 6}px`;
    }).on("pointerleave", () => { rule.style("display", "none"); this.tip.hidden = true; });
    if (click) zone.on("click", (e: PointerEvent) => click(toPx(e)));
  }

  /** PNG of the chart with its title, legend and a credit line. */
  async exportPNG(title: string, credit: string, filename: string) {
    const img = await svgImage(this.svg.node()!);
    if (!img) return;
    const legend = [...this.legend.querySelectorAll("li")].map((li) => li.textContent ?? "");
    const scale = 2, pad = 24, w = img.width, rowH = 18;
    const h = img.height + 44 + Math.ceil(legend.length / 2) * rowH + 30;
    const cv = document.createElement("canvas");
    cv.width = (w + 2 * pad) * scale; cv.height = (h + 2 * pad) * scale;
    const ctx = cv.getContext("2d")!;
    ctx.scale(scale, scale);
    const st = getComputedStyle(document.documentElement);
    ctx.fillStyle = st.getPropertyValue("--bg") || "#fff";
    ctx.fillRect(0, 0, w + 2 * pad, h + 2 * pad);
    ctx.fillStyle = st.getPropertyValue("--ink") || "#000";
    ctx.font = "600 17px -apple-system, Helvetica, sans-serif";
    ctx.fillText(title, pad, pad + 16);
    ctx.drawImage(img, pad, pad + 32);
    ctx.font = "13px -apple-system, Helvetica, sans-serif";
    legend.forEach((t, i) => ctx.fillText(t, pad + (i % 2) * (w / 2), pad + 44 + img.height + Math.floor(i / 2) * rowH));
    ctx.fillStyle = st.getPropertyValue("--ink-2") || "#666";
    ctx.font = "11px -apple-system, Helvetica, sans-serif";
    ctx.fillText(credit, pad, h + pad + 8);
    await download(cv, filename);
  }
}
