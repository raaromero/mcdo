// Key results of the current work, one card each on the Highlights tab. A click applies the preset (state keys of main.ts;
// the keys left out take their defaults) and opens that view, so the plots of the result are drawn at once.
// The sentences are those of docs/progress/work_to_date.tex, Sections 6.3 and 7, verbatim or shortened.
// To add a highlight, add one entry here; the order of the array is the order of the cards and of Previous / Next.
// In Pulse results each chart cell has the id "c-<chart key>" (c-ntw, c-a180, c-dpk, c-xpk, …) and the section of the delay
// against NA has the id "sec-delay-na"; in Scalar vs vector at high NA the profiles across and along the axis are "c-nax" and
// "c-naz". "scroll" names one of them.
import type { State } from "./main";

export type Highlight = {
  id: string;                    // kept in the URL as hl=<id>
  group: string;                 // heading of the card on the Highlights tab
  text: string;                  // the result, one or two full sentences
  opens: string;                 // which view and which plot show it
  preset: Partial<State>;        // settings of that view
  scroll?: string;               // id of the plot (or section) to bring into view once the view has drawn, e.g. "c-xpk"
};

const CW = "Continuous beams at high NA", P0 = "Optical pulses: collinear lenses", P90 = "Optical pulses: crossed lenses",
  P180 = "Optical pulses: facing lenses", DT = "Delay between the pulses";

export const HIGHLIGHTS: Highlight[] = [
  { id: "cw-dof-collinear", group: CW,
    text: "With collinear lenses, as NA increases, the 2CE spot and depth of focus decrease together, and 2CE and 2PE have nearly the same profile. The depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9.",
    opens: "Opens Scalar vs vector at high NA with the 2CE depth of focus against NA at θ = 0 and the profiles at NA 0.9.",
    preset: { mode: "na", metric: "width", sig: "2CE", ths: "0", axis: "z", na: 0.9 } },
  { id: "cw-scalar-dof", group: CW,
    text: "At NA 0.9 the paraxial 2CE depth of focus is 36% longer than the vector one (1.10 against 0.81 µm); at NA 0.5 it is 7% longer.",
    opens: "Opens Scalar vs vector at high NA with the scalar depth of focus over the vector one against NA, θ = 0, and the 2CE profiles of both models at NA 0.9; the profile along the axis gives the two depths of focus.",
    preset: { mode: "na", metric: "gap", sig: "2CE", ths: "0", axis: "z", model: "both", na: 0.9 }, scroll: "c-naz" },
  { id: "cw-scalar-5pct", group: CW,
    text: "The 2CE and 2PE profiles of the scalar model stay within 5% of the vector ones up to NA 0.86 across the axis and NA 0.43 along it, in air. In water the two limits are NA 1.14 and 0.57.",
    opens: "Opens Scalar vs vector at high NA with the scalar width across the axis over the vector one against NA, θ = 0, and the band of ±5%.",
    preset: { mode: "na", metric: "gap", sig: "2CE", ths: "0", axis: "x", na: 0.85 } },
  { id: "cw-dof-crossed", group: CW,
    text: "With crossed lenses the depth of focus is shorter than with collinear lenses, and this advantage decreases as NA increases: it is 13 times shorter at NA 0.2 and 3.4 times at NA 0.7.",
    opens: "Opens Scalar vs vector at high NA with the 2CE depth of focus against NA at θ = 0 and π/2.",
    preset: { mode: "na", metric: "width", sig: "2CE", ths: "0.pi2", axis: "z", na: 0.7 } },
  { id: "cw-2pe-crossed", group: CW,
    text: "With crossed lenses, the 2PE central spot stays at 0.256 µm at all NAs, because the interference of the two beams sets it. 2PE is narrower than 2CE and has stronger side lobes, as in Cambaliza & Saloma (2000).",
    opens: "Opens Scalar vs vector at high NA with the 2PE width across the axis against NA at θ = π/2.",
    preset: { mode: "na", metric: "width", sig: "2PE", ths: "pi2", axis: "x", na: 0.7 } },
  { id: "cw-2pe-facing", group: CW,
    text: "With facing lenses and continuous beams, 2CE has the same profile as with collinear lenses, since I₁I₂ does not depend on the direction of beam 2. 2PE has a standing wave along the axis, with a central lobe of 0.13 to 0.17 µm.",
    opens: "Opens Scalar vs vector at high NA with the 2PE width along the axis against NA at θ = π and the profiles at NA 0.9.",
    preset: { mode: "na", metric: "width", sig: "2PE", ths: "pi", axis: "z", na: 0.9 } },

  { id: "pulse-collinear", group: P0,
    text: "With collinear lenses and pulses, 2CE keeps the continuous-beam profile at all pulse widths computed, down to 4 fs, because the two pulses travel together and overlap over the whole focus.",
    opens: "Opens Pulse results at θ = 0; the two plots against NA at the bottom give the pulse width within 1% of continuous beams and the depth of focus against τ (vector model, air).",
    preset: { mode: "psum", rpth: 0, rk: 5, nth: 0, nm: "diff", nset: "rw_air", nx: "tau", ny: "dof" }, scroll: "c-ntw" },

  { id: "pulse-crossed", group: P90,
    text: "With crossed lenses and pulses, the 2CE profiles match the continuous-beam ones from about 20 to 28 fs. Below that the depth of focus changes by a few percent, so crossed lenses keep the sharpest profile.",
    opens: "Opens Pulse results at θ = π/2; the two plots against NA at the bottom give the pulse width within 1% of continuous beams and the depth of focus against τ (vector model, air).",
    preset: { mode: "psum", rpth: 90, rk: 10, nth: 90, nm: "diff", nset: "rw_air", nx: "tau", ny: "dof" }, scroll: "c-ntw" },

  { id: "pulse-facing-dof", group: P180,
    text: "With facing lenses and pulses, 2CE forms where the two pulses meet, a stretch of FWHM G = cτ/(√2 n), so its depth of focus is shorter than with continuous beams. At NA 0.5 the depth of focus is 3.56 µm for continuous beams and 2.81 µm at 20 fs (scalar model).",
    opens: "Opens Pulse results with the 2CE width along the axis against τ at θ = π and the profile at 20 fs (scalar model, NA 0.5, air).",
    preset: { mode: "psum", rcut: "z", rpth: 180, rk: 20 }, scroll: "c-a180" },
  { id: "pulse-facing-na", group: P180,
    text: "With facing lenses, the pulse width from which the profiles match the continuous-beam ones to 1% grows as NA decreases, from about 25 fs at NA 0.9 to 610 fs at NA 0.2. In water and oil the same results hold at a higher NA, since the focus depends on NA/n.",
    opens: "Opens Pulse results at θ = π; the two plots against NA at the bottom give the pulse width within 1% of continuous beams in air, water and oil, and the largest difference against τ (vector model, air).",
    preset: { mode: "psum", rpth: 180, nth: 180, nm: "diff", nset: "rw_air", nx: "tau", ny: "diff" }, scroll: "c-ntw" },
  { id: "pulse-facing-pupil", group: P180,
    text: "With facing lenses, a longer depth of focus needs a longer pulse to match continuous beams: at NA 0.5, 139 fs for the Gaussian input and 405 fs for the annular pupil with ε = 0.9, against 87 fs for the circular pupil.",
    opens: "Opens Pulse results at θ = π with the largest difference against τ for the annular pupil with ε = 0.9 (vector model, air); the menu of sets also holds the Gaussian input.",
    preset: { mode: "psum", rpth: 180, nth: 180, nm: "diff", nset: "rw_air_eps0.9", nx: "tau", ny: "diff" }, scroll: "c-ndv" },

  { id: "delay-collinear", group: DT,
    text: "With collinear lenses and a delay, the peak falls with the temporal overlap of the two pulses, exp(−2 ln 2 Δt²/τ²), to one half at Δt = 0.71τ and one quarter at Δt = τ, at all NAs.",
    opens: "Opens Pulse results with the peak of the total 2CE against the delay at θ = 0 (scalar model, NA 0.5, air); for 20 fs, Δt = τ is at N = 8.6.",
    preset: { mode: "psum", rdth: 0, rdt: 20, rdn: 8 }, scroll: "c-dpk" },
  { id: "delay-crossed", group: DT,
    text: "With crossed lenses and a delay, the peak falls with the temporal overlap of the two pulses, to about one quarter at Δt = τ.",
    opens: "Opens Pulse results with the peak of the total 2CE against the delay at θ = π/2 (scalar model, NA 0.5, air); for 20 fs, Δt = τ is at N = 8.6.",
    preset: { mode: "psum", rdth: 90, rdt: 20, rdn: 8 }, scroll: "c-dpk" },
  { id: "delay-facing", group: DT,
    text: "With facing lenses and a delay, shorter pulses keep more of the peak at Δt = τ, since the meeting point of the two pulses moves a shorter distance.",
    opens: "Opens Pulse results with the peak of the total 2CE against the delay at θ = π (scalar model, NA 0.5, air); Δt = τ is at N = 4.3 for 10 fs and N = 8.6 for 20 fs.",
    preset: { mode: "psum", rdth: 180, rdt: 10, rdn: 4 }, scroll: "c-dpk" },
  { id: "delay-facing-lowna", group: DT,
    text: "With facing lenses at low NA, the delayed pulses still meet inside the long focus, so the 2CE peak moves along the axis and is kept. At NA 0.1 and 100 fs the peak at Δt = τ is 0.93 of the peak without delay, 14 µm from the focus.",
    opens: "Opens Pulse results at Delay between the pulses, against NA, with the position of the 2CE peak against the delay and the line cΔt/2, θ = π, 100 fs (vector model, air); the chart beside it gives the peak.",
    preset: { mode: "psum", xth: 180, xtau: 100, xnas: "10.20.30.50.70.90" }, scroll: "c-xpos" },
  { id: "delay-facing-highna", group: DT,
    text: "With facing lenses at NA 0.5 and above, the 2CE peak stays at the focus and falls with the temporal overlap of the two pulses, to 0.26 of the peak without delay at Δt = τ and NA 0.5.",
    opens: "Opens Pulse results at Delay between the pulses, against NA, with the 2CE peak against Δt/τ at NA 0.5, 0.7 and 0.9 and the temporal overlap (dotted), θ = π, 100 fs (vector model, air).",
    preset: { mode: "psum", xth: 180, xtau: 100, xnas: "50.70.90" }, scroll: "c-xpk" },
  { id: "delay-pupils", group: DT,
    text: "With facing lenses, pupils with a longer depth of focus keep more of the 2CE peak under a delay: at NA 0.3, 100 fs and Δt = τ, 0.32 for the circular pupil and 0.80 for the annular pupil with ε = 0.9.",
    opens: "Opens Pulse results at Delay between the pulses, against NA, with the 2CE peak at Δt = τ against NA for the circular pupil, the Gaussian input and the annular pupils, θ = π, 100 fs (vector model, air).",
    preset: { mode: "psum", xth: 180, xtau: 100 }, scroll: "c-xpu" },
  { id: "delay-fringes", group: DT,
    text: "Below 20 fs, phase-locked pulses with all photon pairs give fringes in the 2CE peak against the delay, with periods of 2.19, 2.50 and 1.17 fs. The 350-nm pairs alone fall smoothly.",
    opens: "Opens Pulse results at Delay between the pulses, against NA, with all pairs and the 350-nm pairs against the delay on the grid of 0.1 fs, θ = 0, 5 fs, NA 0.5 (vector model, air).",
    preset: { mode: "psum", xth: 0, xtau: 5, xna: 0.5, xpol: "s" }, scroll: "c-xfi" },
  { id: "delay-polarization", group: DT,
    text: "With crossed lenses and the polarization in the plane of the lens axes, the fringes against the delay are about a quarter as deep as with the polarization perpendicular to that plane (0.05 against 0.21 at NA 0.5 and 5 fs), because the two fields are perpendicular at the focus.",
    opens: "Opens Pulse results at Delay between the pulses, against NA, with all pairs and the 350-nm pairs against the delay, θ = π/2, 5 fs, NA 0.5, polarization in the plane of the lens axes; the control of the polarization switches to the other one.",
    preset: { mode: "psum", xth: 90, xtau: 5, xna: 0.5, xpol: "p" }, scroll: "c-xfi" },
];
