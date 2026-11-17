r"""Focused fields of mcdo.twobeam.beam_field on the sweep's cuts, from tables reused for every frequency.

Every cut of the pulse sweep lies on a beam axis (r_b = 0) or in a focal plane (z_b = 0) of each beam: along z the
facing beams (θ = 0, π) are on axis and the crossed beam (θ = π/2) is in its focal plane, across x the reverse. On
such a line the pupil integrals of beam_field depend on the frequency only through ζ = k z_b or ξ = k r_b, so one
table in ζ (axis) or ξ (focal plane) per NA, medium and pupil serves every frequency, pulse width and delay:

    scalar (paraxial):  U = 2 ∫ ρ A(ρ) e^{iφ(ρ)} e^{−i u ρ²/2} J₀(vρ) dρ,   u = (NA/n)² ζ,  v = (NA/n) ξ,   E = e^{iζ} U
    vector (RW):        I_m = ∫ √cosϑ A(ϑ) g_m(ϑ) e^{iζ cosϑ} J_m(ξ sinϑ) dϑ,   I₀ on axis = e^{iζ} Ĩ₀(ζ)

The tables hold the same Simpson sums as beam_field (same ϑ and ρ samples), on a step of 0.02 in ζ and ξ, and a
cubic spline evaluates them; the carrier e^{iζ} is applied exactly, not interpolated. The polarization and the
rotation into the lab frame are those of beam_field. Points off both lines raise an error.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.special import jv

from mcdo.pulsed2ce import C_UM_FS
from mcdo.twobeam import _beam_frame, _to_lab, _simpson_weights

H = 0.02                                                            # table step in ζ and ξ
TINY = 1e-6                                                         # |k r_b| or |k z_b| counted as zero
CHUNK = 4000


class Focus:
    """One lens: NA, refractive index n, model ('paraxial' or 'rw'), obstruction ratio eps, apodization A(ϑ),
    spherical aberration sa (paraxial, as in beam_field) and input polarization psi (rw)."""

    def __init__(self, na, n=1.0, model='paraxial', eps=0.0, apodization=None, sa=0.0, psi=np.pi / 2,
                 n_theta=301, n_rho=401):
        self.na, self.n, self.model, self.psi = na, n, model, psi
        if model == 'paraxial':
            rho = np.linspace(eps, 1.0, n_rho)
            ab = np.exp(2j * np.pi * (sa / 100.0) * rho ** 4)
            if apodization is not None:
                ab = ab * apodization(np.arcsin(rho * na / n))
            self.s, self.wts = rho, 2.0 * _simpson_weights(n_rho, 1.0 - eps) * rho * ab
        elif model == 'rw':
            alpha = np.arcsin(na / n)
            th0 = np.arcsin(eps * np.sin(alpha)) if eps > 0 else 0.0
            th = np.linspace(th0, alpha, n_theta)
            wa = _simpson_weights(n_theta, alpha - th0) * np.sqrt(np.maximum(np.cos(th), 0.0))
            if apodization is not None:
                wa = wa * apodization(th)
            st, ct = np.sin(th), np.cos(th)
            self.s, self.c = st, ct
            self.g = np.stack([wa * st * (1 + ct), wa * st ** 2, wa * st * (1 - ct)])      # I₀, I₁, I₂
        else:
            raise ValueError(f'unknown model {model!r}')
        self.tab = {}

    def _values(self, kind, q):
        """The carrier-free pupil sums at q = ζ (axis) or ξ (focal plane): (len(q), terms)."""
        out = []
        for c0 in range(0, len(q), CHUNK):
            qc = q[c0:c0 + CHUNK]
            if self.model == 'paraxial':
                if kind == 'axis':
                    k = np.exp(-0.5j * (self.na / self.n) ** 2 * np.outer(qc, self.s ** 2))
                else:
                    k = jv(0, (self.na / self.n) * np.outer(qc, self.s))
                out.append((k @ self.wts)[:, None])
            elif kind == 'axis':
                out.append((np.exp(1j * np.outer(qc, self.c - 1.0)) @ self.g[0])[:, None])
            else:
                arg = np.outer(qc, self.s)
                out.append(np.stack([jv(m, arg) @ self.g[m] for m in range(3)], axis=1))
        return np.concatenate(out)

    def _table(self, kind, qmax):
        """Spline over [−qmax, qmax], rebuilt 1.5 times wider when a call needs more."""
        sp = self.tab.get(kind)
        if sp is None or sp.x[-1] < qmax:
            top = 1.5 * qmax + 10 * H
            q = np.arange(-top, top + H / 2, H)
            sp = self.tab[kind] = CubicSpline(q, self._values(kind, q), axis=0)
        return sp

    def fields(self, w, theta, x, z):
        """Fields at angular frequencies w (rad/fs) on lab points (x, 0, z): (n_ω, components, points), the same
        array as np.stack([beam_field(x, z, 2πc/ω, …)[None or :] for ω in w])."""
        xb, yb, zb = _beam_frame(np.asarray(x, float), np.asarray(z, float), theta, 0.0, 0.0)
        rb = np.hypot(xb, yb)
        k = self.n * np.asarray(w, float) / C_UM_FS                                     # n 2π/λ
        kmax = k.max()
        if np.all(kmax * rb < TINY):
            kind, q = 'axis', zb
        elif np.all(kmax * np.abs(zb) < TINY):
            kind, q = 'focal', rb
        else:
            raise ValueError('points are off the beam axis and off the focal plane')
        arg = np.outer(k, q)                                                            # (n_ω, pts)
        V = self._table(kind, np.abs(arg).max())(arg.ravel()).reshape(arg.shape + (-1,))
        carrier = np.exp(1j * np.outer(k, zb))                                          # 1 in the focal plane
        if self.model == 'paraxial':
            return (carrier * V[..., 0])[:, None]
        if kind == 'axis':
            I0, I1, I2 = carrier * V[..., 0], 0.0, 0.0
        else:
            I0, I1, I2 = V[..., 0], V[..., 1], V[..., 2]
        phi = np.arctan2(yb, xb) - self.psi
        ex = -1j * (I0 + I2 * np.cos(2 * phi))
        ey = -1j * I2 * np.sin(2 * phi) + 0 * ex
        ez = -2.0 * I1 * np.cos(phi) + 0 * ex
        c, s = np.cos(self.psi), np.sin(self.psi)
        E = np.stack([c * ex - s * ey, s * ex + c * ey, ez])                            # (3, n_ω, pts)
        return _to_lab(E, theta).transpose(1, 0, 2)
