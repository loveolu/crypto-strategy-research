#!/usr/bin/env python3
"""Regression tests for user_data/research/validator.py.

Runs standalone or under pytest:

    python scripts/test_validator.py
    pytest scripts/test_validator.py -q -o addopts=""

Scope is deliberately narrow: only defects under active repair. The full
golden-value suite is A-003 in research/OPS_BACKLOG.md and is not this file.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "validator_under_test", REPO_ROOT / "user_data" / "research" / "validator.py")
V = importlib.util.module_from_spec(_spec)
sys.modules["validator_under_test"] = V
_spec.loader.exec_module(V)


# --------------------------------------------------------------------------- #
#  Fixtures
# --------------------------------------------------------------------------- #

def synthetic_trades(n: int = 120, seed: int = 7) -> pd.DataFrame:
    """A trade log with genuinely nonzero P&L variance."""
    rng = np.random.default_rng(seed)
    pnl = rng.normal(0.012, 0.05, n)          # mean > 0, sd 5% -> real dispersion
    idx = pd.date_range("2020-01-01", periods=n, freq="7D", tz="UTC")
    return pd.DataFrame({
        "entry": idx, "exit": idx + pd.Timedelta(days=3),
        "side": 1, "bars": 3, "pnl": pnl,
    })


def synthetic_returns(n_bars: int = 900, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0006, 0.02, n_bars)
    idx = pd.date_range("2020-01-01", periods=n_bars, freq="D", tz="UTC")
    return pd.DataFrame({
        "position": 1.0, "ret_gross": r, "ret_net": r,
        "equity": (1 + pd.Series(r, index=idx)).cumprod(),
    }, index=idx)


# --------------------------------------------------------------------------- #
#  ITEM 1 — monte_carlo() must not return a degenerate distribution
# --------------------------------------------------------------------------- #

def test_mc_sharpe_percentiles_are_distinct():
    """p5 < p50 < p95 for Sharpe on a sample with real variance.

    Permuting a P&L vector leaves mean, std and prod(1+x) unchanged, so a
    permutation-only Monte Carlo produces N identical sims: p5 == p50 == p95 and
    the "5th percentile" is the point estimate wearing a percentile label. The
    MC gate in validate() then tests nothing.
    """
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=500)
    p5, p50, p95 = mc["mc_p5_sharpe"], mc["mc_p50_sharpe"], mc["mc_p95_sharpe"]
    spread = p95 - p5
    assert spread > 1e-6, (
        f"Sharpe percentiles are degenerate: p5={p5!r} p50={p50!r} p95={p95!r} "
        f"spread={spread:.3e}. A permutation-invariant statistic cannot produce a "
        f"distribution.")
    assert p5 < p50 < p95, f"percentiles not ordered: {p5} {p50} {p95}"


def test_mc_return_percentiles_are_distinct():
    """Same for terminal return: cumprod(1+x) is permutation-invariant too."""
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=500)
    p5, p50 = mc["mc_p5_return"], mc["mc_p50_return"]
    assert abs(p50 - p5) > 1e-6, (
        f"terminal-return percentiles are degenerate: p5={p5!r} p50={p50!r}")
    assert p5 < p50


def test_mc_maxdd_distribution_exists_and_is_dispersed():
    """MaxDD is order-DEPENDENT, so permutation is the right tool and must disperse."""
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=500)
    for k in ("mc_p50_maxdd", "mc_p95_maxdd"):
        assert k in mc, f"missing MaxDD percentile {k}"
    # p95 is the WORST tail (most negative); p50 the median path
    assert mc["mc_p95_maxdd"] < mc["mc_p50_maxdd"], (
        f"MaxDD distribution not dispersed: p50={mc['mc_p50_maxdd']} "
        f"p95={mc['mc_p95_maxdd']}")
    assert mc["mc_p95_maxdd"] <= 0.0


def test_mc_n_sims_is_reachable_from_validate():
    """validate() must be able to set n_sims; it must not be hardcoded downstream."""
    import inspect
    assert "n_sims" in inspect.signature(V.validate).parameters, (
        "validate() does not expose n_sims")
    assert "n_sims" in inspect.signature(V.monte_carlo).parameters


def test_mc_reports_seed_provenance():
    """The Verdict must say whether the MC figure is single-seed or multi-seed."""
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=200)
    assert "mc_seeds" in mc, "monte_carlo() does not report its seed provenance"
    assert "mc_seed_spread_p5_sharpe" in mc, (
        "monte_carlo() does not report cross-seed spread of the gated statistic")


def test_mc_gate_statistic_is_stable_across_seeds():
    """The gated statistic (p5 Sharpe) must not swing wildly on seed choice."""
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=500)
    assert len(mc["mc_seeds"]) >= 5, "fewer than 5 seeds used"
    assert mc["mc_seed_spread_p5_sharpe"] < abs(mc["mc_p5_sharpe"]) + 1.0, (
        "p5 Sharpe is unstable across seeds")


def test_mc_gate_status_classification():
    """Exhaustive, deterministic classification from per-seed p5 values."""
    assert V.mc_gate_status([0.1, 0.2, 0.05, 0.3, 0.02]) == V.MC_PASS
    assert V.mc_gate_status([-0.1, -0.2, -0.05]) == V.MC_FAIL
    # a single non-positive seed is enough to deny PASS
    assert V.mc_gate_status([0.1, 0.2, -0.01, 0.3]) == V.MC_INSUFFICIENT
    assert V.mc_gate_status([-0.05, 0.2]) == V.MC_INSUFFICIENT
    # exactly zero is NOT > 0, so it cannot contribute to a PASS
    assert V.mc_gate_status([0.0, 0.1]) == V.MC_INSUFFICIENT
    assert V.mc_gate_status([0.0, -0.1]) == V.MC_FAIL
    assert V.mc_gate_status([]) == V.MC_INSUFFICIENT
    assert V.mc_gate_status([float("nan")]) == V.MC_INSUFFICIENT


def test_mc_gate_is_not_the_pooled_threshold():
    """A straddling seed set must not be rescued by a positive pooled figure.

    This is the regression: thresholding the pooled p5 would call
    [+0.05, -0.03, -0.08, -0.02, +0.08] a PASS or FAIL depending only on which
    side of zero the pool happened to land.
    """
    straddle = [0.0484, -0.0341, -0.0816, -0.0176, 0.0814]
    assert V.mc_gate_status(straddle) == V.MC_INSUFFICIENT
    assert V.mc_gate_status([abs(x) for x in straddle]) == V.MC_PASS
    assert V.mc_gate_status([-abs(x) for x in straddle]) == V.MC_FAIL


def test_mc_gate_reported_and_consistent_with_per_seed_values():
    trades, rets = synthetic_trades(), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=200)
    assert mc["mc_gate"] in (V.MC_PASS, V.MC_FAIL, V.MC_INSUFFICIENT)
    assert mc["mc_gate"] == V.mc_gate_status(mc["mc_p5_sharpe_per_seed"]), (
        "reported gate disagrees with its own per-seed values")


def test_mc_insufficient_lands_on_verdict_warnings():
    """An INSUFFICIENT gate must surface as a warning, not just a reason string."""
    per_seed = [0.05, -0.03, -0.08, -0.02, 0.08]
    assert V.mc_gate_status(per_seed) == V.MC_INSUFFICIENT
    msg = V.MC_INSUFFICIENT_WARNING.format(vals=per_seed, pooled=-0.01)
    assert "PARK, never PROMOTE" in msg
    assert "PRE-REGISTERED" in msg


def test_mc_maxdd_carries_its_limitation_in_the_docstring():
    """The permuted MaxDD must not be silently usable for promotion criterion 4."""
    doc = V.monte_carlo.__doc__
    assert "MUST NOT be used for promotion criterion 4" in doc
    assert "volatility clustering" in doc


def test_mc_small_sample_still_short_circuits():
    """Fewer than 30 trades still returns NaNs rather than fabricating a distribution."""
    trades, rets = synthetic_trades(n=10), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=100)
    assert np.isnan(mc["mc_p5_sharpe"])


# --------------------------------------------------------------------------- #
#  ITEM 2 — signal_fn must be computed ONCE on the full series, not per split
# --------------------------------------------------------------------------- #

def _warmup_ohlcv(n_bars: int = 1200, seed: int = 11) -> pd.DataFrame:
    """Trending-ish OHLCV long enough for a 200-bar indicator to matter."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0008, 0.02, n_bars)))
    idx = pd.date_range("2019-01-01", periods=n_bars, freq="D", tz="UTC")
    return pd.DataFrame({
        "open": close, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": 1000.0,
    }, index=idx)


def _long_warmup_signal(d: pd.DataFrame) -> pd.Series:
    """SMA200 regime filter — needs 200 bars of history before it says anything."""
    return (d["close"] > d["close"].rolling(200).mean()).astype(float).fillna(0.0)


def test_warmup_placement_materially_changes_metrics():
    """Fixture guard: the two approaches MUST differ, or this file proves nothing.

    Slicing before computing restarts a 200-bar indicator inside a 180-bar TEST
    window, so the signal is NaN for the entire slice: 0 trades, Sharpe 0.0000,
    regardless of merit. Computing once and slicing keeps the warmup the earlier
    data already provides — which is also what live trading would have.

    This asserts the defect is real and the fixture exercises it. The assertion
    that validator.py takes the CORRECT branch is
    test_validate_computes_signal_once_on_full_series.
    """
    df = _warmup_ohlcv()
    _, _, df_te = V.split_70_15_15(df)
    assert len(df_te) < 200, "fixture no longer exercises warmup truncation"

    sig_full = _long_warmup_signal(df)
    rets_a = V.signal_to_returns(df_te, sig_full.reindex(df_te.index))
    m_a = V.metrics(rets_a, V.extract_trades(rets_a))

    sig_sliced = _long_warmup_signal(df_te)
    rets_b = V.signal_to_returns(df_te, sig_sliced)
    m_b = V.metrics(rets_b, V.extract_trades(rets_b))

    assert m_b["n_trades"] == 0 and m_b["sharpe"] == 0.0, (
        "slice-first should be structurally empty on this fixture, got "
        f"{m_b['n_trades']} trades / Sharpe {m_b['sharpe']}")
    assert m_a["n_trades"] > 0, "compute-once should produce trades"


def test_validate_computes_signal_once_on_full_series():
    """validate()'s TEST metrics must match the compute-once-then-slice result."""
    df = _warmup_ohlcv()
    v = V.validate("warmup_check", df, _long_warmup_signal, n_trials=1, n_sims=50)

    _, _, df_te = V.split_70_15_15(df)
    sig_full = _long_warmup_signal(df)
    rets = V.signal_to_returns(df_te, sig_full.reindex(df_te.index))
    expected = V.metrics(rets, V.extract_trades(rets))

    assert v.test["n_trades"] == expected["n_trades"], (
        f"validate() TEST trades {v.test['n_trades']} != compute-once {expected['n_trades']}")
    assert abs(v.test["sharpe"] - expected["sharpe"]) < 1e-9, (
        f"validate() TEST Sharpe {v.test['sharpe']} != compute-once {expected['sharpe']}")


def test_walk_forward_windows_are_warmup_invariant():
    """Same defect inside walk_forward: each OOS window restarted the indicator."""
    df = _warmup_ohlcv()
    sig_full = _long_warmup_signal(df)
    wf = V.walk_forward(df, _long_warmup_signal, signal=sig_full)
    assert wf, "walk_forward produced no windows"
    total = sum(w["n_trades"] for w in wf)
    assert total > 0, (
        "every walk-forward window is empty — the indicator is being restarted "
        "per window and never clears its warmup")


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main() -> int:
    failed = []
    for fn in TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed.append(fn.__name__)
            print(f"  FAIL  {fn.__name__}: {type(exc).__name__}: {exc}")
    print()
    print(f"{len(TESTS) - len(failed)}/{len(TESTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
