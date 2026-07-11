r"""Multi-trial Monte-Carlo harness.

Every Monte-Carlo experiment should report *statistics*, not a single
realization: run the estimator over several independent seeds, keep the
per-trial data, and report mean ± standard deviation (and the standard error of
the mean). This module is the small, reusable layer that does that — used by the
clear-limit studies and by the Phase-6b scattering runs.

The convention throughout the project is **≥10 trials** (5 minimum), with the
per-trial array saved to ``.npz`` alongside its mean/std/sem, the seed list, and
free-form metadata, so any result is reproducible and its error bar is on record.

Examples
--------
>>> import numpy as np
>>> from mcdo.trials import run_trials, summarize
>>> trials, seeds = run_trials(lambda rng: rng.normal(size=3), n_trials=10)
>>> mean, std, sem = summarize(trials)
"""

import os
import numpy as np


def run_trials(fn, n_trials=10, base_seed=0):
    r"""Run ``fn(rng)`` over ``n_trials`` independent seeds and stack the results.

    Parameters
    ----------
    fn : callable
        ``fn(rng) -> ndarray`` (or scalar). Must accept a
        ``numpy.random.Generator`` and return the same shape on every call.
        Seeding lives entirely here, so trials are independent and reproducible.
    n_trials : int, optional
        Number of independent trials (default 10; the project minimum is 5).
    base_seed : int, optional
        Trial ``i`` uses ``default_rng(base_seed + i)``.

    Returns
    -------
    trials : ndarray, shape ``(n_trials, *result_shape)``
        Stacked per-trial results.
    seeds : ndarray, shape ``(n_trials,)``
        The seeds used (``base_seed + arange(n_trials)``).
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    seeds = base_seed + np.arange(n_trials)
    out = [np.asarray(fn(np.random.default_rng(int(s)))) for s in seeds]
    return np.stack(out, axis=0), seeds


def summarize(trials):
    r"""Mean, sample std (``ddof=1``) and standard error over the trial axis.

    Parameters
    ----------
    trials : ndarray, shape ``(n_trials, ...)``

    Returns
    -------
    mean, std, sem : ndarray
        Per-element mean, standard deviation, and standard error of the mean
        (``std/√n``) across trials.
    """
    trials = np.asarray(trials)
    n = trials.shape[0]
    mean = trials.mean(axis=0)
    std = trials.std(axis=0, ddof=1) if n > 1 else np.zeros_like(mean)
    return mean, std, std / np.sqrt(n)


def save_trials(path, trials, seeds, **meta):
    r"""Save per-trial data + mean/std/sem + seeds + metadata to a ``.npz``.

    Parameters
    ----------
    path : str
        Output ``.npz`` path (parent dirs are created).
    trials : ndarray, shape ``(n_trials, ...)``
    seeds : array_like
    **meta
        Extra arrays/scalars recorded alongside (e.g. ``N=...``, ``label=...``).

    Returns
    -------
    str
        ``path``.
    """
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    mean, std, sem = summarize(trials)
    np.savez_compressed(path, trials=trials, seeds=np.asarray(seeds),
                        mean=mean, std=std, sem=sem,
                        n_trials=trials.shape[0], **meta)
    return path


def load_trials(path):
    r"""Load a trials ``.npz`` into a dict (keys: trials, seeds, mean, std, sem, …)."""
    with np.load(path, allow_pickle=True) as z:
        return {k: z[k] for k in z.files}
