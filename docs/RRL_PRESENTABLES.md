# RRL presentables — papers you can present to the group

*Curated from `LITERATURE.md` + the verified sweep (`paper/literature/
LITERATURE_SWEEP.md`) for journal-club / RRL presentations: ISI or comparably
respected venues, ranked by digestibility. **Rule: verify the full citation
before presenting anything marked (~verify)** — status flags: [V] = verified in
our sweep, [L] = sweep-extracted with source quote but final verification
pending, (~verify) = from domain knowledge only.*

## Tier 1 — easiest wins (short, visual, story-driven)

| paper | venue | why it presents well | tie to our work |
|---|---|---|---|
| Vellekoop & Mosk, "Focusing coherent light through opaque strongly scattering media," Opt. Lett. 32, 2309 (2007) (~verify details) | Opt. Lett. (3 pages) | One figure carries the talk: shaping the input wavefront makes an opaque wall focus light. Launched a whole field. | The conceptual flip our MC phase lives in: scattering as a controllable medium, not noise. |
| Durnin, Miceli & Eberly, "Diffraction-free beams," PRL 58, 1499 (1987) + Durnin JOSA A 4, 651 (1987) | PRL / JOSA A | "A beam that doesn't spread" — provocative claim, simple math (J₀), famous controversy about energy. | The axicon/annulus limit we validated (Phases 3–4). |
| Denk, Strickler & Webb, "Two-photon laser scanning fluorescence microscopy," Science 248, 73 (1990) (~verify) | Science (3 pages) | The iconic application paper; explains *why* focal volumes of fs pulses matter. | The motivation behind the whole lineage (and Blanca–Saloma). |
| Betzig-lab Bessel-beam two-photon volumetric imaging (Nat. Methods, ~2011–2014) [L — pin exact citation] | Nat. Methods | Gorgeous figures; axicon → annulus → extended-DOF imaging in live samples. | The application our headline result de-risks for few-cycle sources. |

## Tier 2 — moderate effort, high relevance (the core RRL set)

| paper | venue | why | tie |
|---|---|---|---|
| **Romallosa, Bantang & Saloma, PRA 68, 033812 (2003)** [V] | PRA | The anchor; you can present it better than anyone — you reproduced every figure. | Phase 1. |
| **Blanca & Saloma, Appl. Opt. 37, 8092 (1998)** [L] | Appl. Opt. | Clear forward-MC story, group lineage, good figures. | The forward problem our MC inverts/extends. |
| **Hayakawa, Potma & Venugopalan, Biomed. Opt. Express 2, 278 (2011)** [L] | BOE | The key modern prior art: vector field MC of tightly focused beams in tissue (NA 0.81–1.31). Present honestly as "the closest thing to our Phase 6." | Positioning for the MC paper. |
| Wang, Jacques & Zheng, "MCML," Comput. Methods Programs Biomed. 47, 131 (1995) | CMPB | The methods classic every transport MC descends from; algorithmic, concrete. | Our `scatter.py` kernel. |
| Lens-axicon tunable two-photon Bessel beams, Nat. Commun. 12 (2021), s41467-021-23249-y [L] | Nat. Commun. | Modern, experimental, self-healing demonstrations. | Phase 4's application, done in the lab. |
| Chen, Wu & Zhan, "Longitudinally polarized needle of light" via annulus + binary phase, Opt. Lasers Eng. 59, 93 (2014) ref-class [V — see sweep] | Opt. Lasers Eng. | One striking idea (a "light needle"), clear figures. | Where annular engineering leads beyond our ε-scan. |
| "Moving halo" polychromatic focus paper, JOSA A 37, 969 (2020) [V] | JOSA A | Short, modern, directly about broadband high-NA foci. | The nearest modern neighbor of our Phase 5 physics. |

## Tier 3 — foundations (present once, cite forever)

| paper | venue | why | tie |
|---|---|---|---|
| Richards & Wolf, Proc. R. Soc. A 253, 358 (1959) | Proc. R. Soc. A | THE vector-focus paper; present the I₀,I₁,I₂ structure + the u,v maps — heavy but you own it (Phase 2 reproduces its figures). | The engine's core. |
| Sheppard & Wilson 1978 (thin-annulus J₀ focal field) [L — pin citation] | Optik/JOSA-era | Short and geometric; pairs with Durnin. | Phase 3's anchor. |
| Farrell, Patterson & Wilson, Med. Phys. 19, 879 (1992) (~verify) | Med. Phys. | Diffusion Green's function with a clean experimental story. | Our rung-6 anchor; MC-phase RRL. |
| Novotny & Hecht, *Principles of Nano-Optics*, ch. 3–4 (book) | CUP | Not a paper — but the cleanest modern derivation; good for a "background" RRL slot. | The recommended on-ramp (see LITERATURE.md §0). |

## How to run these as RRL sessions (practical)
1. **Lead with the anchor you can demo**: any Tier-2 paper tied to a phase can
   end with one slide of OUR reproduction ("here is their Fig. X from our
   engine") — instantly memorable, and it advertises the toolkit.
2. **One paper per session**, 15–20 min: problem → one key equation → one key
   figure → what it enabled → how it touches the thesis.
3. **Order for a semester** (8 sessions): Denk → Durnin → Romallosa → Blanca —
   then MCML → Hayakawa → Vellekoop–Mosk → Betzig Bessel-2P. That sequence IS
   the thesis narrative in literature form: tight focus → structured beams →
   pulsed foci → scattering → control.
4. Verify every (~verify)/[L] citation before its session (sweep terms in
   `paper/literature/LITERATURE_SWEEP.md`).

## The main advancement of the field, relative to this thesis

**Pre-MC (Phases 1–5) — the field's state and our step.** The two relevant
literatures matured *separately*: (i) vector high-NA focusing theory
(Richards–Wolf 1959 → Novotny–Hecht codification) including few-cycle/pulsed
foci (Romallosa 2003; polychromatic-focus numerics 2006–2020), and (ii)
structured-pupil depth-of-focus engineering (Durnin 1987 Bessel beams; annular
DOF ∝ 1/(1−ε²); "needle" beams 2008–2014; Bessel-beam volumetric two-photon
imaging in Nat. Methods-class venues 2011–2017). The field's main open edge
where they meet: **what broadband/few-cycle illumination does to engineered
foci** — treated only piecemeal (chromatic effects on Bessel beams, moving-halo
2020). Our advancement: the first systematic vector-exact map of pulsed ×
structured pupils at high NA, with the bandwidth-invariance of the DOF ratio
(≤0.10% cw→1 fs) as the quantitative headline.

**MC phase (6+) — the field's state and our step.** Transport MC is mature
(MCML 1995 lineage; GPU codes) but is *radiometric* — it propagates weights,
not fields, and launches collimated/diverging rays. The key modern advancement
toward coherent-beam MC is Hayakawa–Potma–Venugopalan (BOE 2, 278, 2011):
electric-field MC for focused Gaussian beams in tissue. Our step beyond it:
arbitrary structured pupils + few-cycle spectra as the SOURCE of the transport
problem, with the deterministic ballistic field kept coherently (amplitude
attenuation, not photon killing) and the whole chain validated rung-by-rung.
Downstream (the field's frontier we can then touch): wavefront-shaping /
focusing-through-turbidity (Vellekoop–Mosk 2007 →) with *pulsed structured*
inputs — essentially untouched territory.
