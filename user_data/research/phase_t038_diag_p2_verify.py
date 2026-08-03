"""
T-038 — INDEPENDENT VERIFICATION OF THE P2 HARM-CENSUS STOP.

phase_t038_bvt.py stopped the ladder at P2: basket Q1-Q5 per-unit-risk return
= -0.4429 (KILL if <= 0) and only 1 of 9 instruments positive (5 needed).  The
verdict of the cycle therefore rests entirely on that one census, and
PROJECT_OPERATOR_MANUAL.md ("Zero-cost pre-gate ladder", lesson 4) records that
pre-gate stops get independently rerun because one sign bug nearly closed the
last reachable axis in this project.

This script recomputes the same statistic through a DIFFERENT code path — plain
numpy rank bucketing instead of pandas quantile/cut/groupby — and then probes
the four ways the stop could be an artifact rather than a finding:

  V1  independent recomputation (numpy ranks)          — is the number the number?
  V2  burn-in exclusion                                 — are the 96 expanding-EWMA
                                                          bars (sigma near zero,
                                                          all landing in Q1)
                                                          manufacturing the sign?
  V3  NON-OVERLAPPING forward windows (every 24th bar)  — the census uses 24-bar
                                                          forward windows on every
                                                          bar, so neighbouring
                                                          observations share 23/24
                                                          of their data
  V4  per-calendar-year census                          — is the sign one episode?

plus a direction cross-check that does not use the per-unit-risk statistic at
all: the realised Sharpe of the basket restricted to bars whose trailing sigma
is in each quintile.

Run:  python user_data/research/phase_t038_diag_p2_verify.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "user_data" / "research"))

import validator as V  # noqa: E402
from phase_t038_bvt import (  # noqa: E402
    BURN_IN, FWD, OUT_DIR, PROGRAM, SPLIT_DATES, EXECUTION_MODE,
    build_basket, ewma_sigma, load_whitelist, p0_reachability, say, head,
)

out: dict = {}


def numpy_quintile_census(sigma: np.ndarray, fsum: np.ndarray, fstd: np.ndarray) -> dict:
    """Q1-Q5 forward per-unit-risk difference via pure numpy ranks.

    Deliberately shares no code with _purr_census(): ranks are computed with
    argsort and bucketed by integer position, so a bug in the pandas
    quantile/cut/groupby path cannot reproduce itself here.
    """
    good = np.isfinite(sigma) & np.isfinite(fsum) & np.isfinite(fstd) & (fstd > 0)
    s, purr = sigma[good], (fsum[good] / fstd[good])
    n = len(s)
    order = np.argsort(s, kind="stable")
    rank = np.empty(n, dtype=int)
    rank[order] = np.arange(n)
    bucket = np.minimum((rank * 5) // n, 4)          # 0..4 == Q1..Q5
    means = [float(purr[bucket == b].mean()) for b in range(5)]
    counts = [int((bucket == b).sum()) for b in range(5)]
    return {"n": n, "q_means": means, "q_counts": counts,
            "q1_minus_q5": means[0] - means[4],
            "unconditional_mean": float(purr.mean())}


def main() -> int:
    head("T-038 — P2 VERIFICATION (independent recomputation + artifact probes)")
    say(f"cost model : {V.describe_cost_model(EXECUTION_MODE)}")
    say(f"data gate  : {V.DATA_INTEGRITY}")
    per_side = V.per_side_cost(EXECUTION_MODE)

    pairs = load_whitelist()
    ok, closes, _ = p0_reachability(pairs)
    if not ok:
        raise RuntimeError("P0 failed inside the verification script")

    tr, vl, te = V.split_by_dates(closes, *SPLIT_DATES)
    for lbl, seg in (("train", tr), ("val", vl), ("test", te)):
        V.assert_no_holdout(seg, label=lbl, program=PROGRAM)
    tv_index = tr.index.append(vl.index)
    census_idx = tv_index[:-FWD]

    basket = build_basket(closes, per_side)
    sigma_b = ewma_sigma(basket["ret_gross"])
    blr = np.log1p(basket["ret_gross"])

    frame = pd.DataFrame({"sigma": sigma_b, "lr": blr})
    frame["fsum"] = frame["lr"].rolling(FWD).sum().shift(-FWD)
    frame["fstd"] = frame["lr"].rolling(FWD).std(ddof=1).shift(-FWD)
    cen = frame.loc[census_idx]

    # ---------------- V1 — independent recomputation ----------------------- #
    head("V1 — INDEPENDENT RECOMPUTATION (numpy ranks, no pandas cut/groupby)")
    v1 = numpy_quintile_census(cen["sigma"].to_numpy(), cen["fsum"].to_numpy(),
                               cen["fstd"].to_numpy())
    say(f"  n = {v1['n']}   unconditional mean per-unit-risk return = {v1['unconditional_mean']:.6f}")
    for i, (m, c) in enumerate(zip(v1["q_means"], v1["q_counts"]), start=1):
        say(f"  Q{i}  n={c:>6}  mean = {m:+.6f}")
    say(f"  Q1 - Q5 = {v1['q1_minus_q5']:+.6f}")
    say(f"  phase_t038_bvt.py reported -0.442905 — agreement to 6dp: "
        f"{abs(v1['q1_minus_q5'] - (-0.442905)) < 1e-6}")
    out["V1_independent"] = v1

    # ---------------- V2 — burn-in exclusion -------------------------------- #
    head(f"V2 — BURN-IN EXCLUSION (first {BURN_IN} bars: expanding EWMA, sigma near zero)")
    b_idx = census_idx[BURN_IN:]
    cen2 = frame.loc[b_idx]
    v2 = numpy_quintile_census(cen2["sigma"].to_numpy(), cen2["fsum"].to_numpy(),
                               cen2["fstd"].to_numpy())
    burn_sigma = frame.loc[census_idx[:BURN_IN], "sigma"]
    say(f"  burn-in sigma min/median/max : {burn_sigma.min():.6f} / "
        f"{burn_sigma.median():.6f} / {burn_sigma.max():.6f}")
    say(f"  n = {v2['n']}")
    for i, m in enumerate(v2["q_means"], start=1):
        say(f"  Q{i}  mean = {m:+.6f}")
    say(f"  Q1 - Q5 = {v2['q1_minus_q5']:+.6f}   sign unchanged: "
        f"{np.sign(v2['q1_minus_q5']) == np.sign(v1['q1_minus_q5'])}")
    out["V2_no_burnin"] = v2

    # ---------------- V3 — non-overlapping forward windows ------------------ #
    head(f"V3 — NON-OVERLAPPING FORWARD WINDOWS (every {FWD}th bar)")
    say("  The gating census evaluates a 24-bar forward window on EVERY bar, so")
    say("  adjacent observations share 23 of 24 returns. Taking every 24th bar")
    say("  makes the forward windows disjoint at the cost of 1/24 of the sample.")
    for off in (0, 8, 16):
        sub = frame.loc[census_idx[off::FWD]]
        v3 = numpy_quintile_census(sub["sigma"].to_numpy(), sub["fsum"].to_numpy(),
                                   sub["fstd"].to_numpy())
        say(f"  offset {off:>2}:  n = {v3['n']:>5}   Q1 = {v3['q_means'][0]:+.6f}   "
            f"Q5 = {v3['q_means'][4]:+.6f}   Q1-Q5 = {v3['q1_minus_q5']:+.6f}")
        out[f"V3_disjoint_offset_{off}"] = v3

    # ---------------- V4 — per calendar year -------------------------------- #
    head("V4 — PER CALENDAR YEAR (is the sign one episode?)")
    say(f"  {'year':<6} {'n':>7} {'Q1':>11} {'Q5':>11} {'Q1-Q5':>11}")
    per_year = {}
    for y, sub in cen.groupby(cen.index.year):
        if len(sub) < 500:
            say(f"  {y:<6} {len(sub):>7}   (fewer than 500 bars — not reported)")
            continue
        vy = numpy_quintile_census(sub["sigma"].to_numpy(), sub["fsum"].to_numpy(),
                                   sub["fstd"].to_numpy())
        per_year[int(y)] = vy
        say(f"  {y:<6} {vy['n']:>7} {vy['q_means'][0]:>11.6f} {vy['q_means'][4]:>11.6f} "
            f"{vy['q1_minus_q5']:>11.6f}")
    out["V4_per_year"] = per_year

    # ---------------- direction cross-check, different statistic ------------ #
    head("CROSS-CHECK — realised basket Sharpe restricted to each sigma quintile")
    say("  Uses no forward window and no per-unit-risk ratio: it asks directly")
    say("  whether the bars the construct would de-risk were good or bad bars.")
    lag2 = frame["sigma"].shift(2)         # what the construct actually acts on
    cc = pd.DataFrame({"sigma_lag2": lag2, "r": basket["ret_gross"]}).loc[tv_index].dropna()
    edges = cc["sigma_lag2"].quantile([0, .2, .4, .6, .8, 1.0]).to_numpy()
    cc["q"] = pd.cut(cc["sigma_lag2"], bins=edges, labels=[1, 2, 3, 4, 5],
                     include_lowest=True)
    say(f"  {'quintile':<10} {'n':>7} {'mean ret':>13} {'sd':>11} {'Sharpe(ann)':>13} {'total ret':>12}")
    qstats = {}
    for k in (1, 2, 3, 4, 5):
        s = cc.loc[cc["q"] == k, "r"]
        sh = float(s.mean() / s.std(ddof=1) * np.sqrt(8760)) if s.std(ddof=1) > 0 else 0.0
        tot = float(np.prod(1.0 + s.to_numpy()) - 1.0)
        qstats[k] = {"n": int(len(s)), "mean": float(s.mean()), "sd": float(s.std(ddof=1)),
                     "sharpe_ann": sh, "total_return": tot}
        say(f"  Q{k:<9} {len(s):>7} {s.mean():>13.8f} {s.std(ddof=1):>11.6f} "
            f"{sh:>13.4f} {tot:>+12.4f}")
    out["cross_check_quintile_sharpe"] = qstats

    say("")
    say("  Reading: if the mechanism existed, Q5 (highest trailing vol) would show")
    say("  the WORST per-unit-risk return — a lower Sharpe and/or negative total.")

    with open(OUT_DIR / "T-038_p2_verification.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    say(f"\nJSON written: {OUT_DIR / 'T-038_p2_verification.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
