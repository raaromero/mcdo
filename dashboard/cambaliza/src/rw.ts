// Vector (Richards–Wolf, Debye) focus of one aplanatic lens, computed in the browser, for beams polarized along y.
// Beam 2 is the same lens turned by θ about y, so both fields stay along y and, in the x–z plane (φ = 0 or π), each is
//   E_y = I₀ − I₂,  I₀ = ∫ √cosθ sinθ (1 + cosθ) J₀(k r sinθ) e^{ikz cosθ} dθ,  I₂ = ∫ √cosθ sinθ (1 − cosθ) J₂(k r sinθ) e^{ikz cosθ} dθ
// over sin θ from ε·NA/n to NA/n (annular pupil: the sine condition), k = 2πn/λ — as model='rw', psi = π/2 in mcdo.twobeam.
// 2CE = |E₁|²|E₂|², 2PE = |E₁ + E₂|⁴ (Eq. 6) or |E₁ + E₂|² (pe = 1), each normalized to its peak.
import { j0, gates } from "./paraxial";

function j1(x: number): number {
  const ax = Math.abs(x);
  if (ax < 8) {
    const y = x * x;
    const a = x * (72362614232.0 + y * (-7895059235.0 + y * (242396853.1 + y * (-2972611.439 + y * (15704.4826 + y * -30.16036606)))));
    const b = 144725228442.0 + y * (2300535178.0 + y * (18583304.74 + y * (99447.43394 + y * (376.9991397 + y))));
    return a / b;
  }
  const z = 8 / ax, y = z * z, xx = ax - 2.356194491;
  const p = 1 + y * (0.183105e-2 + y * (-0.3516396496e-4 + y * (0.2457520174e-5 + y * -0.240337019e-6)));
  const q = 0.04687499995 + y * (-0.2002690873e-3 + y * (0.8449199096e-5 + y * (-0.88228987e-6 + y * 0.105787412e-6)));
  const r = Math.sqrt(0.636619772 / ax) * (Math.cos(xx) * p - z * Math.sin(xx) * q);
  return x < 0 ? -r : r;
}
function j2(x: number): number {
  if (Math.abs(x) < 0.5) { const y = x * x; return (y / 8) * (1 - y / 12 + (y * y) / 384); }
  return (2 * j1(x)) / x - j0(x);
}

export type RWOpts = { na: number; n: number; theta: number; eps: number; l1: number; l2: number; lp: number; pe?: number; nt?: number; tau?: number };

/** Complex E_y of one beam at (x[i], z[i]) µm; theta turns the lens about y (same frame as the paraxial code). */
export function rwField(x: ArrayLike<number>, z: ArrayLike<number>, lam: number, na: number, n: number, theta: number, eps: number, nt = 161) {
  const k = (2 * Math.PI * n) / lam, a1 = Math.asin(Math.min(0.9999, na / n)), a0 = eps > 0 ? Math.asin((eps * na) / n) : 0;
  const ct = new Float64Array(nt), st = new Float64Array(nt), wa = new Float64Array(nt), wb = new Float64Array(nt);
  for (let j = 0; j < nt; j++) {
    const t = a0 + ((a1 - a0) * j) / (nt - 1), w = ((j === 0 || j === nt - 1) ? 1 : j % 2 ? 4 : 2) * (a1 - a0) / (3 * (nt - 1));
    ct[j] = Math.cos(t); st[j] = Math.sin(t);
    const g = w * Math.sqrt(ct[j]) * st[j];
    wa[j] = g * (1 + ct[j]); wb[j] = g * (1 - ct[j]);
  }
  const s = Math.sin(theta), c = Math.cos(theta), N = x.length, re = new Float64Array(N), im = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    const zb = x[i] * s + z[i] * c, rb = Math.abs(x[i] * c - z[i] * s);
    let a = 0, b = 0;
    for (let j = 0; j < nt; j++) {
      const v = k * rb * st[j], amp = wa[j] * j0(v) - wb[j] * j2(v), ph = k * zb * ct[j];
      a += amp * Math.cos(ph); b += amp * Math.sin(ph);
    }
    re[i] = a; im[i] = b;
  }
  return { re, im };
}

export function rwSignals(x: ArrayLike<number>, z: ArrayLike<number>, o: RWOpts) {
  const nt = o.nt ?? 161;
  const a = rwField(x, z, o.l1, o.na, o.n, 0, o.eps, nt), b = rwField(x, z, o.l2, o.na, o.n, o.theta, o.eps, nt);
  const p = rwField(x, z, o.lp, o.na, o.n, 0, o.eps, nt), q = rwField(x, z, o.lp, o.na, o.n, o.theta, o.eps, nt);
  const N = x.length, c2 = new Float64Array(N), p2 = new Float64Array(N);
  let mc = 0, mp = 0;
  for (let i = 0; i < N; i++) {
    const G = gates(x[i], z[i], o);
    c2[i] = (a.re[i] ** 2 + a.im[i] ** 2) * (b.re[i] ** 2 + b.im[i] ** 2) * G.g2;
    const J1 = p.re[i] ** 2 + p.im[i] ** 2, J2 = q.re[i] ** 2 + q.im[i] ** 2, R = p.re[i] * q.re[i] + p.im[i] * q.im[i];   // R = √(J1 J2) cos φ
    p2[i] = o.pe === 1 ? J1 + J2 + 2 * R * G.g1 : J1 * J1 + J2 * J2 + G.g2 * (2 * J1 * J2 + 4 * R * R) + 4 * G.g3 * R * (J1 + J2);
    if (c2[i] > mc) mc = c2[i];
    if (p2[i] > mp) mp = p2[i];
  }
  for (let i = 0; i < N; i++) { c2[i] /= mc; p2[i] /= mp; }
  return { c2: Array.from(c2), p2: Array.from(p2) };
}
