"""
T-038 — H-BasketVolTarget-1h.  Zero-cost pre-gate ladder P0 -> P4.

Contract: research/NEXT_TASK.md (T-038).  Every construction constant below is
pre-registered there; nothing here is chosen by the Engineer.

WHAT THIS TESTS
---------------
Whether scaling the equal-weight, monthly-rebalanced long basket of the nine
config_perp.json USDT perps by  m_t = min(1, sigma_target / sigma_t)  — sigma an
EWMA of the basket's 1h returns, half-life 48 bars, target = TRAIN median,
re-applied only on a 0.10 drift band — beats the frozen perps benchmark net of
real taker costs.

The ladder is run FIRST and STOPS at the first failure.  A stop spends ZERO
trials (PROJECT_OPERATOR_MANUAL.md, "Zero-cost pre-gate ladder").

    P0  reachability      all nine 1h feathers load, cover the window, no gap >24h
    P1  lead/lag          1h volatility is persistent (Spearman sigma_t vs fwd rv)
    P2  harm census       high-trailing-vol hours are worse PER UNIT RISK
    P3  cost-free bound   timing beats a block-shuffle control, and pays its own
                          turnover in-sample
    P4  TEST activity     the multiplier actually fires inside the TEST window

HOLDOUT / DATE-BOUNDARY NOTE — read before interpreting any number here.
-----------------------------------------------------------------------
The perps reserved-holdout boundary is validator.HOLDOUT_BOUNDARIES["perps"] =
Timestamp("2025-09-19", tz="UTC"), i.e. midnight.  assert_no_holdout() rejects
any bar strictly after that instant, and split_by_dates() slices on `idx <= end`.
Both were written for DAILY bars, where a date label and the bar are the same
thing.  On HOURLY bars they mean "the 00:00 bar of the boundary date and nothing
later", so the last 23 hours of each boundary date are excluded.

NEXT_TASK.md mandates calling assert_no_holdout() on every frame, so this script
takes the guard-compliant reading: the evaluation series ends at 2025-09-19
00:00 UTC.  The cost is 23 hourly bars at each split edge — immaterial to P1-P4
(they are censuses over ~20,000 and ~3,600 bars), but NOT immaterial to the
criterion-3 daily pairing, which needs 151 COMPLETE UTC days.  That conflict is
raised in the report; it is not resolved here.

Run:  python user_data/research/phase_t038_bvt.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "user_data" / "research"))

import validator as V  # noqa: E402  (import-time data-integrity gate runs here)

CONFIG_PERP = REPO_ROOT / "user_data" / "config_perp.json"
FUTURES_DIR = REPO_ROOT / "user_data" / "data" / "okx" / "futures"
OUT_DIR = REPO_ROOT / "research" / "results" / "T-038_raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
#  PRE-REGISTERED CONSTANTS — research/NEXT_TASK.md, "Construct specification"
#  and "Zero-cost pre-gate ladder".  None of these may be varied: the variant
#  budget is 1 and the optimization budget is 0.
# --------------------------------------------------------------------------- #
PROGRAM = "perps"
TIMEFRAME = "1h"
WINDOW_START = "2022-12-23"                       # BNB inception = benchmark start
SPLIT_DATES = ("2024-11-22", "2025-04-21", "2025-09-19")
BARS_PER_YEAR = 8760                              # 1h bars
EXECUTION_MODE = "taker"                          # maker_optimistic is barred this cycle

HALF_LIFE = 48                                    # bars
LAMBDA = 2.0 ** (-1.0 / HALF_LIFE)                # 0.985663...
BURN_IN = 96                                      # 2x half-life
BAND = 0.10                                       # no-trade band on the applied multiplier
CAP = 1.0                                         # m in [0, 1]; never leveraged
LAG_BARS = 2                                      # validator.signal_to_returns convention

FWD = 24                                          # forward window, bars (P1, P2)
P1_MEDIAN_MIN = 0.30
P1_EVERY_MIN = 0.15
P2_ASSET_BREADTH_MIN = 5                          # of 9
BLOCK = 168                                       # bootstrap / shuffle block, bars (1 week)
N_SHUFFLES = 200
SHUFFLE_SEED = 7                                  # pre-registered
N_BOOT = 2000
BOOT_SEED = 7                                     # reported CI only, non-gating
P3_SHUFFLE_PCTILE = 90
P4_MIN_EPISODES = 6                               # H-IVGate floor precedent
P4_EPISODE_MIN_BARS = 12
P4_EPISODE_GAP_BARS = 24
P4_ACTIVE_SHARE_MIN = 0.20
P4_EPISODE_THRESHOLD = 0.9

_results: dict = {}


def say(*a):
    print(*a, flush=True)


def head(title: str):
    say("\n" + "=" * 78)
    say(title)
    say("=" * 78)


# --------------------------------------------------------------------------- #
#  Loading
# --------------------------------------------------------------------------- #
def load_whitelist() -> list[str]:
    """The nine instruments, read from config_perp.json — never hardcoded."""
    import rapidjson
    cfg = rapidjson.loads(
        CONFIG_PERP.read_text(encoding="utf-8"),
        parse_mode=rapidjson.PM_COMMENTS | rapidjson.PM_TRAILING_COMMAS)
    pairs = cfg["exchange"]["pair_whitelist"]
    if len(pairs) != 9:
        raise RuntimeError(
            f"config_perp.json whitelist has {len(pairs)} pairs, expected 9. The "
            f"deployment envelope in NEXT_TASK.md names exactly nine instruments.")
    return pairs


def feather_path(pair: str) -> Path:
    return FUTURES_DIR / f"{pair.replace('/', '_').replace(':', '_')}-{TIMEFRAME}-futures.feather"


# --------------------------------------------------------------------------- #
#  P0 — REACHABILITY (environment check; failure = BLOCKED, not a rejection)
# --------------------------------------------------------------------------- #
def p0_reachability(pairs: list[str]) -> tuple[bool, pd.DataFrame, dict]:
    head("P0 — REACHABILITY (environment check, not a hypothesis verdict)")
    boundary = V.holdout_boundary(PROGRAM)
    w_start = pd.Timestamp(WINDOW_START, tz="UTC")
    say(f"holdout boundary (validator.HOLDOUT_BOUNDARIES['{PROGRAM}']) : {boundary}")
    say(f"window start                                                : {w_start}")
    say("")

    rec, cols, ok = {}, {}, True
    for p in pairs:
        fp = feather_path(p)
        if not fp.exists():
            say(f"  MISSING {fp}")
            ok = False
            rec[p] = {"exists": False}
            continue
        raw = pd.read_feather(fp).set_index("date").sort_index()
        if raw.index.tz is None:
            raw.index = raw.index.tz_localize("UTC")
        dup = bool(raw.index.has_duplicates)

        # Coverage is checked on the RAW feather (it extends past the boundary to
        # 2026-05-28); the evaluation slice is taken afterwards.
        covers = raw.index.max() >= boundary

        # SLICE FIRST — everything after the holdout boundary is dropped before
        # any computation, per NEXT_TASK.md "Split specification".
        sl = raw.loc[(raw.index >= w_start) & (raw.index <= boundary)]
        gaps = sl.index.to_series().diff().dropna()
        worst = gaps.max() if len(gaps) else pd.Timedelta(0)
        big = gaps[gaps > pd.Timedelta("24h")]
        n_big = int(len(big))

        rec[p] = {
            "exists": True, "raw_bars": int(len(raw)),
            "raw_first": str(raw.index.min()), "raw_last": str(raw.index.max()),
            "covers_boundary": bool(covers), "duplicate_timestamps": dup,
            "window_bars": int(len(sl)),
            "window_first": str(sl.index.min()) if len(sl) else None,
            "window_last": str(sl.index.max()) if len(sl) else None,
            "worst_internal_gap": str(worst), "n_gaps_over_24h": n_big,
        }
        say(f"  {p:<18} raw {len(raw):>6} bars  {raw.index.min().date()} .. {raw.index.max().date()}"
            f" | window {len(sl):>6} bars  {sl.index.min()} .. {sl.index.max()}"
            f" | worst gap {str(worst):>16} | gaps>24h {n_big} | dup {dup}")
        if not covers or dup or n_big > 0:
            ok = False
        cols[p] = sl["close"].astype(float)

    closes = pd.DataFrame(cols)
    n_before = len(closes)
    closes_full = closes.dropna(how="any")
    say("")
    say(f"union index bars              : {n_before}")
    say(f"all-nine-present bars (basket): {len(closes_full)}")
    say(f"bars dropped for missing legs : {n_before - len(closes_full)}")
    if len(closes_full):
        say(f"basket window                 : {closes_full.index.min()} .. {closes_full.index.max()}")

    # A basket needs every leg on every bar; a bar with a missing leg is not a
    # basket bar.  Report how many were dropped rather than silently aligning.
    if n_before - len(closes_full) > 0:
        say("  NOTE: bars with a missing leg were dropped from the basket index.")

    verdict = ok and len(closes_full) > 0
    say("")
    say(f"P0 VERDICT: {'PASS' if verdict else 'FAIL (environment -> BLOCKED, not a rejection)'}")
    _results["P0"] = {"pass": bool(verdict), "per_instrument": rec,
                      "union_bars": int(n_before), "basket_bars": int(len(closes_full)),
                      "boundary": str(boundary), "window_start": str(w_start)}
    return verdict, closes_full, rec


# --------------------------------------------------------------------------- #
#  Shared construction
# --------------------------------------------------------------------------- #
def month_end_bars(index: pd.DatetimeIndex) -> np.ndarray:
    """Last bar of each calendar month, final bar excluded.

    Same convention as the committed benchmark
    (user_data/research/perps_benchmark.py:month_end_bars) — the benchmark
    operates on 1d bars and this on 1h bars, so "last trading bar of the month"
    resolves to the month's final HOUR here.  The rule itself is unchanged.
    """
    per = index.to_period("M")
    mask = np.zeros(len(index), dtype=bool)
    mask[:-1] = per[:-1] != per[1:]
    return mask


def build_basket(closes: pd.DataFrame, per_side: float) -> pd.DataFrame:
    """Equal-weight, monthly-rebalanced long basket — the benchmark's own loop.

    Copied in construction from perps_benchmark.build_benchmark(rebalance=True):
    weights drift between rebalances, reset to 1/N at each month-end bar, and
    every leg of a rebalance pays ONE side on |w_target - w_drift|.  Entry at
    bar 0 is the same formula against w_drift = 0, i.e. exactly one per-side.
    """
    idx = closes.index
    rets = closes.pct_change()
    n_assets = closes.shape[1]
    equal = np.full(n_assets, 1.0 / n_assets)
    reb_mask = month_end_bars(idx)

    w = equal.copy()
    gross = np.zeros(len(idx))
    cost = np.zeros(len(idx))
    cost[0] = per_side * float(np.abs(equal).sum())
    turnovers = [1.0]

    for t in range(1, len(idx)):
        r = rets.iloc[t].to_numpy()
        g = float(w @ r)
        gross[t] = g
        w = w * (1.0 + r) / (1.0 + g)
        if reb_mask[t]:
            turnover = float(np.abs(equal - w).sum())
            cost[t] = per_side * turnover
            turnovers.append(turnover)
            w = equal.copy()

    out = pd.DataFrame({"ret_gross": gross, "basket_cost": cost,
                        "ret_net": gross - cost}, index=idx)
    out.attrs["n_rebalances"] = int(reb_mask.sum())
    out.attrs["mean_turnover"] = float(np.mean(turnovers[1:])) if len(turnovers) > 1 else 0.0
    out.attrs["total_cost_fraction"] = float(cost.sum())
    return out


def ewma_sigma(ret: pd.Series) -> pd.Series:
    """Annualised EWMA volatility, half-life 48 bars, expanding-initialised.

    pandas' `halflife=` maps to alpha = 1 - exp(-ln2/hl), i.e. decay
    lambda = 2^(-1/48) = the constant NEXT_TASK.md pre-registers.  adjust=True
    makes the early values an EXPANDING weighted estimate that converges to the
    EWMA, which is the "initialized as an expanding estimate" the spec asks for.

    Computed ONCE over the full pre-holdout series and sliced afterwards — never
    per split (Standing Directive 8, warmup truncation).
    """
    return ret.ewm(halflife=HALF_LIFE, adjust=True).std() * np.sqrt(BARS_PER_YEAR)


def apply_band(m_raw: np.ndarray, band: float = BAND, start: float = 1.0) -> np.ndarray:
    """Applied multiplier: adopt m_raw only when it has drifted >= band."""
    out = np.empty(len(m_raw), dtype=float)
    cur = float(start)
    for i in range(len(m_raw)):
        if abs(m_raw[i] - cur) >= band:
            cur = float(m_raw[i])
        out[i] = cur
    return out


def build_multiplier(sigma: pd.Series, sigma_target: float) -> pd.DataFrame:
    """m_raw, m_applied and the lagged (position) multiplier."""
    m_raw = np.minimum(CAP, sigma_target / sigma.to_numpy())
    m_raw[:BURN_IN] = 1.0                      # burn-in: no scaling
    m_raw = np.where(np.isfinite(m_raw), m_raw, 1.0)
    m_app = apply_band(m_raw)
    # Lag: validator.signal_to_returns uses position[t] = signal[t-2].  The
    # multiplier is a fractional weight, so the arithmetic is replicated here
    # rather than routed through that function (which clips to {-1,0,1}).
    m_pos = pd.Series(m_app, index=sigma.index).shift(LAG_BARS).fillna(1.0)
    return pd.DataFrame({"m_raw": m_raw, "m_applied": m_app, "m_pos": m_pos.to_numpy()},
                        index=sigma.index)


def candidate_returns(basket: pd.DataFrame, m_pos: pd.Series, per_side: float) -> pd.DataFrame:
    """Net candidate stream: m*(basket gross) - m*(basket rebalance cost) - exposure-change cost."""
    m = m_pos.to_numpy()
    dm = np.abs(np.diff(m, prepend=m[0]))
    gross = m * basket["ret_gross"].to_numpy()
    cost = m * basket["basket_cost"].to_numpy() + dm * per_side
    net = gross - cost
    return pd.DataFrame({"m_pos": m, "ret_gross": gross, "cost": cost, "ret_net": net,
                         "equity": np.cumprod(1.0 + net)}, index=basket.index)


def sharpe(x: np.ndarray | pd.Series, bars_per_year: int = BARS_PER_YEAR) -> float:
    a = np.asarray(x, dtype=float)
    sd = a.std(ddof=1)
    return float(a.mean() / sd * np.sqrt(bars_per_year)) if sd > 0 else 0.0


def fwd_sum_std(logret: np.ndarray, k: int = FWD) -> tuple[np.ndarray, np.ndarray]:
    """Forward k-bar (sum, std) of log returns over t+1 .. t+k. NaN where truncated."""
    n = len(logret)
    s = np.full(n, np.nan)
    v = np.full(n, np.nan)
    ser = pd.Series(logret)
    fs = ser.rolling(k).sum().to_numpy()
    fv = ser.rolling(k).std(ddof=1).to_numpy()
    s[:n - k] = fs[k:]
    v[:n - k] = fv[k:]
    return s, v


# --------------------------------------------------------------------------- #
#  P1 — VOLATILITY PERSISTENCE (lead/lag analog)
# --------------------------------------------------------------------------- #
def p1_persistence(closes: pd.DataFrame, tv_index: pd.DatetimeIndex) -> bool:
    head("P1 — VOLATILITY PERSISTENCE (lead/lag analog), TRAIN+VAL, per instrument")
    say(f"census bars per instrument: TRAIN+VAL minus the last {FWD} (forward window")
    say(f"must lie inside TRAIN+VAL, so no forward window peeks into TEST)")
    say("")
    say(f"{'instrument':<18} {'n':>7} {'rho(sigma_t, fwd rv)':>22} {'rho(trailing rv, sigma_t+24)':>30}")

    fwd_rho, rev_rho, per = {}, {}, {}
    census_idx = tv_index[:-FWD]
    for p in closes.columns:
        lr = np.log(closes[p] / closes[p].shift(1))
        sig = ewma_sigma(lr)                        # full series, then sliced
        fsum, fstd = fwd_sum_std(lr.to_numpy())
        f = pd.Series(fstd, index=lr.index)

        # forward census: sigma_t  vs  realized vol over t+1..t+24
        a = pd.DataFrame({"x": sig, "y": f}).loc[census_idx].dropna()
        r_fwd = float(a["x"].corr(a["y"], method="spearman"))

        # REVERSED pairing (mandatory sanity check): trailing realized vol over
        # t-23..t  vs  the EWMA displaced 24 bars forward.  If this comes back
        # identical to the forward census the two are the same computation and
        # the verdict is a bug, not a finding.
        trail = lr.rolling(FWD).std(ddof=1)
        b = pd.DataFrame({"x": trail, "y": sig.shift(-FWD)}).loc[census_idx].dropna()
        r_rev = float(b["x"].corr(b["y"], method="spearman"))

        fwd_rho[p], rev_rho[p] = r_fwd, r_rev
        per[p] = {"n": int(len(a)), "rho_forward": r_fwd, "rho_reversed": r_rev}
        say(f"  {p:<16} {len(a):>7} {r_fwd:>22.6f} {r_rev:>30.6f}")

    vals = np.array(list(fwd_rho.values()))
    med = float(np.median(vals))
    worst = float(vals.min())
    worst_name = min(fwd_rho, key=fwd_rho.get)

    # Sanity check (a): the -k and +k sides must DIFFER.
    ident = [p for p in fwd_rho if abs(fwd_rho[p] - rev_rho[p]) < 1e-9]
    say("")
    say(f"sanity (a) forward vs reversed census identical on: {ident if ident else 'none — OK'}")
    if ident:
        raise RuntimeError(
            "forward and reversed censuses are numerically identical on "
            f"{ident}. Exact k<->-k symmetry between two distinct series is a bug "
            "signature (strategy_research_notes.md lesson 20a); the P1 verdict is "
            "not interpretable until this is explained.")
    # Sanity check (b): suspicious cleanliness.
    clean = [p for p in fwd_rho if abs(fwd_rho[p] - round(fwd_rho[p], 4)) == 0.0]
    say(f"sanity (b) correlations exact to 4dp on: {clean if clean else 'none — OK'}")

    ok_med = med >= P1_MEDIAN_MIN
    ok_all = bool((vals > P1_EVERY_MIN).all())
    say("")
    say(f"median rho across 9 : {med:.6f}   (threshold >= {P1_MEDIAN_MIN})  -> {'PASS' if ok_med else 'FAIL'}")
    say(f"minimum rho         : {worst:.6f}  ({worst_name})  (threshold >  {P1_EVERY_MIN})  -> {'PASS' if ok_all else 'FAIL'}")
    verdict = ok_med and ok_all
    say(f"P1 VERDICT: {'PASS' if verdict else 'FAIL -> hypothesis REJECTED at P1, zero trials'}")
    _results["P1"] = {"pass": bool(verdict), "median_rho": med, "min_rho": worst,
                      "min_rho_instrument": worst_name, "per_instrument": per,
                      "thresholds": {"median_min": P1_MEDIAN_MIN, "every_min": P1_EVERY_MIN},
                      "sanity_identical_censuses": ident}
    return verdict


# --------------------------------------------------------------------------- #
#  P2 — MECHANISM EXISTENCE (harm census)
# --------------------------------------------------------------------------- #
def _purr_census(sigma: pd.Series, logret: pd.Series, idx: pd.DatetimeIndex) -> dict:
    """Quintile forward per-unit-risk return census on `idx` (edges from `idx`)."""
    fsum, fstd = fwd_sum_std(logret.to_numpy())
    df = pd.DataFrame({"sigma": sigma, "fsum": fsum, "fstd": fstd},
                      index=logret.index).loc[idx].dropna()
    df = df[df["fstd"] > 0]
    df["purr"] = df["fsum"] / df["fstd"]
    edges = df["sigma"].quantile([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]).to_numpy()
    q = pd.cut(df["sigma"], bins=edges, labels=[1, 2, 3, 4, 5], include_lowest=True)
    df["q"] = q
    means = df.groupby("q", observed=False)["purr"].mean()
    counts = df.groupby("q", observed=False)["purr"].size()
    return {"df": df, "edges": edges.tolist(),
            "q_means": {int(k): float(v) for k, v in means.items()},
            "q_counts": {int(k): int(v) for k, v in counts.items()},
            "q1_minus_q5": float(means.loc[1] - means.loc[5])}


def _block_bootstrap_ci(df: pd.DataFrame, edges: list, n_boot: int, seed: int) -> dict:
    """Moving-block bootstrap 90% CI on the Q1-Q5 per-unit-risk difference."""
    rng = np.random.default_rng(seed)
    sig = df["sigma"].to_numpy()
    purr = df["purr"].to_numpy()
    n = len(df)
    n_blocks = int(np.ceil(n / BLOCK))
    starts_max = n - BLOCK
    lo_edge, hi_edge = edges[1], edges[4]
    out = np.empty(n_boot)
    for i in range(n_boot):
        st = rng.integers(0, starts_max + 1, size=n_blocks)
        take = (st[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n]
        s, p = sig[take], purr[take]
        q1 = p[s <= lo_edge]
        q5 = p[s > hi_edge]
        out[i] = (q1.mean() - q5.mean()) if (len(q1) and len(q5)) else np.nan
    out = out[np.isfinite(out)]
    return {"p5": float(np.percentile(out, 5)), "p50": float(np.percentile(out, 50)),
            "p95": float(np.percentile(out, 95)), "n_resamples": int(len(out)),
            "block": BLOCK, "seed": seed,
            "share_positive": float((out > 0).mean())}


def p2_harm_census(basket: pd.DataFrame, sigma_b: pd.Series, closes: pd.DataFrame,
                   tv_index: pd.DatetimeIndex) -> bool:
    head("P2 — MECHANISM EXISTENCE (harm census), TRAIN+VAL")
    census_idx = tv_index[:-FWD]
    blr = np.log1p(basket["ret_gross"])

    prim = _purr_census(sigma_b, blr, census_idx)
    say("PRIMARY — basket level, quintiles of sigma_t (edges from TRAIN+VAL)")
    say(f"  sigma quintile edges (annualised): {[round(e, 6) for e in prim['edges']]}")
    say(f"  {'quintile':<10} {'n':>8} {'mean fwd 24-bar per-unit-risk return':>40}")
    for k in (1, 2, 3, 4, 5):
        say(f"  Q{k:<9} {prim['q_counts'][k]:>8} {prim['q_means'][k]:>40.6f}")
    d = prim["q1_minus_q5"]
    say(f"  Q1 - Q5 = {d:.6f}   KILL if <= 0")

    ci = _block_bootstrap_ci(prim["df"], prim["edges"], N_BOOT, BOOT_SEED)
    say(f"  moving-block bootstrap 90% CI on Q1-Q5 (block {BLOCK}, {ci['n_resamples']} resamples, "
        f"seed {BOOT_SEED}): [{ci['p5']:.6f}, {ci['p95']:.6f}]  median {ci['p50']:.6f}  "
        f"share>0 {ci['share_positive']:.4f}   (REPORTED, NOT GATING)")

    # 1-bar-forward diagnostic. Per-unit-risk is undefined on a single bar (the
    # std of one observation), so two faithful analogues are reported instead.
    one = pd.DataFrame({"sigma": sigma_b, "f1": blr.shift(-1)}).loc[census_idx].dropna()
    edges = prim["edges"]
    one["q"] = pd.cut(one["sigma"], bins=edges, labels=[1, 2, 3, 4, 5], include_lowest=True)
    m_raw_ret = one.groupby("q", observed=False)["f1"].mean()
    one["f1_over_sigma"] = one["f1"] / one["sigma"]
    m_scaled = one.groupby("q", observed=False)["f1_over_sigma"].mean()
    say("")
    say("  1-bar-forward diagnostic (per-unit-risk undefined at k=1; both analogues shown)")
    say(f"  {'quintile':<10} {'mean fwd 1-bar log ret':>24} {'mean (fwd 1-bar / sigma_t)':>28}")
    for k in (1, 2, 3, 4, 5):
        say(f"  Q{k:<9} {m_raw_ret.loc[k]:>24.8f} {m_scaled.loc[k]:>28.8f}")
    say(f"  Q1 - Q5 raw    = {m_raw_ret.loc[1] - m_raw_ret.loc[5]:+.8f}")
    say(f"  Q1 - Q5 scaled = {m_scaled.loc[1] - m_scaled.loc[5]:+.8f}")

    say("")
    say("SECONDARY — per instrument, per-asset quintile edges")
    say(f"  {'instrument':<18} {'n':>8} {'Q1 mean':>12} {'Q5 mean':>12} {'Q1-Q5':>12}  sign")
    per, n_pos = {}, 0
    for p in closes.columns:
        lr = np.log(closes[p] / closes[p].shift(1))
        sg = ewma_sigma(lr)
        c = _purr_census(sg, lr, census_idx)
        per[p] = {"q1_minus_q5": c["q1_minus_q5"], "q_means": c["q_means"],
                  "n": int(len(c["df"]))}
        pos = c["q1_minus_q5"] > 0
        n_pos += int(pos)
        say(f"  {p:<16} {len(c['df']):>8} {c['q_means'][1]:>12.6f} {c['q_means'][5]:>12.6f} "
            f"{c['q1_minus_q5']:>12.6f}  {'+' if pos else '-'}")

    ok_primary = d > 0
    ok_breadth = n_pos >= P2_ASSET_BREADTH_MIN
    say("")
    say(f"primary  basket Q1-Q5 = {d:.6f}       KILL if <= 0                  -> {'PASS' if ok_primary else 'FAIL'}")
    say(f"secondary breadth     = {n_pos}/9 positive  KILL if < {P2_ASSET_BREADTH_MIN}/9   -> {'PASS' if ok_breadth else 'FAIL'}")
    verdict = ok_primary and ok_breadth
    say(f"P2 VERDICT: {'PASS' if verdict else 'FAIL -> hypothesis REJECTED at P2, zero trials'}")

    _results["P2"] = {"pass": bool(verdict), "basket_q1_minus_q5": d,
                      "basket_q_means": prim["q_means"], "basket_q_counts": prim["q_counts"],
                      "sigma_quintile_edges": prim["edges"],
                      "bootstrap_ci_90": ci,
                      "one_bar_diagnostic": {
                          "q_mean_fwd_logret": {int(k): float(v) for k, v in m_raw_ret.items()},
                          "q_mean_fwd_over_sigma": {int(k): float(v) for k, v in m_scaled.items()},
                          "q1_minus_q5_raw": float(m_raw_ret.loc[1] - m_raw_ret.loc[5]),
                          "q1_minus_q5_scaled": float(m_scaled.loc[1] - m_scaled.loc[5])},
                      "per_instrument": per, "n_instruments_positive": int(n_pos),
                      "breadth_threshold": P2_ASSET_BREADTH_MIN}
    return verdict


# --------------------------------------------------------------------------- #
#  P3 — COST-FREE UPPER BOUND (turnover viability)
# --------------------------------------------------------------------------- #
def block_shuffle(x: np.ndarray, rng: np.random.Generator, block: int = BLOCK) -> np.ndarray:
    """Reorder x in contiguous blocks — preserves the marginal distribution and
    local structure, destroys the alignment between sigma and the return series."""
    n = len(x)
    n_blocks = int(np.ceil(n / block))
    parts = [x[i * block:(i + 1) * block] for i in range(n_blocks)]
    order = rng.permutation(len(parts))
    return np.concatenate([parts[i] for i in order])[:n]


def p3_cost_free_bound(basket: pd.DataFrame, sigma_b: pd.Series, sigma_target: float,
                       mult: pd.DataFrame, tv_index: pd.DatetimeIndex,
                       per_side: float) -> bool:
    head("P3 — COST-FREE UPPER BOUND (turnover viability)")
    tv_basket = basket.loc[tv_index]
    tv_mult = mult.loc[tv_index]
    r = tv_basket["ret_gross"].to_numpy()

    real_gross = sharpe(tv_mult["m_pos"].to_numpy() * r)
    plain_gross = sharpe(r)

    # (a) SHUFFLE CONTROL — the gate.
    rng = np.random.default_rng(SHUFFLE_SEED)
    sig_tv = sigma_b.loc[tv_index].to_numpy()
    shuf = np.empty(N_SHUFFLES)
    for i in range(N_SHUFFLES):
        s = block_shuffle(sig_tv, rng)
        m_raw = np.minimum(CAP, sigma_target / s)
        m_raw = np.where(np.isfinite(m_raw), m_raw, 1.0)
        m_app = apply_band(m_raw)
        m_pos = np.concatenate([np.ones(LAG_BARS), m_app[:-LAG_BARS]])
        shuf[i] = sharpe(m_pos * r)
    p5, p50, p90 = (float(np.percentile(shuf, q)) for q in (5, 50, 90))
    rank = float((shuf < real_gross).mean() * 100.0)

    say("(a) GATE — real vol-timed gross Sharpe vs block-shuffled control")
    say(f"    block {BLOCK} bars, {N_SHUFFLES} shuffles, seed {SHUFFLE_SEED} (pre-registered)")
    say(f"    real vol-timed gross Sharpe (ann.) : {real_gross:+.6f}")
    say(f"    shuffled distribution  p5 / p50 / p90 : {p5:+.6f} / {p50:+.6f} / {p90:+.6f}")
    say(f"    percentile rank of the real value     : {rank:.2f}")
    ok_a = real_gross > p90
    say(f"    KILL if real <= p90  ->  {'PASS' if ok_a else 'FAIL'}")

    say("")
    say("(a2) DIAGNOSTIC, NOT A GATE — plain equal-weight basket gross Sharpe")
    say(f"    plain basket gross Sharpe (ann.)   : {plain_gross:+.6f}")
    say(f"    vol-timed minus plain              : {real_gross - plain_gross:+.6f}")
    say("    This comparison CANNOT distinguish timing from mechanical variance")
    say("    reduction: sigma_target is the TRAIN median, so m < 1 about half the")
    say("    time and the construct systematically holds less in high-vol bars.")

    # (b) net vs net — the second gate.
    cand = candidate_returns(basket, mult["m_pos"], per_side).loc[tv_index]
    net_vt = sharpe(cand["ret_net"].to_numpy())
    net_ew = sharpe(tv_basket["ret_net"].to_numpy())
    dm = np.abs(np.diff(tv_mult["m_pos"].to_numpy(), prepend=tv_mult["m_pos"].to_numpy()[0]))
    turnover = float(dm.sum())
    n_bars = len(tv_index)
    days = n_bars / 24.0
    drag_bps = float(turnover * per_side / (n_bars / BARS_PER_YEAR) * 1e4)

    say("")
    say("(b) GATE — net Sharpe, vol-timed vs equal-weight, same bars, same costs")
    say(f"    net vol-timed Sharpe (ann.)        : {net_vt:+.6f}")
    say(f"    net equal-weight Sharpe (ann.)     : {net_ew:+.6f}")
    ok_b = net_vt > net_ew
    say(f"    KILL if vol-timed <= equal-weight  ->  {'PASS' if ok_b else 'FAIL'}")

    say("")
    say(f"    TRAIN+VAL turnover  sum|d m_applied| : {turnover:.4f} of equity")
    say(f"    exposure changes (bars with dm > 0)  : {int((dm > 0).sum())}")
    say(f"    implied round trips per day          : {turnover / 2.0 / days:.4f}")
    say(f"    annualised cost drag from m-changes  : {drag_bps:.2f} bps/yr")
    say(f"    per-side cost (validator.per_side_cost('{EXECUTION_MODE}')) : {per_side * 1e4:.2f} bps")

    verdict = ok_a and ok_b
    say("")
    say(f"P3 VERDICT: {'PASS' if verdict else 'FAIL -> hypothesis REJECTED at P3, zero trials'}")
    _results["P3"] = {"pass": bool(verdict),
                      "real_gross_sharpe": real_gross,
                      "shuffle_p5": p5, "shuffle_p50": p50, "shuffle_p90": p90,
                      "shuffle_percentile_rank": rank, "gate_a_pass": bool(ok_a),
                      "plain_basket_gross_sharpe": plain_gross,
                      "net_vol_timed_sharpe": net_vt, "net_equal_weight_sharpe": net_ew,
                      "gate_b_pass": bool(ok_b),
                      "turnover_sum_abs_dm": turnover,
                      "n_exposure_changes": int((dm > 0).sum()),
                      "round_trips_per_day": float(turnover / 2.0 / days),
                      "annualised_cost_drag_bps": drag_bps,
                      "per_side_cost": per_side, "n_bars": int(n_bars),
                      "shuffles": N_SHUFFLES, "seed": SHUFFLE_SEED, "block": BLOCK}
    return verdict


# --------------------------------------------------------------------------- #
#  P4 — TEST ACTIVITY FLOOR
# --------------------------------------------------------------------------- #
def count_episodes(m_raw: np.ndarray) -> dict:
    """Episodes of de-risking, per NEXT_TASK.md P4.

    "a maximal run of >= 12 consecutive bars with m_raw < 0.9, separated from the
    next by >= 24 bars at m_raw >= 0.9".  Implemented in two literal steps:
    qualifying runs first, then merge any pair separated by FEWER than 24 quiet
    bars (they are not "separated" and so are not distinct episodes).
    """
    below = m_raw < P4_EPISODE_THRESHOLD
    runs = []
    i = 0
    n = len(below)
    while i < n:
        if below[i]:
            j = i
            while j < n and below[j]:
                j += 1
            runs.append((i, j - 1))
            i = j
        else:
            i += 1
    qualifying = [r for r in runs if (r[1] - r[0] + 1) >= P4_EPISODE_MIN_BARS]
    merged = []
    for r in qualifying:
        if merged and (r[0] - merged[-1][1] - 1) < P4_EPISODE_GAP_BARS:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    return {"all_runs": len(runs), "qualifying_runs": len(qualifying),
            "episodes": len(merged), "spans": merged}


def p4_test_activity(mult: pd.DataFrame, test_index: pd.DatetimeIndex) -> bool:
    head("P4 — TEST ACTIVITY FLOOR (episode floor + TEST concentration)")
    te = mult.loc[test_index]
    m_raw = te["m_raw"].to_numpy()
    ep = count_episodes(m_raw)
    active_share = float((m_raw < 1.0).mean())

    say(f"TEST window: {test_index.min()} .. {test_index.max()}  ({len(test_index)} bars)")
    say(f"  all runs with m_raw < {P4_EPISODE_THRESHOLD}                    : {ep['all_runs']}")
    say(f"  runs of >= {P4_EPISODE_MIN_BARS} consecutive such bars      : {ep['qualifying_runs']}")
    say(f"  after merging runs separated by < {P4_EPISODE_GAP_BARS} quiet bars : {ep['episodes']} EPISODES")
    if ep["spans"]:
        say("  episode spans:")
        for a, b in ep["spans"]:
            say(f"    {test_index[a]} .. {test_index[b]}  ({b - a + 1} bars)")
    say(f"  share of TEST bars with m_raw < 1.0     : {active_share:.4f}")
    say(f"  min / mean / max m_raw over TEST        : {m_raw.min():.4f} / {m_raw.mean():.4f} / {m_raw.max():.4f}")

    ok_ep = ep["episodes"] >= P4_MIN_EPISODES
    ok_share = active_share >= P4_ACTIVE_SHARE_MIN
    say("")
    say(f"  episodes {ep['episodes']} >= {P4_MIN_EPISODES}          -> {'PASS' if ok_ep else 'FAIL'}")
    say(f"  active share {active_share:.4f} >= {P4_ACTIVE_SHARE_MIN}  -> {'PASS' if ok_share else 'FAIL'}")
    verdict = ok_ep and ok_share
    say(f"P4 VERDICT: {'PASS' if verdict else 'FAIL -> hypothesis REJECTED at P4, zero trials'}")
    _results["P4"] = {"pass": bool(verdict), "n_episodes": ep["episodes"],
                      "n_qualifying_runs": ep["qualifying_runs"], "n_all_runs": ep["all_runs"],
                      "episode_spans": [[str(test_index[a]), str(test_index[b]), int(b - a + 1)]
                                        for a, b in ep["spans"]],
                      "active_share": active_share,
                      "m_raw_min": float(m_raw.min()), "m_raw_mean": float(m_raw.mean()),
                      "m_raw_max": float(m_raw.max()),
                      "test_bars": int(len(test_index)),
                      "thresholds": {"min_episodes": P4_MIN_EPISODES,
                                     "min_active_share": P4_ACTIVE_SHARE_MIN}}
    return verdict


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> int:
    head("T-038 — H-BasketVolTarget-1h — ZERO-COST PRE-GATE LADDER")
    say(f"cost model : {V.describe_cost_model(EXECUTION_MODE)}")
    say(f"data gate  : {V.DATA_INTEGRITY}")
    say(f"program    : {PROGRAM}   active in validator: {V.ACTIVE_PROGRAM}")
    say(f"splits     : train_end {SPLIT_DATES[0]}  val_end {SPLIT_DATES[1]}  test_end {SPLIT_DATES[2]}")
    say(f"EWMA       : half-life {HALF_LIFE} bars, lambda {LAMBDA:.9f}, burn-in {BURN_IN}, "
        f"annualised at {BARS_PER_YEAR}")
    say(f"band {BAND}   cap {CAP}   lag {LAG_BARS} bars")
    if V.DATA_INTEGRITY.get("bypassed"):
        raise RuntimeError("data-integrity check was BYPASSED; this run is not evidence.")

    per_side = V.per_side_cost(EXECUTION_MODE)
    pairs = load_whitelist()
    say(f"whitelist  : {pairs}")

    ok, closes, _ = p0_reachability(pairs)
    if not ok:
        _results["verdict"] = "BLOCKED (P0 environment)"
        return 1

    # Splits — date-pinned, via validator.split_by_dates. assert_no_holdout on
    # every frame, per NEXT_TASK.md.
    V.assert_no_holdout(closes, label="full pre-holdout window", program=PROGRAM)
    tr, vl, te = V.split_by_dates(closes, *SPLIT_DATES)
    for lbl, seg in (("train", tr), ("val", vl), ("test", te)):
        V.assert_no_holdout(seg, label=lbl, program=PROGRAM)
    head("SPLITS (date-pinned; assert_no_holdout passed on every frame)")
    for lbl, seg in (("full", closes), ("train", tr), ("val", vl), ("test", te)):
        say(f"  {lbl:<6} {len(seg):>7} bars   {seg.index.min()} .. {seg.index.max()}")
    tv_index = tr.index.append(vl.index)
    say(f"  TRAIN+VAL {len(tv_index)} bars (P1-P3 census window)")
    _results["splits"] = {
        "mode": "date_pinned via validator.split_by_dates",
        "dates": list(SPLIT_DATES),
        "holdout_after": str(V.holdout_boundary(PROGRAM)),
        "bars": {"full": len(closes), "train": len(tr), "val": len(vl), "test": len(te),
                 "train_val": len(tv_index)},
        "edges": {"full": [str(closes.index.min()), str(closes.index.max())],
                  "train": [str(tr.index.min()), str(tr.index.max())],
                  "val": [str(vl.index.min()), str(vl.index.max())],
                  "test": [str(te.index.min()), str(te.index.max())]}}

    # ---- construct, built ONCE over the full pre-holdout series ----
    basket = build_basket(closes, per_side)
    sigma_b = ewma_sigma(basket["ret_gross"])
    sig_train = sigma_b.loc[tr.index].iloc[BURN_IN:]
    sigma_target = float(sig_train.median())
    mult = build_multiplier(sigma_b, sigma_target)

    head("CONSTRUCT (built once on the full pre-holdout series, then split)")
    say(f"  basket rebalances (month-end 1h bars) : {basket.attrs['n_rebalances']}")
    say(f"  mean rebalance turnover               : {basket.attrs['mean_turnover']:.6f}")
    say(f"  total basket cost over window         : {basket.attrs['total_cost_fraction']:.6f} of notional")
    say(f"  sigma_target = TRAIN median of sigma_t (burn-in {BURN_IN} excluded)")
    say(f"    n TRAIN sigma obs used              : {len(sig_train)}")
    say(f"    sigma_target (annualised)           : {sigma_target:.6f}")
    say(f"    TRAIN sigma  min/median/max         : {sig_train.min():.6f} / "
        f"{sig_train.median():.6f} / {sig_train.max():.6f}")
    say(f"  m_raw    share < 1.0 (full window)    : {float((mult['m_raw'] < 1.0).mean()):.4f}")
    say(f"  m_applied share < 1.0 (full window)   : {float((mult['m_applied'] < 1.0).mean()):.4f}")
    _results["construct"] = {
        "n_rebalances": basket.attrs["n_rebalances"],
        "mean_rebalance_turnover": basket.attrs["mean_turnover"],
        "total_basket_cost_fraction": basket.attrs["total_cost_fraction"],
        "sigma_target_annualised": sigma_target,
        "n_train_sigma_obs": int(len(sig_train)),
        "train_sigma_min": float(sig_train.min()),
        "train_sigma_max": float(sig_train.max()),
        "half_life": HALF_LIFE, "lambda": LAMBDA, "burn_in": BURN_IN,
        "band": BAND, "cap": CAP, "lag_bars": LAG_BARS,
        "per_side_cost": per_side}

    # ---- ladder ----
    if not p1_persistence(closes, tv_index):
        _results["verdict"] = "REJECT at P1 (zero trials)"
        return 0
    if not p2_harm_census(basket, sigma_b, closes, tv_index):
        _results["verdict"] = "REJECT at P2 (zero trials)"
        return 0
    if not p3_cost_free_bound(basket, sigma_b, sigma_target, mult, tv_index, per_side):
        _results["verdict"] = "REJECT at P3 (zero trials)"
        return 0
    if not p4_test_activity(mult, te.index):
        _results["verdict"] = "REJECT at P4 (zero trials)"
        return 0

    _results["verdict"] = "ALL PRE-GATES PASSED — proceed to the single trial"
    head("ALL PRE-GATES PASSED")
    say("The ladder is exhausted. The trial is a SEPARATE step (see the report).")

    # Persist the multiplier and basket streams so the trial step and any
    # reviewer re-run start from the same artifact.
    joined = basket.join(mult).join(sigma_b.rename("sigma"))
    joined.to_csv(OUT_DIR / "T-038_basket_multiplier_full.csv")
    say(f"streams written: {OUT_DIR / 'T-038_basket_multiplier_full.csv'}")
    return 0


if __name__ == "__main__":
    rc = 0
    try:
        rc = main()
    finally:
        _results["cost_model"] = V.cost_model_snapshot(EXECUTION_MODE)
        _results["data_integrity"] = V.DATA_INTEGRITY
        _results["warnings"] = V.cost_model_warnings(EXECUTION_MODE) + V.data_integrity_warnings()
        with open(OUT_DIR / "T-038_pregates.json", "w", encoding="utf-8") as f:
            json.dump(_results, f, indent=2, default=str)
        say(f"\nJSON written: {OUT_DIR / 'T-038_pregates.json'}")
    sys.exit(rc)
