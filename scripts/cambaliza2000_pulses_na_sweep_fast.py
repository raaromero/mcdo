r"""cambaliza2000_pulses_na_sweep.py with the pulsed fields from tables (cambaliza2000_fast_field.py); the same
settings, time integral, continuous-beam profiles (beam_field) and output files.

    MODEL=rw MEDIUM=air NAS=0.5 python scripts/cambaliza2000_pulses_na_sweep_fast.py
    BLOCK = points per block of the time integral (default 300; fewer for pulses of thousands of fs, to save memory)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

import cambaliza2000_pulses_na_sweep as S
from cambaliza2000_fast_field import Focus
from mcdo.pulsed2ce import spectrum, C_UM_FS

FOCUS = {}


def focus(na):
    if na not in FOCUS:
        ap = (lambda th: np.exp(-S.APOD * np.sin(th) ** 2 / (na / S.N) ** 2)) if S.APOD else None
        FOCUS[na] = Focus(na, S.N, S.MODEL, S.EPS, ap, psi=S.PSI)
    return FOCUS[na]


def pulsed(na, tau, theta, s, cut, sig, delay=0.0):
    """S.pulsed with np.stack([field(ω, …) for ω in w]) replaced by the tables."""
    l1, l2 = S.LAMS[sig]
    w1, w2 = 2 * np.pi * C_UM_FS / l1, 2 * np.pi * C_UM_FS / l2
    reach = S.N * np.max(np.abs(s)) / C_UM_FS + abs(delay)
    dt = min(tau / 20, 0.4)
    t = np.arange(-(3 * tau + reach), 3 * tau + reach + dt / 2, dt)
    window = 2 * (4 * tau + reach)
    out, crest = np.empty(len(s)), np.empty(len(s))
    specs = [spectrum(l, tau, t_window=window) for l in (l1, l2)]
    for b0 in range(0, len(s), S.BLOCK):
        sb = s[b0:b0 + S.BLOCK]
        x, z = (0 * sb, sb) if cut == 'z' else (sb, 0 * sb)
        env = []
        for (w, a, d), th, dl in zip(specs, (0.0, theta), (0.0, delay)):
            E = focus(na).fields(w, th, x, z)                                          # (n_ω, comp, pts)
            c = a * d * np.exp(-1j * np.outer(t - dl, w - w.mean())) * np.exp(1j * w.mean() * dl)
            env.append(np.tensordot(c, E, axes=(1, 0)))
        e1, e2 = env
        ph = lambda dw: np.exp(1j * dw * t) * dt
        A12 = np.einsum('t,tip,tjp->ijp', ph(S.WE - w1 - w2), e1, e2)
        X = 2 * A12 if sig == '2ce' else A12 + A12.transpose(1, 0, 2)
        A11 = np.einsum('t,tip,tjp->ijp', ph(S.WE - 2 * w1), e1, e1)
        A22 = np.einsum('t,tip,tjp->ijp', ph(S.WE - 2 * w2), e2, e2)
        out[b0:b0 + S.BLOCK] = (np.abs(A11 + X + A22) ** 2).sum(axis=(0, 1))
        crest[b0:b0 + S.BLOCK] = ((np.abs(A11) + np.abs(X) + np.abs(A22)) ** 2).sum(axis=(0, 1))
    return out, crest


S.pulsed = pulsed
S.BLOCK = int(os.environ.get('BLOCK', S.BLOCK))                    # fewer points per block for very long pulses

if __name__ == '__main__':
    S.main()
