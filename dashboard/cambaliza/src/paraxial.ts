// Paraxial scalar focus of one lens (the field of Eq. 1, as in mcdo.twobeam._paraxial), computed in the browser:
//   U = e^{i k z_b} · 2 ∫₀¹ J₀(vρ) e^{−iuρ²/2} ρ dρ,  u = k (NA/n)² z_b,  v = (k/n) NA r_b,  k = 2πn/λ
// with beam 2 turned by θ in real space: z_b = x sinθ + z cosθ, x_b = x cosθ − z sinθ (points in the x–z plane).

/** Bessel J₀ (rational approximation of Numerical Recipes, |error| < 1e-8). */
export function j0(x: number): number {
  const ax = Math.abs(x);
  if (ax < 8) {
    const y = x * x;
    const a = 57568490574.0 + y * (-13362590354.0 + y * (651619640.7 + y * (-11214424.18 + y * (77392.33017 + y * -184.9052456))));
    const b = 57568490411.0 + y * (1029532985.0 + y * (9494680.718 + y * (59272.64853 + y * (267.8532712 + y))));
    return a / b;
  }
  const z = 8 / ax, y = z * z, xx = ax - 0.785398164;
  const p = 1 + y * (-0.1098628627e-2 + y * (0.2734510407e-4 + y * (-0.2073370639e-5 + y * 0.2093887211e-6)));
  const q = -0.1562499995e-1 + y * (0.1430488765e-3 + y * (-0.6911147651e-5 + y * (0.7621095161e-6 - y * 0.934935152e-7)));
  return Math.sqrt(0.636619772 / ax) * (Math.cos(xx) * p - z * Math.sin(xx) * q);
}

const NR = 201;                                   // pupil radii, Simpson's rule
const RHO = Array.from({ length: NR }, (_, i) => i / (NR - 1));
const WS = RHO.map((_, i) => ((i === 0 || i === NR - 1) ? 1 : i % 2 ? 4 : 2) / (3 * (NR - 1)));

/** |U|² of one beam at the points (x[i], z[i]) in µm. */
export function intensity(x: number[], z: number[], lam: number, na: number, n = 1, theta = 0): number[] {
  const k = (2 * Math.PI * n) / lam, s = Math.sin(theta), c = Math.cos(theta);
  return x.map((xi, i) => {
    const zb = xi * s + z[i] * c, rb = Math.abs(xi * c - z[i] * s);
    const u = k * (na / n) ** 2 * zb, v = (k / n) * na * rb;
    let re = 0, im = 0;
    for (let j = 0; j < NR; j++) {
      const r = RHO[j], w = WS[j] * r * j0(v * r), ph = -0.5 * u * r * r;
      re += w * Math.cos(ph); im += w * Math.sin(ph);
    }
    return 4 * (re * re + im * im);                // |2∫…|²; the carrier e^{ikz_b} drops out of |U|²
  });
}

/** 2CE = I₁ I₂ along a cut, normalized to its peak. */
export function twoColor(x: number[], z: number[], l1: number, l2: number, na: number, n: number, theta: number): number[] {
  const a = intensity(x, z, l1, na, n, 0), b = intensity(x, z, l2, na, n, theta);
  const f = a.map((v, i) => v * b[i]);
  const top = Math.max(...f);
  return f.map((v) => v / top);
}

/** The 2CE wavelengths with λ₁ − λ₂ = Δλ and 1/λ₁ + 1/λ₂ = 1/λₑ (µm). */
export function pair(dl: number, le = 0.35): [number, number] {
  const b = dl - 2 * le, c = -le * dl;
  const l2 = (-b + Math.sqrt(b * b - 4 * c)) / 2;
  return [l2 + dl, l2];
}

/** FWHM of the central peak of a profile normalized at s = 0. */
export function fwhm(s: number[], y: number[]): number {
  const i0 = s.reduce((a, v, i) => (Math.abs(v) < Math.abs(s[a]) ? i : a), 0);
  let r = i0, l = i0;
  while (r < y.length - 1 && y[r] >= 0.5 * y[i0]) r++;
  while (l > 0 && y[l] >= 0.5 * y[i0]) l--;
  const h = 0.5 * y[i0];
  if (y[r] >= h || y[l] >= h) return NaN;                        // never falls to half inside the window: no width
  const xr = s[r - 1] + ((h - y[r - 1]) / (y[r] - y[r - 1])) * (s[r] - s[r - 1]);
  const xl = s[l + 1] + ((h - y[l + 1]) / (y[l] - y[l + 1])) * (s[l] - s[l + 1]);
  return xr - xl;
}

/** Complex field (re, im arrays) of one beam at (x[i], z[i]); pupil from ε to 1 (annular: ε > 0); nr odd. */
/** rot "uv": the turn written in Eq. 1, applied to the optical coordinates (u, v) themselves (as rotation='optical' in mcdo.twobeam);
 *  it equals the real-space turn only at θ = 0 and π. Same sense of rotation as the real-space turn. */
export function field(x: ArrayLike<number>, z: ArrayLike<number>, lam: number, na: number, n = 1, theta = 0, eps = 0, nr = NR, rot: "xz" | "uv" = "xz") {
  const k = (2 * Math.PI * n) / lam, s = Math.sin(theta), c = Math.cos(theta);
  const ku = k * (na / n) ** 2, kv = (k / n) * na;
  const rho = Array.from({ length: nr }, (_, i) => eps + ((1 - eps) * i) / (nr - 1));
  const ws = rho.map((r, i) => r * ((i === 0 || i === nr - 1) ? 1 : i % 2 ? 4 : 2) * (1 - eps) / (3 * (nr - 1)));
  const N = x.length, re = new Float64Array(N), im = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    let zb: number, rb: number;
    if (rot === "uv") {
      const u0 = ku * z[i], v0 = kv * x[i];
      zb = (u0 * c + v0 * s) / ku; rb = Math.abs(v0 * c - u0 * s) / kv;
    } else { zb = x[i] * s + z[i] * c; rb = Math.abs(x[i] * c - z[i] * s); }
    const u = ku * zb, v = kv * rb;
    let a = 0, b = 0;
    for (let j = 0; j < nr; j++) {
      const w = ws[j] * j0(v * rho[j]), ph = -0.5 * u * rho[j] * rho[j];
      a += w * Math.cos(ph); b += w * Math.sin(ph);
    }
    const cr = Math.cos(k * zb), ci = Math.sin(k * zb);       // carrier e^{i k z_b}
    re[i] = 2 * (a * cr - b * ci); im[i] = 2 * (a * ci + b * cr);
  }
  return { re, im };
}

/** 2CE = |U₁|²|U₂|² and 2PE = |U₁ + U₂|⁴ (Eq. 6), both normalized to their peak.
 *  pe = 1 gives |U₁ + U₂|² instead (the excitation, which the published Figs. 6a and 7a plot). */
export function signals(x: ArrayLike<number>, z: ArrayLike<number>, o: { na: number; n: number; theta: number; eps: number; l1: number; l2: number; lp: number; nr?: number; rot?: "xz" | "uv"; pe?: number; tau?: number }) {
  const r = o.rot ?? "xz";
  const a = field(x, z, o.l1, o.na, o.n, 0, o.eps, o.nr), b = field(x, z, o.l2, o.na, o.n, o.theta, o.eps, o.nr, r);
  const p = field(x, z, o.lp, o.na, o.n, 0, o.eps, o.nr), q = field(x, z, o.lp, o.na, o.n, o.theta, o.eps, o.nr, r);
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

/** Transform-limited Gaussian pulses (intensity FWHM τ, fs), zero delay, closed form: each pulse passes the point (x, z)
 *  at t_i = n z_b,i / c; time-integrated products of the envelopes give the overlap factors
 *  ∫a₁a₂ → e^{−ln2 Δ²/τ²} (g1), ∫a₁²a₂² → e^{−2ln2 Δ²/τ²} (g2), ∫a₁³a₂ → e^{−1.5ln2 Δ²/τ²} (g3), Δ = t₁ − t₂.
 *  2CE: I₁I₂·g2. 2PE (Eq. 6): J₁² + J₂² + g2(2J₁J₂ + 4R²) + 4 g3 R (J₁ + J₂), R = Re(U₁U₂*); the single-beam terms need no
 *  overlap. Leaves out the change of the focus across the spectrum (within 5% of the full frequency sum at 10 fs). */
export function gates(x: number, z: number, o: { n: number; theta: number; tau?: number }) {
  if (!o.tau) return { g1: 1, g2: 1, g3: 1 };
  const D = (o.n * (z - (x * Math.sin(o.theta) + z * Math.cos(o.theta)))) / 0.299792458, r = (Math.LN2 * D * D) / (o.tau * o.tau);
  return { g1: Math.exp(-r), g2: Math.exp(-2 * r), g3: Math.exp(-1.5 * r) };
}
