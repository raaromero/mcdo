r"""Cambaliza & Saloma (2000) with optical pulses at high NA: widths of the 2PE and 2CE responses against NA.

Vector (Richards-Wolf) focus, air and water, circular pupils, θ = 0, π/2, π; both beams polarized along y, as in
cambaliza2000_high_na.py. Transform-limited Gaussian pulses, zero delay; τ = 20 and 10 fs, continuous beams for
reference. 2CE: ∫ I₁ I₂ dt (λ₁ = 0.750 µm on L1, λ₂ = 0.656 µm on L2). 2PE: ∫ |E₁ + E₂|⁴ dt (both at 0.700 µm).
Width: FWHM of the central peak, transverse (x) and axial (z, DOF).

    python scripts/cambaliza2000_pulses_high_na.py [--rerun]
    -> output/08_two_color/cambaliza2000/pulses/high_na/{widths.csv, dof_pi.png}
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
import matplotlib.ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.twobeam import beam_field, two_color, two_photon, intensity
from mcdo.pulsed2ce import _fields, C_UM_FS

_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'high_na')
os.makedirs(OUT, exist_ok=True)
L1, L2, LP = 0.750, 0.656, 0.700
PSI = np.pi / 2                                                # polarization along y for both beams
THETAS = (0.0, np.pi / 2, np.pi)
TAUS = (20.0, 10.0)
MEDIA = ((1.0, np.round(np.arange(0.2, 0.951, 0.05), 3)), (1.33, np.round(np.arange(0.2, 1.251, 0.05), 3)))


def fwhm(s, y):
    """FWHM of the central peak (at s = 0), normalized to its value at s = 0."""
    i0 = int(np.argmin(np.abs(s)))
    y = y / y[i0]
    r = i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    l = i0
    while l > 0 and y[l] >= 0.5:
        l -= 1
    if y[r] >= 0.5 or y[l] >= 0.5:
        return np.nan
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def pulsed(x, z, na, n, theta, tau, lam_a, lam_b, signal):
    """Time-integrated 2CE (∫ I_a I_b dt) or 2PE (∫ |E_a + E_b|⁴ dt) of two pulses reaching the focus at t = 0."""
    reach = n * np.sqrt(np.max(x ** 2 + z ** 2)) / C_UM_FS
    tw = 3 * tau + reach
    dt = tau / 15
    da, ca, Ea = _fields(x, z, lam_a, tau, 2 * tw, na, n, 0.0, 0.0, 0.0, 'rw', PSI, None)
    db, cb, Eb = _fields(x, z, lam_b, tau, 2 * tw, na, n, theta, 0.0, 0.0, 'rw', PSI, None)
    S = np.zeros(x.shape)
    for t in np.arange(-tw, tw + dt / 2, dt):
        A = np.tensordot(ca * np.exp(-1j * da * t), Ea, axes=(0, 0))
        B = np.tensordot(cb * np.exp(-1j * db * t), Eb, axes=(0, 0))
        S += (intensity(A) * intensity(B) if signal == '2CE' else intensity(A + B) ** 2) * dt
    return S


def widths(na, n):
    """{(signal, axis, θ, τ): FWHM in µm} at one NA; τ = 0 for continuous beams."""
    xs = np.linspace(-2.5 * LP / na, 2.5 * LP / na, 801)
    zs = np.linspace(-2.5 * LP * n / na ** 2, 2.5 * LP * n / na ** 2, 2001)
    out = {}
    for axis, s in (('x', xs), ('z', zs)):
        X, Z = (s, 0 * s) if axis == 'x' else (0 * s, s)
        f = lambda lam, th: beam_field(X, Z, lam, na, n=n, theta=th, model='rw', psi=PSI)
        for th in THETAS:
            if th == np.pi / 2 and na > n * np.sin(np.pi / 4) + 1e-9:       # crossed lenses do not fit
                continue
            out[('2PE', axis, th, 0.0)] = fwhm(s, two_photon(f(LP, 0.0), f(LP, th)))
            out[('2CE', axis, th, 0.0)] = fwhm(s, two_color(f(L1, 0.0), f(L2, th)))
            for tau in TAUS:
                out[('2PE', axis, th, tau)] = fwhm(s, pulsed(X, Z, na, n, th, tau, LP, LP, '2PE'))
                out[('2CE', axis, th, tau)] = fwhm(s, pulsed(X, Z, na, n, th, tau, L1, L2, '2CE'))
    return out


def one(args):
    na, n = args
    W = widths(na, n)
    print(f'n = {n} NA {na:.2f} done', flush=True)
    return [(n, na, sig == '2CE', axis == 'z', th, tau, w) for (sig, axis, th, tau), w in W.items()]


CSV = os.path.join(OUT, 'widths.csv')


def main():
    if '--rerun' in sys.argv or not os.path.exists(CSV):
        from multiprocessing import Pool
        jobs = sorted(((na, n) for n, nas in MEDIA for na in nas), key=lambda j: j[0])     # slow low-NA points first
        with Pool(int(os.environ.get('WORKERS', 5))) as pool:
            rows = [r for rs in pool.map(one, jobs, chunksize=1) for r in rs]
        np.savetxt(CSV, np.array(rows, float), delimiter=',', fmt='%.6g', header='n,NA,is_2CE,is_axial,theta,tau_fs,fwhm_um')
    A = np.loadtxt(CSV, delimiter=',', ndmin=2)

    def sel(n, sig, axis, th, tau):
        m = (A[:, 0] == n) & (A[:, 2] == (sig == '2CE')) & (A[:, 3] == (axis == 'z')) & np.isclose(A[:, 4], th) \
            & (A[:, 5] == tau)
        return A[m][:, [1, 6]]

    # ── DOF at θ = π against NA: pulsed over continuous, 2PE and 2CE, air and water ──
    STY = {20.0: ('#ff7f0e', 'τ = 20 fs'), 10.0: ('#d62728', 'τ = 10 fs')}
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.2), sharey=True)
    for ax, sig in zip(axes, ('2PE', '2CE')):
        for n, mk, tag in ((1.0, 'o', 'air'), (1.33, 's', 'water')):
            cw = sel(n, sig, 'z', np.pi, 0.0)
            for tau in TAUS:
                d = sel(n, sig, 'z', np.pi, tau)
                c, lab = STY[tau]
                ax.plot(d[:, 0], d[:, 1] / cw[:, 1], ('-' if n == 1 else '--') + mk, color=c, mfc=c if n == 1 else 'white',
                        lw=3, ms=10, label=f'{lab}, {tag}')
        ax.axhline(1, color='k', lw=2, ls=':')
        ax.set_xlabel('NA'); ax.set_title(f'{sig}, DOF at θ = π, pulsed / continuous')
    axes[0].set_ylabel('DOF ratio')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1), frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, 'dof_pi.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved -> dof_pi.png')

    lines = ['n NA signal axis θ | CW | 20 fs | 10 fs   (central-peak FWHM, µm)']
    for n in (1.0, 1.33):
        for na in (0.5, 0.7, 0.9, 1.2):
            for sig in ('2PE', '2CE'):
                for axis in ('x', 'z'):
                    for th, lab in zip(THETAS, ('0', 'π/2', 'π')):
                        ws = [sel(n, sig, axis, th, tau) for tau in (0.0,) + TAUS]
                        ws = [w[np.isclose(w[:, 0], na), 1] for w in ws]
                        if all(len(w) for w in ws):
                            lines.append(f'{n} {na} {sig} {axis} {lab} | ' + ' | '.join(f'{w[0]:.3f}' for w in ws))
    open(os.path.join(OUT, 'widths.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
