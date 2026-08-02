# NEXT_TASK.md — T-PROBE (H-FearGreed)

> **PROVENANCE — read this before grading.** The original `research/NEXT_TASK.md` for T-035 was
> **never committed**. It was overwritten in place by the T-036 assignment before any commit
> captured it, and it exists nowhere in the working tree or in git history. This file is therefore
> **reconstructed from committed artifacts**, not a copy of the original, and every clause below
> carries the source it was taken from.
>
> Clauses marked **[VERBATIM]** are quoted exactly from a committed file and are safe to grade
> against. Clauses marked **[DERIVED]** were inferred from what the report and review brief record
> and are *weaker evidence of the original contract* — do not treat a mismatch against a [DERIVED]
> clause as conclusive without checking the cited source yourself.
>
> Sources used:
> - `research/results/T-035_report.md` (committed)
> - `research/review_briefs/T-035_brief.md` (present in working tree)
> - `PROJECT_OPERATOR_MANUAL.md`, "Falsification conditions must be transcribed literally"

**Task ID:** T-PROBE
**Codename:** H-FearGreed
**Program:** spot (pre-perps; `n_trials` was 100 at assignment time)

---

## Hypothesis

**[VERBATIM — `research/results/T-035_report.md` §1]**

> Crypto Fear & Greed Index readings of Extreme Greed (index >= 75) mark froth/euphoria episodes
> that precede idiosyncratic corrections not already captured by the champion's own price-derived
> signals (SMA200/ROC30/EMA20-50 trend gate, rv30 sizing), such that vetoing champion exposure
> (forcing flat) during an active in-market Extreme Greed episode improves risk-adjusted
> performance (TEST Sharpe, Monte Carlo tail) without merely re-discovering the already-CLOSED
> DVOL axis.

---

## Zero-cost pre-gate ladder

The cycle runs these in order and **STOPS at the first failure**. A cycle killed at a pre-gate
spends **zero trials**.

### Step 1 — Reachability pre-gate
**[DERIVED]** Fetch the Crypto Fear & Greed Index and establish coverage over the evaluation
window. Save the raw, unmodified response to `user_data/research/data/fear_greed/` **before any
processing**, and print the first and last raw records so they can be byte-matched against the
saved file. Use `requests`, not `aiohttp`.

### Step 2 — Redundancy pre-gate
**[VERBATIM threshold — `research/review_briefs/T-035_brief.md`:22-23]**

> Step 2 correlation vs rv30 = −0.1382, vs roc30 = 0.7011, both below the 0.90 redundancy bar

**Falsification:** reject if the F&G series correlates with an existing champion signal at
**|ρ| ≥ 0.90** — the axis would be redundant with what the strategy already uses.

### Step 3 — Lead/lag pre-gate
**[VERBATIM — quoted in `research/results/T-035_report.md` §8; the OR reading is independently
confirmed by `research/review_briefs/T-035_brief.md`:31-32 and `PROJECT_OPERATOR_MANUAL.md`:873-879]**

> If the average positive-lag (leading) correlation is not greater than the average negative-lag
> (lagging) correlation **for at least one of the two forward series** (returns or rv30 changes),
> reject — the index does not demonstrably lead price/vol behavior it could usefully anticipate.

**Note for the grader.** "at least one of" is `or`. The manual's standard on this is explicit:
*"A falsification condition is transcribed into code literally, not paraphrased. 'at least one of'
is `or`. 'both' is `and`. Substituting one for the other is a spec deviation even when the verdict
is unchanged."*

---

## Research budget

**[DERIVED — from `research/results/T-035_report.md` §4, which reports "(0/1 budget)", and
`research/review_briefs/T-035_brief.md`:8, which records "budget and bookkeeping compliant"]**

**Maximum 1 strategy variant, 0 optimization runs.** A cycle stopped at a pre-gate spends zero
trials and reports `0/1`. Exceeding the assigned number invalidates the cycle: trials were spent
but never priced into `n_trials`.

---

## Data

**[DERIVED]**

- `user_data/data/okx/BTC_USDT-1d.feather` — read only.
- Fetched axis writes to `user_data/research/data/fear_greed/` — **never** to `user_data/data/`.
- Market data under `user_data/data/` must not be created, modified, deleted, or rebuilt. A cycle
  whose `git diff` touches that tree is INVALID.

---

## Required deliverables

**[DERIVED — the standard 14-section Engineer report format]**

`research/results/<Task ID>_report.md`, with all sections present. Section 11 lists **raw output
locations**: every path a reviewer needs to independently reproduce the numbers. Every figure in
the report must be traceable to a path listed there.

---

## Verdict expectations

**[VERBATIM — `research/review_briefs/T-035_brief.md`:5]**

> Engineer verdict: REJECTED (Step 3 — Lead/lag pre-gate)

Zero trials spent; `n_trials` stays at 100.
