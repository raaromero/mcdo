// Data written by scripts/dashboard_cambaliza_data.py: widths against NA, the wavelength gap, and profiles per NA.

export type Medium = "air" | "water";
export type Signal = "2PE" | "2CE";
export type Axis = "x" | "z";
export type Theta = "0" | "pi2" | "pi";
export type Model = "vector" | "scalar";
export type Pupil = "circ" | "ann";
export type Input = "uni" | "gau";

export type Meta = { na: Record<Medium, number[]>; n: Record<Medium, number>; lam: { l1: number; l2: number; lp: number } };
export type Widths = Record<string, [number, number][]>; // "signal|axis|theta|model|pupil|input|medium" -> [NA, FWHM µm]
export type DLambda = Record<string, [number, number][]>; // "medium|NA|axis|model" -> [Δλ nm, FWHM µm]
export type Profiles = Record<string, number[]>; // "signal|axis|theta|model|pupil|input" -> values; "grid|axis" -> [half, n]

export type Data = { meta: Meta; widths: Widths; dlambda: DLambda };

export const THETAS: Theta[] = ["0", "pi2", "pi"];
export const THETA_LABEL: Record<Theta, string> = { "0": "θ = 0", pi2: "θ = π/2", pi: "θ = π" };

const get = async <T>(path: string): Promise<T> => {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json() as Promise<T>;
};

export async function loadData(): Promise<Data> {
  const [meta, widths, dlambda] = await Promise.all([
    get<Meta>("./data/meta.json"), get<Widths>("./data/widths.json"), get<DLambda>("./data/dlambda.json")]);
  return { meta, widths, dlambda };
}

const cache = new Map<string, Promise<Profiles>>();
export function loadProfiles(medium: Medium, na: number): Promise<Profiles> {
  const key = `${medium}_${+na.toFixed(3)}`;
  if (!cache.has(key)) cache.set(key, get<Profiles>(`./data/profiles/${key}.json`));
  return cache.get(key)!;
}

export const wkey = (s: Signal, a: Axis, t: Theta, m: Model, p: Pupil, i: Input, med: Medium) => `${s}|${a}|${t}|${m}|${p}|${i}|${med}`;

/** FWHM at one NA (µm), or undefined where it is not computed (crossed lenses that do not fit). */
export function widthAt(w: Widths, key: string, na: number): number | undefined {
  return w[key]?.find((p) => Math.abs(p[0] - na) < 1e-6)?.[1];
}

/** Crossed lenses fit at 90° up to NA = n sin 45°. */
export const fits = (t: Theta, na: number, n: number) => t !== "pi2" || na <= n * Math.SQRT1_2 + 1e-9;

export const fmtUm = (v: number) => (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v >= 1 ? v.toFixed(2) : v.toFixed(3));
