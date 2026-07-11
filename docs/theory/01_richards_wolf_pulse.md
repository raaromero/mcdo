# Richards-Wolf vector diffraction and pulsed focal fields
*(Phase 1 — replication of Romallosa, Bantang & Saloma, PRA **68**, 033812 (2003))*

## 1. Vector focal field [R&W59; Rom03 Eqs. 1–7]

For an aplanatic lens uniformly illuminated by an x-polarized plane wave, the
field at observation point $P$ near focus is

$$\mathbf{E}(P) = E_x\,\mathbf{e}_x + E_y\,\mathbf{e}_y + E_z\,\mathbf{e}_z$$

$$E_x = -j\,(I_0 + I_2\cos 2\phi),\qquad
  E_y = -j\,I_2\sin 2\phi,\qquad
  E_z = -2\,I_1\cos\phi$$

with azimuth $\phi$ measured from the polarization (x) axis, and

$$I_0(u,v) = \int_0^{\alpha} \cos^{1/2}\!\theta\,\sin\theta\,(1+\cos\theta)\,
  J_0\!\Big(\tfrac{v\sin\theta}{\sin\alpha}\Big)\,
  e^{\,j u\cos\theta/\sin^2\!\alpha}\, d\theta$$

$$I_1(u,v) = \int_0^{\alpha} \cos^{1/2}\!\theta\,\sin^2\!\theta\,
  J_1\!\Big(\tfrac{v\sin\theta}{\sin\alpha}\Big)\,
  e^{\,j u\cos\theta/\sin^2\!\alpha}\, d\theta$$

$$I_2(u,v) = \int_0^{\alpha} \cos^{1/2}\!\theta\,\sin\theta\,(1-\cos\theta)\,
  J_2\!\Big(\tfrac{v\sin\theta}{\sin\alpha}\Big)\,
  e^{\,j u\cos\theta/\sin^2\!\alpha}\, d\theta$$

Optical coordinates: $u = k\sin^2\!\alpha\; z$, $v = k\sin\alpha\; r$, with
$k = 2\pi n/\lambda$ and $\sin\alpha = X_{NA}/n$.

### Intensity cuts

| cut | formula | zeros? | use |
|---|---|---|---|
| $\phi=\pi/2$ (scan ⟂ polarization) | $\lvert I_0 - I_2\rvert^2$ | **yes** (ring at $r=0.555$ μm for $X_{NA}=0.8$) | **Figs 1–2 of Rom03** |
| $\phi=0$ (scan ∥ polarization) | $\lvert I_0+I_2\rvert^2 + 4\lvert I_1\rvert^2$ | no ($E_z$ fills them) | vector-effect diagnostics |
| azimuthal average | $\lvert I_0\rvert^2 + \lvert I_2\rvert^2 + 2\lvert I_1\rvert^2$ | no | smooth maps |

The paper's statement that the cw profile "contains zero points" and the
island topology of its Fig. 1(a) **require** the $\lvert I_0-I_2\rvert^2$ cut.

CW anchors ($\lambda_c=750$ nm, $X_{NA}=0.8$, $n=1.3$): transverse FWHM
472.8 nm, zero ring 0.555 μm; axial FWHM 2419 nm, first zero 3.05 μm
($u\!\approx\!4\pi$).

## 2. Pulse spectrum [Rom03 Eqs. 8–9]

Unchirped Gaussian pulse, $\tau$ = FWHM of $\lvert E(t)\rvert^2$:

$$E(t) = (2a/\pi)^{1/4} e^{-a t^2} e^{-j\omega_c t},\qquad a = \frac{2\ln 2}{\tau^2}$$

$$E(\omega) = (1/2\pi)^{1/8}(1/a)^{1/4}\,
  e^{-(\omega-\omega_c)^2/(4a)},\qquad
  \lvert E(\omega)\rvert^2 = (1/2\pi)^{1/4}(1/a)^{1/2}\,
  e^{-(\omega-\omega_c)^2/(2a)}$$

FWHM of $\lvert E(\omega)\rvert^2$: $\Delta\omega = 4\ln 2/\tau$
(time-bandwidth product $\Delta\nu\,\tau = 2\ln 2/\pi \approx 0.441$).
For $\tau=1$ fs at $\lambda_c=750$ nm this FWHM spans 483 nm – 1.67 μm.

## 3. Pulsed intensity (Eq. 10) and the spectral-window finding

$$\lvert\mathbf{E}(P)\rvert^2 \;=\; \int \lvert E(\omega)\rvert^2\,
  \lvert\mathbf{E}(P,\omega)\rvert^2\, d\omega$$

evaluated as a Riemann sum over $N_{freq}=201$ uniform samples; each
frequency's CW field uses $k(\omega) = n\omega/c$ in $u, v$. Both CW and
pulsed distributions are normalized to their own peak.

**Critical, numerically-validated finding:** the paper integrated over the
**full positive spectrum** $\omega \in (0, 2\omega_c)$, *not* the FWHM band
its text appears to specify (the quoted "483 nm–1.67 μm" describes the
spectrum's FWHM, not the integration window). Truncating at the FWHM
discards 24% of the spectral weight — precisely the far wings whose large
focal spots fill the CW zeros:

| window | $S_{tr}$ | $S_{ax}$ | $F_{tr}$ | pedestal @ $r=1$ μm |
|---|---|---|---|---|
| ±FWHM/2 (literal reading) | 1.020 | 1.019 | 0.991 | 0.007 |
| **(0, 2ω_c) (correct)** | **1.053** | **1.058** | **0.963** | **0.049** |
| paper | 1.062 | 1.057 | ~0.96 | ~0.05 |

Implementation: `SimConfig.omega_grid()` uses half-width
$\min(4\sigma,\,\omega_c)$ with $\sigma=\sqrt{a}$ — full support for
few-cycle pulses, well-sampled narrow spectra for long pulses
(crossover at $\tau \approx 1.9$ fs).

## 4. Replication conventions discovered

1. **The paper's Fig. 2 panels are swapped**: its (a) "r ±6 μm" is the
   *axial* profile (zeros ±3.05 μm); its (b) "z ±1 μm" is the *transverse*
   one (zero 0.555 μm, sidelobe 0.7 μm).
2. **Fig. 3 energy fraction is a 1-D line integral**
   $\int_{FWHM} I\,dr \big/ \int_{array} I\,dr$ over the 201-point profile —
   *not* cylindrical $\int I\, r\,dr$. Gives plateau 0.777 and 0.62 @ 1 fs
   (paper ≈0.78 / ≈0.65); cylindrical gives 0.46 (wrong).
3. **Linfoot arrays sample in optical coordinates** ($v \in \pm 6.70$,
   $u \in \pm 24.74$ — the Fig-2 windows at $X_{NA}=0.8$), which is what
   makes F and S insensitive to NA (paper Fig. 4a).
4. **Fig. 1 axes** are $r \in \pm 2.0$ μm, $z \in \pm 6.0$ μm (the scan
   dropped decimal points).

## 5. Linfoot criteria [Rom03 §III]

With reference $r(m)$ (CW) and test $a(m)$ (pulsed), both peak-normalized,
$m = -100\ldots 100$:

$$F = 1 - \frac{\langle (r-a)^2\rangle}{\langle r^2\rangle},\qquad
  S = \frac{\langle a^2\rangle}{\langle r^2\rangle},\qquad
  Q = \frac{\langle \lvert a\rvert\lvert r\rvert\rangle}{\langle r^2\rangle},
  \qquad 2Q - S = F$$

Two-photon PSF = (peak-normalized single-photon PSF)².

## 6. Replication scorecard (τ = 1 fs, X_NA = 0.8 unless noted)

| Figure | paper anchor | ours | status |
|---|---|---|---|
| 1 | island topology (cw) / smooth barrel (pulsed) | same | ✓ |
| 2 | zeros 0.555/3.05 μm; pedestal ≈0.1 / 0.05 | 0.555/3.05; 0.13 / 0.049 | ✓ |
| 3 | plateau ≈0.78; 1 fs ≈0.65; linear ≤2 fs | 0.777; 0.62 | ✓ (−3% @1 fs) |
| 4 | $S_{ax}$ 1.057, $S_{tr}$ 1.062, F≈0.96, NA-flat | 1.058, 1.053, 0.96, flat | ✓ ($S_{tr}$ −0.9%) |
| 5 | S(1 fs) on 0.97·τ^0.04 | 0.970 | ✓ exact |

Residuals trace to conventions the paper does not document (exact array
windows; RK4 quadrature details).

## 7. Errors found in predecessor code (mcdo) — fixed on its `cleanup` branch

- `spectral_power()` double-squared the spectrum → effective width √2 too
  narrow (a 1 fs pulse behaved as 1.4 fs).
- Library default window ±FWHM/2 (truncation); validation script used
  ±2.5·FWHM which at τ=1 fs extends into negative frequencies.
- `polarization='circular'` (azimuthal average) cannot reproduce the zero
  structure of the paper's figures.
