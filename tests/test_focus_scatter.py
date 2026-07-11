"""Phase-6b tests — focused beam through a slab, tied to the validation rungs.

The clear limit recovers the focus, energy is conserved exactly, the ballistic
fraction follows the analytic (cone-averaged) Beer-Lambert law, and the
thin-slab scatter counts follow the free-path Poisson law (single-scatter Born).
"""

import numpy as np

from mcdo import SimConfig
from mcdo.focus_scatter import (focal_scatter_trial, split_trial,
                                ballistic_fraction_analytic)
from mcdo.montecarlo import sample_photons
from mcdo.scatter import propagate_slab, hg_sample, rotate

cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=601)
X = np.linspace(-1.5, 1.5, 81)
HE = np.linspace(0.0, 25.0, 41)
NX, NH = X.size, HE.size - 1


def _trial(mu_s, d=20.0, g=0.9, seed=0, npho=40000, mu_a=0.0):
    v = focal_scatter_trial(cfg, npho, mu_s, g, d, X, HE,
                            rng=np.random.default_rng(seed), mu_a=mu_a)
    return split_trial(v, NX, NH)


def test_clear_limit_recovers_core_no_halo():
    """RUNG 1: μ_s=0 → core == clear focus (peak ratio 1), no scattered light."""
    d = _trial(0.0)
    assert abs(float(d['peak_atten']) - 1.0) < 1e-6
    assert d['partition'][1] == 0.0 and d['partition'][2] == 0.0   # no fwd/back scatter
    assert abs(d['partition'][0] - 1.0) < 1e-12                    # all ballistic


def test_energy_conserved():
    """RUNG 3: ballistic + forward + back + absorbed = 1 to machine precision."""
    for mu_s in (0.01, 0.05, 0.1):
        assert abs(_trial(mu_s)['partition'].sum() - 1.0) < 1e-9


def test_beer_lambert_ballistic_fraction():
    """RUNG 2: MC ballistic fraction = analytic ⟨exp(−μ_s d/cosθ)⟩."""
    for mu_s in (0.02, 0.05, 0.1):
        mc = float(_trial(mu_s, npho=80000)['partition'][0])
        an = ballistic_fraction_analytic(cfg, mu_s, 20.0)
        assert abs(mc - an) < 0.012


def test_absorption_adds_a_partition_and_still_conserves():
    """With μ_a>0 some energy is absorbed; the four parts still sum to 1."""
    d = _trial(0.05, mu_a=0.02)
    assert d['partition'][3] > 0.0
    assert abs(d['partition'].sum() - 1.0) < 1e-9


def _poisson_refs(mu_s, d, ngrid=4001):
    """Analytic ⟨e^-μ_sL⟩ and ⟨μ_sL e^-μ_sL⟩ over the launcher density."""
    trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    th = np.linspace(0.0, cfg.alpha, ngrid)
    p = np.sqrt(np.cos(th)) * np.sin(th)
    L = d / np.cos(th)
    norm = trapz(p, th)
    P0 = trapz(p * np.exp(-mu_s * L), th) / norm
    P1 = trapz(p * mu_s * L * np.exp(-mu_s * L), th) / norm
    return P0, P1


def test_thin_slab_scatter_counts_are_poisson():
    """RUNG 4 (Born thin limit): scatter counts follow the free-path Poisson
    law — P(0)=⟨e^-μ_sL⟩, P(1)=⟨μ_sL e^-μ_sL⟩ (L=d/cosθ), and double
    scattering is a τ²-suppressed minority."""
    d_slab, mu_s = 20.0, 0.05 / 20.0                     # τ = 0.05
    kx, ky, kz, w = sample_photons(cfg, 60000, rng=np.random.default_rng(11))
    mu = np.vstack([kx, ky, kz]) / cfg.k_c
    pos = (-d_slab / mu[2])[None, :] * mu
    _, _, nsc, _, _ = propagate_slab(pos, mu, mu_s, 0.9, (-d_slab, 0.0), 400,
                                     np.random.default_rng(12))
    P0_an, P1_an = _poisson_refs(mu_s, d_slab)
    assert abs(np.mean(nsc == 0) - P0_an) < 0.005
    assert abs(np.mean(nsc == 1) - P1_an) < 0.005
    assert np.mean(nsc >= 2) < 0.1 * np.mean(nsc == 1)


def test_diffusion_similarity_relation():
    """RUNG 5 (diffusion thick limit): in the multiple-scattering regime only the
    reduced coefficient μ_s' = μ_s(1−g) matters (transport similarity) — a
    forward-peaked slab (μ_s, g=0.9) transmits like an isotropic one at matched
    μ_s' (μ_s/10, g=0). Pencil beam, non-absorbing slab, N=μ_s'd=8."""
    d, npho = 100.0, 8000

    def transmit(mu_s, g, seed):
        pos = np.zeros((3, npho)); mu = np.zeros((3, npho)); mu[2] = 1.0
        pos2, _, _, w, _ = propagate_slab(pos, mu, mu_s, g, (0.0, d), 3000,
                                          np.random.default_rng(seed))
        return w[pos2[2] > 0.5 * d].sum() / npho

    mu_sp = 8.0 / d                              # μ_s' giving N = 8
    T_iso = transmit(mu_sp, 0.0, 20)
    T_fwd = transmit(mu_sp / (1.0 - 0.9), 0.9, 21)
    assert abs(T_iso - T_fwd) < 0.02             # similarity holds in the thick limit
    assert 0.12 < T_iso < 0.24                   # near diffusion T_d(8) ≈ 0.18


def test_diffusion_greens_mu_eff():
    """RUNG 6 (MCML/Farrell-Patterson benchmark): the isotropic point-source
    fluence decays as φ(r)∝exp(−μ_eff r)/r with μ_eff=√(3 μ_a μ_tr) in the
    diffusion regime (μ_a ≪ μ_s'). Tests absorption + the diffusion propagator,
    independent of the slab/focus geometry."""
    mu_s, mu_a, g, npho = 1.0, 0.05, 0.0, 20000   # albedo 0.95 (diffusive)
    mu_tr = mu_a + mu_s * (1 - g)
    edges = np.linspace(0.0, 15.0, 61); ctr = 0.5 * (edges[:-1] + edges[1:])
    fit = (ctr >= 3.0) & (ctr <= 10.0)
    rng = np.random.default_rng(5)
    pos = np.zeros((3, npho))
    cost = 2 * rng.random(npho) - 1; sint = np.sqrt(np.clip(1 - cost ** 2, 0, 1))
    ph = 2 * np.pi * rng.random(npho)
    mu = np.vstack([sint * np.cos(ph), sint * np.sin(ph), cost])
    w = np.ones(npho); alive = np.ones(npho, bool); fl = np.zeros(ctr.size)
    mu_t = mu_s + mu_a; albedo = mu_s / mu_t
    for _ in range(1500):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        s = -np.log(rng.random(idx.size)) / mu_t
        p0 = pos[:, idx]
        rmid = np.sqrt(((p0 + 0.5 * s * mu[:, idx]) ** 2).sum(0))
        b = np.digitize(rmid, edges) - 1; ok = (b >= 0) & (b < fl.size)
        np.add.at(fl, b[ok], (w[idx] * s)[ok])
        pos[:, idx] = p0 + s * mu[:, idx]; w[idx] *= albedo
        ct, pph = hg_sample(g, idx.size, rng); mu[:, idx] = rotate(mu[:, idx], ct, pph)
        low = w[idx] < 1e-4
        if low.any():
            li = idx[low]; surv = rng.random(li.size) < 0.1
            w[li] = np.where(surv, w[li] * 10.0, 0.0); alive[li[~surv]] = False
    V = 4.0 / 3.0 * np.pi * (edges[1:] ** 3 - edges[:-1] ** 3)
    phi = fl / (V * npho)
    slope = np.polyfit(ctr[fit], np.log(np.clip(ctr * phi, 1e-30, None))[fit], 1)[0]
    mu_eff_mc, mu_eff_an = -slope, np.sqrt(3 * mu_a * mu_tr)
    assert abs(mu_eff_mc - mu_eff_an) / mu_eff_an < 0.05


def test_pure_absorber_transmittance_analytic():
    """Non-trivial energy check (beyond the exhaustive-partition identity):
    for a purely absorbing slab (μ_s=0) every photon exits ballistically with
    weight e^{-μ_a d/cosθ}, so the transmitted fraction must equal the analytic
    cone average ⟨e^{-μ_a d/cosθ}⟩ — this validates the absorption path-length
    bookkeeping independently."""
    d_slab, mu_a = 20.0, 0.03
    kx, ky, kz, w = sample_photons(cfg, 60000, rng=np.random.default_rng(13))
    mu = np.vstack([kx, ky, kz]) / cfg.k_c
    pos = (-d_slab / mu[2])[None, :] * mu
    _, _, nsc, weight, _ = propagate_slab(pos, mu, 0.0, 0.9, (-d_slab, 0.0),
                                          400, np.random.default_rng(14),
                                          mu_a=mu_a)
    assert np.all(nsc == 0)                              # no scattering events
    T_an, _ = _poisson_refs(mu_a, d_slab)                # same ⟨e^-μL⟩ form
    assert abs(weight.mean() - T_an) < 0.002
