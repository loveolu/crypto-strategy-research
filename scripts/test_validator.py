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


def test_walk_forward_warns_on_silent_per_window_fallback():
    """The degraded path must announce itself, like the DSR estimator proxy does."""
    import warnings as _w
    df = _warmup_ohlcv()

    with _w.catch_warnings(record=True) as caught:
        _w.simplefilter("always")
        wf_bad = V.walk_forward(df, _long_warmup_signal)
    assert any(issubclass(c.category, V.ValidatorWarning) for c in caught), (
        "per-window warmup fallback was silent")
    assert all(x["warmup_mode"] == "per_window" for x in wf_bad)

    with _w.catch_warnings(record=True) as caught2:
        _w.simplefilter("always")
        wf_ok = V.walk_forward(df, _long_warmup_signal, signal=_long_warmup_signal(df))
    assert not [c for c in caught2 if issubclass(c.category, V.ValidatorWarning)], (
        "correct path must not warn")
    assert all(x["warmup_mode"] == "full_series" for x in wf_ok)


def test_validator_warnings_survive_the_blanket_ignore():
    """validator.py sets filterwarnings('ignore'); ValidatorWarning must escape it."""
    import warnings as _w
    with _w.catch_warnings(record=True) as caught:
        _w.resetwarnings()
        _w.filterwarnings("ignore")            # reproduce the module-level state
        _w.simplefilter("always", V.ValidatorWarning)
        _w.warn("integrity", V.ValidatorWarning)
        _w.warn("noise", UserWarning)
    cats = [c.category.__name__ for c in caught]
    assert "ValidatorWarning" in cats, "harness-integrity warning was swallowed"


# --------------------------------------------------------------------------- #
#  ITEM 3 — date-pinned splits and a reserved-holdout guard
# --------------------------------------------------------------------------- #

def _series_spanning_holdout(n_bars: int = 900, seed: int = 3) -> pd.DataFrame:
    """OHLCV ending 2026-07-18, i.e. past the declared holdout boundary."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, n_bars)))
    idx = pd.date_range(end="2026-07-18", periods=n_bars, freq="D", tz="UTC")
    return pd.DataFrame({
        "open": close, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": 1000.0,
    }, index=idx)


def test_holdout_guard_raises_on_series_past_boundary():
    df = _series_spanning_holdout()
    assert df.index.max() > V.RESERVED_HOLDOUT_AFTER
    try:
        V.assert_no_holdout(df, label="test-split")
        raise AssertionError("guard did not raise on a series past the boundary")
    except V.HoldoutViolation as exc:
        assert "test-split" in str(exc)
        assert str(V.RESERVED_HOLDOUT_AFTER.date()) in str(exc)


def test_holdout_guard_passes_on_clean_series():
    df = _series_spanning_holdout()
    clean = df.loc[:V.RESERVED_HOLDOUT_AFTER]
    V.assert_no_holdout(clean, label="clean")     # must not raise


def test_holdout_guard_counts_and_names_the_offending_bars():
    df = _series_spanning_holdout()
    try:
        V.assert_no_holdout(df, label="x")
    except V.HoldoutViolation as exc:
        msg = str(exc)
        n = int((df.index > V.RESERVED_HOLDOUT_AFTER).sum())
        assert str(n) in msg, f"guard did not report the offending bar count {n}: {msg}"


def test_split_by_dates_honours_explicit_boundaries():
    df = _series_spanning_holdout()
    b = V.RESERVED_HOLDOUT_AFTER
    d1, d2 = b - pd.Timedelta(days=400), b - pd.Timedelta(days=200)
    tr, vl, te = V.split_by_dates(df, d1, d2, b)
    assert tr.index.max() <= d1
    assert vl.index.min() > d1
    assert vl.index.max() <= d2
    assert te.index.min() > d2
    assert te.index.max() <= b
    # nothing past the boundary survives
    for name, seg in (("train", tr), ("val", vl), ("test", te)):
        assert (seg.index <= V.RESERVED_HOLDOUT_AFTER).all(), f"{name} leaked holdout bars"


def test_split_by_dates_rejects_unordered_dates():
    df = _series_spanning_holdout()
    try:
        V.split_by_dates(df, "2025-12-31", "2025-06-30", "2025-09-19")
        raise AssertionError("unordered split dates were accepted")
    except ValueError:
        pass


def test_validate_raises_when_data_extends_past_holdout():
    """Fractional splits on today's feathers put holdout bars in TEST."""
    df = _series_spanning_holdout()
    try:
        V.validate("holdout_leak", df, _long_warmup_signal, n_trials=1, n_sims=20)
        raise AssertionError("validate() accepted a series extending past the holdout")
    except V.HoldoutViolation:
        pass


def test_validate_accepts_date_pinned_splits_inside_the_boundary():
    b = V.RESERVED_HOLDOUT_AFTER
    df = _series_spanning_holdout()
    df = df.loc[df.index <= b]
    v = V.validate("pinned", df, _long_warmup_signal, n_trials=1, n_sims=20,
                   split_dates=(b - pd.Timedelta(days=400), b - pd.Timedelta(days=200), b))
    assert v.splits["mode"] == "date_pinned"
    assert v.splits["test_end"] == str(b.date())


def test_fractional_split_is_deprecated():
    import warnings as _w
    df = _series_spanning_holdout()
    with _w.catch_warnings(record=True) as caught:
        _w.simplefilter("always")
        V.split_70_15_15(df)
    assert any(issubclass(c.category, V.ValidatorWarning) for c in caught), (
        "split_70_15_15 did not announce that it is deprecated")


# --------------------------------------------------------------------------- #
#  ITEM 4 — bars_per_year must reach walk_forward() and monte_carlo()
# --------------------------------------------------------------------------- #

def _intraday_ohlcv(n_bars: int = 3000, seed: int = 5) -> pd.DataFrame:
    """Hourly-style series ending well before the holdout boundary."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.00005, 0.004, n_bars)))
    idx = pd.date_range(end=V.RESERVED_HOLDOUT_AFTER, periods=n_bars, freq="h", tz="UTC")
    return pd.DataFrame({
        "open": close, "high": close * 1.002, "low": close * 0.998,
        "close": close, "volume": 100.0,
    }, index=idx)


def _fast_signal(d: pd.DataFrame) -> pd.Series:
    return (d["close"] > d["close"].rolling(48).mean()).astype(float).fillna(0.0)


def test_walk_forward_honours_bars_per_year():
    """WF window Sharpes must scale with bars_per_year, like every other Sharpe."""
    df = _intraday_ohlcv()
    sig = _fast_signal(df)
    wf_d = V.walk_forward(df, _fast_signal, signal=sig, bars_per_year=365)
    wf_h = V.walk_forward(df, _fast_signal, signal=sig, bars_per_year=8760)
    assert wf_d and len(wf_d) == len(wf_h)
    # metrics() rounds Sharpe to 4 dp, so on a near-zero window Sharpe the ratio is
    # rounding-dominated. Skip those and use a RELATIVE tolerance; 1% is still ~400x
    # tighter than the defect under test (ratio 1.0 vs 4.9).
    expected = np.sqrt(8760 / 365)          # sqrt(24) ~= 4.899
    for a, b in zip(wf_d, wf_h):
        if abs(a["sharpe"]) < 0.05:
            continue
        ratio = b["sharpe"] / a["sharpe"]
        assert abs(ratio - expected) / expected < 1e-2, (
            f"WF window {a['window']} Sharpe did not scale: {a['sharpe']} -> "
            f"{b['sharpe']} (ratio {ratio:.4f}, expected {expected:.4f})")


def test_monte_carlo_honours_bars_per_year():
    trades, rets = synthetic_trades(), synthetic_returns()
    mc_d = V.monte_carlo(rets, trades, n_sims=100, bars_per_year=365)
    mc_h = V.monte_carlo(rets, trades, n_sims=100, bars_per_year=8760)
    expected = np.sqrt(8760 / 365)
    ratio = mc_h["mc_p50_sharpe"] / mc_d["mc_p50_sharpe"]
    assert abs(ratio - expected) < 1e-6, (
        f"MC Sharpe did not scale: ratio {ratio:.4f}, expected {expected:.4f}")


def test_verdict_full_and_wf_sharpes_scale_consistently():
    """The defect: on hourly data one Verdict mixed 365- and 8760-annualised Sharpes.

    Full-window Sharpe took bars_per_year from validate(); walk-forward hardcoded
    365. The two therefore differed by sqrt(24) = 4.9x inside a single Verdict.
    """
    df = _intraday_ohlcv()
    b = V.RESERVED_HOLDOUT_AFTER
    dates = (b - pd.Timedelta(days=60), b - pd.Timedelta(days=30), b)
    v_d = V.validate("ann365", df, _fast_signal, n_trials=1, n_sims=50,
                     split_dates=dates, bars_per_year=365)
    v_h = V.validate("ann8760", df, _fast_signal, n_trials=1, n_sims=50,
                     split_dates=dates, bars_per_year=8760)
    expected = np.sqrt(8760 / 365)

    full_ratio = v_h.full["sharpe"] / v_d.full["sharpe"]
    assert abs(full_ratio - expected) / expected < 1e-2, f"full-window ratio {full_ratio}"

    assert v_d.wf and len(v_d.wf) == len(v_h.wf)
    for a, b in zip(v_d.wf, v_h.wf):
        if abs(a["sharpe"]) < 0.05:
            continue
        wf_ratio = b["sharpe"] / a["sharpe"]
        assert abs(wf_ratio - full_ratio) / full_ratio < 1e-2, (
            f"walk-forward window {a['window']} annualised on a different basis "
            f"than the full window in the SAME Verdict: wf ratio {wf_ratio:.4f} vs "
            f"full ratio {full_ratio:.4f}")


# --------------------------------------------------------------------------- #
#  ITEM 5 — DSR window, ledger writer, basis, entry point
# --------------------------------------------------------------------------- #

def _tmp_ledger(rows, basis="per_bar"):
    """Write a throwaway ledger. Never touches the real one."""
    import tempfile
    p = Path(tempfile.mkdtemp(prefix="ledger_")) / "trial_sharpe_ledger.csv"
    lines = ["# synthetic test ledger",
             "trial,task_id,construct,sr_hat_per_trade,n_obs,basis,date"]
    for i, (sr, b) in enumerate(rows, 1):
        lines.append(f"{i},T-{100+i},c{i},{sr},500,{b or basis},2026-08-01")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


# --- (a) DSR must be computed on the promotion series -----------------------

def test_dsr_is_computed_on_the_test_split():
    """Criterion 1 must gate the same series criteria 2-4 judge: the TEST split."""
    b = V.RESERVED_HOLDOUT_AFTER
    df = _series_spanning_holdout()
    df = df.loc[df.index <= b]                      # holdout excluded by the caller
    dates = (b - pd.Timedelta(days=400), b - pd.Timedelta(days=200), b)
    v = V.validate("dsr_window", df, _long_warmup_signal, n_trials=3, n_sims=20,
                   split_dates=dates)
    _, _, df_te = V.split_by_dates(df, *dates)
    sig = _long_warmup_signal(df)
    rets_te = V.signal_to_returns(df_te, sig.reindex(df_te.index))
    expected_n = len(rets_te["ret_net"].dropna())

    assert v.dsr.get("window") == "test_split", (
        f"DSR window is {v.dsr.get('window')!r}, expected 'test_split'")
    assert v.dsr["n_obs"] == expected_n, (
        f"DSR n_obs {v.dsr['n_obs']} != TEST-split length {expected_n}")
    # the full-window figure must still be reported, clearly labelled, as diagnostic
    assert "dsr_full_window_diagnostic" in v.dsr


# --- (b) the ledger must have a writer --------------------------------------

def test_append_trial_writes_and_numbers_rows():
    p = _tmp_ledger([])
    r1 = V.append_trial("T-038", "alpha", 0.031, 480, "per_bar", path=p)
    r2 = V.append_trial("T-038", "beta", 0.014, 480, "per_bar", path=p)
    assert r1["trial"] == 1 and r2["trial"] == 2, (r1, r2)
    rows = V.read_trial_ledger(p)
    assert len(rows) == 2
    assert rows[1]["construct"] == "beta"
    assert rows[1]["basis"] == "per_bar"


def test_append_trial_rejects_bad_basis():
    p = _tmp_ledger([])
    try:
        V.append_trial("T-038", "x", 0.01, 100, "per_candle", path=p)
        raise AssertionError("accepted an invalid basis")
    except ValueError as exc:
        assert "basis" in str(exc)


# --- (c) bases must not be mixed --------------------------------------------

def test_trial_variance_refuses_to_mix_bases():
    rows = [(0.02 + i * 0.005, "per_bar") for i in range(9)]
    rows.append((0.09, "per_trade"))          # one contaminating row
    p = _tmp_ledger(rows)
    try:
        V.trial_sharpe_variance(p)
        raise AssertionError("averaged across mixed bases instead of raising")
    except V.LedgerBasisError as exc:
        assert "per_bar" in str(exc) and "per_trade" in str(exc)


def test_trial_variance_works_on_a_single_basis():
    rows = [(0.02 + i * 0.005, "per_bar") for i in range(12)]
    p = _tmp_ledger(rows)
    tv = V.trial_sharpe_variance(p)
    assert tv["source"] == "trials"
    assert tv["basis"] == "per_bar"
    assert tv["n_trials_recorded"] == 12


# --- (d) validate() must require n_trials -----------------------------------

def test_validate_requires_n_trials():
    import inspect
    p = inspect.signature(V.validate).parameters["n_trials"]
    assert p.default is inspect.Parameter.empty, (
        "n_trials still has a default, so DSR can be silently skipped")


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
