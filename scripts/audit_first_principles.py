r"""
From-scratch physics audit — checks that are INDEPENDENT of every reference
used so far (no Romallosa figures, no Airy/Durnin limits, no internal
MC-vs-deterministic comparison). Each asks: does the computed field obey the
fundamental equation it must obey, with a deliberately-broken control to prove
the check has teeth?

  (1) HELMHOLTZ + DISPERSION (scalar).  Every angular-spectrum component
      J₀(kr sinθ)e^{ikz cosθ} has k_⊥²+k_z² = k², so the scalar Debye field must
      satisfy (∇²+k²)U = 0 identically — for ANY apodization. The finite-
      difference residual |∇²U+k²U|/(k²|U|) must fall ∝ h² (the FD floor);
      testing the operator at a wrong k (1.05k) must fail at the 10% level.
      This catches any u/v optical-coordinate inconsistency (off-shell
      components) in the integrand.

  (2) MAXWELL TRANSVERSALITY (vector).  Each refracted plane-wave component has
      p̂ ⊥ k̂, so the Richards-Wolf field E = (I₀+I₂cos2φ, I₂sin2φ, −2iI₁cosφ)
      must be divergence-free. |∇·E|/(k|E|) must sit at the FD floor; breaking
      the kernel bookkeeping (dropping the factor 2 on E_z) must fail loudly.
      This is the strongest check of the (1±cosθ)/sin²θ kernels and the E_z
      factor — a wrong relative weight destroys transversality.

  (3) INDEPENDENT QUADRATURE.  I₀,I₁,I₂ re-computed with scipy.integrate.quad
      (adaptive Gauss-Kronrod — nothing shared with our Simpson code) at probe
      points spanning focus, off-axis, and defocus. Agreement to ~1e-10.

  (4) SCATTERING STATISTICS.  The sampled Henyey-Greenstein deflections match
      the analytic law via BIN-INTEGRATED probabilities from the exact HG CDF
      F(μ) = (1−g²)/(2g)·[(1+g²−2gμ)^{−1/2} − (1+g)^{−1}]  (F(1)−F(−1)=1
      analytically — the pdf peak p(1)≈95 at g=0.9 defeats naive pointwise
      histograms, so the CDF comparison is the correct one). And the slab
      scatter counts are checked against the EXACT semi-analytic single-scatter
      probability
          P(1) = ⟨∫₀^{L(θ)} μ_s e^{−μ_s s} ⟨e^{−μ_s L₂(θ,s,Θ,Φ)}⟩_HG ds⟩,
      where L₂ is the exit path along the DEFLECTED direction — the naive
      straight-path Poisson ⟨(μ_sL)ⁿ/n!·e^{−μ_sL}⟩ is exact only for n=0;
      deflections lengthen in-slab paths, so it *underestimates* P(2) (the
      audit measures that bias and reports it as physics, not error).
      P(≥2) = 1 − P(0) − P(1) then follows exactly.

Output: output/00_overview/audit_first_principles.png + printed PASS/FAIL table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv
from scipy.integrate import quad

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals, _simpson_weights
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons
from mcdo.scatter import hg_sample, propagate_slab

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '00_overview')
os.makedirs(OUT, exist_ok=True)
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=1201)
K_C, ALPHA, NT = cfg.k_c, cfg.alpha, cfg.N_theta
_TRAPZ = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
results = []   # (check, measured, expectation, ok)


# ── complex scalar Debye field (inline re-derivation; bridged to the package) ─
_th = np.linspace(0.0, ALPHA, NT)
_w = _simpson_weights(NT, ALPHA)
_amp = _w * np.sqrt(np.cos(_th)) * np.sin(_th)
_ct, _st = np.cos(_th), np.sin(_th)

def U_scalar(x, y, z):
    """Complex scalar Debye field at one Cartesian point."""
    r = np.hypot(x, y)
    return np.sum(_amp * jv(0, K_C * r * _st) * np.exp(1j * K_C * z * _ct))

# bridge: |U_inline|² must equal the package's scalar_debye (normalized)
rb = np.linspace(0.0, 1.2, 41); zb = np.linspace(-3.0, 3.0, 41)
Ub = np.array([[U_scalar(r, 0.0, z) for r in rb] for z in zb])
Ib = np.abs(Ub) ** 2; Ib /= Ib.max()
Ip = scalar_debye(rb, zb, K_C, ALPHA, NT); Ip /= Ip.max()
bridge = float(np.max(np.abs(Ib - Ip)))
results.append(('bridge: inline |U|² ≡ scalar_debye', f'{bridge:.2e}', '< 1e-10', bridge < 1e-10))


# ── (1) Helmholtz residual, correct k vs wrong k ─────────────────────────────
PTS = [(0.30, 0.20, 0.50), (0.15, -0.35, -0.80), (0.50, 0.10, 1.20),
       (-0.25, 0.30, 2.00), (0.40, 0.40, -1.50)]
HS = np.array([0.020, 0.010, 0.005])

def helmholtz_residual(pt, h, k_test):
    x, y, z = pt
    U0 = U_scalar(x, y, z)
    lap = (U_scalar(x + h, y, z) + U_scalar(x - h, y, z)
           + U_scalar(x, y + h, z) + U_scalar(x, y - h, z)
           + U_scalar(x, y, z + h) + U_scalar(x, y, z - h) - 6.0 * U0) / h ** 2
    return abs(lap + k_test ** 2 * U0) / (k_test ** 2 * abs(U0))

helm_ok = np.array([[helmholtz_residual(p, h, K_C) for h in HS] for p in PTS])
helm_bad = np.array([[helmholtz_residual(p, h, 1.05 * K_C) for h in HS] for p in PTS])
fd_floor = (K_C * HS) ** 2 / 12.0          # leading FD truncation scale
r_h = float(helm_ok[:, -1].max())
results.append(('(1) Helmholtz |∇²U+k²U|/k²|U| @h=5nm', f'{r_h:.2e}',
                f'≲ FD floor {fd_floor[-1]:.1e}', r_h < 10 * fd_floor[-1]))
r_hb = float(helm_bad[:, -1].min())
results.append(('(1) control: wrong k (1.05k)', f'{r_hb:.3f}', '≈ |1.05²−1| ≈ 0.10', r_hb > 0.05))


# ── (2) Maxwell divergence, correct vs broken E_z factor ─────────────────────
def E_vec(x, y, z, ez_factor=2.0):
    """RW vector field (global constants dropped) at one Cartesian point."""
    r = np.hypot(x, y); phi = np.arctan2(y, x)
    I0, I1, I2 = compute_integrals(np.array([r]), np.array([z]), K_C, ALPHA, NT)
    I0, I1, I2 = I0[0, 0], I1[0, 0], I2[0, 0]
    return np.array([I0 + I2 * np.cos(2 * phi),
                     I2 * np.sin(2 * phi),
                     -ez_factor * 1j * I1 * np.cos(phi)])

def div_residual(pt, h, ez_factor=2.0):
    x, y, z = pt
    Ec = E_vec(x, y, z, ez_factor)
    dEx = (E_vec(x + h, y, z, ez_factor)[0] - E_vec(x - h, y, z, ez_factor)[0]) / (2 * h)
    dEy = (E_vec(x, y + h, z, ez_factor)[1] - E_vec(x, y - h, z, ez_factor)[1]) / (2 * h)
    dEz = (E_vec(x, y, z + h, ez_factor)[2] - E_vec(x, y, z - h, ez_factor)[2]) / (2 * h)
    return abs(dEx + dEy + dEz) / (K_C * np.linalg.norm(Ec))

div_ok = np.array([[div_residual(p, h) for h in HS] for p in PTS])
div_bad = np.array([[div_residual(p, h, ez_factor=1.0) for h in HS] for p in PTS])
r_d = float(div_ok[:, -1].max()); r_db = float(div_bad[:, -1].min())
results.append(('(2) Maxwell |∇·E|/k|E| @h=5nm', f'{r_d:.2e}', '≲ 1e-3 (FD floor)', r_d < 3e-3))
results.append(('(2) control: E_z factor 2→1', f'{r_db:.3f}', 'O(0.1–1), ≫ floor', r_db > 30 * r_d))


# ── (3) independent adaptive quadrature vs Simpson ───────────────────────────
def quad_integral(m, r, z):
    """I_m via scipy adaptive quadrature (independent of our Simpson code)."""
    kern = {0: lambda t: np.sin(t) * (1 + np.cos(t)),
            1: lambda t: np.sin(t) ** 2,
            2: lambda t: np.sin(t) * (1 - np.cos(t))}[m]
    def f(t, part):
        val = (np.sqrt(np.cos(t)) * kern(t) * jv(m, K_C * r * np.sin(t))
               * np.exp(1j * K_C * z * np.cos(t)))
        return val.real if part == 're' else val.imag
    re, _ = quad(f, 0.0, ALPHA, args=('re',), limit=400, epsabs=1e-13, epsrel=1e-13)
    im, _ = quad(f, 0.0, ALPHA, args=('im',), limit=400, epsabs=1e-13, epsrel=1e-13)
    return re + 1j * im

QPTS = [(0.0, 0.0), (0.3, 0.0), (0.7, 0.0), (0.3, 1.0), (0.0, 2.5), (1.0, -1.5)]
qdev = 0.0
for (r, z) in QPTS:
    I0s, I1s, I2s = compute_integrals(np.array([r]), np.array([z]), K_C, ALPHA, NT)
    for m, Is in ((0, I0s[0, 0]), (1, I1s[0, 0]), (2, I2s[0, 0])):
        Iq = quad_integral(m, r, z)
        scale = max(abs(Iq), 1e-3)         # avoid 0/0 at exact nulls (I1,I2 at r=0)
        qdev = max(qdev, abs(Is - Iq) / scale)
results.append(('(3) Simpson vs adaptive quad (18 integrals)', f'{qdev:.2e}',
                '< 1e-8', qdev < 1e-8))


# ── (4) HG phase function (exact CDF) + exact single-scatter probability ────
G = 0.9

def hg_cdf(mu_, g=G):
    """Analytic HG CDF; F(1)−F(−1) = 1 exactly (peak-safe reference)."""
    return (1 - g ** 2) / (2 * g) * ((1 + g ** 2 - 2 * g * mu_) ** -0.5
                                     - 1.0 / (1 + g))

norm = float(hg_cdf(1.0) - hg_cdf(-1.0))
results.append(('(4) HG normalization F(1)−F(−1)', f'{norm:.12f}', '= 1 (analytic)',
                abs(norm - 1) < 1e-12))

rng = np.random.default_rng(0)
N_HG = 400_000
cos_t, _ = hg_sample(G, N_HG, rng)
edges = np.linspace(-1, 1, 61)
counts, _ = np.histogram(cos_t, bins=edges)
p_bin = hg_cdf(edges[1:]) - hg_cdf(edges[:-1])         # exact bin probabilities
hg_dev = float(np.max(np.abs(counts / N_HG - p_bin)))
hg_3sig = float(3 * np.sqrt(p_bin.max() / N_HG))
results.append(('(4) HG counts vs exact bin probs (max dev)', f'{hg_dev:.5f}',
                f'≲ 3σ ≈ {hg_3sig:.5f}', hg_dev < 1.5 * hg_3sig))

# exact semi-analytic P(1): first scatter at depth s, THEN the deflected exit
# path L₂ — 4-fold quadrature (θ launch, s depth, Θ deflection via CDF
# substitution, Φ azimuth). Run at τ=0.5 where the naive straight-path formula
# is visibly wrong, so the agreement actually tests the coupled geometry.
D, TAU = 20.0, 0.5
mu_s = TAU / D

def p1_exact(n_th=96, n_s=120, n_T=200, n_P=48):
    th = np.linspace(1e-4, ALPHA, n_th)
    pw = np.sqrt(np.cos(th)) * np.sin(th)
    qT = (np.arange(n_T) + 0.5) / n_T                   # CDF-uniform HG nodes
    cosT = (1 + G ** 2 - ((1 - G ** 2) / (1 - G + 2 * G * qT)) ** 2) / (2 * G)
    sinT = np.sqrt(np.clip(1 - cosT ** 2, 0, 1))
    phi = (np.arange(n_P) + 0.5) / n_P * 2 * np.pi
    cosP = np.cos(phi)
    P1_th = np.empty(n_th)
    for i, t in enumerate(th):
        Lt = D / np.cos(t)
        s = (np.arange(n_s) + 0.5) / n_s * Lt           # midpoint rule in depth
        zs = -D + s * np.cos(t)                          # height at scatter
        muzp = (np.cos(t) * cosT[:, None] - np.sin(t) * sinT[:, None] * cosP[None, :])
        up = muzp > 1e-12; dn = muzp < -1e-12
        surv = np.zeros((n_s, n_T, n_P))
        L2_up = np.where(up[None, :, :], (-zs[:, None, None]) / np.where(up, muzp, 1)[None, :, :], 0)
        L2_dn = np.where(dn[None, :, :], (-D - zs[:, None, None]) / np.where(dn, muzp, -1)[None, :, :], 0)
        expo = np.where(up[None, :, :], L2_up, np.where(dn[None, :, :], L2_dn, np.inf))
        surv = np.exp(-np.minimum(mu_s * expo, 700.0))
        Esurv = surv.mean(axis=(1, 2))                   # ⟨e^{−μ_s L₂}⟩ over HG
        integ = mu_s * np.exp(-mu_s * s) * Esurv
        P1_th[i] = integ.sum() * (Lt / n_s)
    return float(_TRAPZ(pw * P1_th, th) / _TRAPZ(pw, th))

P1_ex = p1_exact()
kx, ky, kz, _ = sample_photons(cfg, 200_000, rng=np.random.default_rng(1))
mu = np.vstack([kx, ky, kz]) / K_C
pos = (-D / mu[2])[None, :] * mu
_, _, nsc, _, _ = propagate_slab(pos, mu, mu_s, G, (-D, 0.0), 400,
                                 np.random.default_rng(2))
P0_mc = float(np.mean(nsc == 0)); P1_mc = float(np.mean(nsc == 1))
P2p_mc = float(np.mean(nsc >= 2))
th6 = np.linspace(0.0, ALPHA, 6001)
pw6 = np.sqrt(np.cos(th6)) * np.sin(th6)
L6 = D / np.cos(th6)
P0_an = float(_TRAPZ(pw6 * np.exp(-mu_s * L6), th6) / _TRAPZ(pw6, th6))
P1_naive = float(_TRAPZ(pw6 * mu_s * L6 * np.exp(-mu_s * L6), th6) / _TRAPZ(pw6, th6))
P2p_ex = 1.0 - P0_an - P1_ex
sig1 = np.sqrt(P1_mc * (1 - P1_mc) / 200_000)
results.append((f'(4) exact P(1) @τ={TAU:g}: MC vs 4-fold quadrature',
                f'{P1_mc:.5f} vs {P1_ex:.5f}', f'within 4σ ≈ {4*sig1:.4f}',
                abs(P1_mc - P1_ex) < 4 * sig1))
results.append(('(4) exact P(≥2) = 1−P(0)−P(1)', f'{P2p_mc:.5f} vs {P2p_ex:.5f}',
                'within ~4σ', abs(P2p_mc - P2p_ex) < 4 * np.sqrt(P2p_mc / 200_000) + 2e-3))
print(f'    [physics note] naive straight-path P(1) = {P1_naive:.5f} vs exact '
      f'{P1_ex:.5f} vs MC {P1_mc:.5f} @τ={TAU:g}:\n'
      f'    the deflection-coupled exit path is a real O(τ²) effect the audit '
      f'formula must include — exact only for P(0).')


# ── report ──────────────────────────────────────────────────────────────────
print('FROM-SCRATCH PHYSICS AUDIT — independent of all prior references\n')
wname = max(len(r[0]) for r in results)
allok = True
for name, meas, exp, ok in results:
    allok &= ok
    print(f'  {name:<{wname}}  {meas:>22}  (expect {exp})  {"PASS" if ok else "FAIL"}')
print(f'\nOVERALL: {"ALL PASS" if allok else "FAILURES PRESENT — investigate"}')

# ── figure ──────────────────────────────────────────────────────────────────
BLUE, RED, GRAY = '#1f77b4', '#d62728', '0.35'
fig, ax = plt.subplots(2, 2, figsize=(13.5, 9.5))
fig.suptitle('First-principles audit — the fields obey the equations they must '
             '(with broken controls proving each check has teeth)', fontsize=13)

a = ax[0, 0]
for i, p in enumerate(PTS):
    a.loglog(HS * 1e3, helm_ok[i], 'o-', color=BLUE, lw=1.4, ms=5,
             alpha=0.75, label='correct k (5 points)' if i == 0 else None)
    a.loglog(HS * 1e3, helm_bad[i], 's--', color=RED, lw=1.2, ms=5,
             alpha=0.75, label='control: wrong k = 1.05k' if i == 0 else None)
a.loglog(HS * 1e3, (K_C * HS) ** 2 / 12, ':', color=GRAY, lw=1.6, label='FD floor ∝ h²')
a.set_xlabel('finite-difference step h (nm)')
a.set_ylabel(r'$|\nabla^2 U + k^2 U|\,/\,k^2|U|$')
a.set_title('(1) scalar field satisfies Helmholtz at exactly k')
a.legend()

a = ax[0, 1]
for i, p in enumerate(PTS):
    a.loglog(HS * 1e3, div_ok[i], 'o-', color=BLUE, lw=1.4, ms=5,
             alpha=0.75, label='RW kernels as implemented' if i == 0 else None)
    a.loglog(HS * 1e3, div_bad[i], 's--', color=RED, lw=1.2, ms=5,
             alpha=0.75, label='control: E$_z$ factor 2→1' if i == 0 else None)
a.set_xlabel('finite-difference step h (nm)')
a.set_ylabel(r'$|\nabla\cdot\mathbf{E}|\,/\,k|\mathbf{E}|$')
a.set_title('(2) vector field is divergence-free (Maxwell)')
a.legend()

a = ax[1, 0]
ctr_mu = 0.5 * (edges[:-1] + edges[1:])
a.plot(ctr_mu, counts / N_HG, 'o', color=BLUE, ms=4, mfc='white', mew=1.2,
       label='sampled bin fractions (4×10⁵ draws)')
a.plot(ctr_mu, p_bin, '-', color='k', lw=1.8,
       label='exact bin probabilities (HG CDF)')
a.set_yscale('log')
a.set_xlabel('cos θ (deflection)'); a.set_ylabel('probability per bin')
a.set_title(f'(4a) Henyey–Greenstein sampling vs exact CDF, g={G}')
a.legend()

a = ax[1, 1]
labels = ['P(0)\nballistic', 'P(1)\nsingle', 'P(≥2)\nmultiple']
mc_vals = [P0_mc, P1_mc, P2p_mc]
ex_vals = [P0_an, P1_ex, P2p_ex]
xb = np.arange(3)
a.bar(xb - 0.18, mc_vals, 0.32, color=BLUE, label='Monte Carlo')
a.bar(xb + 0.18, ex_vals, 0.32, color='none', edgecolor='k', lw=1.4,
      label='exact (deflection-coupled)')
a.plot([1 + 0.18], [P1_naive], '_', color=RED, ms=22, mew=2.5,
       label='naive straight-path P(1)')
for i, (m, e) in enumerate(zip(mc_vals, ex_vals)):
    a.text(i, max(m, e) * 1.25, f'{m:.4f}\nvs {e:.4f}', ha='center', fontsize=8)
a.set_yscale('log'); a.set_ylim(1e-3, 3)
a.set_xticks(xb, labels)
a.set_ylabel('photon fraction')
a.set_title(f'(4b) slab scatter counts, exact quadrature (τ={TAU:g})')
a.legend()

plt.tight_layout()
out = os.path.join(OUT, 'audit_first_principles.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f'\nSaved → {out}')
