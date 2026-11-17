// Two transform-limited pulses passing through the common focus, computed in the browser (as scripts/cambaliza2000_pulse_video.py):
// each pulse is a sum over its spectrum of monochromatic paraxial foci (field() of paraxial.ts, the carrier e^{ikz} kept),
//   e_j(P, t) = Σ_ω c(ω) e^{−i(ω − ω_j)t} U_ω(P),   c(ω) = exp(−(ω − ω_j)²τ²/8ln2)·(ω/ω_j)·δω,
// and the two-photon amplitude to the narrow 350-nm level counts all photon pairs from both beams (phase-locked pulses):
//   A(P, t) = ∫₋∞ᵗ E² e^{iω_e t′} dt′ = A₁₁ + 2A₁₂ + A₂₂,  |A(P, t)|² = the excitation accumulated up to t; after the pulses, the signal.
// 2CE: 750 + 656 nm; 2PE: both at 700 nm. Beam 2 arrives `delay` fs after beam 1.
import { field } from "./paraxial";

export const C = 0.299792458;                                      // µm/fs
export type PulseOpts = { sig: "2CE" | "2PE"; tau: number; theta: number; na: number; n: number; delay: number;
  xh: number; zh: number; nx: number; nz: number; nl: number; frames: number };
export type PulseRun = {
  t: Float64Array;                                                 // frame times (fs)
  xs: number[]; zs: number[]; zl: number[];                        // map grid, axis line
  I1: Float32Array[]; I2: Float32Array[]; P: Float32Array[];   // P: I₁I₂ (2CE) or |E₁ + E₂|⁴ (2PE) now
  all: Float32Array[]; one: Float32Array[];      // maps, one per frame (one: the cross pairs alone, |2A₁₂|²)
  lI1: Float32Array[]; lI2: Float32Array[]; lP: Float32Array[]; lall: Float32Array[]; lone: Float32Array[];   // along the axis
  cw: Float32Array;                                                // continuous beams along the axis (2CE: I₁I₂, 2PE: |U₁+U₂|⁴)
  spec: { nu1: number[]; nu2: number[]; s1: number[]; s2: number[]; a1: Float32Array; a2: Float32Array; n: number[] };   // n: frequencies in each sum   // spectra at the focus, pulse strength there per frame
  lams: [number, number];
  focus: { fe: Float64Array; fk: Int32Array; t0: number; dt: number; w1: number; w2: number };   // both envelopes at the focus at every step (re, im, re, im), the steps of the frames
};

function spectrum(lam: number, tau: number, window: number) {
  const w0 = (2 * Math.PI * C) / lam, s = (2 * Math.sqrt(Math.LN2)) / tau, span = 7 * s;
  const n = Math.max(21, Math.ceil((span * 1.25 * window) / (2 * Math.PI)) + 1);
  const w = Array.from({ length: n }, (_, i) => w0 - span / 2 + (span * i) / (n - 1)), dw = w[1] - w[0];
  const c = w.map((v) => Math.exp(-((v - w0) ** 2) * tau * tau / (8 * Math.LN2)) * (v / w0) * dw);
  return { w, d: w.map((v) => v - w0), c, w0 };
}

export function runPulses(o: PulseOpts): PulseRun {
  const [l1, l2] = o.sig === "2CE" ? [0.75, 0.656] : [0.7, 0.7];
  const xs = Array.from({ length: o.nx }, (_, i) => -o.xh + (2 * o.xh * i) / (o.nx - 1));
  const zs = Array.from({ length: o.nz }, (_, i) => -o.zh + (2 * o.zh * i) / (o.nz - 1));
  const zl = Array.from({ length: o.nl }, (_, i) => -o.zh + (2 * o.zh * i) / (o.nl - 1));
  const X: number[] = [], Z: number[] = [];
  for (const z of zs) for (const x of xs) { X.push(x); Z.push(z); }
  const nm = X.length;
  for (const z of zl) { X.push(0); Z.push(z); }
  const N = X.length, iF = nm + zl.reduce((a, v, i) => (Math.abs(v) < Math.abs(zl[a]) ? i : a), 0);
  const reach = (o.n * Math.hypot(o.xh, o.zh)) / C, D = Math.abs(o.delay);
  const dt = Math.min(o.tau / 20, 0.4);                            // resolves ω₂ − ω₁ = 0.36 rad/fs
  const t0 = -(2 * o.tau + reach + D), nt = Math.ceil((2 * -t0) / dt) + 1;
  const window = 2 * (3 * o.tau + reach + D);
  const beams = [[l1, 0, 0], [l2, o.theta, o.delay]].map(([lam, th, del]) => {
    const sp = spectrum(lam, o.tau, window);
    const F = sp.w.map((w) => field(X, Z, (2 * Math.PI * C) / w, o.na, o.n, th, 0, 101));
    return { ...sp, F, del };
  });
  const WE = (2 * Math.PI * C) / 0.35, [b1, b2] = beams;
  const d11 = WE - 2 * b1.w0, d12 = WE - b1.w0 - b2.w0, d22 = WE - 2 * b2.w0;
  const e = [new Float64Array(2 * N), new Float64Array(2 * N)];
  const A11 = new Float64Array(2 * N), A12 = new Float64Array(2 * N), A22 = new Float64Array(2 * N);
  const every = Math.max(1, Math.ceil(nt / o.frames));
  const out: PulseRun = { t: new Float64Array(0), xs, zs, zl, I1: [], I2: [], P: [], all: [], one: [], lI1: [], lI2: [], lP: [], lall: [], lone: [],
    cw: new Float32Array(o.nl), spec: { nu1: [], nu2: [], s1: [], s2: [], a1: new Float32Array(0), a2: new Float32Array(0), n: [] }, lams: [l1, l2], focus: { fe: new Float64Array(0), fk: new Int32Array(0), t0: 0, dt: 0, w1: 0, w2: 0 } };
  const ts: number[] = [], a1: number[] = [], a2: number[] = [], fk: number[] = [];
  const fe = new Float64Array(4 * nt);
  for (let k = 0; k < nt; k++) {
    const t = t0 + k * dt;
    beams.forEach((b, j) => {                                       // envelope of each pulse at time t (beam 2 delayed)
      const E = e[j]; E.fill(0);
      const tt = t - b.del;
      for (let q = 0; q < b.w.length; q++) {
        const cr = b.c[q] * Math.cos(b.d[q] * tt), ci = -b.c[q] * Math.sin(b.d[q] * tt), F = b.F[q];
        for (let i = 0; i < N; i++) {
          const fr = F.re[i], fi = F.im[i];
          E[2 * i] += cr * fr - ci * fi; E[2 * i + 1] += cr * fi + ci * fr;
        }
      }
    });
    const p11 = [Math.cos(d11 * t) * dt, Math.sin(d11 * t) * dt], p12 = [Math.cos(d12 * t) * dt, Math.sin(d12 * t) * dt],
      p22 = [Math.cos(d22 * t) * dt, Math.sin(d22 * t) * dt];
    const [E1, E2] = e;
    for (let i = 0; i < N; i++) {
      const ar = E1[2 * i], ai = E1[2 * i + 1], br = E2[2 * i], bi = E2[2 * i + 1];
      const sr = ar * ar - ai * ai, si = 2 * ar * ai, ur = br * br - bi * bi, ui = 2 * br * bi, mr = ar * br - ai * bi, mi = ar * bi + ai * br;
      A11[2 * i] += sr * p11[0] - si * p11[1]; A11[2 * i + 1] += sr * p11[1] + si * p11[0];
      A12[2 * i] += mr * p12[0] - mi * p12[1]; A12[2 * i + 1] += mr * p12[1] + mi * p12[0];
      A22[2 * i] += ur * p22[0] - ui * p22[1]; A22[2 * i + 1] += ur * p22[1] + ui * p22[0];
    }
    fe[4 * k] = E1[2 * iF]; fe[4 * k + 1] = E1[2 * iF + 1]; fe[4 * k + 2] = E2[2 * iF]; fe[4 * k + 3] = E2[2 * iF + 1];
    if (k % every && k !== nt - 1) continue;
    fk.push(k);
    const I1 = new Float32Array(N), I2 = new Float32Array(N), P = new Float32Array(N), all = new Float32Array(N), one = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      I1[i] = E1[2 * i] ** 2 + E1[2 * i + 1] ** 2; I2[i] = E2[2 * i] ** 2 + E2[2 * i + 1] ** 2;
      P[i] = o.sig === "2CE" ? I1[i] * I2[i] : ((E1[2 * i] + E2[2 * i]) ** 2 + (E1[2 * i + 1] + E2[2 * i + 1]) ** 2) ** 2;   // 2PE: the fields add (Eq. 6 now)
      const re = A11[2 * i] + 2 * A12[2 * i] + A22[2 * i], im = A11[2 * i + 1] + 2 * A12[2 * i + 1] + A22[2 * i + 1];
      all[i] = re * re + im * im; one[i] = 4 * (A12[2 * i] ** 2 + A12[2 * i + 1] ** 2);
    }
    ts.push(t); a1.push(I1[iF]); a2.push(I2[iF]);
    out.I1.push(I1.slice(0, nm)); out.I2.push(I2.slice(0, nm)); out.P.push(P.slice(0, nm)); out.all.push(all.slice(0, nm)); out.one.push(one.slice(0, nm));
    out.lI1.push(I1.slice(nm)); out.lI2.push(I2.slice(nm)); out.lP.push(P.slice(nm)); out.lall.push(all.slice(nm)); out.lone.push(one.slice(nm));
  }
  out.t = Float64Array.from(ts);
  out.focus = { fe, fk: Int32Array.from(fk), t0, dt, w1: b1.w0, w2: b2.w0 };
  const m1 = Math.max(...a1), m2 = Math.max(...a2);
  const sp = (b: typeof b1) => {                                    // |a(ω)(ω/ω_j) U_ω(focus)|² on a fine grid (display only), normalized
    const sg = (2 * Math.sqrt(Math.LN2)) / o.tau, M = 400;
    const w = Array.from({ length: M }, (_, i) => b.w0 - 3.5 * sg + (7 * sg * i) / (M - 1));
    const s = w.map((v) => {
      const a = Math.exp(-((v - b.w0) ** 2) * o.tau * o.tau / (8 * Math.LN2)) * (v / b.w0), U = field([X[iF]], [Z[iF]], (2 * Math.PI * C) / v, o.na, o.n, 0, 0, 101);
      return (a * Math.hypot(U.re[0], U.im[0])) ** 2;
    }), top = Math.max(...s);
    return { nu: w.map((v) => (v / (2 * Math.PI)) * 1e3), s: s.map((v) => v / top) };
  };
  const S1 = sp(b1), S2 = sp(b2);
  out.spec = { nu1: S1.nu, nu2: S2.nu, s1: S1.s, s2: S2.s, a1: Float32Array.from(a1, (v) => v / m1), a2: Float32Array.from(a2, (v) => v / m2),
    n: [b1.w.length, b2.w.length] };
  const u1 = field(zl.map(() => 0), zl, l1, o.na, o.n, 0), u2 = field(zl.map(() => 0), zl, l2, o.na, o.n, o.theta);
  let top = 0;
  for (let i = 0; i < o.nl; i++) {
    const J1 = u1.re[i] ** 2 + u1.im[i] ** 2, J2 = u2.re[i] ** 2 + u2.im[i] ** 2;
    out.cw[i] = o.sig === "2CE" ? J1 * J2 : ((u1.re[i] + u2.re[i]) ** 2 + (u1.im[i] + u2.im[i]) ** 2) ** 2;
    top = Math.max(top, out.cw[i]);
  }
  for (let i = 0; i < o.nl; i++) out.cw[i] /= top;
  return out;
}

/** Two-photon sum spectrum at the focus, accumulated up to t: for each kind of pair (750 + 750, 750 + 656, 656 + 656 nm in 2CE) the
 *  amplitude to a level at sum frequency Ω, A_ab(Ω, t) = ∫₋∞ᵗ e_a e_b e^{i(Ω − ω_a − ω_b)t′} dt′ (×2 for the cross pairs), on a grid of
 *  sum wavelengths λ = 2πc/Ω (nm), one snapshot per frame. At λ = 350 nm these are A₁₁, 2A₁₂, A₂₂ of the excitation. */
export function pairSpectra(run: PulseRun, lam: number[]) {
  const { fe, fk, t0, dt, w1, w2 } = run.focus, nt = fe.length / 4, M = lam.length;
  const kinds = [[2 * w1, 0, 0, 1], [w1 + w2, 0, 2, 2], [2 * w2, 2, 2, 1]] as const;   // ω_a + ω_b, which envelopes, weight
  const acc = kinds.map(() => new Float64Array(2 * M));
  const rot = kinds.map(([ws]) => lam.map((l) => (2 * Math.PI * C * 1e3) / l - ws));   // Ω − ω_a − ω_b (rad/fs)
  const snaps: Float32Array[][] = [];
  let f = 0;
  for (let k = 0; k < nt; k++) {
    const t = t0 + k * dt;
    kinds.forEach(([, a, b, wt], q) => {
      const ar = fe[4 * k + a], ai = fe[4 * k + a + 1], br = fe[4 * k + b], bi = fe[4 * k + b + 1];
      const pr = (ar * br - ai * bi) * wt * dt, pi = (ar * bi + ai * br) * wt * dt, A = acc[q], R = rot[q];
      for (let m = 0; m < M; m++) {
        const c = Math.cos(R[m] * t), s = Math.sin(R[m] * t);
        A[2 * m] += pr * c - pi * s; A[2 * m + 1] += pr * s + pi * c;
      }
    });
    if (f < fk.length && fk[f] === k) {
      snaps.push(acc.map((A) => Float32Array.from({ length: M }, (_, m) => A[2 * m] ** 2 + A[2 * m + 1] ** 2)));
      f++;
    }
  }
  return snaps;                                                     // [frame][kind][λ]: |A_ab|²
}
