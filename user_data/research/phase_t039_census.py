#!/usr/bin/env python
"""
T-039 / H-IntradayEdgeFloor-1h
==============================

72-cell conditional-mean census on the nine OKX USDT perpetual swaps at 1h.

Assigned by research/NEXT_TASK.md (2026-08-03). This script IS the whole cycle:
there is no strategy object, no backtest, no optimization and no trial. It is
arithmetic on held feathers plus a pre-registered family-wise placebo control.

Pre-registered design (do not change without a new NEXT_TASK.md):
    6 state variables x 6 horizons x 2 tails = 72 cells
    horizons {1,2,4,8,12,24} bars, tails TOP (10th decile) / BOT (1st decile)
    census window  = TRAIN+VAL, minus each instrument's final 24 bars
    placebo        = 1,000 circular-shift draws, seed 20260803
    gates          = G0 coverage, G1 non-degeneracy, G2 economic, G3 breadth,
                     G4 placebo, G5 TEST presence; a cell PASSES only on
                     G1 and G2 and G3 and G4 and G5 (conjunctive).

Every cost figure resolves from validator.COST_MODEL via round_trip_cost();
nothing is hardcoded. Importing validator verifies the data manifest and fails
closed. This script only READS under user_data/data/ and writes nothing there.

Re-runnable unmodified: every random draw is seeded, so output is byte-identical.

Outputs -> research/results/T-039_raw/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validator as V  # noqa: E402  (import-time data-manifest gate is deliberate)

REPO = HERE.parents[1]
FUTURES_DIR = REPO / "user_data" / "data" / "okx" / "futures"
OUT = REPO / "research" / "results" / "T-039_raw"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Pre-registered constants (NEXT_TASK.md, "Research budget" / "Split spec")
# --------------------------------------------------------------------------- #
INSTRUMENTS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
VARIABLES = ["mom_24", "vol_ratio", "volume_z", "range_pos", "cs_mom_rank", "illiq"]
HORIZONS = [1, 2, 4, 8, 12, 24]
TAILS = ["TOP", "BOT"]

TRAIN_END, VAL_END, TEST_END = "2024-11-22", "2025-04-21", "2025-09-19"
PROGRAM, FREQ = "perps", "1h"

TRIM_BARS = 24            # NEXT_TASK.md "Census window": "minus its final 24 bars"
TRIM_SENSITIVITY = 25     # diagnostic only - see report section on the off-by-one

SEED = 20260803
N_DRAWS = 1000
MIN_OFFSET = 720

G1_POOLED_MIN = 1000
G1_PER_INSTRUMENT_MIN = 50
G3_BREADTH_MIN = 5
G5_TEST_DATE_MIN = 30

# Windows for the six variables, all backward-looking.
W_MOM = 24
W_VOL_FAST, W_VOL_SLOW = 24, 168
W_VOLUME = 168
W_RANGE = 24
W_ILLIQ = 24
CS_MIN_PRESENT = 6


# --------------------------------------------------------------------------- #
# Logging: everything printed is also captured to a raw artifact.
# --------------------------------------------------------------------------- #
class Tee:
    def __init__(self, path):
        self.fh = open(path, "w", encoding="utf-8", newline="\n")
        self.stdout = sys.stdout

    def write(self, s):
        self.stdout.write(s)
        self.fh.write(s)

    def flush(self):
        self.stdout.flush()
        self.fh.flush()


def hr(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# --------------------------------------------------------------------------- #
# Data loading + G0
# --------------------------------------------------------------------------- #
def load_instrument(sym: str) -> pd.DataFrame:
    """Read the 1h futures feather directly.

    validator.load() resolves against DATA_DIR with a flat filename convention and
    will not find the futures tree (NEXT_TASK.md, "Environment notes").
    """
    fp = FUTURES_DIR / f"{sym}_USDT_USDT-1h-futures.feather"
    df = pd.read_feather(fp)
    df = df.set_index("date").sort_index()
    return df.astype({"open": float, "high": float, "low": float,
                      "close": float, "volume": float})


def g0_coverage(raw: dict) -> pd.DataFrame:
    rows = []
    for sym, df in raw.items():
        idx = df.index
        strictly_increasing = bool(idx.is_monotonic_increasing) and bool(idx.is_unique)
        n_dupes = int(len(idx) - idx.nunique())
        rows.append({
            "instrument": sym,
            "bars": len(df),
            "first": str(idx[0]),
            "last": str(idx[-1]),
            "strictly_increasing": strictly_increasing,
            "duplicate_timestamps": n_dupes,
            "tz": str(idx.tz),
            "nan_close": int(df["close"].isna().sum()),
            "zero_volume_bars": int((df["volume"] == 0).sum()),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# State variables - computed on each instrument's FULL 1h series, then sliced
# (NEXT_TASK.md "Warmup", directive 8). All are causal: value at t uses bars <= t.
# --------------------------------------------------------------------------- #
def per_instrument_variables(df: pd.DataFrame) -> pd.DataFrame:
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    logc = np.log(c)
    r = logc.diff()

    out = pd.DataFrame(index=df.index)

    # 1. mom_24 = log(c_t) - log(c_{t-24})
    out["mom_24"] = logc.diff(W_MOM)

    # 2. vol_ratio = std(r, 24 ending t) / std(r, 168 ending t); pandas ddof=1
    fast = r.rolling(W_VOL_FAST, min_periods=W_VOL_FAST).std()
    slow = r.rolling(W_VOL_SLOW, min_periods=W_VOL_SLOW).std()
    out["vol_ratio"] = fast / slow.replace(0.0, np.nan)

    # 3. volume_z on log1p(volume), 168-bar mean/std ending t
    lv = np.log1p(v)
    mu = lv.rolling(W_VOLUME, min_periods=W_VOLUME).mean()
    sd = lv.rolling(W_VOLUME, min_periods=W_VOLUME).std()
    out["volume_z"] = (lv - mu) / sd.replace(0.0, np.nan)

    # 4. range_pos = (c - min(l,24)) / (max(h,24) - min(l,24)); NaN if denom == 0
    lo = l.rolling(W_RANGE, min_periods=W_RANGE).min()
    hi = h.rolling(W_RANGE, min_periods=W_RANGE).max()
    out["range_pos"] = (c - lo) / (hi - lo).replace(0.0, np.nan)

    # 6. illiq = mean_24( |r_s| / (v_s * c_s) ) * 1e9; v_s == 0 -> NaN, window NaN
    #    if any contributing bar is NaN (rolling min_periods == window gives this).
    quote = (v * c).replace(0.0, np.nan)
    amihud = (r.abs() / quote)
    out["illiq"] = amihud.rolling(W_ILLIQ, min_periods=W_ILLIQ).mean() * 1e9

    # cs_mom_rank is cross-sectional; filled in by add_cs_mom_rank().
    return out


def add_cs_mom_rank(varframes: dict) -> None:
    """Cross-sectional rank of mom_24 across instruments present at each timestamp.

    scaled = (rank - 1) / (n_present - 1) in [0,1]; NaN if n_present < 6.
    Ties take pandas' default 'average' method (mom_24 is continuous; exact ties
    are effectively absent, and the count is reported below).
    """
    panel = pd.DataFrame({sym: vf["mom_24"] for sym, vf in varframes.items()})
    panel = panel.sort_index()
    n_present = panel.notna().sum(axis=1)
    ranks = panel.rank(axis=1, method="average", na_option="keep")
    scaled = (ranks.sub(1.0)).div((n_present - 1).replace(0, np.nan), axis=0)
    scaled = scaled.where(n_present >= CS_MIN_PRESENT)
    for sym, vf in varframes.items():
        vf["cs_mom_rank"] = scaled[sym].reindex(vf.index)
    return panel, n_present


def forward_returns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executable and naive forward log returns on the FULL series.

    executable: fwd_h(t) = log(c_{t+1+h}) - log(c_{t+1})    <- used by every gate
    naive:      fwd_h(t) = log(c_{t+h})   - log(c_t)        <- diagnostic ONLY
    """
    logc = np.log(df["close"])
    ex = pd.DataFrame(index=df.index)
    na = pd.DataFrame(index=df.index)
    for h in HORIZONS:
        ex[f"fwd_{h}"] = logc.shift(-(1 + h)) - logc.shift(-1)
        na[f"fwd_{h}"] = logc.shift(-h) - logc
    return ex, na


# --------------------------------------------------------------------------- #
# Matrix computation
# --------------------------------------------------------------------------- #
def decile_thresholds(cens: dict) -> dict:
    """Per instrument, per variable: (q10, q90) on the census window (TRAIN+VAL).

    Never re-estimated on TEST.
    """
    thr = {}
    for sym, d in cens.items():
        q = np.full((2, len(VARIABLES)), np.nan)
        for j, _var in enumerate(VARIABLES):
            col = d["V"][:, j]
            if np.isfinite(col).sum() > 0:
                q[0, j] = np.nanquantile(col, 0.10)
                q[1, j] = np.nanquantile(col, 0.90)
        thr[sym] = q
    return thr


def tail_mask(col: np.ndarray, q10: float, q90: float, tail: str) -> np.ndarray:
    if tail == "TOP":
        return col >= q90          # 10th (highest) decile
    return col <= q10              # 1st (lowest) decile


def compute_matrix(cens: dict, thr: dict, fwd_key: str) -> pd.DataFrame:
    """Full 72-cell matrix. fwd_key is 'F' (executable) or 'Fn' (naive)."""
    # Unconditional means over ALL census bars, pooled and per instrument.
    pooled_sum = np.zeros(len(HORIZONS))
    pooled_cnt = np.zeros(len(HORIZONS))
    uncond_i = {}
    for sym, d in cens.items():
        Fm = d[fwd_key]
        valid = np.isfinite(Fm)
        pooled_sum += np.nansum(np.where(valid, Fm, 0.0), axis=0)
        pooled_cnt += valid.sum(axis=0)
        uncond_i[sym] = np.nansum(np.where(valid, Fm, 0.0), axis=0) / valid.sum(axis=0)
    mu_uncond = pooled_sum / pooled_cnt

    rows = []
    for j, var in enumerate(VARIABLES):
        for tail in TAILS:
            masks = {sym: tail_mask(d["V"][:, j], thr[sym][0, j], thr[sym][1, j], tail)
                     for sym, d in cens.items()}
            for hi, h in enumerate(HORIZONS):
                vals, per_inst_mu, per_inst_n = [], {}, {}
                for sym, d in cens.items():
                    x = d[fwd_key][masks[sym], hi]
                    x = x[np.isfinite(x)]
                    per_inst_n[sym] = int(x.size)
                    per_inst_mu[sym] = float(x.mean()) if x.size else np.nan
                    vals.append(x)
                pooled = np.concatenate(vals) if vals else np.array([])
                n_bucket = int(pooled.size)
                mu_cell = float(pooled.mean()) if n_bucket else np.nan
                sd_cell = float(pooled.std(ddof=1)) if n_bucket > 1 else np.nan
                excess = mu_cell - mu_uncond[hi]
                d_sign = 1 if excess > 0 else -1

                n_eff = n_bucket / h
                se_mu = sd_cell / np.sqrt(n_eff) if n_bucket else np.nan

                breadth = sum(1 for sym in cens
                              if np.isfinite(per_inst_mu[sym])
                              and d_sign * (per_inst_mu[sym] - uncond_i[sym][hi]) > 0)

                row = {
                    "variable": var, "h": h, "tail": tail,
                    "mu_cell_bps": mu_cell * 1e4,
                    "mu_uncond_bps": mu_uncond[hi] * 1e4,
                    "excess_bps": excess * 1e4,
                    "d": d_sign,
                    "d_excess_bps": d_sign * excess * 1e4,
                    "d_mu_cell_bps": d_sign * mu_cell * 1e4,
                    "sd_bucket_bps": sd_cell * 1e4,
                    "n_bucket": n_bucket,
                    "n_eff": n_eff,
                    "se_mu_cell_bps": se_mu * 1e4,
                    "breadth_count": breadth,
                    "min_per_instrument_n": int(min(per_inst_n.values())),
                }
                for sym in INSTRUMENTS:
                    row[f"n_{sym}"] = per_inst_n[sym]
                    row[f"excess_{sym}_bps"] = (per_inst_mu[sym] - uncond_i[sym][hi]) * 1e4
                rows.append(row)
    return pd.DataFrame(rows), mu_uncond, uncond_i


# --------------------------------------------------------------------------- #
# Placebo control (G4)
# --------------------------------------------------------------------------- #
def placebo_control(cens: dict, thr: dict, mu_uncond: np.ndarray, rng) -> tuple:
    """1,000 circular-shift draws; M_draw = max over the 72 cells of |excess|.

    Shift each instrument's six state-variable series forward by the SAME k,
    leaving its return series in place, then recompute thresholds and all 72
    |excess| values.

    Implementation note (verified, not assumed): a circular shift permutes the
    variable's values without changing the multiset, so the recomputed decile
    thresholds are EXACTLY the unshifted ones and the shifted mask is
    roll(mask, k). assert_shift_thresholds_invariant() below proves this on real
    data before the loop runs, so the loop gathers rows at (idx + k) % n instead
    of re-sorting 54 arrays per draw. This is an optimization of the specified
    computation, not a change to it.
    """
    syms = list(cens.keys())
    n_i = {s: cens[s]["V"].shape[0] for s in syms}
    n_min = min(n_i.values())

    # Original tail index arrays, per instrument / variable / tail.
    idx_map = {}
    for s in syms:
        for j in range(len(VARIABLES)):
            for tail in TAILS:
                m = tail_mask(cens[s]["V"][:, j], thr[s][0, j], thr[s][1, j], tail)
                idx_map[(s, j, tail)] = np.flatnonzero(m)

    lo, hi = MIN_OFFSET, n_min - MIN_OFFSET
    M = np.empty(N_DRAWS)
    argmax_rec = []
    first_draw_cells = None
    for draw in range(N_DRAWS):
        k = int(rng.integers(lo, hi, endpoint=True))
        cells = np.empty((len(VARIABLES), len(TAILS), len(HORIZONS)))
        for j in range(len(VARIABLES)):
            for ti, tail in enumerate(TAILS):
                tot = np.zeros(len(HORIZONS))
                cnt = np.zeros(len(HORIZONS))
                for s in syms:
                    idx = idx_map[(s, j, tail)]
                    if idx.size == 0:
                        continue
                    rows = cens[s]["F"][(idx + k) % n_i[s]]
                    valid = np.isfinite(rows)
                    tot += np.nansum(np.where(valid, rows, 0.0), axis=0)
                    cnt += valid.sum(axis=0)
                mu = np.divide(tot, cnt, out=np.full(len(HORIZONS), np.nan),
                               where=cnt > 0)
                cells[j, ti, :] = np.abs(mu - mu_uncond)
        M[draw] = np.nanmax(cells)
        aj, at, ah = np.unravel_index(np.nanargmax(cells), cells.shape)
        argmax_rec.append({"draw": draw, "k": k, "M_bps": M[draw] * 1e4,
                           "argmax_variable": VARIABLES[aj],
                           "argmax_tail": TAILS[at],
                           "argmax_h": HORIZONS[ah]})
        if draw == 0:
            first_draw_cells = cells.copy()
    return M, first_draw_cells, n_min, (lo, hi), pd.DataFrame(argmax_rec)


def assert_shift_thresholds_invariant(cens: dict, thr: dict, k: int) -> dict:
    """Prove the circular shift leaves decile thresholds exactly unchanged."""
    worst = 0.0
    checked = 0
    for sym, d in cens.items():
        n = d["V"].shape[0]
        for j in range(len(VARIABLES)):
            col = d["V"][:, j]
            rolled = np.roll(col, k)
            for qi, q in ((0, 0.10), (1, 0.90)):
                a = np.nanquantile(rolled, q)
                b = thr[sym][qi, j]
                worst = max(worst, abs(a - b))
                checked += 1
    return {"pairs_checked": checked, "max_abs_threshold_difference": float(worst)}


# --------------------------------------------------------------------------- #
# G5 - TEST presence (state variable ONLY; no TEST forward return is computed)
# --------------------------------------------------------------------------- #
def g5_test_presence(test_vars: dict, thr: dict, test_dates: pd.DatetimeIndex) -> pd.DataFrame:
    all_dates = sorted({d.date() for d in test_dates})
    rows = []
    for j, var in enumerate(VARIABLES):
        for tail in TAILS:
            fired_dates = set()
            per_inst = {}
            for sym, tv in test_vars.items():
                col = tv["V"][:, j]
                m = tail_mask(col, thr[sym][0, j], thr[sym][1, j], tail)
                dts = {d.date() for d in tv["index"][m]}
                per_inst[sym] = len(dts)
                fired_dates |= dts
            row = {"variable": var, "tail": tail,
                   "test_dates_total": len(all_dates),
                   "pooled_fired_dates": len(fired_dates),
                   "min_instrument_fired_dates": min(per_inst.values()),
                   "median_instrument_fired_dates": int(np.median(list(per_inst.values())))}
            for sym in INSTRUMENTS:
                row[f"dates_{sym}"] = per_inst[sym]
            rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Spearman correlation + effective number of independent tests
# --------------------------------------------------------------------------- #
def spearman_pooled(cens: dict) -> tuple[pd.DataFrame, dict]:
    stacked = np.vstack([d["V"] for d in cens.values()])
    df = pd.DataFrame(stacked, columns=VARIABLES)
    corr = df.corr(method="spearman", min_periods=1000)

    # Li & Ji (2005) effective number of independent tests from the eigenvalues.
    C = corr.to_numpy()
    C = np.where(np.isfinite(C), C, 0.0)
    np.fill_diagonal(C, 1.0)
    eig = np.linalg.eigvalsh(C)
    eig = np.clip(eig, 0.0, None)
    m_eff_liji = float(sum((1.0 if e >= 1 else 0.0) + (e - np.floor(e)) for e in eig))
    # Cheverud-Nyholt variance form, reported alongside as a second estimator.
    m = len(VARIABLES)
    m_eff_cn = float(1 + (m - 1) * (1 - np.var(eig, ddof=1) / m))
    return corr, {"eigenvalues": [float(e) for e in eig],
                  "m_eff_li_ji": m_eff_liji,
                  "m_eff_cheverud_nyholt": m_eff_cn,
                  "raw_variables": m}


# --------------------------------------------------------------------------- #
def main() -> int:
    tee = Tee(OUT / "run_log.txt")
    sys.stdout = tee
    try:
        return _run()
    finally:
        sys.stdout = tee.stdout
        tee.fh.close()


def _run() -> int:
    hr("T-039 / H-IntradayEdgeFloor-1h - 72-cell conditional-mean census")
    print(f"pandas {pd.__version__} | numpy {np.__version__} | python {sys.version.split()[0]}")
    print(f"repo root: {REPO}")

    # ---- cost model: resolved, never typed ------------------------------- #
    hr("Cost model (resolved from validator.COST_MODEL)")
    print("describe_cost_model('taker'):")
    print("  " + V.describe_cost_model("taker"))
    per_side = V.per_side_cost("taker")
    rt = V.round_trip_cost("taker")
    RT_BPS = rt * 1e4
    C1_EXCESS_BPS = 2.0 * RT_BPS      # "exceeds ... by at least 2 x the round trip"
    C1_MU_BPS = 1.0 * RT_BPS          # "d * mu_cell >= 18.0 bps"
    print(f"  per_side_cost('taker')   = {per_side!r}  -> {per_side*1e4:.4f} bps/side")
    print(f"  round_trip_cost('taker') = {rt!r}  -> {RT_BPS:.4f} bps round trip")
    print(f"  G2 threshold C1a (2 x round trip) = {C1_EXCESS_BPS:.4f} bps")
    print(f"  G2 threshold C1b (1 x round trip) = {C1_MU_BPS:.4f} bps")
    for w in V.cost_model_warnings("taker"):
        print("  WARNING: " + w)
    (OUT / "cost_model.txt").write_text(
        V.describe_cost_model("taker")
        + f"\nper_side_cost('taker')={per_side!r} ({per_side*1e4:.4f} bps)"
        + f"\nround_trip_cost('taker')={rt!r} ({RT_BPS:.4f} bps)"
        + f"\nG2 C1a={C1_EXCESS_BPS:.4f} bps ; G2 C1b={C1_MU_BPS:.4f} bps\n",
        encoding="utf-8")

    hr("Data integrity (validator import-time gate)")
    snap = V.data_integrity_snapshot()
    print(json.dumps(snap, indent=2, default=str))
    if snap.get("bypassed"):
        print("FATAL: data verification was bypassed. This run is not evidence.")
        return 2

    # ---- load + G0 -------------------------------------------------------- #
    hr("G0 - coverage")
    raw = {s: load_instrument(s) for s in INSTRUMENTS}
    cov = g0_coverage(raw)
    print(cov.to_string(index=False))
    cov.to_csv(OUT / "g0_coverage.csv", index=False)
    print(f"\npooled bars (all nine, full series): {int(cov['bars'].sum())}")
    g0_ok = bool(cov["strictly_increasing"].all()
                 and (cov["duplicate_timestamps"] == 0).all()
                 and (cov["nan_close"] == 0).all())
    print(f"G0: {'PASS' if g0_ok else 'FAIL'}")
    if not g0_ok:
        print("FATAL: G0 failed -> BLOCK per NEXT_TASK.md. Stopping.")
        return 3

    # ---- variables on the FULL series, then slice ------------------------- #
    hr("State variables (computed on each full 1h series, then sliced)")
    varframes = {s: per_instrument_variables(df) for s, df in raw.items()}
    panel, n_present = add_cs_mom_rank(varframes)
    rmin = panel.rank(axis=1, method="min")
    rmax = panel.rank(axis=1, method="max")
    ties = int(((rmin != rmax) & panel.notna()).sum().sum())
    print(f"cs_mom_rank panel: {panel.shape[0]} timestamps, "
          f"rows with n_present >= {CS_MIN_PRESENT}: "
          f"{int((n_present >= CS_MIN_PRESENT).sum())}, exact mom_24 ties: {ties}")
    fwd = {s: forward_returns(df) for s, df in raw.items()}

    # ---- split ------------------------------------------------------------ #
    hr("Split (validator.split_by_dates, date-pinned) + holdout assertions")
    print(f"split triple: train_end={TRAIN_END} val_end={VAL_END} test_end={TEST_END}")
    print(f"holdout_boundary('{PROGRAM}', freq='{FREQ}') = "
          f"{V.holdout_boundary(PROGRAM, freq=FREQ)}")
    print(f"holdout_boundary('{PROGRAM}') [daily reading] = {V.holdout_boundary(PROGRAM)}")

    holdout_lines = []
    try:
        V.assert_no_holdout(raw["BTC"], label="RAW FULL SERIES (BTC)",
                            program=PROGRAM)
        holdout_lines.append("RAW FULL SERIES (BTC): unexpectedly passed")
    except V.HoldoutViolation as e:
        holdout_lines.append(
            "RAW FULL SERIES (BTC): guard RAISES as expected -> "
            + str(e).split(" (")[0]
            + "  [this frame is never an evaluation window; only backward-looking "
              "rolling windows are read from it, and every analysed frame is sliced "
              "before use]")
    print(holdout_lines[-1])

    cens, test_vars, split_report = {}, {}, []
    for sym in INSTRUMENTS:
        df = raw[sym]
        tr, va, te = V.split_by_dates(df, TRAIN_END, VAL_END, TEST_END)
        for name, frame in (("train", tr), ("val", va), ("test", te)):
            V.assert_no_holdout(frame, label=f"{sym} {name}", program=PROGRAM)
            holdout_lines.append(f"{sym} {name}: OK ({len(frame)} bars, "
                                 f"{frame.index[0]} .. {frame.index[-1]})")
        trval = pd.concat([tr, va])
        V.assert_no_holdout(trval, label=f"{sym} train+val", program=PROGRAM)
        holdout_lines.append(f"{sym} train+val: OK ({len(trval)} bars)")

        census_idx = trval.index[:-TRIM_BARS]
        cframe = df.loc[census_idx]
        V.assert_no_holdout(cframe, label=f"{sym} census", program=PROGRAM)
        holdout_lines.append(f"{sym} census: OK ({len(cframe)} bars, "
                             f"{census_idx[0]} .. {census_idx[-1]})")

        vf = varframes[sym].loc[census_idx]
        ex, na = fwd[sym]
        cens[sym] = {
            "index": census_idx,
            "V": vf[VARIABLES].to_numpy(dtype=float),
            "F": ex.loc[census_idx][[f"fwd_{h}" for h in HORIZONS]].to_numpy(dtype=float),
            "Fn": na.loc[census_idx][[f"fwd_{h}" for h in HORIZONS]].to_numpy(dtype=float),
            "trval_index": trval.index,
        }
        # G5 frame: state variable ONLY. No forward return is taken here.
        test_vars[sym] = {
            "index": te.index,
            "V": varframes[sym].loc[te.index][VARIABLES].to_numpy(dtype=float),
        }
        split_report.append({
            "instrument": sym, "train_bars": len(tr), "val_bars": len(va),
            "test_bars": len(te), "trainval_bars": len(trval),
            "census_bars": len(census_idx),
            "census_first": str(census_idx[0]), "census_last": str(census_idx[-1]),
            "test_first": str(te.index[0]), "test_last": str(te.index[-1]),
            "test_dates": len({d.date() for d in te.index}),
            "max_bar_read_by_fwd24": str(
                df.index[df.index.get_loc(census_idx[-1]) + 1 + max(HORIZONS)]),
        })
    sr = pd.DataFrame(split_report)
    print("\n" + sr.to_string(index=False))
    sr.to_csv(OUT / "split_report.csv", index=False)
    (OUT / "holdout_assertions.txt").write_text("\n".join(holdout_lines) + "\n",
                                                encoding="utf-8")
    pooled_trval = int(sr["trainval_bars"].sum())
    pooled_census = int(sr["census_bars"].sum())
    print(f"\npooled TRAIN+VAL bars before the {TRIM_BARS}-bar trim: {pooled_trval} "
          f"(Director-verified figure: 252162)")
    print(f"pooled census bars after the trim: {pooled_census}")
    print(f"TEST dates (should be 151): {sorted(set(sr['test_dates']))}")
    print(f"max bar any executable forward return reads: "
          f"{max(sr['max_bar_read_by_fwd24'])}")

    # NaN audit of the forward matrices inside the census window
    nan_f = {s: int(np.isnan(d["F"]).sum()) for s, d in cens.items()}
    print(f"NaNs in executable forward matrices over census window: {nan_f}")

    # ---- thresholds ------------------------------------------------------- #
    hr("Decile thresholds (per instrument, TRAIN+VAL only)")
    thr = decile_thresholds(cens)
    trows = []
    for sym in INSTRUMENTS:
        for j, var in enumerate(VARIABLES):
            col = cens[sym]["V"][:, j]
            n_valid = int(np.isfinite(col).sum())
            top_n = int(np.sum(tail_mask(col, thr[sym][0, j], thr[sym][1, j], "TOP")))
            bot_n = int(np.sum(tail_mask(col, thr[sym][0, j], thr[sym][1, j], "BOT")))
            trows.append({"instrument": sym, "variable": var,
                          "q10": thr[sym][0, j], "q90": thr[sym][1, j],
                          "n_valid": n_valid, "n_census": col.size,
                          "n_TOP": top_n, "n_BOT": bot_n,
                          "TOP_frac_of_valid": top_n / n_valid if n_valid else np.nan,
                          "BOT_frac_of_valid": bot_n / n_valid if n_valid else np.nan})
    tdf = pd.DataFrame(trows)
    tdf.to_csv(OUT / "decile_thresholds.csv", index=False)
    print(tdf.groupby("variable")[["TOP_frac_of_valid", "BOT_frac_of_valid"]]
          .agg(["min", "max"]).to_string())

    # Sensitivity: thresholds estimated on the untrimmed TRAIN+VAL instead.
    cens_trval = {}
    for sym in INSTRUMENTS:
        ix = cens[sym]["trval_index"]
        cens_trval[sym] = {"V": varframes[sym].loc[ix][VARIABLES].to_numpy(dtype=float)}
    thr_trval = decile_thresholds(cens_trval)
    max_thr_delta = max(
        float(np.nanmax(np.abs(thr[s] - thr_trval[s]) /
                        np.where(np.abs(thr[s]) > 0, np.abs(thr[s]), np.nan)))
        for s in INSTRUMENTS)
    print(f"\nmax |relative| threshold difference, census-window vs full TRAIN+VAL "
          f"estimation: {max_thr_delta:.3e}")

    # ---- the 72-cell matrix ---------------------------------------------- #
    hr("72-cell matrix - EXECUTABLE anchor (used by every gate)")
    mat, mu_uncond, uncond_i = compute_matrix(cens, thr, "F")
    print("mu_uncond by horizon (bps, pooled over census window):")
    for hi, h in enumerate(HORIZONS):
        print(f"  h={h:>2}: {mu_uncond[hi]*1e4:+.4f} bps")
    pd.DataFrame({"h": HORIZONS, "mu_uncond_bps": mu_uncond * 1e4}).to_csv(
        OUT / "mu_uncond_executable.csv", index=False)

    hr("72-cell matrix - NAIVE anchor (DIAGNOSTIC ONLY, used by NO gate)")
    mat_naive, mu_uncond_naive, _ = compute_matrix(cens, thr, "Fn")
    for hi, h in enumerate(HORIZONS):
        print(f"  h={h:>2}: mu_uncond_naive = {mu_uncond_naive[hi]*1e4:+.4f} bps")
    mat_naive.to_csv(OUT / "matrix_naive_DIAGNOSTIC_ONLY.csv", index=False)

    lag_delta = (mat_naive.set_index(["variable", "h", "tail"])["excess_bps"]
                 - mat.set_index(["variable", "h", "tail"])["excess_bps"])
    print(f"\nexecution-lag effect on excess (naive - executable), bps: "
          f"mean {lag_delta.mean():+.3f}, median {lag_delta.median():+.3f}, "
          f"max |delta| {lag_delta.abs().max():.3f} "
          f"(cell: {lag_delta.abs().idxmax()})")

    # ---- placebo control (G4) -------------------------------------------- #
    hr(f"Placebo control - {N_DRAWS} circular-shift draws, seed {SEED}")
    rng = np.random.default_rng(SEED)
    inv = assert_shift_thresholds_invariant(cens, thr, k=1234)
    print(f"threshold-invariance proof (k=1234): {inv}")
    if inv["max_abs_threshold_difference"] != 0.0:
        print("FATAL: circular shift changed a decile threshold. Stopping.")
        return 4

    M, first_cells, n_min, krange, argmax_df = placebo_control(cens, thr, mu_uncond, rng)
    print(f"N_min (shortest census window) = {n_min}; "
          f"k drawn from Uniform[{krange[0]}, {krange[1]}] inclusive")
    argmax_df.to_csv(OUT / "placebo_argmax_by_draw.csv", index=False)
    print("\nwhich cell supplies the family-wise max, by horizon (counts over 1000 draws):")
    print(argmax_df["argmax_h"].value_counts().sort_index().to_string())
    print("\n...by variable:")
    print(argmax_df["argmax_variable"].value_counts().to_string())
    ctrl = {
        "draws": N_DRAWS, "seed": SEED, "n_min": int(n_min),
        "k_low": int(krange[0]), "k_high": int(krange[1]),
        "mean_M_bps": float(M.mean() * 1e4), "sd_M_bps": float(M.std(ddof=1) * 1e4),
        "P50_M_bps": float(np.percentile(M, 50) * 1e4),
        "P95_M_bps": float(np.percentile(M, 95) * 1e4),
        "P99_M_bps": float(np.percentile(M, 99) * 1e4),
        "min_M_bps": float(M.min() * 1e4), "max_M_bps": float(M.max() * 1e4),
    }
    for k_, v_ in ctrl.items():
        print(f"  {k_}: {v_}")
    pd.DataFrame({"draw": np.arange(N_DRAWS), "M_bps": M * 1e4}).to_csv(
        OUT / "placebo_draws.csv", index=False)

    # Mandatory sanity assertions
    hr("Mandatory sanity assertions (strategy_research_notes lesson 20)")
    a1 = ctrl["sd_M_bps"] > 0 and ctrl["P95_M_bps"] > 0
    print(f"  (1) sd(M) > 0 and P95(M) > 0 : {a1}  "
          f"[sd={ctrl['sd_M_bps']:.4f} bps, P95={ctrl['P95_M_bps']:.4f} bps]")
    unshifted_abs = np.abs(
        mat.set_index(["variable", "tail", "h"])["excess_bps"]
           .unstack("h")[HORIZONS].loc[[(v, t) for v in VARIABLES for t in TAILS]]
           .to_numpy().reshape(len(VARIABLES), len(TAILS), len(HORIZONS)))
    shifted_abs = first_cells * 1e4
    n_diff = int(np.sum(~np.isclose(shifted_abs, unshifted_abs, rtol=0, atol=1e-12)))
    a2 = n_diff > 0
    print(f"  (2) >=1 cell differs shifted vs unshifted : {a2}  "
          f"[{n_diff} of 72 cells differ on draw 1; "
          f"max |difference| = {np.nanmax(np.abs(shifted_abs - unshifted_abs)):.4f} bps]")
    ctrl["assertion_sd_and_p95_positive"] = bool(a1)
    ctrl["assertion_shift_changes_cells"] = bool(a2)
    ctrl["cells_differing_on_draw1"] = n_diff
    (OUT / "placebo_summary.json").write_text(json.dumps(ctrl, indent=2), encoding="utf-8")
    if not (a1 and a2):
        print("FATAL: placebo control degenerate -> BLOCK per NEXT_TASK.md. Stopping.")
        return 5

    # ---- Spearman + effective test count --------------------------------- #
    hr("Pairwise Spearman correlation of the six variables (pooled, NOT gating)")
    corr, eff = spearman_pooled(cens)
    print(corr.round(4).to_string())
    corr.to_csv(OUT / "spearman_variables.csv")
    off = corr.to_numpy().copy()
    np.fill_diagonal(off, 0.0)
    max_abs = float(np.nanmax(np.abs(off)))
    pairs_over_90 = [(VARIABLES[i], VARIABLES[j], float(corr.iloc[i, j]))
                     for i in range(len(VARIABLES)) for j in range(i + 1, len(VARIABLES))
                     if abs(corr.iloc[i, j]) > 0.90]
    print(f"\nmax |off-diagonal rho| = {max_abs:.4f}; pairs exceeding |0.90|: "
          f"{pairs_over_90 if pairs_over_90 else 'none'}")
    eff["max_abs_offdiag_rho"] = max_abs
    eff["pairs_over_0_90"] = pairs_over_90
    eff["effective_cells_li_ji_variable_axis_only"] = eff["m_eff_li_ji"] * len(TAILS) * len(HORIZONS)
    eff["effective_cells_cheverud_variable_axis_only"] = eff["m_eff_cheverud_nyholt"] * len(TAILS) * len(HORIZONS)
    print(f"eigenvalues: {[round(e,4) for e in eff['eigenvalues']]}")
    print(f"M_eff (Li & Ji 2005) over the 6 variables = {eff['m_eff_li_ji']:.4f}")
    print(f"M_eff (Cheverud-Nyholt)                   = {eff['m_eff_cheverud_nyholt']:.4f}")
    print(f"implied effective cells (variable axis only, x12) = "
          f"{eff['effective_cells_li_ji_variable_axis_only']:.2f} of a raw 72")
    (OUT / "effective_tests.json").write_text(json.dumps(eff, indent=2), encoding="utf-8")

    # ---- G5 --------------------------------------------------------------- #
    hr("G5 - TEST presence (state variable read ONLY; no TEST forward return)")
    test_idx_all = pd.DatetimeIndex(sorted(set().union(
        *[set(tv["index"]) for tv in test_vars.values()])))
    g5 = g5_test_presence(test_vars, thr, test_idx_all)
    print(g5[["variable", "tail", "test_dates_total", "pooled_fired_dates",
              "min_instrument_fired_dates", "median_instrument_fired_dates"]]
          .to_string(index=False))
    g5.to_csv(OUT / "g5_test_presence.csv", index=False)

    # ---- gates ------------------------------------------------------------ #
    hr("Gate evaluation - G1 and G2 and G3 and G4 and G5, conjunctive")
    p95 = ctrl["P95_M_bps"]
    g5_map = {(r.variable, r.tail): r.pooled_fired_dates for r in g5.itertuples()}

    mat["G1_pooled_ok"] = mat["n_bucket"] >= G1_POOLED_MIN
    mat["G1_per_instrument_ok"] = mat["min_per_instrument_n"] >= G1_PER_INSTRUMENT_MIN
    mat["G1"] = mat["G1_pooled_ok"] & mat["G1_per_instrument_ok"]
    mat["G2a_d_excess_ge_2rt"] = mat["d_excess_bps"] >= C1_EXCESS_BPS
    mat["G2b_d_mu_cell_ge_rt"] = mat["d_mu_cell_bps"] >= C1_MU_BPS
    mat["G2"] = mat["G2a_d_excess_ge_2rt"] & mat["G2b_d_mu_cell_ge_rt"]
    mat["G3"] = mat["breadth_count"] >= G3_BREADTH_MIN
    mat["G4"] = mat["excess_bps"].abs() > p95
    mat["g5_fired_dates"] = [g5_map[(r.variable, r.tail)] for r in mat.itertuples()]
    mat["G5"] = mat["g5_fired_dates"] >= G5_TEST_DATE_MIN
    mat["PASS"] = mat["G1"] & mat["G2"] & mat["G3"] & mat["G4"] & mat["G5"]
    mat["status"] = np.where(~mat["G1"], "INELIGIBLE",
                      np.where(~mat["G5"], "TEST-ABSENT",
                        np.where(mat["PASS"], "PASS", "FAIL")))
    mat.to_csv(OUT / "matrix_executable.csv", index=False)

    cols = ["variable", "h", "tail", "mu_cell_bps", "mu_uncond_bps", "excess_bps",
            "d", "se_mu_cell_bps", "n_bucket", "n_eff", "breadth_count",
            "G1", "G2", "G3", "G4", "G5", "status"]
    with pd.option_context("display.width", 250, "display.max_rows", 200):
        print(mat[cols].round(4).to_string(index=False))

    n_pass = int(mat["PASS"].sum())
    print(f"\nG4 threshold P95(M) = {p95:.4f} bps; "
          f"largest |excess| in the real matrix = {mat['excess_bps'].abs().max():.4f} bps")
    print(f"cells passing G1: {int(mat['G1'].sum())}/72 | "
          f"G2: {int(mat['G2'].sum())}/72 | G3: {int(mat['G3'].sum())}/72 | "
          f"G4: {int(mat['G4'].sum())}/72 | G5: {int(mat['G5'].sum())}/72")
    print(f"\nCELLS PASSING ALL FIVE GATES: {n_pass}")
    print("VERDICT: " + ("pre-gate PASS" if n_pass else "REJECT"))

    # ---- sensitivity: threshold estimation window and the 24 vs 25 trim ---- #
    hr("Sensitivity checks (diagnostic; neither is a gate)")
    mat_thr_alt, _, _ = compute_matrix(cens, thr_trval, "F")
    alt_pass = ((mat_thr_alt["n_bucket"] >= G1_POOLED_MIN)
                & (mat_thr_alt["min_per_instrument_n"] >= G1_PER_INSTRUMENT_MIN)
                & (mat_thr_alt["d_excess_bps"] >= C1_EXCESS_BPS)
                & (mat_thr_alt["d_mu_cell_bps"] >= C1_MU_BPS)
                & (mat_thr_alt["breadth_count"] >= G3_BREADTH_MIN)
                & (mat_thr_alt["excess_bps"].abs() > p95))
    base_pass = mat["G1"] & mat["G2"] & mat["G3"] & mat["G4"]
    print(f"(a) thresholds estimated on untrimmed TRAIN+VAL instead of the census "
          f"window: cells changing G1-G4 status = {int((alt_pass != base_pass).sum())}; "
          f"max |excess| shift = "
          f"{(mat_thr_alt['excess_bps'] - mat['excess_bps']).abs().max():.4f} bps")
    mat_thr_alt.to_csv(OUT / "matrix_sensitivity_trainval_thresholds.csv", index=False)

    cens25 = {}
    for sym in INSTRUMENTS:
        ix = cens[sym]["trval_index"][:-TRIM_SENSITIVITY]
        ex, na = fwd[sym]
        cens25[sym] = {
            "index": ix,
            "V": varframes[sym].loc[ix][VARIABLES].to_numpy(dtype=float),
            "F": ex.loc[ix][[f"fwd_{h}" for h in HORIZONS]].to_numpy(dtype=float),
            "Fn": na.loc[ix][[f"fwd_{h}" for h in HORIZONS]].to_numpy(dtype=float),
        }
    thr25 = decile_thresholds(cens25)
    mat25, mu25, _ = compute_matrix(cens25, thr25, "F")
    p25 = ((mat25["n_bucket"] >= G1_POOLED_MIN)
           & (mat25["min_per_instrument_n"] >= G1_PER_INSTRUMENT_MIN)
           & (mat25["d_excess_bps"] >= C1_EXCESS_BPS)
           & (mat25["d_mu_cell_bps"] >= C1_MU_BPS)
           & (mat25["breadth_count"] >= G3_BREADTH_MIN)
           & (mat25["excess_bps"].abs() > p95))
    print(f"(b) trim of {TRIM_SENSITIVITY} bars instead of {TRIM_BARS} (so that NO "
          f"forward return reads a TEST bar at h=24): cells changing G1-G4 status = "
          f"{int((p25 != base_pass).sum())}; max |excess| shift = "
          f"{(mat25['excess_bps'] - mat['excess_bps']).abs().max():.4f} bps; "
          f"cells passing all of G1-G4 = {int(p25.sum())}")
    mat25.to_csv(OUT / "matrix_sensitivity_trim25.csv", index=False)

    # ---- headline summary (every reported figure traceable to this block) -- #
    hr("Headline summary")
    best = mat.loc[mat["excess_bps"].abs().idxmax()]
    per_h = (mat.assign(abs_excess=mat["excess_bps"].abs())
                .sort_values("abs_excess", ascending=False)
                .groupby("h").head(1)
                .sort_values("h")[["h", "variable", "tail", "excess_bps",
                                   "d_mu_cell_bps", "se_mu_cell_bps",
                                   "breadth_count", "G2", "G4"]])
    print("largest |excess| per horizon:")
    print(per_h.round(4).to_string(index=False))
    per_h.to_csv(OUT / "best_cell_per_horizon.csv", index=False)

    # Economics by horizon: this is the cycle's objective stated as a table.
    # Cost is FIXED per round trip; conditional edge grows roughly with sqrt(h),
    # so the affordable horizon is an arithmetic question, not a modelling one.
    HOURS_PER_YEAR = 24 * V.ANNUALIZATION_DAILY
    econ = []
    for h in HORIZONS:
        sub = mat[mat["h"] == h]
        b = sub.loc[sub["d_mu_cell_bps"].idxmax()]
        rt_per_year = HOURS_PER_YEAR / h
        econ.append({
            "h": h,
            "max_abs_excess_bps": float(sub["excess_bps"].abs().max()),
            "best_gross_per_trade_cell": f"{b['variable']} {b['tail']}",
            "best_d_mu_cell_bps": float(b["d_mu_cell_bps"]),
            "best_cell_breadth": int(b["breadth_count"]),
            "round_trip_cost_bps": RT_BPS,
            "gross_edge_to_cost_ratio": float(b["d_mu_cell_bps"]) / RT_BPS,
            "net_per_trade_bps": float(b["d_mu_cell_bps"]) - RT_BPS,
            "round_trips_per_year": rt_per_year,
            "annual_cost_drag_pct": RT_BPS / 1e4 * rt_per_year * 100.0,
        })
    econ = pd.DataFrame(econ)
    print("\nEconomics by horizon (best in-sample cell per horizon; selection NOT priced here):")
    print(econ.round(4).to_string(index=False))
    econ.to_csv(OUT / "economics_by_horizon.csv", index=False)

    binding = "placebo noise floor P95(M)" if p95 > C1_EXCESS_BPS else "cost wall (2 x round trip)"
    required = max(p95, C1_EXCESS_BPS)
    summary = {
        "verdict": "REJECT" if n_pass == 0 else "pre-gate PASS",
        "cells_total": int(len(mat)),
        "cells_passing_all_five": n_pass,
        "status_counts": {k: int(v) for k, v in mat["status"].value_counts().items()},
        "gate_pass_counts": {g: int(mat[g].sum()) for g in ["G1", "G2", "G3", "G4", "G5"]},
        "max_abs_excess_bps": float(mat["excess_bps"].abs().max()),
        "max_abs_excess_cell": f"{best['variable']} h={int(best['h'])} {best['tail']}",
        "cells_clearing_G2a_abs_excess_ge_2rt": [
            f"{r.variable} h={r.h} {r.tail} (excess {r.excess_bps:+.4f} bps)"
            for r in mat[mat["G2a_d_excess_ge_2rt"]].itertuples()],
        "cells_clearing_G2_both_clauses": [
            f"{r.variable} h={r.h} {r.tail}" for r in mat[mat["G2"]].itertuples()],
        "C1a_2x_round_trip_bps": C1_EXCESS_BPS,
        "C1b_1x_round_trip_bps": C1_MU_BPS,
        "P95_M_bps": p95,
        "binding_constraint": binding,
        "excess_required_to_clear_G2a_and_G4_bps": float(required),
        "excess_required_in_round_trips": float(required / RT_BPS),
        "execution_lag_effect_on_excess_bps": {
            "mean": float(lag_delta.mean()), "median": float(lag_delta.median()),
            "max_abs": float(lag_delta.abs().max())},
        "pooled_trainval_bars_before_trim": pooled_trval,
        "pooled_census_bars_after_trim": pooled_census,
        "trim_bars": TRIM_BARS,
        "max_bar_read_by_any_executable_forward_return": max(sr["max_bar_read_by_fwd24"]),
        "g5_test_absent_cells": [f"{r.variable} {r.tail} "
                                 f"({r.pooled_fired_dates} of {r.test_dates_total} dates)"
                                 for r in g5.itertuples()
                                 if r.pooled_fired_dates < G5_TEST_DATE_MIN],
        "sensitivity_trainval_thresholds_status_changes": int((alt_pass != base_pass).sum()),
        "sensitivity_trim25_status_changes": int((p25 != base_pass).sum()),
    }
    print(json.dumps(summary, indent=2))
    (OUT / "summary_stats.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # ---- robustness outputs for any passing cell -------------------------- #
    hr("Robustness outputs for passing cells")
    if n_pass == 0:
        print("No cell passed; per NEXT_TASK.md items 1-3 are not required.")
    else:
        rob = robustness_for_passing(mat[mat["PASS"]], cens, thr, raw, varframes, fwd)
        rob.to_csv(OUT / "robustness_passing_cells.csv", index=False)
        print(rob.to_string(index=False))

    hr("Bookkeeping")
    print("strategy variants evaluated : 0 of 0 assigned")
    print("optimization runs           : 0 of 0 assigned")
    print("trials spent                : 0  (n_trials 0 -> 0)")
    ledger = REPO / "research" / "trial_sharpe_ledger.csv"
    if ledger.exists():
        body = [ln for ln in ledger.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]
        # body[0] is the CSV header; DATA rows are what the 10-row DSR threshold counts.
        n_ledger = max(len(body) - 1, 0)
        print(f"trial_sharpe_ledger.csv: {n_ledger} data rows "
              f"({len(ledger.read_text(encoding='utf-8').splitlines())} physical lines, "
              f"of which {len(body)-1} data + 1 header + comments) - unchanged by this cycle")
    else:
        print("trial_sharpe_ledger.csv: MISSING")
    print(f"placebo draws               : {N_DRAWS} of {N_DRAWS} assigned, seed {SEED}")
    print(f"state variables / horizons / tails: {len(VARIABLES)} / {len(HORIZONS)} / {len(TAILS)}")
    return 0


def robustness_for_passing(passing, cens, thr, raw, varframes, fwd) -> pd.DataFrame:
    """Per-year, three disjoint sub-windows, common-window re-run, long/short flag."""
    rows = []
    for r in passing.itertuples():
        j = VARIABLES.index(r.variable)
        hi = HORIZONS.index(r.h)

        def excess_over(mask_fn, label):
            tot = cnt = 0.0
            utot = ucnt = 0.0
            for sym, d in cens.items():
                sel = mask_fn(d["index"])
                if sel.sum() == 0:
                    continue
                col = d["V"][:, j][sel]
                f = d["F"][sel, hi]
                m = tail_mask(col, thr[sym][0, j], thr[sym][1, j], r.tail) & np.isfinite(f)
                tot += f[m].sum(); cnt += m.sum()
                ok = np.isfinite(f)
                utot += f[ok].sum(); ucnt += ok.sum()
            if cnt == 0 or ucnt == 0:
                return label, np.nan, 0
            return label, (tot / cnt - utot / ucnt) * 1e4, int(cnt)

        for year in (2022, 2023, 2024, 2025):
            lab, ex, n = excess_over(lambda ix, y=year: ix.year == y, f"year_{year}")
            rows.append({"variable": r.variable, "h": r.h, "tail": r.tail,
                         "view": lab, "excess_bps": ex, "n_bucket": n})

        all_idx = np.concatenate([d["index"].asi8 for d in cens.values()])
        cuts = np.quantile(all_idx, [1 / 3, 2 / 3])
        for wi, (lo, hi_) in enumerate([(-np.inf, cuts[0]), (cuts[0], cuts[1]),
                                        (cuts[1], np.inf)], start=1):
            lab, ex, n = excess_over(
                lambda ix, a=lo, b=hi_: (ix.asi8 > a) & (ix.asi8 <= b), f"subwindow_{wi}")
            rows.append({"variable": r.variable, "h": r.h, "tail": r.tail,
                         "view": lab, "excess_bps": ex, "n_bucket": n})

        common = pd.Timestamp("2022-12-23 00:00", tz="UTC")
        lab, ex, n = excess_over(lambda ix: ix >= common, "common_window_2022-12-23+")
        rows.append({"variable": r.variable, "h": r.h, "tail": r.tail,
                     "view": lab, "excess_bps": ex, "n_bucket": n})

        implies_long = (r.d == 1 and r.tail == "TOP") or (r.d == -1 and r.tail == "BOT")
        rows.append({"variable": r.variable, "h": r.h, "tail": r.tail,
                     "view": "construct_direction",
                     "excess_bps": np.nan, "n_bucket": 0,
                     "note": "LONG-implying" if implies_long
                             else "SHORT-implying - CLOSED FAMILY, flag only"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    sys.exit(main())
