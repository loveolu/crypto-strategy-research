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


def test_mc_small_sample_still_short_circuits():
    """Fewer than 30 trades still returns NaNs rather than fabricating a distribution."""
    trades, rets = synthetic_trades(n=10), synthetic_returns()
    mc = V.monte_carlo(rets, trades, n_sims=100)
    assert np.isnan(mc["mc_p5_sharpe"])


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
