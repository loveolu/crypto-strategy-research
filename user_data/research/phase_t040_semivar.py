"""
T-040 / H-SemiVarSizing-1h — downside-semideviation exposure sizing, 9-perp 1h basket.

ASSIGNMENT: research/NEXT_TASK.md (T-040, Research Director, 2026-08-05).

HYPOTHESIS (verbatim from the assignment)
-----------------------------------------
On 1h OKX perpetual bars, forward risk-adjusted returns of the nine-instrument
equal-weight basket are DECREASING in trailing *downside* semideviation, even
though T-038 measured them as INCREASING in trailing *total* volatility — and an
exposure multiplier that cuts exposure as downside semideviation rises therefore
improves the basket's risk-adjusted return net of its own turnover cost.

WHAT THIS SCRIPT RUNS, IN ORDER (stop at the first failure)
-----------------------------------------------------------
  P1   persistence of the conditioner      KILL if median(rho) < 0.30 OR min(rho) <= 0.15
  P2   harm census on dsd (the science)    KILL if D_bar <= 0 OR B < 5
  P2b  circular-shift null control         KILL if one-tailed p > 0.05
  P3   cost-admissibility REQUIREMENT      STOP (zero trials) if Sharpe(o) <= Sharpe(b)
  TRIAL  full validation on TEST           only if P1, P2, P2b pass AND P3's requirement is met

F1/F2/F3 are the falsification conditions and the top-level connective between
them is OR. P3 is NOT a falsification condition (see the assignment, "P3 —
Cost-admissibility REQUIREMENT"): a de-risking multiplier raises Sharpe on any
volatility-clustered series whether or not the hypothesised relationship exists,
so P3 produces NO evidence about the hypothesis in either direction.

PRE-REGISTERED, NOT TUNABLE
---------------------------
W = 168 bars (7 days) · quintiles · h = 24 bars · fwd_pur response · trim 25 bars ·
m in [0.25, 1.00] quantized to 0.25 · target = TRAIN median · 1,000 placebo draws
at seed 20260805 · MC 1,000 sims at seeds (11, 20260805, 777) · n_trials = 1.

COSTS resolve from validator.COST_MODEL through per_side_cost("taker") only.
Nothing here hardcodes a fee, a slippage or a spread number.

WARMUP (standing directive 8): dsd/usd/sd and every forward variable are computed
over the FULL 1h series from each instrument's first bar; the TRAIN+VAL slice is
taken AFTERWARDS. Indicators are never recomputed inside a split.

FORWARD-WINDOW TRIM: the last 25 bars (max(h)+1) of the TRAIN+VAL slice are
dropped before anchors are selected, so no retained anchor's forward window can
reach val_end. Asserted, not assumed (see _assert_forward_window_contained).

Run:  python user_data/research/phase_t040_semivar.py
Outputs: research/results/T-040_raw/   (JSON + CSV; every reported figure lives there)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "user_data" / "research"))

import validator as V          # noqa: E402  (import-time data-integrity gate runs here)
import perps_benchmark as PB   # noqa: E402  (authoritative basket-construction rule)

TASK_ID = "T-040"
OUT_DIR = REPO_ROOT / "research" / "results" / f"{TASK_ID}_raw"
FUTURES_DIR = REPO_ROOT / "user_data" / "data" / "okx" / "futures"
BENCH_TEST_CSV = REPO_ROOT / "research" / "benchmarks" / "perps_equal_weight_benchmark_TEST_returns.csv"

PROGRAM = "perps"
TIMEFRAME = "1h"
EXECUTION_MODE = "taker"
BARS_PER_YEAR = 8760                      # 1h bars, 365 days
N_TRIALS = 1                              # 0 before this cycle + 1 for the single variant

# --- pre-registered parameters (NEXT_TASK.md; none of these may be tuned) ----
W = 168                                   # 7 days
H = 24                                    # forward horizon, bars
TRIM = 25                                 # max(h) + 1
N_QUANTILES = 5
M_MIN, M_MAX, M_STEP = 0.25, 1.00, 0.25
PLACEBO_DRAWS = 1000
PLACEBO_SEED = 20260805
MC_SIMS = 1000
MC_SEEDS = (11, 20260805, 777)
STABILITY_W = (120, 168, 240)
STABILITY_M_MIN = (0.00, 0.25, 0.50)

# --- pre-registered thresholds ----------------------------------------------
P1_MEDIAN_FLOOR = 0.30                    # KILL if median(rho) < this
P1_MIN_FLOOR = 0.15                       # KILL if min(rho) <= this
P2_BREADTH_FLOOR = 5                      # KILL if B < this
P2B_P_CEILING = 0.05                      # KILL if one-tailed p > this
RECONCILIATION_CORR_FLOOR = 0.99          # Director-set; below this STOP and BLOCK
BENCH_TEST_SHARPE_PER_PERIOD = 0.123321   # committed benchmark, daily TEST
BENCH_TEST_MAXDD = -0.2502                # committed benchmark, daily TEST
CRIT3_RATIO = 1.10
CRIT4_RATIO = 1.25
DSR_BAR = 0.95

# --- frozen split triple (A-005; not this cycle's to change) ----------------
SPLIT_DATES = ("2024-11-22", "2025-04-21", "2025-09-19")
TRAIN_END_1H = pd.Timestamp("2024-11-22 23:00", tz="UTC")
VAL_END_1H = pd.Timestamp("2025-04-21 23:00", tz="UTC")
TEST_END_1H = pd.Timestamp("2025-09-19 23:00", tz="UTC")

#: First bar on which all nine instruments have data (BNB inception). Asserted,
#: not assumed — PB.WINDOW_START is the daily reading of the same fact.
WINDOW_START_DATE = PB.WINDOW_START        # "2022-12-23"


# --------------------------------------------------------------------------- #
#  Loading
# --------------------------------------------------------------------------- #
def load_closes_1h(pairs: list[str]) -> tuple[dict[str, pd.Series], dict]:
    """Per-instrument 1h close series, each from its OWN first bar (warmup rule).

    Returns (series_by_pair, integrity_record). Zero-volume bars are NOT dropped
    and NOT special-cased: this construct reads `close` only, a zero-volume bar
    still carries a settled close, and dropping bars would put a hole in a
    contiguous hourly index that every rolling window depends on. Their count is
    recorded so the Reviewer can see the decision rather than infer it.
    """
    out, rec = {}, {}
    for p in pairs:
        stem = p.replace("/", "_").replace(":", "_")
        fp = FUTURES_DIR / f"{stem}-{TIMEFRAME}-futures.feather"
        if not fp.exists():
            raise FileNotFoundError(f"missing 1h futures feather for {p}: {fp}")
        df = pd.read_feather(fp).set_index("date").sort_index()
        if df.index.has_duplicates:
            raise RuntimeError(f"{fp.name}: duplicate timestamps")
        gaps = df.index.to_series().diff().dropna()
        bad = gaps[gaps != pd.Timedelta("1h")]
        if len(bad):
            raise RuntimeError(f"{fp.name}: {len(bad)} non-hourly gap(s); first at {bad.index[0]}")
        if df["close"].isna().any():
            raise RuntimeError(f"{fp.name}: NaN close")
        zv = df.index[df["volume"] == 0]
        rec[p] = {
            "file": fp.name,
            "n_bars": int(len(df)),
            "first": str(df.index.min()),
            "last": str(df.index.max()),
            "n_zero_volume_bars": int(len(zv)),
            "zero_volume_in_train_val": int((zv <= VAL_END_1H).sum()),
            "zero_volume_in_test": int(((zv > VAL_END_1H) & (zv <= TEST_END_1H)).sum()),
            "zero_volume_handling": "kept as ordinary bars; construct reads close only",
        }
        out[p] = df["close"].astype(float)
    return out, rec


# --------------------------------------------------------------------------- #
#  Conditioners and forward variables — computed on the FULL series
# --------------------------------------------------------------------------- #
def conditioners(close: pd.Series, w: int = W, h: int = H) -> pd.DataFrame:
    """Every quantity the assignment defines, on the FULL series. All causal
    except the deliberately forward-looking fwd_* columns, which exist only as
    the response variable and are protected by the 25-bar anchor trim.

        r[t]       = close[t]/close[t-1] - 1
        dsd[t]     = sqrt( (1/W) * sum_{s=t-W+1..t} min(r[s],0)^2 )   PRIMARY
        usd[t]     = sqrt( (1/W) * sum_{s=t-W+1..t} max(r[s],0)^2 )   diagnostic
        sd[t]      = population std of r over the same W bars          diagnostic
        fwd_ret[t] = close[t+h]/close[t] - 1
        fwd_vol[t] = population std of { r[s] : s = t+1..t+h }
        fwd_pur[t] = fwd_ret[t] / fwd_vol[t]
        fwd_dsd[t] = sqrt( (1/h) * sum_{s=t+1..t+h} min(r[s],0)^2 )    P1 response
    """
    r = close / close.shift(1) - 1.0
    neg2 = np.minimum(r, 0.0) ** 2
    pos2 = np.maximum(r, 0.0) ** 2
    out = pd.DataFrame(index=close.index)
    out["r"] = r
    out["dsd"] = np.sqrt(neg2.rolling(w).mean())
    out["usd"] = np.sqrt(pos2.rolling(w).mean())
    out["sd"] = r.rolling(w).std(ddof=0)
    out["fwd_ret"] = close.shift(-h) / close - 1.0
    out["fwd_vol"] = r.rolling(h).std(ddof=0).shift(-h)
    out["fwd_dsd"] = np.sqrt(neg2.rolling(h).mean().shift(-h))
    with np.errstate(divide="ignore", invalid="ignore"):
        out["fwd_pur"] = np.where(out["fwd_vol"] > 0,
                                  out["fwd_ret"] / out["fwd_vol"], np.nan)
    return out


def _assert_forward_window_contained(anchors: pd.DatetimeIndex,
                                     full_index: pd.DatetimeIndex,
                                     label: str) -> None:
    """No retained anchor's h-bar forward window may reach val_end."""
    if not len(anchors):
        raise RuntimeError(f"{label}: empty anchor set")
    pos = full_index.get_indexer(anchors)
    last_read = full_index[pos.max() + H]
    if last_read >= VAL_END_1H:
        raise RuntimeError(
            f"{label}: forward window of the last anchor reads {last_read}, at or "
            f"beyond val_end {VAL_END_1H}. The 25-bar trim did not hold.")


def build_anchor_frame(cond: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """TRAIN+VAL census anchors for one instrument.

    Order is exactly the assignment's: compute on the full series (done by
    conditioners()), THEN slice TRAIN+VAL, THEN trim the last TRIM bars, THEN
    drop bars whose response is undefined.
    """
    tv = cond.loc[cond.index <= VAL_END_1H]
    n_tv_raw = len(tv)
    trimmed = tv.iloc[:-TRIM] if TRIM else tv
    n_trimmed = len(trimmed)
    need = ["dsd", "usd", "sd", "fwd_pur", "fwd_dsd", "fwd_vol"]
    warm = trimmed.dropna(subset=["dsd", "usd", "sd", "fwd_ret", "fwd_vol", "fwd_dsd"])
    n_after_warmup = len(warm)
    zero_fwd_vol = int((warm["fwd_vol"] == 0).sum())
    anchors = warm.dropna(subset=need)
    _assert_forward_window_contained(anchors.index, cond.index, "anchor set")
    rec = {
        "n_train_val_bars_raw": n_tv_raw,
        "n_after_25_bar_trim": n_trimmed,
        "n_after_warmup_drop": n_after_warmup,
        "n_dropped_zero_fwd_vol": zero_fwd_vol,
        "n_anchors": int(len(anchors)),
        "first_anchor": str(anchors.index.min()),
        "last_anchor": str(anchors.index.max()),
        "last_bar_read_by_forward_window": str(
            cond.index[cond.index.get_indexer(anchors.index).max() + H]),
    }
    return anchors, rec


# --------------------------------------------------------------------------- #
#  P1 — persistence of the conditioner
# --------------------------------------------------------------------------- #
def p1_persistence(anchors_by_pair: dict[str, pd.DataFrame]) -> dict:
    rows = []
    for p, a in anchors_by_pair.items():
        rho, pval = sps.spearmanr(a["dsd"].to_numpy(), a["fwd_dsd"].to_numpy())
        rows.append({"pair": p, "rho": float(rho), "p_value": float(pval),
                     "n": int(len(a))})
    rhos = np.array([x["rho"] for x in rows], dtype=float)
    med, mn = float(np.median(rhos)), float(rhos.min())
    fired = (med < P1_MEDIAN_FLOOR) or (mn <= P1_MIN_FLOOR)     # F1: literal OR
    return {
        "gate": "P1 / F1",
        "statistic": "spearman(dsd[t], forward 24-bar realized downside semideviation)",
        "per_instrument": rows,
        "median_rho": med,
        "min_rho": mn,
        "kill_clause": f"median(rho) < {P1_MEDIAN_FLOOR} OR min(rho) <= {P1_MIN_FLOOR}",
        "clause_a_median_below_floor": bool(med < P1_MEDIAN_FLOOR),
        "clause_b_min_at_or_below_floor": bool(mn <= P1_MIN_FLOOR),
        "F1_fired": bool(fired),
        "note": ("P1 is a NECESSARY condition only. Any autocorrelated series passes a "
                 "persistence test; passing it is not evidence for the hypothesis and "
                 "may not be cited as support."),
    }


# --------------------------------------------------------------------------- #
#  P2 — harm census
# --------------------------------------------------------------------------- #
def _quintile_diff(cond_vals: np.ndarray, resp_vals: np.ndarray,
                   edges: np.ndarray | None = None) -> tuple[float, dict]:
    """mean(resp | Q1) - mean(resp | Q5), quintiles of `cond`.

    `edges=None` estimates the quintile thresholds on the supplied sample (the
    assignment's rule: thresholds per instrument on that instrument's TRAIN+VAL
    bars). Passing explicit edges is used only by the non-gating robustness view
    that holds the full-window thresholds fixed.
    """
    if edges is None:
        edges = np.quantile(cond_vals, np.linspace(0, 1, N_QUANTILES + 1))
    q = np.clip(np.searchsorted(edges[1:-1], cond_vals, side="right"), 0, N_QUANTILES - 1)
    m1 = resp_vals[q == 0]
    m5 = resp_vals[q == N_QUANTILES - 1]
    if not len(m1) or not len(m5):
        return float("nan"), {"n_q1": int(len(m1)), "n_q5": int(len(m5))}
    means = [float(resp_vals[q == k].mean()) if (q == k).any() else float("nan")
             for k in range(N_QUANTILES)]
    return float(m1.mean() - m5.mean()), {
        "n_q1": int(len(m1)), "n_q5": int(len(m5)),
        "quintile_means": means,
        "quintile_counts": [int((q == k).sum()) for k in range(N_QUANTILES)],
    }


def census(anchors_by_pair: dict[str, pd.DataFrame], conditioner: str) -> dict:
    """D[i], D_bar and breadth B for one conditioner column."""
    rows = []
    for p, a in anchors_by_pair.items():
        d, det = _quintile_diff(a[conditioner].to_numpy(), a["fwd_pur"].to_numpy())
        rows.append({"pair": p, "D": d, "n": int(len(a)), **det})
    d_vals = np.array([x["D"] for x in rows], dtype=float)
    d_bar = float(d_vals.mean())
    breadth = int((d_vals > 0).sum())
    return {"conditioner": conditioner, "per_instrument": rows,
            "D_bar": d_bar, "breadth": breadth, "n_instruments": len(rows)}


def p2_harm_census(anchors_by_pair: dict[str, pd.DataFrame]) -> dict:
    primary = census(anchors_by_pair, "dsd")
    d_bar, breadth = primary["D_bar"], primary["breadth"]
    fired = (d_bar <= 0.0) or (breadth < P2_BREADTH_FLOOR)      # F2: literal OR
    diag_sd = census(anchors_by_pair, "sd")
    diag_usd = census(anchors_by_pair, "usd")
    return {
        "gate": "P2 / F2",
        "response": "fwd_pur = fwd_ret / fwd_vol (per-unit-risk, h = 24 bars)",
        "primary_dsd": primary,
        "diagnostic_sd": diag_sd,
        "diagnostic_usd": diag_usd,
        "kill_clause": f"D_bar <= 0 OR B < {P2_BREADTH_FLOOR}",
        "clause_a_D_bar_non_positive": bool(d_bar <= 0.0),
        "clause_b_breadth_below_floor": bool(breadth < P2_BREADTH_FLOOR),
        "F2_fired": bool(fired),
        "diagnostic_expectations": {
            "sd": "expected NEGATIVE (T-038's finding on a matched window)",
            "usd": "expected STRONGLY NEGATIVE if the contamination hypothesis is right",
        },
    }


def robustness_views(anchors_by_pair: dict[str, pd.DataFrame]) -> dict:
    """Per-calendar-year and three disjoint equal-bar-count sub-windows.

    Reported, NON-GATING (assignment: adopted from T-038 Engineer rec. 5). Two
    threshold conventions are reported for each view, because "D_bar recomputed"
    does not say whether the quintile edges are re-estimated inside the view:
      * refit  — edges re-estimated within the view (the natural reading of
                 "recomputed", and how D is defined in P2)
      * fixed  — edges held at the full TRAIN+VAL values
    Both are shown so the sign does not depend on an unstated choice.
    """
    master = max(anchors_by_pair.values(), key=len).index
    thirds = np.array_split(np.arange(len(master)), 3)
    sub_bounds = [(master[ix[0]], master[ix[-1]]) for ix in thirds]

    full_edges = {p: np.quantile(a["dsd"].to_numpy(), np.linspace(0, 1, N_QUANTILES + 1))
                  for p, a in anchors_by_pair.items()}

    def _view(mask_fn, label):
        out_refit, out_fixed, counts = [], [], {}
        for p, a in anchors_by_pair.items():
            sel = a[mask_fn(a.index)]
            counts[p] = int(len(sel))
            if len(sel) < 5 * N_QUANTILES:
                out_refit.append(np.nan)
                out_fixed.append(np.nan)
                continue
            d_r, _ = _quintile_diff(sel["dsd"].to_numpy(), sel["fwd_pur"].to_numpy())
            d_f, _ = _quintile_diff(sel["dsd"].to_numpy(), sel["fwd_pur"].to_numpy(),
                                    edges=full_edges[p])
            out_refit.append(d_r)
            out_fixed.append(d_f)
        r = np.array(out_refit, dtype=float)
        f = np.array(out_fixed, dtype=float)
        return {
            "view": label, "bar_counts": counts,
            "D_bar_refit_edges": float(np.nanmean(r)) if np.isfinite(r).any() else None,
            "breadth_refit_edges": int(np.nansum(r > 0)),
            "D_bar_fixed_edges": float(np.nanmean(f)) if np.isfinite(f).any() else None,
            "breadth_fixed_edges": int(np.nansum(f > 0)),
            "n_instruments_evaluable": int(np.isfinite(r).sum()),
        }

    years = sorted({t.year for t in master})
    per_year = [_view(lambda ix, y=y: ix.year == y, f"year {y}") for y in years]
    per_third = [
        _view(lambda ix, a=a, b=b: (ix >= a) & (ix <= b),
              f"sub-window {k+1}: {a.date()} .. {b.date()}")
        for k, (a, b) in enumerate(sub_bounds)]
    signs = [v["D_bar_refit_edges"] for v in per_year + per_third
             if v["D_bar_refit_edges"] is not None]
    return {
        "note": "REPORTED, NON-GATING",
        "per_calendar_year": per_year,
        "three_disjoint_sub_windows": per_third,
        "sign_flips_across_views": bool(len(signs) > 1 and
                                        (min(signs) < 0 < max(signs))),
    }


#: Fixed, arbitrary timestamp for the hand-arithmetic spot check. Chosen before
#: any result was seen and never varied; it is a unit test, not a sample.
SPOT_CHECK = ("SOL/USDT:USDT", pd.Timestamp("2024-06-05 07:00", tz="UTC"))


def leakage_and_arithmetic_checks(closes: dict[str, pd.Series],
                                  anchors_by_pair: dict[str, pd.DataFrame],
                                  census_fn) -> dict:
    """Lookahead / leakage / arithmetic verification. Every check RAISES on failure.

    1. TRUNCATION INVARIANCE — the decisive proof that no bar after val_end
       influences any reported figure. The whole census is recomputed on inputs
       physically truncated at val_end and the results must be BIT-identical.
       Directive 8 requires indicators be computed on the full series (so warmup
       is not truncated), which does mean the loader reads post-val bars; this
       check demonstrates that none of them reaches a reported number.
    2. INDEPENDENT CODE PATH — D[i] recomputed with pandas qcut + groupby
       instead of quantile + searchsorted, for all nine instruments.
    3. HAND ARITHMETIC — dsd/usd/sd/fwd_ret/fwd_vol/fwd_pur at one fixed
       timestamp against explicit slice arithmetic, plus the exact decomposition
       identity dsd^2 + usd^2 == mean(r^2) that the hypothesis rests on.
    """
    out: dict = {}

    trunc_anchors = {}
    for p, s in closes.items():
        a, _ = build_anchor_frame(conditioners(s.loc[s.index <= VAL_END_1H]))
        trunc_anchors[p] = a
    same_index = all(anchors_by_pair[p].index.equals(trunc_anchors[p].index)
                     for p in closes)
    c_full, c_trunc = census_fn(anchors_by_pair, "dsd"), census_fn(trunc_anchors, "dsd")
    p1_full, p1_trunc = p1_persistence(anchors_by_pair), p1_persistence(trunc_anchors)
    identical = (same_index
                 and c_full["D_bar"] == c_trunc["D_bar"]
                 and c_full["breadth"] == c_trunc["breadth"]
                 and p1_full["median_rho"] == p1_trunc["median_rho"])
    if not identical:
        raise RuntimeError(
            "LOOKAHEAD CHECK FAILED: truncating every input series at val_end "
            f"changes the census (D_bar {c_full['D_bar']!r} -> {c_trunc['D_bar']!r}). "
            "A post-val bar is reaching a reported figure. STOP condition.")
    out["truncation_invariance"] = {
        "check": ("recompute the whole census on inputs physically truncated at "
                  "val_end; results must be bit-identical"),
        "anchor_sets_identical": bool(same_index),
        "D_bar_full_series_input": repr(c_full["D_bar"]),
        "D_bar_truncated_input": repr(c_trunc["D_bar"]),
        "P1_median_rho_full": repr(p1_full["median_rho"]),
        "P1_median_rho_truncated": repr(p1_trunc["median_rho"]),
        "bit_identical": True,
    }

    # Two independent binning conventions. They are NOT bit-identical, and the
    # reason is a genuine tie-handling difference rather than an arithmetic bug:
    # `dsd` carries thousands of exactly-repeated values (a 168-bar RMS of the
    # negative returns repeats whenever the window's negative set repeats), and
    # where a quintile edge lands on a tied value, pandas' right-closed interval
    # (a, b] puts the ties in the LOWER bin while searchsorted(side="right") puts
    # them in the UPPER one. It moves 0-6 bars per instrument out of ~28,775.
    #
    # The pre-registered implementation (searchsorted) is primary; it was fixed
    # before any result was seen. What must be verified is not bit-equality but
    # that the KILL clauses do not turn on the convention, so that is what is
    # asserted, with both conventions' figures recorded either way.
    rows, d_ss, d_qc = [], [], []
    for p, a in anchors_by_pair.items():
        q = pd.qcut(a["dsd"], N_QUANTILES, labels=False)
        mu = a.groupby(q)["fwd_pur"].mean()
        alt = float(mu.iloc[0] - mu.iloc[-1])
        scr, _ = _quintile_diff(a["dsd"].to_numpy(), a["fwd_pur"].to_numpy())
        n_moved = int((q.to_numpy() != np.clip(np.searchsorted(
            np.quantile(a["dsd"].to_numpy(), np.linspace(0, 1, N_QUANTILES + 1))[1:-1],
            a["dsd"].to_numpy(), side="right"), 0, N_QUANTILES - 1)).sum())
        rows.append({"pair": p, "D_searchsorted": scr, "D_qcut": alt,
                     "abs_difference": abs(alt - scr), "n_bars_binned_differently": n_moved,
                     "n_duplicate_dsd_values": int(len(a) - a["dsd"].nunique())})
        d_ss.append(scr)
        d_qc.append(alt)
    ss = {"D_bar": float(np.mean(d_ss)), "breadth": int((np.array(d_ss) > 0).sum())}
    qc = {"D_bar": float(np.mean(d_qc)), "breadth": int((np.array(d_qc) > 0).sum())}
    same_verdict = ((ss["D_bar"] <= 0) == (qc["D_bar"] <= 0) and
                    (ss["breadth"] < P2_BREADTH_FLOOR) == (qc["breadth"] < P2_BREADTH_FLOOR))
    if not same_verdict:
        raise RuntimeError(
            f"BINNING CONVENTION CHANGES THE VERDICT: searchsorted {ss} vs qcut {qc}. "
            f"A KILL clause that turns on a tie-handling convention is not a result. "
            f"STOP condition.")
    out["independent_code_path"] = {
        "check": ("D[i] via pandas qcut+groupby (right-closed bins) vs the "
                  "pre-registered quantile+searchsorted(side='right'), all nine"),
        "per_instrument": rows,
        "max_abs_difference": float(max(r["abs_difference"] for r in rows)),
        "cause": ("tied dsd values at quintile edges; the two conventions assign "
                  "ties to opposite bins, moving 0-6 bars per instrument"),
        "searchsorted_PRIMARY": ss,
        "qcut_alternative": qc,
        "kill_clauses_agree_under_both_conventions": True}

    pair, t = SPOT_CHECK
    c = closes[pair]
    r = c / c.shift(1) - 1.0
    i = c.index.get_loc(t)
    win = r.iloc[i - W + 1:i + 1]
    man = {
        "dsd": float(np.sqrt((np.minimum(win, 0.0) ** 2).mean())),
        "usd": float(np.sqrt((np.maximum(win, 0.0) ** 2).mean())),
        "sd": float(win.std(ddof=0)),
        "fwd_ret": float(c.iloc[i + H] / c.iloc[i] - 1.0),
        "fwd_vol": float(r.iloc[i + 1:i + 1 + H].std(ddof=0)),
    }
    man["fwd_pur"] = man["fwd_ret"] / man["fwd_vol"]
    cond = conditioners(c)
    scr = {k: float(cond[k].loc[t]) for k in man}
    if not all(np.isclose(man[k], scr[k], rtol=1e-9, atol=0.0) for k in man):
        raise RuntimeError(f"HAND ARITHMETIC MISMATCH at {t}: {man} vs {scr}")
    ident_lhs = man["dsd"] ** 2 + man["usd"] ** 2
    ident_rhs = float((win ** 2).mean())
    if not np.isclose(ident_lhs, ident_rhs, rtol=1e-12, atol=0.0):
        raise RuntimeError("decomposition identity dsd^2+usd^2 == mean(r^2) FAILED")
    out["hand_arithmetic"] = {
        "pair": pair, "timestamp": str(t), "manual": man, "script": scr,
        "agree_rtol_1e-9": True,
        "decomposition_identity_dsd2_plus_usd2_eq_mean_r2": {
            "lhs": ident_lhs, "rhs": ident_rhs, "holds": True}}

    out["forward_window_containment"] = {
        "check": ("every retained anchor's h-bar forward window ends strictly before "
                  "val_end; asserted in build_anchor_frame for all nine"),
        "val_end_1h": str(VAL_END_1H),
        "last_bar_read_any_instrument": max(
            str(cond_.index[cond_.index.get_indexer(anchors_by_pair[p].index).max() + H])
            for p, cond_ in ((p, conditioners(closes[p])) for p in closes)),
        "holds": True}
    return out


def post_verdict_diagnostics(anchors_by_pair: dict[str, pd.DataFrame]) -> dict:
    """POST-VERDICT, NON-GATING. Computed AFTER F2 has already been evaluated on
    the pre-registered statistic; it cannot and does not change any verdict.

    It exists to answer the one question the assignment asks the Engineer to
    judge in prose (T-038 Engineer recommendation 4, "ADAPTED, not rejected"):
    is the sign of D a GRADIENT across the conditioner, or a few extreme bars?
    Three views of the same census, no new conditioner, horizon or response:

      * D computed from quintile MEDIANS instead of means — a tail-insensitive
        version of the same difference;
      * D computed from 1%-symmetrically-trimmed quintile means;
      * Spearman rank correlation of quintile index (1..5) against quintile mean
        — a monotonicity score, +1 = clean gradient, ~0 = no ordering.
    """
    rows = []
    for p, a in anchors_by_pair.items():
        cond_v, resp_v = a["dsd"].to_numpy(), a["fwd_pur"].to_numpy()
        edges = np.quantile(cond_v, np.linspace(0, 1, N_QUANTILES + 1))
        q = np.clip(np.searchsorted(edges[1:-1], cond_v, side="right"),
                    0, N_QUANTILES - 1)
        means, medians, trimmed = [], [], []
        for k in range(N_QUANTILES):
            v = np.sort(resp_v[q == k])
            cut = int(len(v) * 0.01)
            means.append(float(v.mean()))
            medians.append(float(np.median(v)))
            trimmed.append(float(v[cut:len(v) - cut].mean()))
        mono = float(sps.spearmanr(np.arange(1, N_QUANTILES + 1), means).statistic)
        rows.append({
            "pair": p,
            "D_mean_prereg": means[0] - means[-1],
            "D_median": medians[0] - medians[-1],
            "D_trimmed_1pct": trimmed[0] - trimmed[-1],
            "monotonicity_rho": mono,
            "q_means": means, "q_medians": medians, "q_trimmed": trimmed,
        })
    def _bar(key):
        v = np.array([r[key] for r in rows], dtype=float)
        return {"D_bar": float(v.mean()), "breadth_positive": int((v > 0).sum())}
    return {
        "note": ("POST-VERDICT, NON-GATING, computed after F2 was evaluated on the "
                 "pre-registered statistic. Changes no gate and no verdict."),
        "per_instrument": rows,
        "pooled_mean_prereg": _bar("D_mean_prereg"),
        "pooled_median": _bar("D_median"),
        "pooled_trimmed_1pct": _bar("D_trimmed_1pct"),
        "median_monotonicity_rho": float(np.median([r["monotonicity_rho"] for r in rows])),
    }


# --------------------------------------------------------------------------- #
#  P2b — circular-shift null control
# --------------------------------------------------------------------------- #
def p2b_placebo(anchors_by_pair: dict[str, pd.DataFrame], d_bar: float) -> dict:
    """1,000 draws, one shared offset k per draw, conditioner rolled, response
    left in place, quintile thresholds re-estimated on the rolled series.

    THIS IS NOT A FAMILY-WISE CORRECTION. P2 tests one pre-registered
    conditioner, one horizon, one response; a max-statistic over a family of one
    is the statistic itself. What this control prices is the autocorrelation and
    volatility-clustering structure the circular roll PRESERVES, which makes the
    null distribution of D_bar neither centred nor scaled the textbook way.
    """
    pairs = list(anchors_by_pair)
    cond = {p: anchors_by_pair[p]["dsd"].to_numpy() for p in pairs}
    resp = {p: anchors_by_pair[p]["fwd_pur"].to_numpy() for p in pairs}
    n_min = int(min(len(v) for v in cond.values()))
    lo, hi = W, n_min - W
    if hi <= lo:
        raise RuntimeError(f"placebo offset range empty: [{lo}, {hi}] at N_min={n_min}")

    rng = np.random.default_rng(PLACEBO_SEED)
    draws = np.empty(PLACEBO_DRAWS, dtype=float)
    offsets = np.empty(PLACEBO_DRAWS, dtype=int)
    first_draw_check = None

    for j in range(PLACEBO_DRAWS):
        k = int(rng.integers(lo, hi + 1))
        offsets[j] = k
        ds = []
        differs = []
        for p in pairs:
            rolled = np.roll(cond[p], k)
            differs.append(bool(np.any(rolled != cond[p])))
            d, _ = _quintile_diff(rolled, resp[p])
            ds.append(d)
        draws[j] = float(np.mean(ds))
        if j == 0:
            first_draw_check = {"k": k, "rolled_differs_all_nine": bool(all(differs)),
                                "n_differing": int(sum(differs)),
                                "M_draw_1": float(draws[0]),
                                "M_draw_1_differs_from_D_bar": bool(draws[0] != d_bar)}

    # --- mandatory sanity assertions: a failure is a STOP condition ----------
    sd_m = float(draws.std(ddof=1))
    if not sd_m > 0:
        raise RuntimeError("P2b sanity assertion FAILED: sd(M) == 0 — the circular "
                           "roll is not doing anything. STOP condition.")
    if not first_draw_check["rolled_differs_all_nine"]:
        raise RuntimeError("P2b sanity assertion FAILED: on draw 1 the rolled "
                           "conditioner equals the unrolled one for at least one "
                           f"instrument ({first_draw_check['n_differing']}/9 differ). "
                           "STOP condition.")
    if not first_draw_check["M_draw_1_differs_from_D_bar"]:
        raise RuntimeError("P2b sanity assertion FAILED: M_draw(1) == D_bar. "
                           "STOP condition.")

    p_one = float((draws >= d_bar).mean())
    p_two = float((np.abs(draws) >= abs(d_bar)).mean())
    pct = {f"P{q}": float(np.percentile(draws, q)) for q in (1, 5, 25, 50, 75, 95, 99)}
    fired = p_one > P2B_P_CEILING                                # F3
    return {
        "gate": "P2b / F3",
        "not_a_family_wise_correction": (
            "P2b is NOT a family-wise correction and must not be described as one. "
            "The family here is ONE pre-registered conditioner/horizon/response. It "
            "prices the autocorrelation and volatility-clustering structure the "
            "circular roll preserves."),
        "multiple_testing_statement": (
            "This cycle carries NO multiple-testing protection beyond its single "
            "pre-registration. A follow-on construct built on this cell inherits "
            "ONE test, not 72."),
        "n_draws": PLACEBO_DRAWS, "seed": PLACEBO_SEED,
        "N_min_anchors": n_min, "offset_range": [lo, hi],
        "offset_mean": float(offsets.mean()),
        "D_bar_observed": d_bar,
        "mean_M": float(draws.mean()), "sd_M": sd_m,
        "min_M": float(draws.min()), "max_M": float(draws.max()),
        "percentiles_M": pct,
        "P95_M": pct["P95"], "P99_M": pct["P99"],
        "p_one_tailed": p_one,
        "p_two_tailed": p_two,
        "share_M_positive": float((draws > 0).mean()),
        "median_M": pct["P50"],
        "sanity_assertions": {"sd_M_positive": True, **first_draw_check},
        "kill_clause": f"one-tailed p > {P2B_P_CEILING}",
        "F3_fired": bool(fired),
        "draws_artifact": "p2b_null_draws.csv",
        "_draws": draws, "_offsets": offsets,
    }


# --------------------------------------------------------------------------- #
#  P3 — cost-admissibility requirement (NOT a falsification condition)
# --------------------------------------------------------------------------- #
def build_basket_1h(closes: pd.DataFrame, per_side: float) -> pd.DataFrame:
    """Equal-weight monthly-rebalanced long basket at 1h, via the committed rule.

    PB.build_benchmark IS the authoritative construction (assignment: "read its
    header and reuse the rule; do not invent a second construction"). Its
    month_end_bars() marks the last bar of each calendar month at whatever
    resolution it is handed, which at 1h is the last 1h bar of the month —
    exactly what this assignment specifies.
    """
    bars, _, rec = PB.build_benchmark(closes, per_side, rebalance=True)
    bars.attrs["turnover_record"] = rec
    return bars


def quantize(m_raw: pd.Series) -> pd.Series:
    """Nearest of {0.25, 0.50, 0.75, 1.00}."""
    return (np.round(m_raw / M_STEP) * M_STEP).clip(M_MIN, M_MAX)


def overlay(b: pd.Series, m: pd.Series, per_side: float) -> pd.DataFrame:
    """o[t] = m[t-2]*b[t] - |m[t-2] - m[t-3]| * per_side_cost("taker").

    The 2-bar lag matches validator.signal_to_returns' documented convention:
    the conditioner is complete at the close of t-2, execution is at the open of
    t-1, and the position is held from the close of t-1 onward.
    """
    m2, m3 = m.shift(2), m.shift(3)
    turn = (m2 - m3).abs()
    gross = m2 * b
    cost = turn * per_side
    return pd.DataFrame({"m_applied": m2, "turnover": turn,
                         "ret_gross": gross, "ret_net": gross - cost,
                         "cost": cost}, index=b.index)


def per_period_sharpe(x: pd.Series) -> float:
    """Per-period Sharpe with the sample sd (ddof=1), matching metrics()."""
    x = x.dropna()
    sd = float(x.std())
    return float(x.mean() / sd) if sd > 0 else 0.0


def multiplier_series(b: pd.Series, w: int = W, m_min: float = M_MIN,
                      quantized: bool = True) -> tuple[pd.Series, float]:
    """dsd_basket -> target (TRAIN median) -> clipped, quantized multiplier."""
    dsd_b = np.sqrt((np.minimum(b, 0.0) ** 2).rolling(w).mean())
    target = float(dsd_b.loc[dsd_b.index <= TRAIN_END_1H].median())
    m_raw = (target / dsd_b).clip(lower=m_min, upper=M_MAX)
    m = quantize(m_raw) if quantized else m_raw
    if quantized and m_min != M_MIN:
        m = m.clip(lower=m_min)
    return m, target


def turnover_report(o: pd.DataFrame, per_side: float, label: str) -> dict:
    t = o["turnover"].dropna()
    m = o["m_applied"].dropna()
    return {
        "label": label,
        "sum_abs_delta_m": float(t.sum()),
        "n_multiplier_changes": int((t > 0).sum()),
        "total_turnover_cost_bps": float(t.sum() * per_side * 1e4),
        "mean_m": float(m.mean()),
        "share_m_at_1.00": float((m >= M_MAX - 1e-12).mean()),
        "n_bars": int(len(m)),
    }


def p3_cost_admissibility(bars: pd.DataFrame, per_side: float) -> dict:
    b = bars["ret_net"]
    m, target = multiplier_series(b)
    o = overlay(b, m, per_side)

    # Identical evaluation window for both series: TRAIN+VAL bars on which the
    # overlay is defined (m[t-2] and m[t-3] both exist). Comparing Sharpe(o) on a
    # short window against Sharpe(b) on a long one would not be like-for-like.
    ok = o["ret_net"].notna() & o["turnover"].notna()
    win = ok & (b.index <= VAL_END_1H)
    b_w, o_w = b[win], o.loc[win, "ret_net"]

    s_b, s_o = per_period_sharpe(b_w), per_period_sharpe(o_w)
    met = s_o > s_b

    # Frequency diagnostic: the same construct without the quantizer. NOT a
    # variant, never evaluated on TEST, does not count against the budget.
    m_c, _ = multiplier_series(b, quantized=False)
    o_c = overlay(b, m_c, per_side)
    ok_c = o_c["ret_net"].notna() & o_c["turnover"].notna() & (b.index <= VAL_END_1H)

    return {
        "gate": "P3 — cost-admissibility REQUIREMENT (NOT a falsification condition)",
        "status_statement": (
            "P3 is a cost check ONLY. A de-risking multiplier raises Sharpe on any "
            "volatility-clustered series whether or not the hypothesised relationship "
            "exists, so P3 may not be cited anywhere as evidence that the mechanism "
            "exists. The evidence is P2 and P2b."),
        "window": {"first": str(b_w.index.min()), "last": str(b_w.index.max()),
                   "n_bars": int(len(b_w)),
                   "definition": "TRAIN+VAL bars where m[t-2] and m[t-3] are both defined"},
        "target_train_median_dsd_basket": target,
        "sharpe_b_per_period": s_b,
        "sharpe_o_per_period": s_o,
        "sharpe_b_annualised": s_b * float(np.sqrt(BARS_PER_YEAR)),
        "sharpe_o_annualised": s_o * float(np.sqrt(BARS_PER_YEAR)),
        "delta_per_period": s_o - s_b,
        "requirement": "Sharpe(o) > Sharpe(b) over TRAIN+VAL",
        "requirement_met": bool(met),
        "turnover_quantized": turnover_report(o.loc[win], per_side, "quantized (the construct)"),
        "frequency_diagnostic_continuous": {
            **turnover_report(o_c.loc[ok_c], per_side, "continuous m_raw (diagnostic only)"),
            "sharpe_o_per_period": per_period_sharpe(o_c.loc[ok_c, "ret_net"]),
            "note": ("REPORTED, NON-GATING, NOT a variant, NOT evaluated on TEST. Exists "
                     "to tell the next Director whether the mechanism extends to a "
                     "higher-frequency implementation."),
        },
    }


# --------------------------------------------------------------------------- #
#  Reporting helpers
# --------------------------------------------------------------------------- #
def _w(name: str, obj) -> str:
    fp = OUT_DIR / name
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        obj.to_csv(fp, float_format="%.12g", lineterminator="\n")
    else:
        fp.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    return f"research/results/{TASK_ID}_raw/{name}"


def hr(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_side = V.per_side_cost(EXECUTION_MODE)
    round_trip = V.round_trip_cost(EXECUTION_MODE)
    boundary_1h = V.holdout_boundary(PROGRAM, freq=TIMEFRAME)

    pairs = PB.load_whitelist()
    closes, data_rec = load_closes_1h(pairs)

    hr(f"{TASK_ID} / H-SemiVarSizing-1h — downside semideviation, 9-perp 1h basket")
    print(f"Data        : {V.data_integrity_snapshot()}")
    print(f"Costs       : {V.describe_cost_model(EXECUTION_MODE)}")
    print(f"per_side_cost('{EXECUTION_MODE}') = {per_side:.6f} "
          f"({per_side * 1e4:.1f} bps)   round trip {round_trip * 1e4:.1f} bps")
    print(f"Splits      : train<={SPLIT_DATES[0]} val<={SPLIT_DATES[1]} test<={SPLIT_DATES[2]}"
          f"   1h boundary {boundary_1h}   holdout after it is UNTOUCHED")
    print(f"Instruments : {', '.join(p.split('/')[0] for p in pairs)}")

    # ---------------- conditioners on the FULL series, then slice ------------
    cond_by_pair, anchors_by_pair, anchor_rec = {}, {}, {}
    for p in pairs:
        c = conditioners(closes[p])
        cond_by_pair[p] = c
        a, rec = build_anchor_frame(c)
        anchors_by_pair[p] = a
        anchor_rec[p] = rec
    pooled = int(sum(r["n_anchors"] for r in anchor_rec.values()))
    print(f"\nCensus anchors (TRAIN+VAL, warmup {W}, trim {TRIM}): pooled {pooled} bars")
    for p in pairs:
        r = anchor_rec[p]
        print(f"  {p.split('/')[0]:5s} raw {r['n_train_val_bars_raw']:6d} -> anchors "
              f"{r['n_anchors']:6d}  {r['first_anchor'][:16]} .. {r['last_anchor'][:16]}"
              f"  (fwd window ends {r['last_bar_read_by_forward_window'][:16]})")

    hr("Lookahead / leakage / arithmetic verification (raises on any failure)")
    checks = leakage_and_arithmetic_checks(closes, anchors_by_pair, census)
    ti = checks["truncation_invariance"]
    print(f"  truncation invariance : D_bar {ti['D_bar_full_series_input']} (full input) "
          f"== {ti['D_bar_truncated_input']} (truncated at val_end) -> "
          f"{ti['bit_identical']}")
    icp = checks["independent_code_path"]
    print(f"  independent code path : max |diff| {icp['max_abs_difference']:.3e} "
          f"(tie-handling at quintile edges) — D_bar searchsorted "
          f"{icp['searchsorted_PRIMARY']['D_bar']:+.6f} (breadth "
          f"{icp['searchsorted_PRIMARY']['breadth']}/9) vs qcut "
          f"{icp['qcut_alternative']['D_bar']:+.6f} (breadth "
          f"{icp['qcut_alternative']['breadth']}/9); KILL clauses agree: "
          f"{icp['kill_clauses_agree_under_both_conventions']}")
    print(f"  hand arithmetic       : {checks['hand_arithmetic']['pair']} "
          f"{checks['hand_arithmetic']['timestamp']} agree, and "
          f"dsd^2+usd^2 == mean(r^2) holds")
    print(f"  forward containment   : last bar any forward window reads = "
          f"{checks['forward_window_containment']['last_bar_read_any_instrument']} "
          f"< val_end {checks['forward_window_containment']['val_end_1h']}")

    artifacts = {}
    artifacts["lookahead_checks"] = _w("lookahead_checks.json", checks)
    artifacts["anchor_census_shape"] = _w("anchor_census_shape.json",
                                          {"per_instrument": anchor_rec,
                                           "pooled_anchor_bars": pooled,
                                           "data_inventory": data_rec})

    results: dict = {
        "task": TASK_ID,
        "hypothesis": "H-SemiVarSizing-1h",
        "program": PROGRAM,
        "cost_model": V.cost_model_snapshot(EXECUTION_MODE),
        "data_manifest": V.data_integrity_snapshot(),
        "splits": {"train_end": SPLIT_DATES[0], "val_end": SPLIT_DATES[1],
                   "test_end": SPLIT_DATES[2], "mode": "date_pinned",
                   "holdout_after_1h": str(boundary_1h),
                   "holdout_untouched": True},
        "pre_registered": {"W": W, "h": H, "trim": TRIM, "quantiles": N_QUANTILES,
                           "m_range": [M_MIN, M_MAX], "m_step": M_STEP,
                           "placebo_draws": PLACEBO_DRAWS, "placebo_seed": PLACEBO_SEED,
                           "mc_sims": MC_SIMS, "mc_seeds": list(MC_SEEDS),
                           "n_trials": N_TRIALS},
        "anchor_shape": {"per_instrument": anchor_rec, "pooled_anchor_bars": pooled},
        "data_inventory": data_rec,
        "lookahead_checks": checks,
    }

    # ------------------------------- P1 --------------------------------------
    hr("P1 — persistence of the conditioner (F1)")
    p1 = p1_persistence(anchors_by_pair)
    results["P1"] = p1
    for row in p1["per_instrument"]:
        print(f"  {row['pair'].split('/')[0]:5s} rho {row['rho']:+.6f}  n {row['n']}")
    print(f"  median rho {p1['median_rho']:+.6f} (floor {P1_MEDIAN_FLOOR})   "
          f"min rho {p1['min_rho']:+.6f} (floor > {P1_MIN_FLOOR})")
    print(f"  F1 fired: {p1['F1_fired']}")
    artifacts["p1"] = _w("p1_persistence.csv", pd.DataFrame(p1["per_instrument"]))
    if p1["F1_fired"]:
        results["verdict"] = {"stopped_at": "P1", "F1_fired": True, "F2_fired": None,
                              "F3_fired": None, "trials_spent": 0}
        return _finish(results, artifacts)

    # ------------------------------- P2 --------------------------------------
    hr("P2 — harm census on dsd (F2). THIS IS WHERE THE SCIENCE IS.")
    p2 = p2_harm_census(anchors_by_pair)
    rob = robustness_views(anchors_by_pair)
    results["P2"] = p2
    results["P2_robustness"] = rob
    for key, lbl in (("primary_dsd", "dsd  PRIMARY"), ("diagnostic_sd", "sd   diag"),
                     ("diagnostic_usd", "usd  diag")):
        c = p2[key]
        print(f"\n  {lbl}:  D_bar {c['D_bar']:+.6f}   breadth {c['breadth']}/9")
        for row in c["per_instrument"]:
            print(f"    {row['pair'].split('/')[0]:5s} D {row['D']:+.6f}  n {row['n']:6d}  "
                  f"q-means " + " ".join(f"{x:+.4f}" for x in row["quintile_means"]))
    print(f"\n  KILL clause: {p2['kill_clause']}")
    print(f"    D_bar <= 0 ? {p2['clause_a_D_bar_non_positive']}   "
          f"B < 5 ? {p2['clause_b_breadth_below_floor']}")
    print(f"  F2 fired: {p2['F2_fired']}")
    print("\n  Robustness (non-gating):")
    for v in rob["per_calendar_year"] + rob["three_disjoint_sub_windows"]:
        print(f"    {v['view']:44s} D_bar(refit) "
              f"{('%+.6f' % v['D_bar_refit_edges']) if v['D_bar_refit_edges'] is not None else 'n/a':>12s}"
              f"  breadth {v['breadth_refit_edges']}/9   D_bar(fixed) "
              f"{('%+.6f' % v['D_bar_fixed_edges']) if v['D_bar_fixed_edges'] is not None else 'n/a':>12s}")
    print(f"    sign flips across views: {rob['sign_flips_across_views']}")

    frames = []
    for key in ("primary_dsd", "diagnostic_sd", "diagnostic_usd"):
        f = pd.DataFrame(p2[key]["per_instrument"])
        f.insert(0, "conditioner", p2[key]["conditioner"])
        frames.append(f)
    artifacts["p2"] = _w("p2_census.csv", pd.concat(frames, ignore_index=True))
    artifacts["p2_robustness"] = _w("p2_robustness_views.json", rob)

    if p2["F2_fired"]:
        pv = post_verdict_diagnostics(anchors_by_pair)
        results["P2_post_verdict_diagnostics"] = pv
        artifacts["p2_post_verdict"] = _w("p2_post_verdict_diagnostics.json", pv)
        print("\n  Post-verdict diagnostics (non-gating; F2 already evaluated):")
        print(f"    D_bar from quintile MEANS   (pre-registered) "
              f"{pv['pooled_mean_prereg']['D_bar']:+.6f}  "
              f"breadth {pv['pooled_mean_prereg']['breadth_positive']}/9")
        print(f"    D_bar from quintile MEDIANS                  "
              f"{pv['pooled_median']['D_bar']:+.6f}  "
              f"breadth {pv['pooled_median']['breadth_positive']}/9")
        print(f"    D_bar from 1%-TRIMMED means                  "
              f"{pv['pooled_trimmed_1pct']['D_bar']:+.6f}  "
              f"breadth {pv['pooled_trimmed_1pct']['breadth_positive']}/9")
        print(f"    median monotonicity rho (quintile index vs mean) "
              f"{pv['median_monotonicity_rho']:+.4f}")
        for r in pv["per_instrument"]:
            print(f"      {r['pair'].split('/')[0]:5s} mono rho {r['monotonicity_rho']:+.4f}  "
                  f"D_mean {r['D_mean_prereg']:+.6f}  D_med {r['D_median']:+.6f}  "
                  f"D_trim {r['D_trimmed_1pct']:+.6f}")
        results["verdict"] = {"stopped_at": "P2", "F1_fired": False, "F2_fired": True,
                              "F3_fired": None, "trials_spent": 0}
        return _finish(results, artifacts)

    # ------------------------------- P2b -------------------------------------
    hr("P2b — circular-shift null control (F3). NOT a family-wise correction.")
    p2b = p2b_placebo(anchors_by_pair, p2["primary_dsd"]["D_bar"])
    draws, offsets = p2b.pop("_draws"), p2b.pop("_offsets")
    artifacts["p2b_draws"] = _w(
        "p2b_null_draws.csv",
        pd.DataFrame({"draw": np.arange(1, PLACEBO_DRAWS + 1),
                      "offset_k": offsets, "M_draw": draws}).set_index("draw"))
    results["P2b"] = p2b
    print(f"  draws {p2b['n_draws']}  seed {p2b['seed']}  N_min {p2b['N_min_anchors']}  "
          f"offset range {p2b['offset_range']}")
    print(f"  D_bar observed {p2b['D_bar_observed']:+.6f}")
    print(f"  null: mean {p2b['mean_M']:+.6f}  sd {p2b['sd_M']:.6f}  "
          f"median {p2b['median_M']:+.6f}  share>0 {p2b['share_M_positive']:.4f}")
    print("  distribution: " + "  ".join(
        f"{k} {v:+.6f}" for k, v in
        [("min", p2b["min_M"])] + list(p2b["percentiles_M"].items()) + [("max", p2b["max_M"])]))
    print(f"  P95 {p2b['P95_M']:+.6f}   P99 {p2b['P99_M']:+.6f}")
    print(f"  one-tailed p {p2b['p_one_tailed']:.4f} (kill if > {P2B_P_CEILING})   "
          f"two-tailed p {p2b['p_two_tailed']:.4f}")
    print(f"  F3 fired: {p2b['F3_fired']}")
    artifacts["p2b"] = _w("p2b_null_summary.json", p2b)

    if p2b["F3_fired"]:
        results["verdict"] = {"stopped_at": "P2b", "F1_fired": False, "F2_fired": False,
                              "F3_fired": True, "trials_spent": 0}
        return _finish(results, artifacts)

    # ------------------------------- P3 --------------------------------------
    hr("P3 — cost-admissibility REQUIREMENT (not a falsification condition)")
    start = pd.Timestamp(WINDOW_START_DATE, tz="UTC")
    joined = pd.DataFrame(closes).dropna()
    if joined.index.min().date() != start.date():
        raise RuntimeError(
            f"first all-nine 1h bar is {joined.index.min()}, not on {start.date()} "
            f"(PB.WINDOW_START). Pre-registered; resolve deliberately.")
    tv_closes = joined.loc[joined.index <= VAL_END_1H]
    V.assert_no_holdout(tv_closes, label="P3 TRAIN+VAL closes", program=PROGRAM)
    bars_tv = build_basket_1h(tv_closes, per_side)
    p3 = p3_cost_admissibility(bars_tv, per_side)
    p3["basket_window"] = {"first": str(tv_closes.index.min()),
                           "last": str(tv_closes.index.max()),
                           "n_bars": int(len(tv_closes)),
                           "turnover_record": bars_tv.attrs["turnover_record"]}
    results["P3"] = p3
    print(f"  basket {p3['basket_window']['first']} .. {p3['basket_window']['last']}  "
          f"({p3['basket_window']['n_bars']} 1h bars, "
          f"{p3['basket_window']['turnover_record']['n_rebalances']} monthly rebalances)")
    print(f"  target (TRAIN median dsd_basket) = {p3['target_train_median_dsd_basket']:.8f}")
    print(f"  evaluation window {p3['window']['first']} .. {p3['window']['last']} "
          f"({p3['window']['n_bars']} bars)")
    print(f"  Sharpe(b) per-period {p3['sharpe_b_per_period']:+.6f}  "
          f"({p3['sharpe_b_annualised']:+.4f} annualised, sqrt(8760))")
    print(f"  Sharpe(o) per-period {p3['sharpe_o_per_period']:+.6f}  "
          f"({p3['sharpe_o_annualised']:+.4f} annualised)")
    print(f"  delta {p3['delta_per_period']:+.6f}   requirement met: {p3['requirement_met']}")
    tq = p3["turnover_quantized"]
    print(f"  turnover: sum|dm| {tq['sum_abs_delta_m']:.4f}  changes "
          f"{tq['n_multiplier_changes']}  cost {tq['total_turnover_cost_bps']:.2f} bps  "
          f"mean m {tq['mean_m']:.4f}  share at 1.00 {tq['share_m_at_1.00']:.4f}")
    fc = p3["frequency_diagnostic_continuous"]
    print(f"  continuous-m diagnostic: sum|dm| {fc['sum_abs_delta_m']:.4f}  changes "
          f"{fc['n_multiplier_changes']}  cost {fc['total_turnover_cost_bps']:.2f} bps  "
          f"Sharpe(o) {fc['sharpe_o_per_period']:+.6f}")
    artifacts["p3"] = _w("p3_cost_admissibility.json", p3)

    if not p3["requirement_met"]:
        results["verdict"] = {
            "stopped_at": "P3", "F1_fired": False, "F2_fired": False, "F3_fired": False,
            "p3_requirement_met": False, "trials_spent": 0,
            "statement": ("cost-admissibility requirement NOT met. This is NOT a "
                          "falsification of the hypothesis: P1, P2 and P2b passed and "
                          "that finding stands on its own.")}
        return _finish(results, artifacts)

    results["verdict_pre_gates"] = {
        "F1_fired": False, "F2_fired": False, "F3_fired": False,
        "p3_requirement_met": True,
        "statement": "all pre-gates passed; proceeding to the single assigned variant"}
    # THE TRIAL STAGE WAS NEVER WRITTEN, and this raises rather than pretending.
    #
    # T-040 terminated at F2 on 2026-08-05: the dsd harm census came back
    # D_bar = -0.426586 with breadth 0/9, so BOTH kill clauses fired and the
    # cycle spent zero trials. A trial stage is code that would never have run,
    # and shipping an unexercised full-validation path as if it had been
    # exercised is how a report acquires numbers nobody computed.
    #
    # If a re-run reaches this line, the census no longer reproduces. That is a
    # STOP condition and a finding in itself: the Reviewer must report the
    # discrepancy, not route around it by writing the missing stage.
    raise RuntimeError(
        "ALL PRE-GATES PASSED — but this script has no trial stage. The T-040 "
        "cycle terminated at F2 (D_bar = -0.426586, breadth 0/9) and spent zero "
        "trials, so the trial stage was never implemented. Reaching this line "
        "means the P2 census no longer reproduces; STOP and report it.")


def _finish(results: dict, artifacts: dict) -> dict:
    results["artifacts"] = artifacts
    results["warnings"] = (V.data_integrity_warnings()
                           + V.cost_model_warnings(EXECUTION_MODE))
    artifacts["results"] = _w("t040_results.json", results)
    hr("VERDICT")
    v = results.get("verdict") or results.get("verdict_pre_gates")
    print(json.dumps(v, indent=2, default=str))
    print("\nWARNINGS — reproduce verbatim in any report quoting these numbers")
    for x in results["warnings"]:
        print(f"  !! {x}\n")
    print(f"Artifacts in research/results/{TASK_ID}_raw/:")
    for k, p in artifacts.items():
        print(f"  {k:26s} {p}")
    return results


if __name__ == "__main__":
    main()
