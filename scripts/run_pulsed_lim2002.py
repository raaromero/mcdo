r"""Lim & Saloma (2002) with optical pulses: every result of the paper, pulsed.

Each pulse is a coherent sum over its spectrum (mcdo.pulsed2ce.spectrum): every
frequency is focused on its own, with its phase, so the pulse travels through the
focus at c/n and reaches its geometric focus at t = 0. Beam 2 arrives Δt later.

    2CE:  F_2c(P) ∝ ∫ I_1(P, t) I_2(P, t − Δt) dt              (the I_1 I_2 term; τ ≳ 8 fs)
    2PE:  F_2p(P) ∝ ∫ |E_1(P, t) + e^{iω_0Δt} E_2(P, t − Δt)|^4 dt   (both at 700 nm, carrier factored out)

Per model and pulse duration τ it saves, for 2CE and 2PE at θ = π and π/2:
  psf2, psf3   aligned PSF and the PSF with O′ = (0.4, 1.0) µm (Figs. 2–3), window ±1 × ±5 µm
  peak, F, C, Q  peak and Linfoot's criteria against the offset of O′ (Figs. 4–6), offsets ±1 × ±5 µm
  delay        peak lost and F against the time delay Δt/τ, aligned foci
  delay_z      (θ = π) peak against the offset z_c and the time delay
Offsets of O′ (zero included) use the translation of beam 2's field on an extended grid, as in the replication.

    MODEL=scalar python scripts/run_pulsed_lim2002.py           # scalar 2CE, NA 0.5 (stage 1)
    MODEL=rw NA=0.7 python scripts/run_pulsed_lim2002.py        # vector, unpolarized 2CE, s-polarized 2PE (stage 2)
    -> output/08_two_color/lim2002/pulsed_lim2002/{model}_na{NA}_tau{τ}.npz
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo.pulsed2ce import C_UM_FS, spectrum
from mcdo.twobeam import beam_field

MODEL = os.environ.get('MODEL', 'scalar')
NA = float(os.environ.get('NA', '0.5'))
TAUS = [float(t) for t in os.environ.get('TAUS', '100,20,10').split(',')]
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'pulsed_lim2002')
os.makedirs(OUT, exist_ok=True)
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
TH = {'pi': np.pi, 'pi2': np.pi / 2}
DX, DZ = 0.02, 0.05                       # window steps (µm): ±1 × ±5 µm
NXW, NZW = 50, 100
SX, SZ = 4, 8                             # offset steps in window samples: 0.08 µm, 0.4 µm
OX, OZ = np.arange(-48, 49, SX), np.arange(-96, 97, SZ)     # offsets ±0.96 × ±4.8 µm (25 × 25), zero included
O3 = (20, 20)                                                 # Fig. 3: O′ = (0.4, 1.0) µm, in window samples (z, x)
DELAYS = np.array([-2, -1.5, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 1.5, 2])   # Δt/τ
PX, PZ = OX.max(), OZ.max()


def grids():
    xw, zw = np.arange(-NXW, NXW + 1) * DX, np.arange(-NZW, NZW + 1) * DZ
    xe, ze = np.arange(-NXW - PX, NXW + PX + 1) * DX, np.arange(-NZW - PZ, NZW + PZ + 1) * DZ
    return np.meshgrid(xw, zw), np.meshgrid(xe, ze)


def spectral_fields(lam0, tau, theta, X, Z, tw, psi):
    """Frequency offsets, weights and the focal field of each frequency on (X, Z)."""
    w, a, dw = spectrum(lam0, tau, t_window=2 * tw)
    kw = dict(model='rw', psi=psi) if MODEL == 'rw' else {}
    E = np.stack([beam_field(X, Z, 2 * np.pi * C_UM_FS / wm, NA, 1.0, theta=theta, **kw) for wm in w]).astype(np.complex64)
    return (w - w.mean()).astype(np.float32), (a * dw).astype(np.complex64), E


def at_time(spec, t):
    dw, c, E = spec
    return np.tensordot(c * np.exp(-1j * dw * t).astype(np.complex64), E, axes=(0, 0))


def inten(f):
    return (np.abs(f) ** 2).sum(axis=0) if MODEL == 'rw' else np.abs(f) ** 2


def run(pair, th, tau):
    (XW, ZW), (XE, ZE) = grids()
    la, lb = LAMS[pair]
    reach = np.hypot(XE.max(), ZE.max()) / C_UM_FS
    tw = 3 * tau + reach + 2 * tau
    dt = tau / 15
    t = np.arange(-tw, tw + dt / 2, dt)
    w0 = 2 * np.pi * C_UM_FS / la
    psis = (0.0, np.pi / 2) if (MODEL == 'rw' and pair == '2ce') else (np.pi / 2,)
    B1 = [spectral_fields(la, tau, 0.0, XW, ZW, tw, p) for p in psis]
    B2 = [spectral_fields(lb, tau, TH[th], XE, ZE, tw, p) for p in psis]
    nzw, nxw = XW.shape
    sl = lambda f, iz, ix: f[..., PZ - iz:PZ - iz + nzw, PX - ix:PX - ix + nxw]
    S = np.zeros((OZ.size, OX.size, nzw, nxw))                 # signal for every offset of O′
    S3 = np.zeros((nzw, nxw))                                    # Fig. 3 offset
    Sd = np.zeros((DELAYS.size, nzw, nxw))                     # aligned, every time delay
    Sdz = np.zeros((DELAYS.size, OZ.size, nzw, nxw)) if th == 'pi' else None
    for ti in t:
        if pair == '2ce':
            I1 = sum(inten(at_time(b, ti)) for b in B1) / len(B1)
            I2 = sum(inten(at_time(b, ti)) for b in B2) / len(B2)
            for i, iz in enumerate(OZ):
                for j, ix in enumerate(OX):
                    S[i, j] += I1 * sl(I2, iz, ix)
            S3 += I1 * sl(I2, *O3)
            for k, d in enumerate(DELAYS):
                I2d = sum(inten(at_time(b, ti - d * tau)) for b in B2) / len(B2)
                Sd[k] += I1 * sl(I2d, 0, 0)
                if Sdz is not None:
                    for i, iz in enumerate(OZ):
                        Sdz[k, i] += I1 * sl(I2d, iz, 0)
        else:
            E1, E2 = at_time(B1[0], ti), at_time(B2[0], ti)
            for i, iz in enumerate(OZ):
                for j, ix in enumerate(OX):
                    S[i, j] += inten(E1 + sl(E2, iz, ix)) ** 2
            S3 += inten(E1 + sl(E2, *O3)) ** 2
            for k, d in enumerate(DELAYS):
                E2d = at_time(B2[0], ti - d * tau) * np.exp(1j * w0 * d * tau)
                Sd[k] += inten(E1 + sl(E2d, 0, 0)) ** 2
                if Sdz is not None:
                    for i, iz in enumerate(OZ):
                        Sdz[k, i] += inten(E1 + sl(E2d, iz, 0)) ** 2
    i0, j0 = int(np.flatnonzero(OZ == 0)[0]), int(np.flatnonzero(OX == 0)[0])
    assert np.allclose(S[i0, j0], Sd[int(np.flatnonzero(DELAYS == 0)[0])], rtol=1e-4)   # aligned map = zero time delay
    tref = S[i0, j0]; tn = tref / tref.max(); t2 = np.mean(tn ** 2)
    P = S.reshape(OZ.size, OX.size, -1).max(axis=2) / tref.max()
    an = S / S.reshape(OZ.size, OX.size, -1).max(axis=2)[..., None, None]
    F = 1 - ((tn - an) ** 2).mean(axis=(2, 3)) / t2
    C = (an ** 2).mean(axis=(2, 3)) / t2
    Q = (an * tn).mean(axis=(2, 3)) / t2
    dn = Sd / Sd.reshape(DELAYS.size, -1).max(axis=1)[:, None, None]
    out = dict(x=XW[0], z=ZW[:, 0], xc=OX * DX, zc=OZ * DZ, delays=DELAYS * tau,
               psf2=tn, psf3=S3 / S3.max(),
               peak=P, F=F, C=C, Q=Q,
               delay_peak=Sd.reshape(DELAYS.size, -1).max(axis=1) / tref.max(),
               delay_F=1 - ((tn - dn) ** 2).mean(axis=(1, 2)) / t2)
    if Sdz is not None:
        out['delay_z_peak'] = Sdz.reshape(DELAYS.size, OZ.size, -1).max(axis=2) / tref.max()
    return out


for tau in TAUS:
    path = os.path.join(OUT, f'{MODEL}_na{NA:g}_tau{tau:g}.npz')
    if os.path.exists(path):
        continue
    res = {}
    for pair in ('2ce', '2pe'):
        for th in ('pi', 'pi2'):
            t0 = time.time()
            for k, v in run(pair, th, tau).items():
                res[f'{pair}_{th}_{k}'] = v
            print(f'{MODEL} NA {NA:g} τ {tau:g} fs {pair} {th}: {time.time() - t0:.0f} s', flush=True)
    np.savez_compressed(path, **res)
    print('Saved ->', path, flush=True)
