"""
Corrected NA-threshold study — redo of the progress report's slides 24–28.

Question: at what NA does scalar (Debye) theory diverge from vector (RW),
and does Gaussian illumination really fail earlier than uniform?

Fix vs the report: the scalar reference is the scalar Debye integral WITH
THE SAME A(θ) as the RW computation (the report compared RW-Gaussian
against a paraxial Gaussian-beam formula — invalid at high NA — and used
circular-polarization quantities that hide the linear-pol anisotropy).

Outputs:
  output/verify_apod_thresholds.png
  printed threshold table (1% / 5% FWHM deviation, RMSE vs NA)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye
from mcdo.apodization import gaussian as gaussian_apod

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

v_arr = np.linspace(0.0, 10.0, 401)


def fwhm_x(x, y):
    half = y.max() / 2.0
    i = np.where(np.diff((y >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [y[i + 1], y[i]], [x[i + 1], x[i]])


def profiles(cfg, apod):
    """Total and Ex-only intensity + scalar, all with the SAME A(θ), normalized."""
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha,
                                   NT, apodization=apod)
    I0, I1, I2 = I0[0], I1[0], I2[0]
    I_full = np.abs(I0) ** 2 + np.abs(I2) ** 2 + 2 * np.abs(I1) ** 2
    I_s = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT,
                       apodization=apod)[0]
    return I_full / I_full.max(), I_s / I_s.max()


illums = {
    'uniform':       None,
    'Gaussian, truncation coefficient 1': 1.0,
    'Gaussian, truncation coefficient 4': 4.0,
}

XNA_vals = np.arange(0.05, 1.26, 0.05)
res = {name: {'dev_full': [], 'rmse_full': []}
       for name in illums}

for xna in XNA_vals:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    for name, at in illums.items():
        apod = None if at is None else gaussian_apod(at, cfg.sin2_alpha)
        I_full, I_s = profiles(cfg, apod)
        f_s = fwhm_x(v_arr, I_s)
        res[name]['dev_full'].append(100 * abs(fwhm_x(v_arr, I_full) / f_s - 1))
        res[name]['rmse_full'].append(np.sqrt(np.mean((I_full - I_s) ** 2)))

print("Thresholds: NA where |FWHM(vector) − FWHM(scalar, same A)| exceeds")
print(f"{'illumination':<40} {'intensity':<10} {'>1%':>6} {'>5%':>6}")
for name in illums:
    for cut in ['full']:
        dev = np.array(res[name][f'dev_{cut}'])
        t1 = XNA_vals[np.argmax(dev > 1.0)] if (dev > 1.0).any() else np.nan
        t5 = XNA_vals[np.argmax(dev > 5.0)] if (dev > 5.0).any() else np.nan
        print(f"{name:<16} {cut:<6} {t1:>6.2f} {t5:>6.2f}")

print("\nFWHM at X_NA=1.17 (sin alpha = 0.9):")
for name, at in illums.items():
    cfg = SimConfig(lam_c=LAM, X_NA=1.17, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    apod = None if at is None else gaussian_apod(at, cfg.sin2_alpha)
    I_full, I_s = profiles(cfg, apod)
    print(f"  {name:<40} full={fwhm_x(v_arr, I_full):.3f}  "
          f"scalar={fwhm_x(v_arr, I_s):.3f} v-units "
          f"(full dev {100*abs(fwhm_x(v_arr, I_full)/fwhm_x(v_arr, I_s)-1):.1f}%)")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(20.5, 6.8))
fig.suptitle('Vector against scalar Debye with the same pupil amplitude, 750 nm',
             fontsize=13)

ax = axes[0]
for name, style in zip(illums, ['k-o', 'C0--s', 'C3:^']):
    ax.plot(XNA_vals, res[name]['dev_full'], style, ms=6, lw=2.0, label=name)
ax.axhline(1, color='gray', lw=1.2, ls=':')
ax.axhline(5, color='gray', lw=1.2, ls='--')
ax.set_yscale('log'); ax.set_ylim(1e-3, 60)
ax.set_xlabel('Numerical aperture'); ax.set_ylabel('FWHM deviation from scalar (%)')
ax.set_title('(a) Focal-width deviation from scalar theory', fontsize=11); ax.legend(fontsize=9)

ax = axes[1]
for name, style in zip(illums, ['k-o', 'C0--s', 'C3:^']):
    ax.plot(XNA_vals, res[name]['rmse_full'], style, ms=6, lw=2.0, label=name)
ax.axhline(0.01, color='gray', lw=1.2, ls=':')
ax.axhline(0.05, color='gray', lw=1.2, ls='--')
ax.set_yscale('log'); ax.set_ylim(1e-5, 0.5)
ax.set_xlabel('Numerical aperture'); ax.set_ylabel('RMSE against scalar')
ax.set_title('(b) RMSE against the scalar prediction', fontsize=11)
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'verify_apod_thresholds.png')
from mcdo.figio import save_panels
save_panels(fig, fig.axes, os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization', 'panels'), 'verify_apod_thresholds')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
