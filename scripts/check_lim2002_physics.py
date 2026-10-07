r"""Physics checks for every part of the 2CE study: analytic limits, symmetries, identities and
agreement between independent calculations. Each check states what is expected and what is
obtained; the deck shows them on a "Physics checks" slide per part.

    python scripts/check_lim2002_physics.py
    -> output/08_two_color/lim2002/physics_checks.csv   (part, check, expected, obtained, passed)
"""

import csv
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from scipy.special import j1

from mcdo import linfoot
from mcdo.apodization import gaussian
from mcdo.pulsed2ce import C_UM_FS, gate_fwhm, spectrum, two_color_cw, two_color_pulsed
from mcdo.twobeam import beam_field, intensity

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
ROWS = []


def check(part, what, expected, obtained, ok):
    ROWS.append((part, what, expected, obtained, 'yes' if ok else 'NO'))
    print(f'[{"ok" if ok else "FAIL"}] {part}: {what}: expected {expected}; obtained {obtained}', flush=True)


def rows(path):
    paths = [path] + glob.glob(path.replace('.csv', '_*.csv'))
    a = np.concatenate([np.loadtxt(p, delimiter=',', ndmin=2) for p in paths if os.path.exists(p)])
    return a[np.argsort(a[:, 0])]


def at(a, na):
    return a[np.isclose(a[:, 0], na)][0]


# ── Part 1: replication (scalar 2CE, NA 0.5) ──
z = np.linspace(-6, 6, 1201); x = np.zeros_like(z)
I = intensity(beam_field(x, z, 0.75, 0.5)); u = 2 * np.pi / 0.75 * 0.25 * z
e = np.max(np.abs(I / I.max() - np.sinc(u / (4 * np.pi)) ** 2))
check('replication', 'on-axis intensity is sinc²(u/4) (Born & Wolf)', '< 1e-6', f'{e:.1e}', e < 1e-6)
r = np.linspace(1e-4, 2, 801); I = intensity(beam_field(r, 0 * r, 0.75, 0.5)); v = 2 * np.pi / 0.75 * 0.5 * r
e = np.max(np.abs(I / I.max() - (2 * j1(v) / v) ** 2))
check('replication', 'focal-plane intensity is the Airy pattern', '< 1e-6', f'{e:.1e}', e < 1e-6)
lam_e = 1 / (1 / 0.750 + 1 / 0.656)
check('replication', 'energy condition 1/λ_e = 1/λ_1 + 1/λ_2', '350 nm', f'{1000 * lam_e:.0f} nm', abs(lam_e - 0.35) < 0.001)
X, Z = np.meshgrid(np.linspace(-1, 1, 101), np.linspace(-5, 5, 101))
t = intensity(beam_field(X, Z, 0.75, 0.5)) * intensity(beam_field(X, Z, 0.656, 0.5, theta=np.pi / 2))
a = intensity(beam_field(X, Z, 0.75, 0.5)) * intensity(beam_field(X, Z, 0.656, 0.5, theta=np.pi / 2, xc=0.3, zc=0.8))
tn, an = t / t.max(), a / a.max()
F, C, Q = linfoot.fidelity(tn, an), np.mean(an ** 2) / np.mean(tn ** 2), np.mean(an * tn) / np.mean(tn ** 2)
check('replication', 'Linfoot identity F = 2Q − C', '0', f'{abs(F - (2 * Q - C)):.1e}', abs(F - (2 * Q - C)) < 1e-12)
U1 = beam_field(X, Z, 0.7, 0.5); U2 = beam_field(X, Z, 0.7, 0.5, theta=np.pi)
e = np.max(np.abs(np.abs(U1) ** 2 - np.abs(U2[::-1]) ** 2)) / np.max(np.abs(U1) ** 2)
check('replication', 'beam 2 at θ = π is the mirror image of beam 1 in z', '< 1e-9', f'{e:.1e}', e < 1e-9)
xc = np.linspace(0, 1.0, 11) * 0.75
P = []
for d in xc:
    s_ = intensity(beam_field(X, Z, 0.75, 0.5)) * intensity(beam_field(X, Z, 0.656, 0.5, theta=np.pi / 2, xc=d))
    P.append(s_.max())
P = np.array(P) / P[0]; c2 = np.polyfit(xc / 0.75, P, 2)[0]
check('replication', '2CE, θ = π/2: peak against x_c (paper: −0.06 x_c²)', '≈ −0.06', f'{c2:.3f}', abs(c2 + 0.06) < 0.01)

# ── Part 2: vector 2CE, uniform input ──
z = np.linspace(-40, 40, 801)
Ip = intensity(beam_field(0 * z, z, 0.75, 0.1)); Iv = 0.5 * sum(intensity(beam_field(0 * z, z, 0.75, 0.1, model='rw', psi=p))
                                                             for p in (0, np.pi / 2))
e = np.max(np.abs(Ip / Ip.max() - Iv / Iv.max()))
check('vector', 'vector focus reduces to the paraxial one at NA 0.1 (on axis)', '< 1%', f'{100 * e:.2f}%', e < 0.01)
for key, col, exp, lab in (('pi', 3, -1, 'across the axis'), ('pi', 4, -2, 'along the axis')):
    a = rows(os.path.join(D, f'na_breakdown_{key}.csv'))
    sl = np.polyfit(np.log(a[:, 0]), np.log(a[:, col]), 1)[0]
    check('vector', f'20% tolerance {lab} scales with the spot, NA^{exp}', f'NA^{exp}', f'NA^{sl:.2f}', abs(sl - exp) < 0.15)
z = np.linspace(-2, 2, 801)
L = lambda I: np.ptp(z[I >= 0.5 * I.max()])
Id = intensity(beam_field(0 * z, z, 0.75, 0.8, model='debye'))
Iv = 0.5 * sum(intensity(beam_field(0 * z, z, 0.75, 0.8, model='rw', psi=p)) for p in (0, np.pi / 2))
e = abs(L(Id) / L(Iv) - 1)
check('vector', 'scalar Debye focus length equals the vector one (NA 0.8): the small-angle phase sets the difference',
      '< 3%', f'{100 * e:.1f}%', e < 0.03)
x = np.linspace(-1, 1, 401)
Ec = beam_field(x, 0 * x, 0.75, 0.9, model='rw', psi=0.0) + 1j * beam_field(x, 0 * x, 0.75, 0.9, model='rw', psi=np.pi / 2)
Iu = 0.5 * sum(intensity(beam_field(x, 0 * x, 0.75, 0.9, model='rw', psi=p)) for p in (0, np.pi / 2))
e = np.max(np.abs(intensity(Ec) / 2 - Iu)) / Iu.max()
check('vector', 'unpolarized average equals circular polarization', '< 1e-12', f'{e:.1e}', e < 1e-12)

# ── Part 3: Linfoot's criteria against NA ──
fs = sorted(glob.glob(os.path.join(D, 'fidelity', '2ce_pi_na*_n1.npz')))
if len(fs) >= 2:
    a, b = np.load(fs[0]), np.load(fs[-1])
    e = np.max(np.abs(a['F_sca'] - b['F_sca']))
    check('fidelity', 'in units of the spot, scalar 2CE gives the same F map at all NAs', '< 0.02', f'{e:.3f}', e < 0.02)
cache = os.path.join(D, 'linfoot_na')
for f in sorted(glob.glob(os.path.join(cache, '*_scalar_na0.5.npz')))[:2]:
    d = np.load(f); i0, j0 = np.argmin(np.abs(d['zc'])), np.argmin(np.abs(d['xc']))
    ok = abs(d['F'][i0, j0] - 1) < 1e-9 and abs(d['C'][i0, j0] - 1) < 1e-9 and abs(d['Q'][i0, j0] - 1) < 1e-9
    check('fidelity', f'F = C = Q = 1 for the aligned PSF ({os.path.basename(f)[:7]})', '1', f'{d["F"][i0, j0]:.6f}', ok)

# ── Part 4: Gaussian input ──
z = np.linspace(-15, 15, 601)
Iu = intensity(beam_field(0 * z, z, 0.75, 0.5)); Ig = intensity(beam_field(0 * z, z, 0.75, 0.5, apodization=gaussian(1e-4, 0.25)))
e = np.max(np.abs(Iu / Iu.max() - Ig / Ig.max()))
check('gaussian', 'α_t → 0 recovers uniform input', '< 1e-4', f'{e:.1e}', e < 1e-4)
a, g = rows(os.path.join(D, 'na_breakdown_pi.csv')), rows(os.path.join(D, 'na_breakdown_at4_pi.csv'))
r = at(g, 0.5)[3] / at(a, 0.5)[3]
check('gaussian', 'Gaussian focus is wider, so the tolerance is larger (NA 0.5, across)', '> 1', f'{r:.2f}×', r > 1)

# ── Part 5: time delay ──
pd = np.genfromtxt(os.path.join(D, 'phase_delay', 'phase_delay.csv'), delimiter=',', dtype=None, encoding=None, comments='#')
ce = np.array([row[3] for row in pd if row[0] == '2ce'])
check('delay', '2CE peak lost does not depend on the time delay', '0', f'max {ce.max():.1e}%', ce.max() < 1e-9)
pe = [(row[2], row[3]) for row in pd if row[0] == '2pe' and row[1] == 'pi2']
ph = np.array([p for p, _ in pe]); lo = np.array([l for _, l in pe])
e = abs(lo[0] - lo[-1]); s = np.max(np.abs(lo - lo[::-1]))
check('delay', '2PE peak lost is periodic in φ (2π) and symmetric about π', '0', f'{max(e, s):.1e}%', max(e, s) < 1e-6)
tvs = np.loadtxt(os.path.join(D, 'phase_delay', 'time_vs_space.csv'), delimiter=',')
i = np.argmin(np.abs(tvs[:, 0] - 0.7 / C_UM_FS / 2))
check('delay', 'half a period of time delay costs about what a 0.5 λ_{2p} misalignment costs (θ = π/2)', 'within 5 points',
      f'{tvs[i, 2]:.1f}% against {tvs[i, 3]:.1f}%', abs(tvs[i, 2] - tvs[i, 3]) < 5)

# ── Part 6: polarization ──
s_, p_ = rows(os.path.join(D, 'na_breakdown_pols_pi.csv')), rows(os.path.join(D, 'na_breakdown_polp_pi.csv'))
e = np.max(np.abs(s_[:, 4] / p_[:, 4] - 1))
check('polarization', 's–s and p–p give the same tolerance along the axis (θ = π)', '< 1%', f'{100 * e:.2f}%', e < 0.01)
r = at(p_, 0.9)[3] / at(s_, 0.9)[3]
check('polarization', 'tolerance across the axis is wider along the polarization (p–p over s–s, NA 0.9)', '> 1', f'{r:.2f}×', r > 1)
q = rows(os.path.join(D, 'quoted_vs_na_polp_m3.csv'))
check('polarization', 'crossed p–p 2PE beams barely interfere: little peak lost at NA 0.5', '< 2%', f'{at(q, 0.5)[1]:.1f}%',
      at(q, 0.5)[1] < 2)

# ── pulses ──
w, a_, dw = spectrum(0.75, 20.0, t_window=400.0)
E = np.array([beam_field(np.array([0.0]), np.array([0.0]), 2 * np.pi * C_UM_FS / wm, 0.5)[0] for wm in w])
tt = np.linspace(-200, 200, 4001); f = np.array([np.sum(a_ * dw * E * np.exp(-1j * (w - w.mean()) * ti)) for ti in tt])
I = np.abs(f) ** 2; fw = np.ptp(tt[I >= I.max() / 2])
check('pulses', 'pulse duration at the focus equals τ (20 fs)', '20 fs', f'{fw:.1f} fs', abs(fw - 20) < 0.5)
S = two_color_pulsed(np.array([0.0]), np.array([0.0]), 0.5, theta=np.pi / 2, tau1=20.0,
                     delay=np.array([0.0, 20.0]), model='paraxial')
r = S[1, 0] / S[0, 0]
check('pulses', 'overlap at the focus for a time delay τ: exp(−2 ln2) = 0.25', '0.250', f'{r:.3f}', abs(r - 0.25) < 0.01)
zz = np.linspace(-3, 3, 7); Xp, Zp = np.meshgrid(np.linspace(-0.8, 0.8, 5), zz)
p = two_color_pulsed(Xp, Zp, 0.5, tau1=2000.0, model='paraxial'); c = two_color_cw(Xp, Zp, 0.5, model='paraxial')
e = np.max(np.abs(p / p.max() - c / c.max()))
check('pulses', 'long pulses (2 ps) give the continuous-beam PSF', '< 0.5%', f'{100 * e:.2f}%', e < 5e-3)
zg = np.linspace(-8, 8, 161)
g = two_color_pulsed(0 * zg, zg, 0.1, tau1=20.0, model='paraxial', delay=15.0) / two_color_cw(0 * zg, zg, 0.1, model='paraxial')
zc = zg[np.argmax(g)]
check('pulses', 'facing lenses: the pulses meet at z = cΔt/2n (Δt = 15 fs)', f'{C_UM_FS * 7.5:.2f} µm', f'{zc:.2f} µm',
      abs(zc - C_UM_FS * 7.5) < 0.15)

with open(os.path.join(D, 'physics_checks.csv'), 'w', newline='') as fh:
    w_ = csv.writer(fh); w_.writerow(['part', 'check', 'expected', 'obtained', 'passed']); w_.writerows(ROWS)
print(f'{sum(r[4] == "yes" for r in ROWS)} of {len(ROWS)} checks pass')
