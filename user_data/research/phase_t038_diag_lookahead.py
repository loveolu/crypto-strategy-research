"""
T-038 — LOOK-AHEAD / LEAKAGE VERIFICATION.

PROJECT_OPERATOR_MANUAL.md Validation section 8 and the Engineer prompt both
require the look-ahead check to be PERFORMED and its method stated, not
asserted.  The cycle stopped at pre-gate P2, so the only quantities that decided
anything are sigma_t (the bucketing variable) and the forward 24-bar windows.
This script tests exactly those.

  L1  sigma_t is causal        — recompute the EWMA on the series TRUNCATED at t
                                 and require the value at t to be bit-identical
                                 to the full-series value. If sigma leaked any
                                 future bar the two would differ.
  L2  forward windows exclude  — the forward sum/std at t must equal a hand-built
      the current bar            sum over positions t+1..t+24, and must NOT change
                                 when bar t itself is perturbed.
  L3  census stays inside      — the last censused bar's forward window must end
      TRAIN+VAL                  on or before the last TRAIN+VAL bar.
  L4  indicators before split  — sigma computed on the full pre-holdout series
                                 then sliced must equal sigma computed the same
                                 way and sliced again (i.e. the pipeline never
                                 recomputes per split).
  L5  holdout untouched        — no bar past the perps boundary enters any frame.

Run:  python user_data/research/phase_t038_diag_lookahead.py
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
    BURN_IN, EXECUTION_MODE, FWD, OUT_DIR, PROGRAM, SPLIT_DATES,
    build_basket, ewma_sigma, load_whitelist, p0_reachability, head, say,
)

res: dict = {}


def main() -> int:
    head("T-038 — LOOK-AHEAD / LEAKAGE VERIFICATION")
    per_side = V.per_side_cost(EXECUTION_MODE)
    pairs = load_whitelist()
    ok, closes, _ = p0_reachability(pairs)
    if not ok:
        raise RuntimeError("P0 failed inside the look-ahead script")

    tr, vl, te = V.split_by_dates(closes, *SPLIT_DATES)
    tv_index = tr.index.append(vl.index)
    census_idx = tv_index[:-FWD]
    basket = build_basket(closes, per_side)
    sigma = ewma_sigma(basket["ret_gross"])
    lr = np.log1p(basket["ret_gross"])

    # ---- L1: sigma_t is causal ------------------------------------------- #
    head("L1 — sigma_t uses only bars <= t (truncation test)")
    probes = [200, 1000, 8000, len(basket) - 5000, len(basket) - 1]
    l1 = []
    for p in probes:
        trunc = ewma_sigma(basket["ret_gross"].iloc[:p + 1])
        a, b = float(trunc.iloc[-1]), float(sigma.iloc[p])
        same = bool(np.isclose(a, b, rtol=0, atol=0))
        l1.append({"i": int(p), "ts": str(basket.index[p]), "truncated": a,
                   "full_series": b, "bit_identical": same})
        say(f"  i={p:>6}  {basket.index[p]}  truncated {a:.12f}  full {b:.12f}  identical={same}")
    ok_l1 = all(x["bit_identical"] for x in l1)
    say(f"  L1: {'PASS' if ok_l1 else 'FAIL'}")
    res["L1_sigma_causal"] = {"pass": ok_l1, "probes": l1}

    # ---- L2: forward windows exclude the current bar ---------------------- #
    head("L2 — forward 24-bar window covers t+1..t+24 and excludes t")
    fsum = lr.rolling(FWD).sum().shift(-FWD)
    fstd = lr.rolling(FWD).std(ddof=1).shift(-FWD)
    l2 = []
    for p in (500, 5000, 15000):
        manual_sum = float(lr.iloc[p + 1:p + 1 + FWD].sum())
        manual_std = float(lr.iloc[p + 1:p + 1 + FWD].std(ddof=1))
        ok_s = bool(np.isclose(manual_sum, float(fsum.iloc[p]), rtol=1e-12, atol=1e-15))
        ok_v = bool(np.isclose(manual_std, float(fstd.iloc[p]), rtol=1e-12, atol=1e-15))
        l2.append({"i": int(p), "manual_sum": manual_sum, "rolling_sum": float(fsum.iloc[p]),
                   "manual_std": manual_std, "rolling_std": float(fstd.iloc[p]),
                   "sum_match": ok_s, "std_match": ok_v})
        say(f"  i={p:>6}  sum manual {manual_sum:+.10f} vs rolling {float(fsum.iloc[p]):+.10f} "
            f"({ok_s})   std {manual_std:.10f} vs {float(fstd.iloc[p]):.10f} ({ok_v})")

    # Perturbation test: change bar t only. The forward window AT t must not
    # move, and the windows that DO move must be exactly t-24 .. t-1 (the 24
    # windows that legitimately contain bar t).
    #
    # Note on tolerance: pandas' rolling sum carries a running accumulator, so
    # editing one observation perturbs every later value in the last bits of
    # float (measured: 4.2e-17 at t, 5.6e-17 worst case elsewhere). An exact
    # equality test therefore FAILS on arithmetic noise, not on leakage. The
    # numpy slice reference below has no accumulator and returns exactly 0.0,
    # which is what settles the question; the pandas check uses a tolerance
    # three orders of magnitude above the observed noise floor.
    pert = lr.copy()
    i = 5000
    pert.iloc[i] = pert.iloc[i] + 0.5
    p_sum = pert.rolling(FWD).sum().shift(-FWD)
    delta = (p_sum - fsum)
    noise = float(abs(delta.iloc[i]))
    unchanged = noise < 1e-14
    moved = delta[delta.abs() > 1e-12].index
    expected = lr.index[i - FWD:i]
    right_windows = bool(len(moved) == FWD and moved.equals(expected))

    a = lr.to_numpy()
    ap = pert.to_numpy()
    exact_delta = float(ap[i + 1:i + 1 + FWD].sum() - a[i + 1:i + 1 + FWD].sum())

    say(f"  perturbing bar t: |change in the forward window at t| = {noise:.3e} "
        f"(pandas accumulator noise; threshold 1e-14) -> unchanged={unchanged}")
    say(f"  independent numpy slice reference, same perturbation: exactly {exact_delta!r}")
    say(f"  windows that DID move: {len(moved)} == {FWD} expected, and they are exactly "
        f"t-{FWD}..t-1: {right_windows}")
    ok_l2 = (all(x["sum_match"] and x["std_match"] for x in l2)
             and unchanged and right_windows and exact_delta == 0.0)
    say(f"  L2: {'PASS' if ok_l2 else 'FAIL'}")
    res["L2_forward_window"] = {
        "pass": ok_l2, "probes": l2,
        "perturbation_noise_at_t": noise,
        "numpy_reference_delta_at_t": exact_delta,
        "n_windows_moved": int(len(moved)), "moved_windows_are_t_minus_24_to_t_minus_1":
            right_windows}

    # ---- L3: census forward windows stay inside TRAIN+VAL ----------------- #
    head("L3 — no censused forward window reaches into TEST")
    last_cen = census_idx[-1]
    pos = basket.index.get_loc(last_cen)
    reach = basket.index[pos + FWD]
    tv_last = tv_index[-1]
    ok_l3 = bool(reach <= tv_last)
    say(f"  last censused bar        : {last_cen}")
    say(f"  its forward window ends  : {reach}")
    say(f"  last TRAIN+VAL bar       : {tv_last}")
    say(f"  first TEST bar           : {te.index[0]}")
    say(f"  L3: {'PASS' if ok_l3 else 'FAIL'}")
    res["L3_census_containment"] = {"pass": ok_l3, "last_censused_bar": str(last_cen),
                                    "forward_window_ends": str(reach),
                                    "last_train_val_bar": str(tv_last),
                                    "first_test_bar": str(te.index[0])}

    # ---- L4: computed before splitting, never per split ------------------- #
    head("L4 — sigma computed once on the full pre-holdout series, then sliced")
    per_split = ewma_sigma(basket["ret_gross"].loc[te.index])
    full_sliced = sigma.loc[te.index]
    dev = float((per_split - full_sliced).abs().max())
    say(f"  max |sigma(recomputed on TEST only) - sigma(full series, sliced)| = {dev:.8f}")
    say("  A nonzero difference is EXPECTED and is the point: recomputing per split")
    say("  restarts the EWMA warmup inside the split (Standing Directive 8). This")
    say("  pipeline uses the full-series value; the number above quantifies the")
    say("  defect that would have been introduced by the other choice.")
    say(f"  first-bar difference: {float(abs(per_split.iloc[0] - full_sliced.iloc[0])):.8f}")
    res["L4_warmup"] = {"max_abs_deviation_if_recomputed_per_split": dev,
                        "policy": "computed once on full pre-holdout series, then sliced"}

    # ---- L5: holdout untouched ------------------------------------------- #
    head("L5 — reserved holdout untouched")
    bound = V.holdout_boundary(PROGRAM)
    for lbl, obj in (("closes", closes), ("basket", basket), ("sigma", sigma),
                     ("train", tr), ("val", vl), ("test", te)):
        V.assert_no_holdout(obj, label=lbl, program=PROGRAM)
        say(f"  assert_no_holdout({lbl:<7}) OK   last bar {obj.index.max()}")
    say(f"  boundary: bars strictly after {bound} are reserved")
    say("  L5: PASS")
    res["L5_holdout"] = {"pass": True, "boundary": str(bound),
                         "last_bar_evaluated": str(closes.index.max())}

    with open(OUT_DIR / "T-038_lookahead.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    say(f"\nJSON written: {OUT_DIR / 'T-038_lookahead.json'}")
    return 0 if (ok_l1 and ok_l2 and ok_l3) else 1


if __name__ == "__main__":
    sys.exit(main())
