"""Tests for the multi-trial harness — reproducibility, statistics, round-trip."""

import numpy as np

from mcdo.trials import run_trials, summarize, save_trials, load_trials


def test_run_trials_reproducible_and_independent():
    """Same base_seed → identical trials; different seeds → different draws."""
    f = lambda rng: rng.normal(size=4)
    a, sa = run_trials(f, n_trials=6, base_seed=0)
    b, _ = run_trials(f, n_trials=6, base_seed=0)
    assert a.shape == (6, 4)
    assert np.array_equal(sa, np.arange(6))
    assert np.allclose(a, b)              # reproducible
    assert not np.allclose(a[0], a[1])    # independent seeds differ


def test_summarize_matches_numpy():
    trials = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    mean, std, sem = summarize(trials)
    assert np.allclose(mean, [3.0, 4.0])
    assert np.allclose(std, np.std(trials, axis=0, ddof=1))
    assert np.allclose(sem, std / np.sqrt(3))


def test_save_load_roundtrip(tmp_path):
    """Saved .npz round-trips per-trial data + stats + metadata."""
    trials, seeds = run_trials(lambda rng: rng.random(3), n_trials=10)
    p = str(tmp_path / "t.npz")
    save_trials(p, trials, seeds, N=1234, label="x")
    d = load_trials(p)
    assert d["trials"].shape == (10, 3)
    assert int(d["n_trials"]) == 10 and int(d["N"]) == 1234
    assert np.allclose(d["mean"], trials.mean(0))
    assert np.allclose(d["std"], trials.std(0, ddof=1))
