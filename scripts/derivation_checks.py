r"""Numbers of the derivation documents docs/two_color/derivations/*.tex: each closed form against the engine
(mcdo.twobeam) and against the stored results it explains.

    python scripts/derivation_checks.py > output/08_two_color/derivation_checks.txt      (about two minutes)
    python scripts/derivation_checks.py --widths > output/08_two_color/derivation_checks_widths.txt      (Part 5 alone,
        about two minutes)

Part 1, scalar focal field: half-width points of the Airy and sinc^2 profiles and of their powers; the widths at NA 0.5;
the depth of focus of the paraxial model against the non-paraxial weights of the axial integral; the integral of the
intensity over a plane z, which is the same in all planes.
Part 2, vector field: transversality of the ray field, the share of I1 and I2, the Romallosa width, Gauss's law, the
same integral over a plane for the vector field, the widths across and along the polarization.
Part 3, two beams: the rotation, the 2PE standing-wave fringe, crossed lenses, the displacement of Lim & Saloma (2002),
the spherical aberration of Lim & Saloma (2003), and the identity F = 2Q - C of Linfoot's criteria on every stored row.
Pulses (docs/two_color/pulse_derivations.tex, Sections 3, 6 and 7): when a focused pulse arrives on the axis, the
temporal overlap at 5 fs with the factor omega/omega_0, and the 2CE of facing lenses with a delay against the stored
profiles of the delay sweep.
Part 5 (--widths): every width of the high-NA pupil study against the fields of Parts 1 to 3 written out again.
"""
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import j1, jv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from mcdo.rw_integrals import compute_integrals  # noqa: E402
from mcdo.twobeam import _paraxial, beam_field, intensity, two_color, two_photon  # noqa: E402
from mcdo.pulsed2ce import C_UM_FS, _fields, two_color_cw  # noqa: E402
from cambaliza2000_pulses_sweep import fwhm  # noqa: E402

L1, L2, LP = 0.750, 0.656, 0.700
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
airy2 = lambda v: np.where(np.abs(v) < 1e-12, 1.0, 2 * j1(v) / np.where(np.abs(v) < 1e-12, 1.0, v)) ** 2   # across, v = (2 pi / lam) NA r
sinc2 = lambda y: np.sinc(np.asarray(y) / np.pi) ** 2         # along the axis, y = u / 4 (np.sinc(x) = sin(pi x) / (pi x))
gl_t, gl_w = np.polynomial.legendre.leggauss(400)


def head(s):
    print('\n' + s + '\n' + '-' * len(s))


def axial(w, lam, na, n, z):
    """|integral of w(t) exp(i k z t) dt|^2 over t = cos(theta) in [cos(alpha), 1]: the on-axis intensity."""
    c = np.sqrt(1 - (na / n) ** 2)
    t = 0.5 * (1 - c) * gl_t + 0.5 * (1 + c)
    k = 2 * np.pi * n / lam
    return np.abs(np.exp(1j * k * np.outer(z, t)) @ (w(t) * gl_w)) ** 2


def mean_t(w, na, n=1.0):
    c = np.sqrt(1 - (na / n) ** 2)
    t = 0.5 * (1 - c) * gl_t + 0.5 * (1 + c)
    return np.sum(w(t) * t * gl_w) / np.sum(w(t) * gl_w)


def plane_integral(f, R=40.0, nr=2001):
    """Integral of f(r) r dr from 0 to infinity: Simpson out to R and to R/2, the tail beyond extrapolated as 1/r."""
    def simpson(rmax, m):
        r = np.linspace(0, rmax, m)
        vals = np.concatenate([f(r[i:i + 500]) for i in range(0, m, 500)])
        w = np.ones(m)
        w[1:-1:2], w[2:-1:2] = 4, 2
        return np.sum(w * vals * r) * (r[1] - r[0]) / 3
    return 2 * simpson(R, nr) - simpson(R / 2, nr // 2 + 1)


def stored_widths(nodes=150):
    """Part 5 (option --widths): every width of the high-NA pupil study (cambaliza2000/high_na/pupils/widths.csv)
    against the fields written out again from Parts 1 to 3, with Gauss-Legendre integrals in the angle (vector) or in
    the pupil radius (paraxial) in place of the engine's Simpson grids, and the half-maximum point found as a root."""
    gt, gw = np.polynomial.legendre.leggauss(nodes)
    gl = lambda a, b: (0.5 * (b - a) * gt + 0.5 * (b + a), 0.5 * (b - a) * gw)

    def frame(th, x, z):                                  # Part 3, Section 1, Step 2, focus at the origin
        xb, zb = x * np.cos(th) - z * np.sin(th), x * np.sin(th) + z * np.cos(th)
        return np.abs(xb), np.where(xb >= 0, 0.0, np.pi), zb

    def vec(lam, na, n, eps, at, th, psi, x, z):          # Part 2: I0, I1, I2, the components, then the lab frame
        k, al = 2 * np.pi * n / lam, np.arcsin(na / n)
        t, w = gl(np.arcsin(eps * np.sin(al)), al)
        a = np.sqrt(np.cos(t)) * np.exp(-at * np.sin(t) ** 2 / np.sin(al) ** 2) * np.sin(t) * w
        rb, pb, zb = frame(th, x, z)
        ph, arg = np.exp(1j * k * np.outer(zb, np.cos(t))), k * np.outer(rb, np.sin(t))
        I0, I1, I2 = [(ph * jv(m, arg)) @ (a * c) for m, c in ((0, 1 + np.cos(t)), (1, np.sin(t)), (2, 1 - np.cos(t)))]
        f = pb - psi
        ex, ey, ez = -1j * (I0 + I2 * np.cos(2 * f)), -1j * I2 * np.sin(2 * f), -2 * I1 * np.cos(f)
        ex, ey = np.cos(psi) * ex - np.sin(psi) * ey, np.sin(psi) * ex + np.cos(psi) * ey
        return np.stack([np.cos(th) * ex + np.sin(th) * ez, ey, -np.sin(th) * ex + np.cos(th) * ez])

    def par(lam, na, n, eps, at, th, x, z):               # Part 1, Section 2, with the carrier, pupil eps to 1, exp(-at rho^2)
        k = 2 * np.pi * n / lam
        rb, _, zb = frame(th, x, z)
        rho, w = gl(eps, 1.0)
        U = (np.exp(-0.5j * np.outer(k * (na / n) ** 2 * zb, rho ** 2)) * jv(0, np.outer(k * na / n * rb, rho))) @ (
            2 * w * np.exp(-at * rho ** 2) * rho)
        return np.exp(1j * k * zb) * U

    I = lambda E: np.sum(np.abs(E) ** 2, axis=0) if E.ndim == 2 else np.abs(E) ** 2
    PSI = {'s': np.pi / 2, 'p': 0.0}

    def signal(r, x, z):
        args = (r.NA, r.n, r.eps, r.alpha_t)
        if r.model == 'scalar':
            F = lambda lam, th: par(lam, *args, th, x, z)
            return I(F(L1, 0.0)) * I(F(L2, r.theta)) if r.signal == '2CE' else I(F(LP, 0.0) + F(LP, r.theta)) ** 2
        F = lambda lam, th, pol: vec(lam, *args, th, PSI[pol], x, z)
        if r.model == 'unpol':
            return 0.25 * (I(F(L1, 0.0, 's')) + I(F(L1, 0.0, 'p'))) * (I(F(L2, r.theta, 's')) + I(F(L2, r.theta, 'p')))
        if r.signal == '2CE':
            return I(F(L1, 0.0, r.model)) * I(F(L2, r.theta, r.model))
        return I(F(LP, 0.0, r.model) + F(LP, r.theta, r.model)) ** 2

    def width(r):
        f = lambda s: signal(r, s if r.axis == 'x' else 0 * s, s if r.axis == 'z' else 0 * s)
        f0 = f(np.zeros(1))[0]
        if not f0 > 1e-12 * f(np.linspace(-1, 1, 41)).max():
            return np.nan                                  # dark centre (2PE, p, facing lenses)
        long_ = r.axis == 'z' and not np.isclose(r.theta, np.pi / 2)
        step = 0.2 * LP * r.n / r.NA ** 2 / (1 - r.eps ** 2) if long_ else 0.05 * LP / r.NA
        if r.signal == '2PE' and r.theta != 0:
            step = min(step, 0.004)                        # the central fringe
        lo = 0.0
        for _ in range(1000):
            s = lo + step * np.arange(1, 51)
            j = np.nonzero(f(s) / f0 < 0.5)[0]
            if j.size:
                a = s[j[0] - 1] if j[0] else lo
                return 2 * brentq(lambda q: f(np.array([q]))[0] / f0 - 0.5, a, s[j[0]], xtol=1e-10)
            lo = s[-1]
        return np.nan

    D = pd.read_csv(os.path.join(OUT, 'cambaliza2000', 'high_na', 'pupils', 'widths.csv'))
    D['check'] = [width(r) for r in D.itertuples()]
    D['rel'] = D.fwhm / D.check - 1
    head('5. All stored widths of the high-NA pupil study against the fields of Parts 1-3 written out again')
    print(f'{len(D)} widths (air and water; circular and annular pupils; uniform and Gaussian input; paraxial and vector '
          f's, p, unpolarized; 2CE and 2PE; theta = 0, pi/2, pi; across and along the axis); no width in both: '
          f'{int((D.fwhm.isna() & D.check.isna()).sum())}, in one of the two: {int((D.fwhm.isna() ^ D.check.isna()).sum())}')
    D['th'] = D.theta.map(lambda v: ('0', 'pi/2', 'pi')[int(round(2 * v / np.pi))])
    g = D.groupby(['signal', 'th']).rel.agg(lambda v: np.nanmax(np.abs(v)) if v.notna().any() else np.nan)
    print('largest |stored / check - 1|: ' + '; '.join(f'{s} theta = {th}: {v:.1e}' for (s, th), v in g.items()))
    top = D.loc[D.rel.abs().idxmax()]
    print(f'largest: n {top.n:g}, NA {top.NA:g}, eps {top.eps:g}, alpha_t {top.alpha_t:g}, {top.signal} {top.axis} '
          f'theta = {top.th} {top.model}: stored {top.fwhm:.6f}, root {top.check:.6f} µm')
    if top.th == 'pi/2':                                   # the transverse window of the stored run, 2001 points
        s = np.linspace(-2.5 * LP / top.NA, 2.5 * LP / top.NA, 2001)
        y = signal(top, s if top.axis == 'x' else 0 * s, s if top.axis == 'z' else 0 * s)
        y, r = y / y[1000], 1000                           # the stored width: half of the value at the centre
        while y[r] >= 0.5:
            r += 1
        l = 1000
        while y[l] >= 0.5:
            l -= 1
        grid = np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])
        print(f'the same fields on the stored grid, with its linear interpolation between points: {grid:.6f} µm')


if '--widths' in sys.argv:
    stored_widths()
    sys.exit(0)


# ══ Part 1 ══════════════════════════════════════════════════════════════════════════════════════════════════════════
head('1a. Half-width points (where the profile is 1/2 of its peak)')
vh1 = brentq(lambda v: airy2(v) - 0.5, 0.5, 3.0)
vh2 = brentq(lambda v: airy2(v) ** 2 - 0.5, 0.5, 3.0)
yh1 = brentq(lambda y: sinc2(y) - 0.5, 0.1, 3.0)
yh2 = brentq(lambda y: sinc2(y) ** 2 - 0.5, 0.1, 3.0)
print(f'[2J1(v)/v]^2 = 1/2 at v = {vh1:.4f};   [2J1(v)/v]^4 = 1/2 at v = {vh2:.4f}')
print(f'sinc^2(u/4) = 1/2 at u/4 = {yh1:.4f};  sinc^4(u/4) = 1/2 at u/4 = {yh2:.4f}')
print(f'one beam:  FWHM across = {vh1 / np.pi:.4f} lam/NA,  along = {4 * yh1 / np.pi:.4f} n lam/NA^2')
print(f'2PE, |U|^4: FWHM across = {vh2 / np.pi:.4f} lam/NA,  along = {4 * yh2 / np.pi:.4f} n lam/NA^2')

head('1b. Widths at NA 0.5 in air, paraxial model: closed form, engine, stored (replication_numbers.txt)')
na = 0.5
x = np.linspace(-1.5, 1.5, 30001)
z = np.linspace(-6.0, 6.0, 30001)
v_of = lambda lam, r: 2 * np.pi * na * r / lam
u4_of = lambda lam, zz: 2 * np.pi * na ** 2 * zz / lam / 4
cf = {'1PE 750 nm': (airy2(v_of(L1, x)), sinc2(u4_of(L1, z))),
      '1PE 656 nm': (airy2(v_of(L2, x)), sinc2(u4_of(L2, z))),
      '2PE 700 nm, θ = 0': (airy2(v_of(LP, x)) ** 2, sinc2(u4_of(LP, z)) ** 2),
      '2CE 750 × 656 nm, θ = 0': (airy2(v_of(L1, x)) * airy2(v_of(L2, x)), sinc2(u4_of(L1, z)) * sinc2(u4_of(L2, z)))}
stored = {'2PE 700 nm, θ = 0': (0.517, 3.572), '2CE 750 × 656 nm, θ = 0': (0.516, 3.562)}
xe, ze = np.linspace(-0.8, 0.8, 1601), np.linspace(-4.0, 4.0, 1601)
for key, (fx, fz) in cf.items():
    wx, wz = fwhm(x, fx), fwhm(z, fz)
    if key.startswith('1PE'):
        lam = L1 if '750' in key else L2
        ex = fwhm(xe, intensity(beam_field(xe, 0 * xe, lam, na)))
        ez = fwhm(ze, intensity(beam_field(0 * ze, ze, lam, na)))
    elif key.startswith('2PE'):
        ex = fwhm(xe, two_photon(beam_field(xe, 0 * xe, LP, na), beam_field(xe, 0 * xe, LP, na)))
        ez = fwhm(ze, two_photon(beam_field(0 * ze, ze, LP, na), beam_field(0 * ze, ze, LP, na)))
    else:
        ex = fwhm(xe, two_color(beam_field(xe, 0 * xe, L1, na), beam_field(xe, 0 * xe, L2, na)))
        ez = fwhm(ze, two_color(beam_field(0 * ze, ze, L1, na), beam_field(0 * ze, ze, L2, na)))
    st = stored.get(key)
    sts = f'   stored {st[0]:.3f} / {st[1]:.3f}' if st else ''
    print(f'{key:26s} closed form {wx:.4f} / {wz:.4f} µm   engine {ex:.4f} / {ez:.4f}{sts}')

head('1d. Why 2CE at θ = 0 has nearly the 2PE spot: the quadratic mean of 1/λ1 and 1/λ2')
lam_m = (0.5 * (1 / L1 ** 2 + 1 / L2 ** 2)) ** -0.5
print(f'lam_m = (2 / (1/lam1^2 + 1/lam2^2))^(1/2) = {1000 * lam_m:.1f} nm; 2PE at lam_m, NA 0.5: '
      f'{vh2 / np.pi * lam_m / 0.5:.4f} / {4 * yh2 / np.pi * lam_m / 0.25:.4f} µm against 2CE 0.5157 / 3.5620; '
      f'ratio of means (1/lam): {lam_m / LP:.4f}')

head('1e. Annular pupil, obstruction ratio eps, NA 0.5: focal plane (Babinet), closed form against engine and stored')
x = np.linspace(-1.5, 1.5, 30001)
xs = np.where(np.abs(x) < 1e-12, 1e-12, x)
ann = lambda lam, eps: ((2 * (j1(2 * np.pi * 0.5 * xs / lam) - eps * j1(eps * 2 * np.pi * 0.5 * xs / lam))
                         / (2 * np.pi * 0.5 * xs / lam)) / (1 - eps ** 2)) ** 2
j0l = lambda lam: jv(0, 2 * np.pi * 0.5 * x / lam) ** 2
xe = np.linspace(-0.8, 0.8, 1601)
e2p = fwhm(xe, two_photon(beam_field(xe, 0 * xe, LP, 0.5, eps=0.99), beam_field(xe, 0 * xe, LP, 0.5, eps=0.99)))
e2c = fwhm(xe, two_color(beam_field(xe, 0 * xe, L1, 0.5, eps=0.99), beam_field(xe, 0 * xe, L2, 0.5, eps=0.99)))
print(f'eps = 0.99: 2PE {fwhm(x, ann(LP, 0.99) ** 2):.4f} µm (engine {e2p:.4f}, stored 0.365); 2CE '
      f'{fwhm(x, ann(L1, 0.99) * ann(L2, 0.99)):.4f} (engine {e2c:.4f}, stored 0.364)')
print(f'eps -> 1 (J0): one beam 750 nm {fwhm(x, j0l(L1)):.4f} µm; 2PE {fwhm(x, j0l(LP) ** 2):.4f}; 2CE '
      f'{fwhm(x, j0l(L1) * j0l(L2)):.4f}; along the axis the depth of focus grows as 1 / (1 - eps^2) = '
      f'{1 / (1 - 0.99 ** 2):.1f} at eps = 0.99')

head('1c. Depth of focus: weight of the axial integral over t = cos(theta), one beam, 750 nm, air')
print('paraxial: uniform weight over a range sin^2(alpha)/2;  uniform solid angle: uniform over 1 - cos(alpha);')
print('Debye with the aplanatic factor: sqrt(t);  vector focus on the axis (|I0|^2): sqrt(t) (1 + t)')
zz = np.linspace(-12, 12, 24001)
for na in (0.5, 0.7, 0.9):
    a = np.arcsin(na)
    par = 4 * yh1 / np.pi * L1 / na ** 2
    uni = fwhm(zz, axial(lambda t: np.ones_like(t), L1, na, 1.0, zz))
    deb = fwhm(zz, axial(np.sqrt, L1, na, 1.0, zz))
    vec = fwhm(zz, axial(lambda t: np.sqrt(t) * (1 + t), L1, na, 1.0, zz))
    eng = fwhm(zz, intensity(beam_field(0 * zz, zz, L1, na, model='rw')))
    print(f'NA {na}: paraxial {par:.3f} µm; uniform solid angle {uni:.3f} (ratio {par / uni:.3f}, 1 + tan^2(alpha/2) = '
          f'{1 + np.tan(a / 2) ** 2:.3f}); Debye sqrt(t) {deb:.3f} (ratio {par / deb:.3f}); vector {vec:.3f} '
          f'(ratio {par / vec:.3f}); engine rw {eng:.3f}')
z2 = np.linspace(-6, 6, 24001)
for na, st_par, st_vec in ((0.5, 3.562, 3.326), (0.9, 1.099, 0.807)):
    w = lambda t: np.sqrt(t) * (1 + t)
    v2 = fwhm(z2, axial(w, L1, na, 1.0, z2) * axial(w, L2, na, 1.0, z2))
    p2 = fwhm(z2, sinc2(2 * np.pi * na ** 2 * z2 / L1 / 4) * sinc2(2 * np.pi * na ** 2 * z2 / L2 / 4))
    print(f'2CE θ = 0, NA {na}: paraxial {p2:.3f} (stored {st_par}), vector from the weights {v2:.3f} (stored {st_vec}),'
          f' ratio {p2 / v2:.3f}')

head('1f. Integral of |U|^2 r dr over a plane z (Section 1, Step 6, and Section 2, Step 6), 750 nm, air')
print('ratio to the closed form: Debye (1 - cos alpha) / k^2 (the engine leaves out the 2 pi of Eq. 6); '
      'paraxial 2 / (2 pi NA / lam)^2')
kk = 2 * np.pi / L1
for na in (0.5, 0.9):
    out = [f'z = {z0:g} µm: {plane_integral(lambda r, z0=z0: np.abs(beam_field(r, 0 * r + z0, L1, na, model="debye", n_theta=1501)) ** 2) / ((1 - np.sqrt(1 - na ** 2)) / kk ** 2):.6f}'
           for z0 in (0.0, 2.0)]
    print(f'Debye, NA {na}: ' + '; '.join(out))
out = [f'z = {z0:g} µm: {plane_integral(lambda r, z0=z0: np.abs(_paraxial(r, 0 * r + z0, kk, 0.5, 1.0, n_rho=1501)) ** 2) / (2 / (kk * 0.5) ** 2):.6f}'
       for z0 in (0.0, 2.0)]
print('paraxial, NA 0.5 (1501 pupil points): ' + '; '.join(out))

# ══ Part 2 ══════════════════════════════════════════════════════════════════════════════════════════════════════════
head('2a. The ray field is transverse: k_hat . e_hat over a grid of (theta, phi)')
th, ph = np.meshgrid(np.linspace(0, 1.4, 141), np.linspace(0, 2 * np.pi, 181))
e = np.array([np.cos(th) * np.cos(ph) ** 2 + np.sin(ph) ** 2, (np.cos(th) - 1) * np.sin(ph) * np.cos(ph),
              -np.sin(th) * np.cos(ph)])
kh = np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
print(f'max |k.e| = {np.abs(np.sum(kh * e, 0)).max():.1e};  |e| - 1 within {np.abs(np.linalg.norm(e, axis=0) - 1).max():.1e}')

head('2b. Share of I1 (E_z) and I2 (E_y, asymmetry) in the focal plane, 750 nm, air, x-polarized')
r = np.linspace(0, 3.0, 3001)
for na in (0.1, 0.5, 0.7, 0.9):
    k, a = 2 * np.pi / L1, np.arcsin(na)
    I0, I1, I2 = (np.asarray(q)[0] for q in compute_integrals(r, np.array([0.0]), k, a, 801))   # shape (nz, nr)
    pk = np.abs(I0[0]) ** 2
    ez = (4 * np.abs(I1) ** 2).max() / pk
    ey = (np.abs(I2) ** 2).max() / pk
    wpar = fwhm(np.r_[-r[::-1], r[1:]], np.r_[(np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2)[::-1], (np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2)[1:]])
    wper = fwhm(np.r_[-r[::-1], r[1:]], np.r_[(np.abs(I0 - I2) ** 2)[::-1], (np.abs(I0 - I2) ** 2)[1:]])
    wsc = vh1 / np.pi * L1 / na
    print(f'NA {na}: max |E_z|^2 = {100 * ez:.2f}% and max |I2|^2 = {100 * ey:.3f}% of the peak; FWHM along the '
          f'polarization {wpar:.4f} µm, across {wper:.4f}, paraxial {wsc:.4f}')

head('2c. Romallosa et al. (2003): FWHM across the axis, NA 0.8, n = 1.3, 750 nm, across the polarization')
xr = np.linspace(-1.0, 1.0, 8001)
print(f'{1000 * fwhm(xr, intensity(beam_field(xr, 0 * xr, 0.750, 0.8, 1.3, model="rw", psi=np.pi / 2, n_theta=801))):.1f} nm '
      f'(paper 472.8 nm)')

k, a = 2 * np.pi * 1.3 / 0.750, np.arcsin(0.8 / 1.3)
rr = np.linspace(0, 1.0, 4001)
I0, I1, I2 = (np.asarray(q)[0] for q in compute_integrals(rr, np.array([0.0]), k, a, 801))
sym = lambda y: (np.r_[-rr[::-1], rr[1:]], np.r_[y[::-1], y[1:]])
print('Eqs. 2 and 3 of the paper as printed read I0 + 2 I2 cos(phi) and I2 sin(phi); Richards and Wolf have cos 2phi, sin 2phi:')
for name, y in (('Richards-Wolf across the polarization, |I0 - I2|^2', np.abs(I0 - I2) ** 2),
                ('Richards-Wolf along the polarization, |I0 + I2|^2 + 4|I1|^2', np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2),
                ('as printed, phi = pi/2: |I0|^2 + |I2|^2', np.abs(I0) ** 2 + np.abs(I2) ** 2),
                ('as printed, phi = 0: |I0 + 2 I2|^2 + 4|I1|^2', np.abs(I0 + 2 * I2) ** 2 + 4 * np.abs(I1) ** 2)):
    print(f'  {name:60s} {1000 * fwhm(*sym(y)):.1f} nm')

head('2d. Gauss law, NA 0.9, air, 750 nm: |div E| / (k max|E|) on a grid near the focus, factor of E_z')
h = 1e-3
gx, gy, gz = np.meshgrid(np.linspace(-0.6, 0.6, 13), np.linspace(-0.6, 0.6, 13), np.linspace(-0.6, 0.6, 13), indexing='ij')
k, a = 2 * np.pi / L1, np.arcsin(0.9)


def field(px, py, pz, fz):
    rr, pp = np.hypot(px, py).ravel(), np.arctan2(py, px).ravel()
    out = []
    for ri, pi_, zi in zip(rr, pp, pz.ravel()):
        I0, I1, I2 = (np.asarray(q).ravel()[0] for q in compute_integrals(np.array([ri]), np.array([zi]), k, a, 401))
        out.append((-1j * (I0 + I2 * np.cos(2 * pi_)), -1j * I2 * np.sin(2 * pi_), fz * I1 * np.cos(pi_)))
    return np.array(out).T.reshape((3,) + px.shape)


sel = (slice(None, None, 3),) * 3
px, py, pz = gx[sel], gy[sel], gz[sel]
for fz, name in ((-2.0, '-2'), (-2.0j, '-2i')):
    div = ((field(px + h, py, pz, fz)[0] - field(px - h, py, pz, fz)[0])
           + (field(px, py + h, pz, fz)[1] - field(px, py - h, pz, fz)[1])
           + (field(px, py, pz + h, fz)[2] - field(px, py, pz - h, fz)[2])) / (2 * h)
    emax = np.abs(field(np.zeros(1), np.zeros(1), np.zeros(1), fz)[0]).max()
    print(f'factor {name:4s}: max |div E| / (k |E(0)|) = {np.abs(div).max() / (k * emax):.1e}')

head('2e. Integral of the mean of |E|^2 over psi, r dr, over a plane z (Section 3, Step 8), 750 nm, air')
print('ratio to 4 (1 - cos alpha) / k^2; |E|^2 at 45 degrees to the polarization is |I0|^2 + |I2|^2 + 2 |I1|^2, its mean')
for na in (0.5, 0.9):
    out = [f'z = {z0:g} µm: {plane_integral(lambda r, z0=z0: intensity(beam_field(r, 0 * r + z0, L1, na, model="rw", psi=np.pi / 4, n_theta=1501))) / (4 * (1 - np.sqrt(1 - na ** 2)) / kk ** 2):.6f}'
           for z0 in (0.0, 2.0)]
    print(f'vector, NA {na}: ' + '; '.join(out))

# ══ Part 3 ══════════════════════════════════════════════════════════════════════════════════════════════════════════
head('3a. Rotation: beam at θ = π is beam 1 at (-x, -z); vector field turns with the beam')
xg, zg = np.meshgrid(np.linspace(-1, 1, 41), np.linspace(-2, 2, 41))
d_par = np.abs(intensity(beam_field(xg, zg, L1, 0.5, theta=np.pi)) - intensity(beam_field(-xg, -zg, L1, 0.5))).max()
Ea = beam_field(xg, zg, L1, 0.8, theta=np.pi, model='rw', psi=0.0)
Eb = beam_field(-xg, -zg, L1, 0.8, model='rw', psi=0.0)
d_vec = np.abs(np.stack([-Eb[0], Eb[1], -Eb[2]]) - Ea).max() / np.abs(Eb).max()
print(f'paraxial intensity: max difference {d_par:.1e};  vector field, (Ex, Ey, Ez) -> (-Ex, Ey, -Ez): {d_vec:.1e}')

zz = np.linspace(-3, 3, 6001)
for rot in ('geometric', 'optical'):
    F = two_color(beam_field(0 * zz, zz, L1, 0.5), beam_field(0 * zz, zz, L2, 0.5, theta=np.pi / 2, rotation=rot))
    print(f'2CE, θ = π/2, NA 0.5, depth of focus with the {rot} rotation: {fwhm(zz, F):.3f} µm (Fig. 3b of Cambaliza & '
          f'Saloma: about 0.67 µm)')

head('3b. 2PE with facing lenses: the standing-wave fringe on the axis')
ac = np.arccos(2 ** -0.25)
for na in (0.5, 0.9):
    kp = 2 * np.pi / LP
    zf = np.linspace(-0.6, 0.6, 24001)
    s_par = LP / 2 / (1 - na ** 2 / 4)
    t_mean = mean_t(lambda t: np.sqrt(t) * (1 + t), na)
    s_vec = LP / 2 / t_mean
    Fp = two_photon(beam_field(0 * zf, zf, LP, na), beam_field(0 * zf, zf, LP, na, theta=np.pi))
    Fv = two_photon(beam_field(0 * zf, zf, LP, na, model='rw'), beam_field(0 * zf, zf, LP, na, theta=np.pi, model='rw'))
    pk = lambda F: zf[1:-1][(F[1:-1] > F[:-2]) & (F[1:-1] > F[2:]) & (zf[1:-1] > 0.05)][0]
    print(f'NA {na}: paraxial spacing lam/(2(1 - NA^2/4)) = {s_par:.4f} µm (engine {pk(Fp):.4f}), central FWHM '
          f'2 arccos(2^-1/4) / (k (1 - NA^2/4)) = {2 * ac / (kp * (1 - na ** 2 / 4)):.4f} (engine {fwhm(zf, Fp):.4f});')
    print(f'        vector <cos theta> = {t_mean:.4f}: spacing lam/(2<cos>) = {s_vec:.4f} µm (engine {pk(Fv):.4f}), '
          f'central FWHM {2 * ac / (kp * t_mean):.4f} (engine {fwhm(zf, Fv):.4f})')

head('3c. 2CE with crossed lenses, NA 0.5, paraxial: across = Airy(750) x axial(656); along = axial(750) x Airy(656)')
x = np.linspace(-3, 3, 60001)
wx = fwhm(x, airy2(2 * np.pi * 0.5 * x / L1) * sinc2(2 * np.pi * 0.25 * x / L2 / 4))
wz = fwhm(x, sinc2(2 * np.pi * 0.25 * x / L1 / 4) * airy2(2 * np.pi * 0.5 * x / L2))
print(f'closed form {wx:.4f} / {wz:.4f} µm; stored 0.763 / 0.670; one-beam spots {vh1 / np.pi * L1 / 0.5:.4f} (750) and '
      f'{vh1 / np.pi * L2 / 0.5:.4f} (656)')

x = np.linspace(-1.5, 1.5, 30001)
kp = 2 * np.pi / LP
u = kp * 0.25 * x
F2 = np.abs(airy2(kp * 0.5 * x) ** 0.5 * np.sign(2 * j1(kp * 0.5 * xs) / (kp * 0.5 * xs))
            + np.exp(1j * (kp * x - u / 4)) * np.sinc(u / 4 / np.pi)) ** 4
print(f'2PE crossed, NA 0.5, on the x axis |2J1(v)/v + exp(i(kx - u/4)) sinc(u/4)|^4: FWHM {fwhm(x, F2):.4f} µm '
      f'(stored 0.256); without the Airy envelope 4 arccos(2^-1/4) / (k (1 - NA^2/4)) = {4 * ac / (kp * 0.9375):.4f}')

head('3d. Crossed lenses fit while alpha <= 45 degrees: NA <= n / sqrt(2)')
for med, n in (('air', 1.0), ('water', 1.33), ('oil', 1.515)):
    print(f'{med}: NA <= {n / np.sqrt(2):.3f}')

head('3e. Lim & Saloma (2002): peak 2CE fluorescence against a displacement d of the focus of L2, NA 0.5, paraxial')
b = lambda lam: (2 * np.pi * 0.5 / lam) ** 2 / 4                 # across: I = 1 - b r^2
c = lambda lam: (2 * np.pi * 0.25 / lam) ** 2 / 48               # along:  I = 1 - c z^2
red = lambda p, q: p * q / (p + q)
cases = [('θ = π, in the focal plane (xc)', red(b(L1), b(L2)), [(0.37, 0.823), (1.33, 0.061)], '-0.588 xc^2 + 0.883'),
         ('θ = π, along the axis (zc)', red(c(L1), c(L2)), [(1.8, 0.909), (2.7, 0.807)], '-0.027 zc^2 + 0.999 (paper -0.027 zc^2 + 0.996)'),
         ('θ = π/2, in the focal plane (xc)', red(b(L1), c(L2)), [(0.37, 0.991), (1.33, 0.889)], '-0.063 xc^2 + 0.999 (paper -0.06 xc^2 + 1)'),
         ('θ = π/2, along the axis (zc)', red(c(L1), b(L2)), [(1.8, 0.845), (2.7, 0.682)], '-0.045 zc^2 + 0.996 (paper -0.045 zc^2 + 0.986)')]
for name, kr, pts, fit in cases:
    kl = kr * L1 ** 2
    est = ', '.join(f'd = {dd} lam1: exp {np.exp(-kl * dd ** 2):.3f} (stored {sv:.3f})' for dd, sv in pts)
    print(f'{name}: kappa_r = {kr:.4f} µm^-2 = {kl:.4f} per lam1^2 (stored fit {fit}); {est}')

head('3f. Lim & Saloma (2003): primary spherical aberration phi, collinear lenses, NA 0.5, paraxial')
var = 1 / 5 - 2 / 4 + 1 / 3 - (1 / 3 - 1 / 2) ** 2
print(f'rms of t^2 - t over the pupil (t = rho^2): {np.sqrt(var):.5f} waves per unit A, A = phi / 100')
for phi in (16, 60):
    A = phi / 100
    z1, z2 = 2 * A * L1 / 0.25, 2 * A * L2 / 0.25
    S = np.exp(-(2 * np.pi * A * np.sqrt(var)) ** 2)
    kz = red(c(L1), c(L2))
    same = S ** 2 * np.exp(-kz * (z1 - z2) ** 2)
    opp = S ** 2 * np.exp(-kz * (z1 + z2) ** 2)
    print(f'phi = {phi}: focal shift 2 A lam / NA^2 = {z1:.3f} µm (750) and {z2:.3f} µm (656); Strehl (Marechal) '
          f'{S:.3f}; peak with equal aberrations {same:.3f}, opposite {opp:.3f}')
A = 0.6
S = np.exp(-(2 * np.pi * A * np.sqrt(var)) ** 2)
print(f'crossed lenses, |phi| = 60: foci {2 * A * L1 / 0.25:.2f} µm along z (L1) and {2 * A * L2 / 0.25:.2f} µm along x '
      f'(L2); peak about S^2 exp(-c1 z1^2 - c2 x2^2) = {S ** 2 * np.exp(-c(L1) * (2 * A * L1 / 0.25) ** 2 - c(L2) * (2 * A * L2 / 0.25) ** 2):.3f}'
      f' (stored 0.07 for both signs)')
X, Z = np.meshgrid(np.linspace(-1.0, 1.0, 101), np.linspace(-5.0, 5.0, 101))
F0 = two_color(beam_field(X, Z, L1, 0.5), beam_field(X, Z, L2, 0.5)).max()
for a1, a2 in ((16, 16), (60, 60), (60, -60)):
    F = two_color(beam_field(X, Z, L1, 0.5, sa=a1), beam_field(X, Z, L2, 0.5, sa=a2))
    i = np.unravel_index(F.argmax(), F.shape)
    print(f'engine phi1 = {a1}, phi2 = {a2}: peak {F.max() / F0:.3f} at z = {Z[i]:+.2f} µm '
          f'(stored: 0.84 at 60/60, 0.07 at 60/-60, z = +0.90 at 16/16)')

head("3g. Linfoot's criteria: F = 2Q - C on every stored row")
num = r'([-+]?\d+\.\d+)'
worst, rows = 0.0, 0
for fn in ('cambaliza2000/high_na/metrics.txt', 'cambaliza2000/high_na/linfoot/linfoot_all.txt', 'linfoot_numbers.txt'):
    txt = open(os.path.join(OUT, fn)).read()
    for f_, c_, q_ in re.findall(rf'F {num}\s+C {num}\s+Q {num}', txt):
        worst, rows = max(worst, abs(float(f_) - (2 * float(q_) - float(c_)))), rows + 1
lines = open(os.path.join(OUT, 'linfoot_numbers.txt')).read().splitlines()
for sig in ('2CE θ = π', '2CE θ = π/2', '2PE θ = π', '2PE θ = π/2'):
    vals = {}
    for ln in lines:
        m = re.match(rf'{re.escape(sig)} ([FCQ]): xc=1 λ1 {num}\s+zc=1.33 λ1 {num}\s+zc=2.7 λ1 {num}', ln)
        if m:
            vals[m.group(1)] = [float(g) for g in m.groups()[1:]]
    if len(vals) == 3:
        for f_, c_, q_ in zip(vals['F'], vals['C'], vals['Q']):
            worst, rows = max(worst, abs(f_ - (2 * q_ - c_))), rows + 1
print(f'{rows} rows; largest |F - (2Q - C)| = {worst:.4f} (rounding of the printed values)')

# ══ Pulses (pulse_derivations.tex) ══════════════════════════════════════════════════════════════════════════════════
DS = os.path.join(OUT, 'cambaliza2000', 'pulses', 'delay_sweep')
vec_w = lambda t: np.sqrt(t) * (1 + t)                       # weight of the vector field on the axis (Part 1, Section 7)
mcos = lambda na, model: 1 - na ** 2 / 4 if model == 'paraxial' else mean_t(vec_w, na)

head('4a. When a focused pulse arrives on the axis (Section 3, Step 2): centroid in time of |E(z_b, t)|^2 over n z_b / c')
print('engine spectral sum, 750 nm, 20 fs, air; <cos theta> is the mean over the cone with the weight of the model')
zb = np.array([0.25, 2.0, 5.0, 15.0])
tc = np.arange(-120.0, 120.0, 20.0 / 60)
for model in ('paraxial', 'rw'):
    for na in (0.1, 0.3, 0.5, 0.7, 0.9):
        dw, cc, E = _fields(0 * zb, zb, L1, 20.0, 240.0, na, 1.0, 0.0, 0.0, 0.0, model, 0.0, None)
        Ft = np.tensordot(cc[:, None] * np.exp(-1j * np.outer(dw, tc)), E, axes=(0, 0))
        It = (np.abs(Ft) ** 2).sum(axis=1) if Ft.ndim == 3 else np.abs(Ft) ** 2
        r = (tc[:, None] * It).sum(0) / It.sum(0) / (zb / C_UM_FS)
        print(f'{model:8s} NA {na:.1f}: <cos theta> = {mcos(na, model):.4f};  centroid at z_b = 0.25, 2, 5, 15 µm: '
              + ', '.join(f'{x:.4f}' for x in r))

head('4b. Facing lenses, 2CE (350-nm pairs) on the axis: stored profiles against I1 I2 exp[-2 ln2 (2z/v - dt)^2 / tau^2]')
print('largest difference over z and the delays 0, 0.5, 1, 1.5, 2 tau, as a fraction of the peak without delay;')
print('v = c / (n <cos theta>) (Section 7), and in brackets v = c / n')
for st, model in (('rw_air', 'rw'), ('paraxial_air', 'paraxial')):
    for na in (0.1, 0.2, 0.3, 0.5, 0.7, 0.9):
        f = np.load(os.path.join(DS, st, f'na{na:g}_coarse.npz'))
        s_ = f['2ce_pi_z_s']
        cw = two_color_cw(0 * s_, s_, na, theta=np.pi, model=model)
        out = []
        for tau in (10, 20, 100):
            P, d = f[f'2ce_pi_z_{tau}_p'][2], f[f'2ce_pi_z_{tau}_d']
            e = []
            for m in (mcos(na, model), 1.0):
                C = np.array([cw * np.exp(-2 * np.log(2) * (2 * s_ * m / C_UM_FS - dl) ** 2 / tau ** 2) for dl in d])
                e.append(np.abs(C / C[0].max() - P).max())
            out.append(f'{tau} fs {e[0]:.3f} ({e[1]:.3f})')
        print(f'{st:13s} NA {na:.1f}: ' + ';  '.join(out))

head('4c. Facing lenses, 100 fs, vector model in air: the focus as a Gaussian of FWHM D (Section 7, Steps 5 to 9)')
for na in (0.1, 0.2, 0.3, 0.5):
    z = np.linspace(-1, 1, 40001) * 9 * L1 / na ** 2
    D = fwhm(z, two_color_cw(0 * z, z, na, theta=np.pi, model='rw'))
    out = []
    for DD, m in ((D, mcos(na, 'rw')), (3.562 * (0.5 / na) ** 2, 1.0)):
        G, zm = C_UM_FS * 100 / (np.sqrt(2) * m), C_UM_FS * 100 / (2 * m)
        out.append((np.exp(-4 * np.log(2) * zm ** 2 / (DD ** 2 + G ** 2)), zm * DD ** 2 / (DD ** 2 + G ** 2),
                    DD * G / np.hypot(DD, G), zm, G))
    t = pd.read_parquet(os.path.join(DS, 'rw_air', f'na{na:g}_coarse.parquet')).query(
        "sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100")
    r1, r0 = t[np.isclose(t.delay_tau, 1.0)].iloc[0], t[np.isclose(t.delay_tau, 0.0)].iloc[0]
    a, b = out
    print(f'NA {na:.1f}: D = {D:.3f} µm, <cos theta> = {mcos(na, "rw"):.4f}, z_m = {a[3]:.2f}, G = {a[4]:.2f} µm | peak at '
          f'dt = tau {a[0]:.3f} (stored {r1.rel_cross:.3f}) | position {a[1]:.2f} ({r1.pos_cross:.2f}) µm | FWHM without '
          f'delay {a[2]:.2f} ({r0.fwhm_cross:.2f}) µm')
    print(f'        with c/n and the scalar D = {3.562 * (0.5 / na) ** 2:.2f} µm: peak {b[0]:.3f}, position {b[1]:.2f}, '
          f'FWHM {b[2]:.2f} µm')

head('4d. Temporal overlap at a fixed point with the factor omega/omega_0 of each photon (Section 6, Step 5), collinear')
w1, w2 = 2 * np.pi * C_UM_FS / L1, 2 * np.pi * C_UM_FS / L2
bb, P12 = 1 / w1 - 1 / w2, w1 * w2
for tau in (5.0, 10.0, 100.0):
    s2 = 4 * np.log(2) / tau ** 2
    t = pd.read_parquet(os.path.join(DS, 'rw_air', 'na0.5_coarse.parquet')).query(
        f"sig == '2ce' and theta == '0' and cut == 'z' and tau == {tau:g}").set_index('delay_tau').rel_cross
    out = []
    for fct in (0.5, 1.0, 2.0):
        dt = fct * tau
        corr = ((1 - s2 / (2 * P12) + s2 ** 2 * dt ** 2 / (4 * P12)) ** 2 + (bb * s2 * dt / 2) ** 2) / (1 - s2 / (2 * P12)) ** 2
        out.append(f'dt = {fct:g} tau: Gaussian {np.exp(-s2 * dt ** 2 / 2):.6f} x {corr:.4f} = '
                   f'{np.exp(-s2 * dt ** 2 / 2) * corr:.6f} (stored {t.loc[fct]:.6f})')
    print(f'{tau:5.0f} fs: ' + ';  '.join(out))
