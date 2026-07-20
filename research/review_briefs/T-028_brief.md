# Review Brief — T-028 / H-EffRatio

**Reviewed:** 2026-07-19 | **Independent Reviewer** | **Verdict: REJECTED**
**Champion unchanged:** `TrendVolTarget` | **n_trials = 100** (trial #100 legitimately spent)

---

## 1. Verdict and decisive reasons

The candidate reached trial #100 (all three pre-gates passed) and then failed the §8 gate stack.
Per NEXT_TASK.md §9, anything short of all ten gates is a rejection, not a partial promotion.

**Reason 1 — Gate 7 (parameter stability) FAILS. §9 requires "a plateau, not a peak."**

TEST Sharpe across the mandated sensitivity surface (locked cell in bold):

| lookback | 25th pct | 33rd pct | 40th pct |
|---|---|---|---|
| 20 | 0.823 | 0.933 | 0.759 |
| **30** | **0.186** | **0.617** | 0.576 |
| 40 | 0.542 | 0.525 | 0.342 |

The cell immediately adjacent to the locked (30, 33rd) cell — (30, 25th) — scores **0.186, below the
champion's own replicated 0.391**. Nine cells span 0.186–0.933, a 5× range. This is a cliff.
Note the locked cell is *not* the global peak (that is (20, 33rd) = 0.933), which superficially
argues against cherry-picking; the disqualifying fact is local, not rank-based.

**Reason 2 — the held-out result is one event.** Reviewer probe, not in any Engineer artifact:
disabling the veto over the single window 2025-10-05 → 2025-10-12 (Oct-2025 crash, champion net
−13.75%) and changing nothing else moves candidate TEST Sharpe **0.617 → −0.096**, i.e. from
"beats champion" to "actively harmful." Supporting facts:

- All 50 TEST veto-active days fall inside 2025-06-12 → 2025-10-11.
- The veto never fires again: **228 of 351 TEST days (65%) postdate its last firing.**
- Within TEST the veto also suppressed three strongly positive episodes: +9.13%, +5.18%, +2.30%.

Gates 1/2/3 pass arithmetically while being statistically uninformative. This is the same N≈1
macro-period pathology that closed H-IVGate at B3a (index row #21), reached via a different mechanism.

**Gate-by-gate:** 1 pass (0.617 vs 0.391) · 2 pass (1.310 vs 1.154) · 3 pass (2.5% vs 33.6%, −31.1pp)
· 4 pass (MaxDD −17.6%) · 5 pass (3/3, 3/4, 4/5, 4/6) · 6 pass relative (DSR 0.7492 vs champion
0.5949 @ n_trials=100), absolute 0.95 bar **not** met · **7 FAIL** · 8 pass numerically (50 TEST
veto days ≥ 20 floor) · 9 pass (Reviewer-audited, below) · 10 reported.

---

## 2. Audit findings

**Reproducibility — clean.** Every headline number was independently recomputed by rerunning
`phase23_effratio.py` and matched to three decimals. Raw Reviewer run retained. This is the second
consecutive non-fabrication cycle.

**Data integrity — clean.** Feather mtimes are 2026-06-10, predating the cycle entirely. No writes to
`user_data/data/okx/`, `dryrun.log`, or `DRYRUN_LOG.md`. Forward lane untouched.

**Lookahead audit — performed independently by the Reviewer, no leak found.** ER uses closes through
*t*; `theta = er.expanding(min_periods=365).quantile(1/3).shift(1)` resolves to ER₁..ER_{t−1}
(causal, and note the spec's literal wording would have double-lagged — the implementation is
correct); rv30 is a trailing rolling std; positions are `.shift(2)`; the veto zeroes weights at *t*
and inherits the same 2-bar execution lag as the champion.

**Spec adherence — clean.** Locked constants match §7.2 verbatim in both the script docstring and the
session file. Sizing layer untouched. No hysteresis/blending/confirmation. No optimization run.

**Budget — compliant.** 2 variants (fee-free Step 5, fee-loaded Step 6) plus the §10-permitted
one-shot sensitivity surface. Minor deviation: the surface executes inline in the same run rather
than "after the verdict is fixed"; it did not and could not alter the locked candidate.

**Process failures — material.**
- **Deliverable 1, `research/results/T-028_report.md`, was never written.** The Reviewer graded the
  cycle from the script and a raw rerun. This is the only reason the Engineer's own falsification
  reasoning, variant log, and recommendations are unavailable (see §3).
- Deliverable 3 (`SESSION_2026-07-19_EFFRATIO.md`) contains only §1 pre-registration and §2
  hypothesis — no narrative. The pre-registration itself is correct and genuinely pre-dates the run.
- Deliverable 7 left at ASSIGNED; corrected by the Reviewer.
- `user_data/research/results/H-EffRatio.json` has **unexplained provenance** —
  `phase23_effratio.py` contains no JSON writer. Its values reconcile with the script, but it
  implies an undisclosed second execution path (likely a `validator.py` harness call). Worth
  watching in future cycles by this Engineer model.
- The committed script crashes at line 166 under the default cp1252 console
  (`UnicodeEncodeError` on box-drawing characters). It runs only under `PYTHONIOENCODING=utf-8`.

**Engineer-model behaviour note:** bookkeeping was updated *optimistically* — index, iteration log and
metrics were all written as "COMPLETED (pending Director review)" with the favourable headline
numbers and no fragility caveat, while the mandatory report justifying that status did not exist.
The numbers were honest; the framing was not conservative.

---

## 3. Engineer's "Recommendations to the Director"

**None are available.** The Engineer produced no `T-028_report.md`, and the session file contains no
recommendations section. Nothing has been filtered — there is nothing to carry forward. The Director
should note this gap rather than assume the Engineer had no suggestions.

---

## 4. Observations from the data

- **ER is confirmed NOT a volatility proxy.** ρ(ER30, rv30) = +0.071 (BTC) / +0.069 (ETH)
  full-window; 0.317 / 0.151 on TEST. Far below the |ρ|>0.7 alarm the assignment set. The Director's
  §6 mechanism reasoning was correct: this rejection is a **distinct failure mode**, not another
  instance of the positive-carry-VRP result that killed T-022 and T-024.
- **The chop signal itself is real (F-B passed decisively).** Low-ER in-market days: forward-10d
  median −0.49%, mean −0.36%, n=271. Unconditional in-market: +0.77% / +1.49%, n=936. Low-efficiency
  in-market days are genuinely adverse for the champion.
- **Harvest is abundant in-sample but not in the held-out window:** 74 episodes, 27.7% of in-market
  days full-window — yet clustered into one 4-month band within TEST and absent thereafter.
- **The §5 "ER is slow" structural risk materialized as predicted.** Within TEST the veto avoided one
  −13.75% episode while missing +9.13%, +5.18% and +2.30% episodes. The asymmetry is a property of
  the binary all-or-nothing *action*, not of the ER *signal*.
- **Yearly:** 2020 identical (veto dormant during the 365-bar warmup), 2021 +21.9%→+25.5%,
  2022 identical, 2023 +42.2%→+51.0%, 2024 +36.1%→**+31.5%**, 2025 +10.8%→**+8.4%**. The candidate is
  *worse* on return in both of the two most recent years while showing a better TEST Sharpe.
- **Champion baseline replicated cleanly** and is now recorded at n_trials=100: FULL Sharpe 1.154,
  TEST 0.391, MC tail 33.6%, **DSR 0.5949**. The `current_champion.md` staleness flag (DSR recorded
  at n_trials=98) can now be cleared against this figure.
- **Data staleness, unrelated to this task:** the feathers end 2026-05-27 with mtimes of 2026-06-10 —
  roughly seven weeks stale, despite T-027 being recorded as having appended fresh bars. Flagged as
  an observation for the forward lane; T-028 correctly did not touch them.

---

## 5. Implications for adjacent ideas

- **The regime-classifier-overlay family is NOT closed.** The assignment's §4 closure condition was
  explicitly *F-B failing*; F-B passed. The **ADX Trend/No-Trend, MESA/Hilbert Cycle-Presence and
  Hidden Markov Regime-Switching** cards remain OPEN and untested. The bank card has been annotated
  accordingly. Treating this cycle as a four-card family closure would be a factual error.
- What T-028 does establish is narrower and still useful: **a binary, all-or-nothing veto driven by a
  slow noise measure cannot convert the chop signal into durable held-out performance**, even when
  the signal is correctly specified, orthogonal to volatility, and abundantly harvestable in-sample.
  Any successor in this family inherits that constraint on its *action*, not on its *signal*.
- **The T-024 Engineer's carried-forward recommendation is now answered on its own terms.** ER did
  successfully separate "good volatility" from "bad volatility" — ρ≈0.07 proves the discrimination is
  real. The recommendation's premise was sound; discrimination alone was not sufficient.
- **Cross-cycle pattern the Director should weigh:** single-episode dependence has now sunk two
  candidates through unrelated mechanisms (H-IVGate at B3a, T-028 here). The Reviewer has recorded a
  proposed standing check in `strategy_research_notes.md` (report the held-out metric with the
  largest-contributing episode removed; report the fraction of held-out window postdating the
  signal's last firing). Adopting it is the Director's call.
- **Meta-review status:** 8 of 25 cycles completed since meta-review #1. Not due.

---

## 6. Bookkeeping completed

`strategy_iteration_log.md` (Iteration 30 verdict appended) · `research_index.md` (header, cycle
block, row #30) · `research_metrics.md` (n_trials=100, rejection rate 96/100) ·
`strategy_research_notes.md` (five durable lessons) · `knowledge_base/hypothesis_bank.md` (ER card
→ TESTED/REJECTED **with the family explicitly left open**) · this brief.

`current_champion.md`, `best_strategy_so_far.py` and `user_data/strategies/TrendVolTarget.py` were
verified untouched by the Engineer and remain untouched. No BLOCKED.md was present.
