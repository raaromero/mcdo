# The field before Romallosa — how tight-focusing theory was built

*The ~130-year chain of ideas that Romallosa, Bantang & Saloma (2003) stands
on, told as seven conceptual moves. Each move: the idea, the key formula, where
it lives in `mcdo`, and what to read. Dates marked (~verify) are confident but
should be checked against sources before citing in a manuscript. Companion to
`docs/LITERATURE.md` (which says *what* to read; this says *why the field looks
the way it does*).*

---

## Move 0 — Light is a wave of the electromagnetic field
**Maxwell (1865); Helmholtz equation.**
Maxwell's equations imply that in empty (or uniform, linear) media every
Cartesian field component obeys the wave equation; a monochromatic field
$E\,e^{-\mathrm{i}\omega t}$ therefore obeys the **Helmholtz equation**
$(\nabla^2+k^2)E=0$ with $k=n\omega/c$, and the full vector field additionally
obeys $\nabla\!\cdot\!\mathbf{E}=0$. Everything downstream is bookkeeping of
solutions of these two constraints.
**In mcdo:** these are literally our first-principles audit checks
(`audit_first_principles.py`) — the computed fields satisfy Helmholtz and
transversality at the finite-difference floor.
**Read:** Griffiths ch. 9.

## Move 1 — Propagation as superposition: the diffraction integrals
**Huygens (1678) → Fresnel (1818) → Kirchhoff (1882) → Rayleigh–Sommerfeld
(1896).**
Huygens' picture — every point of a wavefront is a source of secondary
wavelets — was made quantitative by Fresnel (interference of the wavelets
explains diffraction) and *derived from the wave equation* by Kirchhoff using
Green's theorem: the field anywhere is an integral of the field over a
surface. Kirchhoff's boundary conditions were mathematically inconsistent;
Rayleigh and Sommerfeld repaired them (the Rayleigh–Sommerfeld integrals).
The enduring lesson: **propagation is linear superposition — fields anywhere
are integrals over fields elsewhere.**
**In mcdo:** every integral we evaluate is a descendant of this move.
**Read:** Goodman ch. 3 (does this cleanly, then pivots to Move 3's picture).

## Move 2 — The classical focus: Airy, Lommel, Gouy
**Airy (1835); Lommel (1885); Gouy (1890).**
Airy applied Fraunhofer diffraction to a telescope's circular aperture and got
the focal-plane pattern $[2J_1(v)/v]^2$ — the **Airy disk**, the first
statement that a "focal point" is really a diffraction pattern of finite size
$\sim\lambda/\mathrm{NA}$. Lommel solved the harder problem of the **entire
3-D focal region** (his $U_n, V_n$ functions are still in Born & Wolf §8.8),
introducing the dimensionless focal coordinates that we still use:
$$u = k z\sin^2\!\alpha, \qquad v = k r\sin\alpha .$$
Gouy discovered the $\pi$ phase anomaly through focus. All of this is
**scalar and paraxial** — light treated as a number, angles small.
**In mcdo:** `airy_intensity`, and the $(u,v)$ coordinates used everywhere.
**Read:** B&W §8.5/§8.8 *later, as lookup*; the Airy limit is our
`test_low_NA_transverse_is_airy`.

## Move 3 — Debye's pivot: the focus as a bundle of plane waves
**Debye (1909).**
Debye reformulated the converging wave not as wavelets from an aperture but as
a **superposition of plane waves whose directions fill the geometric cone**
converging on the focus:
$$U(P)\;=\;\int_{\text{cone}} a(\hat{s})\, e^{\mathrm{i}k\hat{s}\cdot P}\,
\mathrm{d}\Omega .$$
Valid when the aperture subtends many Fresnel zones ($N_F\gg1$ — true for any
real objective). This is *the* conceptual pivot of our whole project: it is
the *angular-spectrum* picture, and it is why a "photon" in our Monte Carlo is
a plane-wave component with direction $\hat{k}$ and a phase — the clear-limit
MC is a Monte-Carlo evaluation of Debye's integral.
**In mcdo:** `debye.py` (scalar), the launcher's very design
(`montecarlo.py`), `direction_sampling_explained.md`.
**Read:** Goodman ch. 3 → N&H ch. 3 intro.

## Move 4 — The microscope thread: Abbe's geometry
**Abbe (1873): the sine condition; resolution as interference.**
Abbe showed that a well-corrected (aplanatic) objective maps a ray at pupil
radius $\rho$ to focal angle $\theta$ via $\rho=f\sin\theta$, and that image
formation is interference of the diffracted orders the aperture admits
(resolution $\propto\lambda/\mathrm{NA}$). Two consequences we use constantly:
(i) the **pupil→angle map** — our apodization $A(\theta)$ *is* the beam profile
read through $\rho=f\sin\theta$; (ii) energy conservation as a ray bends onto
the converging sphere gives the **aplanatic factor** $\sqrt{\cos\theta}$.
Zernike (1934, aberration polynomials; phase contrast) and Hopkins (1940s–50s,
defocus/partial coherence) industrialized the scalar theory of imaging.
**In mcdo:** `apodization.py`, the $\sqrt{\cos\theta}$ in every integral, the
sine condition in the launcher's pupil map.
**Read:** N&H ch. 3 (states it exactly as used).

## Move 5 — The vector completion: Ignatowsky → Wolf → Richards & Wolf
**Ignatowsky (1919–20, ~verify); Wolf (1959); Richards & Wolf (1959);
Boivin & Wolf (1965).**
At high NA, "light as a number" fails: rays arrive from steep angles and their
**polarization vectors cannot all be parallel** after refraction. Ignatowsky
first wrote vector focusing integrals for aplanatic systems (long overlooked);
Wolf's 1959 paper I built the general **vector Debye–Wolf integral**, and
Richards & Wolf's paper II worked out the aplanatic, linearly-polarized case —
the three integrals
$$I_{0,1,2}(r,z)=\int_0^\alpha A(\theta)\sqrt{\cos\theta}\;K_{0,1,2}(\theta)\,
J_{0,1,2}(kr\sin\theta)\,e^{\mathrm{i}kz\cos\theta}\,\mathrm{d}\theta,$$
$K_0=\sin\theta(1{+}\cos\theta)$, $K_1=\sin^2\theta$,
$K_2=\sin\theta(1{-}\cos\theta)$, with
$\mathbf{E}\propto(I_0{+}I_2\cos2\phi,\;I_2\sin2\phi,\;-2\mathrm{i}I_1\cos\phi)$.
New physics appears: a **longitudinal field** $E_z$, an **elongated,
anisotropic focal spot**, polarization-dependent zeros. Boivin & Wolf mapped
the energy flow near focus. This move *is* the deterministic engine of `mcdo`
— and it is why our Phase-2 result (thresholds depend on polarization, cut,
direction) had to come out the way it did: the anisotropy was in RW 1959 all
along; we quantified where it bites.
**In mcdo:** `rw_integrals.py` wholesale; `polarization.py`.
**Read:** N&H ch. 3–4 first, then the two 1959 papers.

## Move 6 — Scoring images: Linfoot's criteria
**Linfoot (1950s; book 1964, ~verify).**
Post-war optical design needed *numbers* for "how faithful is this image":
Linfoot's fidelity $F$, structural content $S$, correlation quality $Q$
(with $2Q-S=F$) compare a test distribution to a reference. Romallosa's
innovation was to point these image-evaluation metrics at the *focal
intensity itself* (pulsed vs cw) — that's where the paper's $S=1.058$ scores
come from.
**In mcdo:** `linfoot.py` + the identity test.
**Read:** the definitions (our docstrings suffice); Linfoot's book as lookup.

## Move 7 — The ultrafast thread: pulses meet lenses
**fs lasers + CPA (Strickland & Mourou 1985); Bor (1988–89, ~verify);
Kempe–Rudolph (1992); Horváth–Bor (1990s–2003); Brabec & Krausz (RMP 2000);
two-photon microscopy (Denk, Strickler & Webb 1990).**
Femtosecond pulses forced optics to take **bandwidth** seriously: Bor showed
lenses distort pulse fronts (chromatic delay between pupil center and edge);
Kempe & Rudolph built the space–time theory of fs focusing; Horváth & Bor
developed the diffraction theory (and the truncated-Gaussian pupil
$A(\theta)=e^{-\alpha_t\sin^2\theta/\sin^2\alpha}$ we use). Brabec & Krausz's
review defined the **few-cycle regime** — bandwidth comparable to the carrier,
$\Delta\omega\sim\omega_c$ — where a pulse can no longer be "a wavelength with
an envelope." Meanwhile two-photon microscopy (1990) made the *focal volume of
a fs pulse at high NA* the signal-generating element of an entire imaging
field — the reason groups like Saloma's (already doing confocal/two-photon and
photon-counting work) cared about exactly this focal region.
The key physical simplification, inherited by Romallosa's Eq. 10: detectors
are slow, distinct frequencies do not interfere in the *time-integrated*
intensity, so the pulsed focus is the **incoherent spectral sum** of
monochromatic (Move-5) foci — each $\omega$ sees the same cone geometry, at
its own scale $v\propto\omega$.
**In mcdo:** `config.py` (spectrum, TBP), `intensity.py` (Eq. 10),
the full-window finding.
**Read:** Brabec & Krausz for the regime; Kempe–Rudolph / Horváth–Bor as
lookup.

---

## The confluence: Romallosa 2003 in one sentence

**Romallosa, Bantang & Saloma (2003) = Move 5 (vector Richards–Wolf focusing)
evaluated across Move 7 (a few-cycle spectrum, summed incoherently) and scored
with Move 6 (Linfoot criteria)** — the first careful account of what an
octave of bandwidth does to the *vector* focal volume. Everything our project
adds (Babinet annuli, axicon phases, apodization sweeps, and the Monte-Carlo
transport into scattering media) is Moves 8+ built on this stack — which is
why we validated each move's limit (Airy, Debye, RW anchors, Linfoot identity,
Eq.-10 anchors) before extending it.

## Timeline at a glance

| year | who | move |
|---|---|---|
| 1678/1818 | Huygens / Fresnel | wavelets + interference |
| 1835 | Airy | focal-plane diffraction pattern |
| 1865 | Maxwell | light = EM wave |
| 1873 | Abbe | sine condition; resolution as interference |
| 1882/1896 | Kirchhoff / Rayleigh–Sommerfeld | rigorous diffraction integrals |
| 1885 | Lommel | 3-D focal region; $(u,v)$ coordinates |
| 1890 | Gouy | focal phase anomaly |
| 1909 | Debye | focus = cone of plane waves |
| 1919–20 | Ignatowsky (~verify) | first vector focusing integrals |
| 1934 | Zernike | aberration polynomials |
| 1959 | Wolf; Richards & Wolf | the vector Debye–Wolf theory; $I_{0,1,2}$ |
| ~1956/64 | Linfoot | image-quality criteria $F,S,Q$ |
| 1965 | Boivin & Wolf | energy flow near the vector focus |
| 1977–86 | Sheppard et al.; Stamnes | confocal-era focal engineering; *Waves in Focal Regions* |
| 1985 | Strickland & Mourou | CPA → intense fs pulses |
| 1988–92 | Bor; Kempe & Rudolph | fs pulses through lenses |
| 1990 | Denk, Strickler & Webb | two-photon microscopy (why focal volumes matter) |
| 2000 | Brabec & Krausz | the few-cycle regime |
| **2003** | **Romallosa, Bantang & Saloma** | **few-cycle × vector focus × Linfoot** |
