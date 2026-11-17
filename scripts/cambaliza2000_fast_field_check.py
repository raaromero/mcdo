r"""Checks of the tabulated fields (cambaliza2000_fast_field.py) before the pulse sweep may use them.

    1. fields:  the tables against beam_field for every model, medium, NA, pupil, input, angle and cut the queue runs,
                at frequencies spanning the widest spectrum (4-fs pulses at 750 and 656 nm);
    2. sweep:   pulsed profiles from the tables against the same function with beam_field, and against the stored
                results of the current code (na_sweep/*/na*.npz);
    3. papers:  published quantities on the cuts from both, Cambaliza & Saloma (2000), Lim & Saloma (2002),
                Romallosa et al. (2003) and Lim & Saloma (2003).

    PART=1,2,3 python scripts/cambaliza2000_fast_field_check.py   ->  na_sweep/fast_check.txt (appended)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

from mcdo.pulsed2ce import spectrum, C_UM_FS
from mcdo.twobeam import beam_field
from cambaliza2000_fast_field import Focus

PARTS = os.environ.get('PART', '1,2,3').split(',')
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'na_sweep')
LOG = os.path.join(D, 'fast_check.txt')
NS = {'air': 1.0, 'water': 1.33, 'oil': 1.515}
THETAS = (0.0, np.pi / 2, np.pi)


def say(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def apod_of(alpha, na, n):
    return (lambda th: np.exp(-alpha * np.sin(th) ** 2 / (na / n) ** 2)) if alpha else None


def cut_points(na, n, eps, cut, every=1):
    zspan = 5 * n * (0.5 / na) ** 2 / max(1 - eps ** 2, 1e-3) ** (1 if eps else 0)
    s = np.linspace(-zspan, zspan, 2 * int(50 * zspan) + 1) if cut == 'z' else np.linspace(-0.75 / na, 0.75 / na, 301)
    return s[::every] if every > 1 else s


def part1():
    """Largest |E_table − E_beam_field| over the cut, relative to the largest |E| on it, per configuration."""
    sp = [spectrum(l, 4.0) for l in (0.750, 0.656)]
    ws = np.concatenate([w[np.linspace(0, len(w) - 1, 5).astype(int)] for w, _, _ in sp])
    cfgs = []
    for model in ('paraxial', 'rw'):
        for med, nas in (('air', (0.1, 0.3, 0.5, 0.7, 0.9, 0.95)), ('water', (0.5, 0.9, 1.2, 1.25)),
                         ('oil', (0.5, 1.0, 1.4, 1.45))):
            for na in nas:
                cfgs.append((model, med, na, 0.0, 0.0, 0.0))
        for na in (0.3, 0.5, 0.9):
            for eps in (0.5, 0.9, 0.99):
                cfgs.append((model, 'air', na, eps, 0.0, 0.0))
            cfgs.append((model, 'air', na, 0.0, 4.0, 0.0))
        cfgs += [(model, 'water', 1.2, 0.0, 4.0, 0.0), (model, 'oil', 1.4, 0.0, 4.0, 0.0)]
    cfgs += [('paraxial', 'air', 0.5, 0.0, 0.0, sa) for sa in (-60.0, 16.0, 60.0)]        # Lim & Saloma (2003)
    worst = 0.0
    for model, med, na, eps, al, sa in cfgs:
        n = NS[med]
        ap = apod_of(al, na, n)
        F = Focus(na, n, model, eps, ap, sa)
        kw = dict(model='rw', psi=np.pi / 2) if model == 'rw' else dict(sa=sa)
        t0, err = time.time(), 0.0
        for cut in ('z', 'x'):
            s = cut_points(na, n, eps, cut)
            s = s[::max(1, len(s) // 1500)]
            x, z = (0 * s, s) if cut == 'z' else (s, 0 * s)
            for th in THETAS:
                new = F.fields(ws, th, x, z)
                for i, wm in enumerate(ws):
                    old = beam_field(x, z, 2 * np.pi * C_UM_FS / wm, na, n, theta=th, eps=eps, apodization=ap, **kw)
                    old = old if model == 'rw' else old[None]
                    err = max(err, np.abs(new[i] - old).max() / np.abs(old).max())
        worst = max(worst, err)
        say(f'fields {model} {med} NA {na:g} eps {eps:g} alpha {al:g} sa {sa:g}: largest relative difference '
            f'{err:.1e} ({time.time() - t0:.0f} s)')
    say(f'FIELDS largest relative difference over all configurations: {worst:.1e}')


SWEEP_CFGS = [('paraxial', 'air', 0.3, 0, 0), ('paraxial', 'air', 0.9, 0, 0), ('rw', 'air', 0.3, 0, 0),
              ('rw', 'air', 0.9, 0, 0), ('rw', 'air', 0.95, 0, 0), ('rw', 'water', 1.2, 0, 0),
              ('rw', 'oil', 1.4, 0, 0), ('paraxial', 'oil', 1.4, 0, 0), ('rw', 'air', 0.5, 0.5, 0),
              ('rw', 'air', 0.5, 0.9, 0), ('paraxial', 'air', 0.5, 0.99, 0), ('rw', 'air', 0.5, 0.99, 0),
              ('rw', 'air', 0.5, 0, 4), ('rw', 'water', 1.2, 0, 4), ('paraxial', 'air', 0.5, 0, 4)]


def sweep_case(args):
    """One configuration: both pulsed functions on the same points, for the angles, cuts, signals, widths, delays."""
    model, med, na, eps, al = args
    os.environ.update(MODEL=model, MEDIUM=med, EPS=str(eps), APOD=str(al))
    import importlib
    import cambaliza2000_pulses_na_sweep as S
    importlib.reload(S)
    import cambaliza2000_pulses_na_sweep_fast as SF
    importlib.reload(SF)                                                           # patches S.pulsed
    lines, worst, t_old, t_new = [], 0.0, 0.0, 0.0
    old_pulsed = OLD[0]
    for cut in ('z', 'x'):
        s = S.grid(na, cut)
        s = s[::max(1, len(s) // 400)]                                              # the reach keeps max |s|
        for sig in ('2ce', '2pe'):
            for tk, th in (('0', 0.0), ('pi2', np.pi / 2), ('pi', np.pi)):
                if tk == 'pi2' and na > S.N * np.sin(np.pi / 4) + 1e-9:
                    continue
                for tau, dl in ((4.0, 0.0), (20.0, 0.0), (20.0, 1.0), (1000.0, 0.0)):
                    t0 = time.time()
                    p0, c0 = old_pulsed(S, na, tau, th, s, cut, sig, dl * tau)
                    t1 = time.time()
                    p1, c1 = SF.pulsed(na, tau, th, s, cut, sig, dl * tau)
                    t_old, t_new = t_old + t1 - t0, t_new + time.time() - t1
                    d = max(np.abs(p1 / p1.max() - p0 / p0.max()).max(), np.abs(c1 / c1.max() - c0 / c0.max()).max(),
                            abs(p1.max() / p0.max() - 1))
                    worst = max(worst, d)
    return (f'sweep {model} {med} NA {na:g} eps {eps:g} alpha {al:g}: largest difference of the normalized profiles '
            f'and peaks {worst:.1e}; time {t_old:.0f} s with beam_field, {t_new:.0f} s with the tables'), worst


def _old_pulsed(S, na, tau, theta, s, cut, sig, delay=0.0):
    """The sweep's pulsed() as written, with its own beam_field calls (a copy is kept because the import patches it)."""
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
            E = np.stack([S.field(wm, na, th, x, z, w=True) for wm in w])
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


OLD = [_old_pulsed]


def stored_case(args):
    """Profiles stored by the current code, recomputed with the tables on the stored points."""
    folder, f, keys = args
    model, med = folder.split('_')[:2]
    os.environ.update(MODEL=model, MEDIUM=med, EPS='0', APOD='0')
    import importlib
    import cambaliza2000_pulses_na_sweep as S
    importlib.reload(S)
    import cambaliza2000_pulses_na_sweep_fast as SF
    importlib.reload(SF)
    d = np.load(os.path.join(D, folder, f))
    na, worst, t0 = float(d['na']), 0.0, time.time()
    for key in keys:
        sig, tk, cut, tau = key.split('_')
        th = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}[tk]
        p, c = SF.pulsed(na, float(tau), th, d[f'{sig}_{tk}_{cut}_s'], cut, sig)
        worst = max(worst, np.abs(p / p.max() - d[key]).max(), np.abs(c / c.max() - d[key + '_crest']).max())
    return (f'stored {folder} NA {na:g} ({len(keys)} profiles, {time.time() - t0:.0f} s with the tables): largest '
            f'difference {worst:.1e}'), worst


def part2():
    from multiprocessing import Pool
    worst = 0.0
    jobs = []
    for folder in ('paraxial_air', 'rw_air', 'paraxial_water', 'rw_water'):
        for f in sorted(os.listdir(os.path.join(D, folder))):
            if not f.endswith('.npz'):
                continue
            d = np.load(os.path.join(D, folder, f))
            prof = [k.split('_') for k in d.files if k.count('_') == 3 and k.split('_')[3] not in ('s', 'cw')]
            keys = ['_'.join(k) for k in prof if (k[2] == 'x' and k[3] in ('5', '10', '100', '500'))
                    or (k[2] == 'z' and k[3] == '10' and float(d['na']) >= 0.3)]
            jobs.append((folder, f, sorted(set(keys))))
    with Pool(int(os.environ.get('WORKERS', 2))) as pool:
        for msg, w in pool.imap_unordered(sweep_case, SWEEP_CFGS):
            say(msg)
            worst = max(worst, w)
        for msg, w in pool.imap_unordered(stored_case, jobs):
            say(msg)
            worst = max(worst, w)
    say(f'SWEEP largest difference over all configurations: {worst:.1e}')


def part3():
    """Published quantities on the cuts, from beam_field and from the tables (continuous beams)."""
    from cambaliza2000_pulses_sweep import fwhm
    worst = 0.0

    def both(na, n, model, eps, al, sa, lam, th, x, z, psi=np.pi / 2):
        ap = apod_of(al, na, n)
        kw = dict(model='rw', psi=psi) if model == 'rw' else dict(sa=sa)
        old = beam_field(x, z, lam, na, n, theta=th, eps=eps, apodization=ap, **kw)
        old = old if model == 'rw' else old[None]
        new = Focus(na, n, model, eps, ap, sa, psi=psi).fields([2 * np.pi * C_UM_FS / lam], th, x, z)[0]
        return old, new

    def inten(E):
        return (np.abs(E) ** 2).sum(0)

    def profile(na, n, model, eps, al, sa, sig, th, cut, span):
        s = np.linspace(-span, span, 4001)
        x, z = (0 * s, s) if cut == 'z' else (s, 0 * s)
        l1, l2 = (0.750, 0.656) if sig == '2ce' else (0.700, 0.700)
        a1, b1 = both(na, n, model, eps, al, sa, l1, 0.0, x, z)
        a2, b2 = both(na, n, model, eps, al, sa, l2, th, x, z)
        if sig == '2ce':
            return s, inten(a1) * inten(a2), inten(b1) * inten(b2)
        return s, inten(a1 + a2) ** 2, inten(b1 + b2) ** 2

    rows = []
    # Cambaliza & Saloma (2000): NA 0.5, circular and annular (ε = 0.99) pupils, θ = 0, π/2, π
    for eps in (0.0, 0.99):
        for sig in ('2ce', '2pe'):
            for tk, th in (('0', 0.0), ('π/2', np.pi / 2), ('π', np.pi)):
                for cut, span in (('x', 1.0), ('z', 5.0)):
                    rows.append((f'Cambaliza & Saloma (2000), {sig.upper()}, ε = {eps:g}, θ = {tk}, FWHM along {cut} (µm)',
                                 (0.5, 1.0, 'paraxial', eps, 0.0, 0.0, sig, th, cut, span)))
    # Lim & Saloma (2002): vector focus at high NA, uniform and Gaussian (α = 4) input
    for na, n in ((0.9, 1.0), (1.2, 1.33)):
        for al in (0.0, 4.0):
            for tk, th in (('0', 0.0), ('π', np.pi)):
                for cut, span in (('x', 1.0), ('z', 3.0)):
                    rows.append((f'Lim & Saloma (2002), 2CE, NA {na:g}, n {n:g}, α = {al:g}, θ = {tk}, FWHM along {cut} (µm)',
                                 (na, n, 'rw', 0.0, al, 0.0, '2ce', th, cut, span)))
    # Lim & Saloma (2003): primary spherical aberration φ1 = φ2, NA 0.5
    for sa in (16.0, 60.0):
        for tk, th in (('0', 0.0), ('π/2', np.pi / 2), ('π', np.pi)):
            for cut, span in (('x', 1.0), ('z', 5.0)):
                rows.append((f'Lim & Saloma (2003), 2CE, φ = {sa:g}, θ = {tk}, FWHM along {cut} (µm)',
                             (0.5, 1.0, 'paraxial', 0.0, 0.0, sa, '2ce', th, cut, span)))
    for label, args in rows:
        s, yo, yn = profile(*args)
        fo, fn = fwhm(s, yo), fwhm(s, yn)
        d = max(np.abs(yn / yo.max() - yo / yo.max()).max(), abs(yn.max() / yo.max() - 1))
        worst = max(worst, d)
        say(f'papers {label}: {fo:.4f} with beam_field, {fn:.4f} with the tables; profiles differ by {d:.1e}')
    for sa in (16.0, 60.0):                                                          # LS03 Fig. 4, peak at O
        o = [both(0.5, 1.0, 'paraxial', 0.0, 0.0, p, l, 0.0, np.zeros(1), np.zeros(1)) for p in (0.0, sa)
             for l in (0.750, 0.656)]
        po = inten(o[2][0]) * inten(o[3][0]) / (inten(o[0][0]) * inten(o[1][0]))
        pn = inten(o[2][1]) * inten(o[3][1]) / (inten(o[0][1]) * inten(o[1][1]))
        worst = max(worst, abs(pn[0] / po[0] - 1))
        say(f'papers Lim & Saloma (2003), 2CE peak at O, φ = {sa:g} over φ = 0: {po[0]:.6f} with beam_field, '
            f'{pn[0]:.6f} with the tables')
    # Romallosa et al. (2003): focal width across the polarization, NA 0.8, n 1.3, 750 nm; published 472.8 nm
    r = np.linspace(-2.0, 2.0, 8001)
    o, nw = both(0.8, 1.3, 'rw', 0.0, 0.0, 0.0, 0.750, 0.0, r, 0 * r)
    wo, wn = fwhm(r, inten(o)) * 1000, fwhm(r, inten(nw)) * 1000
    worst = max(worst, np.abs(inten(nw) - inten(o)).max() / inten(o).max())
    say(f'papers Romallosa et al. (2003), focal width across the polarization: {wo:.1f} nm with beam_field, '
        f'{wn:.1f} nm with the tables (published 472.8 nm)')
    say(f'PAPERS largest difference over all quantities: {worst:.1e}')


if __name__ == '__main__':
    say(f'--- {time.strftime("%Y-%m-%d %H:%M")} parts {",".join(PARTS)}')
    if '1' in PARTS:
        part1()
    if '3' in PARTS:
        part3()
    if '2' in PARTS:
        part2()
