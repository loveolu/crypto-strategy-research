# T-030 / H-ADXGate — Independent Reviewer Brief

**Verdict: REJECT — valid pre-gate stop at F-P2 (episode dispersion). Zero trials spent; n_trials = 100.**
**Champion `TrendVolTarget` stands unchanged. The regime-classifier-overlay family (ER, ADX,
MESA/Hilbert, HMM) is CLOSED on the frozen research dataset** — binding per the pre-registered
family implication in T-030's NEXT_TASK §3 (F-P2 branch). Reopening condition, pre-registered and
quoted in the hypothesis-bank ledger: frozen window extended ≥ 6 months beyond 2026-05-27 with a
freshly cut held-out split, OR a forward-dry-run-lane documented completed in-market chop episode.
Not a re-parameterization.

Reviewer: fresh-context session, 2026-07-19. Graded against `research/NEXT_TASK.md` (T-030) and
`research/results/T-030_report.md`; verified by (a) full end-to-end rerun of
`user_data/research/phase25_adxgate.py` (Python 3.13) and (b) an **independent recomputation of the
decisive census using `talib.ADX` instead of the Engineer's pandas implementation**, with champion
weights rebuilt from spec.

---

## 1. Verdict and decisive reasons

- **F-P2 triggered exactly as pre-registered.** TEST-split veto days: 45, spanning 5 distinct
  calendar months (2025-06 through 2025-10 — passes the ≥3 clause), but the last veto day is
  **2025-10-10** and **229 of 351 TEST days (65.2%) postdate it** — over the 50% limit. Stop
  honored; `sys.exit` fires before Steps 5–7; trial #101 never constructed; 0/2 variant budget
  consumed (the stop precedes both budgeted variants).
- **The stop is meaningful because everything upstream passed.** F-P0 replication landed
  *identically* on the T-028/T-029 Reviewer baseline (FULL Sharpe 1.154 / TEST 0.391 / MC tail
  33.6%). F-H1 vol-proxy gate passed on the full window (|ρ(ADX14, rv30)| = 0.247 BTC / 0.181
  ETH vs 0.70 limit). F-H2 harm census passed (veto-day forward-10d median −0.13% / mean +0.78%,
  both strictly below unconditional +0.77% / +1.49%, n=222 vs 936). F-P1 materiality passed by a
  wide margin (224 veto days = 22.9% of 977 in-market days; 45 in TEST vs 20 floor). The ADX card
  received a fair test and died on dispersion, not on validity or materiality.
- **The headline finding the assignment demanded, confirmed:** the absolute literature threshold
  does NOT pass where the distribution-relative one failed. ADX < 20 (no fitted parameters, no
  distribution drift possible) produced its last TEST firing on 2025-10-10 — one day after ER's
  2025-10-09 — with a postdating fraction of 65.2% vs ER's 65.5%. Third firing-set concentration
  failure, now spanning two structurally different signals and both threshold constructions. The
  pathology is a property of the frozen evaluation window (no classifier-detectable in-market chop
  after Oct-2025), which is precisely the pre-registered F-P2 closure rationale.
- **Every reported number reproduced exactly on rerun, and the decisive F-P2/F-H2 numbers
  reproduced again through the independent TA-Lib path** (224/45 veto days; months Jun–Oct 2025;
  last veto 2025-10-10; 229/351 = 65.2%; harm census identical to the digit). The verdict does not
  rest on the Engineer's code.

## 2. Audit findings worth remembering

- **Integrity CLEAN — sixth consecutive clean cycle.** All frozen research feathers at the
  2026-06-10 18:28 baseline mtime; forward-lane feathers exactly at the T-027 refresh timestamp
  (2026-07-19 11:59) and untouched by this cycle (cycle artifacts written ~23:26); the feather
  modifications visible in git status are the *uncommitted T-027 refresh*, not this cycle's doing.
  All protected files (`best_strategy_so_far.py`, `TrendVolTarget.py`, `validator.py`,
  `freqtrade_dsr.py`, `dryrun_monitor.py`, `DRYRUN_LOG.md`, `dryrun.log`) predate the cycle.
  Budget: 0 optimization runs, 0 trials, no undisclosed variants, no new repo-root clutter.
- **Implementation quality: high.** ADX implemented exactly per the locked §7.2 formula and
  cross-checked in-script against TA-Lib (MAD 0.0022 BTC / 0.0055 ETH — effectively exact).
  Lookahead clean: OHLC at bar close only, `.shift(1)` on the veto mask, `.shift(2)` on positions,
  60-bar warmup enforced, NaN defaults to no-veto. Pre-registration written to the session file and
  module docstring before execution, verbatim.
- **Engineer behaviour this cycle: honest and compliant.** Report written unprompted, verdict
  phrased as a stop naming the specific falsifier, bookkeeping conservative (n_trials left at 100
  everywhere), Step 2 diagnostic values all present in the report itself (the exact T-029
  deficiency, fixed this time).
- **Report deficiencies (non-fatal, all verified by rerun):** Step 1 replication values (required
  by §7.3 to be reported) appear only in script output — report §5 says "N/A"; the TEST veto-day
  count (45) and the turnover change (72.25 → 58.00, −14.25) likewise appear only in script
  output. Second consecutive cycle with a required-values-only-in-script-output gap (T-029's was
  Step 2; T-030 fixed Step 2 but dropped Step 1). Directors may want the deliverables list to say
  "Step 1 AND Step 2 values in the report body".
- **Bookkeeping defects found and repaired by this Reviewer:** iteration-log entry mislabeled
  "Iteration 25" (corrected to 32; T-029 is 31); index banner cycle counter left at 9 of 25 while
  simultaneously declaring cycle #10 closed (advanced to 10); `research_metrics.md` not updated at
  all (updated); **deliverable 7 under-delivered** — the family closure was recorded on the ER card
  and as a ledger row, but the required closure notes on the MESA/Hilbert and HMM cards were
  missing, and the ledger row omitted the required reopening-condition quote (all added). The
  ledger row also said "#30, #31, #32 all fail F-P2", which misstates T-028 — it was rejected
  post-trial on Gate 7 + single-episode fragility; F-P2 applies to it only post-hoc (corrected).
- **Engineer model behaviour pattern (for Director calibration):** numbers impeccable and honestly
  stopped, but multi-file bookkeeping instructions are executed partially — this is now the second
  cycle running where the analysis is clean and the paperwork needs Reviewer repair.

## 3. Engineer's "Recommendations to the Director" (carried forward faithfully)

1. **Regime-classifier family is closed** as pre-registered (ER, ADX, MESA/Hilbert, HMM on the
   frozen dataset); reopening requires the ≥6-month window extension with fresh held-out split or
   a forward-lane documented completed in-market chop episode. "Do not attempt further
   chop-classifier variations on this dataset."
2. **Harm is real but unharvestable:** the F-H2 census again confirmed low-directionality days are
   adverse (median −0.13% vs +0.77% unconditional); the problem is concentration in the TEST
   window, not the theory of chop harm.
3. **Dataset staleness:** "We have repeatedly hit the limits of the TEST split (2025-06 to
   2026-05). The recent 8-month period lacks the specific signatures needed to validate regime
   classifiers. We should prioritize hypotheses that do not rely on recent chop episodes to
   demonstrate out-of-sample edge."

*(Reviewer note on #2, fact not recommendation: "harm is real" holds on the median and on
below-baseline means, but the ADX veto-day mean is **positive** (+0.78%) — unlike ER's −0.36%.
ADX-chop is a milder adverse condition than ER-chop; a veto on such days gives up positive expected
carry in exchange for variance reduction.)*

## 4. Observations from the data

- **ADX is borderline a volatility proxy in the recent regime.** ρ(ADX14, rv30) on the TEST split
  alone: **+0.709 (BTC)** — above the 0.70 alarm the full-window gate applies — and +0.420 (ETH),
  vs full-window +0.247 / +0.181. T-029 saw the same full-vs-TEST divergence for ER (+0.07 →
  +0.32). Two data points now show orthogonality claims validated full-window weakening materially
  in the 2025–26 regime. If any orthogonality-gated construct is ever assigned again, the gated
  quantity should be reported per split and a large divergence treated as a red flag.
- **ADX and ER select substantially different days** (Jaccard overlap on in-market days: 0.35
  full-window, 0.64 TEST). The concentration pathology is therefore not because ADX re-found ER's
  day-set — two mostly-different day-sets both dry up at the same Oct-2025 boundary, which is what
  makes the window-property conclusion strong.
- **TEST-split chop is plentiful but front-loaded.** BTC in-market days with ADX < 20 are 47.1% of
  the TEST split (vs 14.6% full-window) — the signal fires *more* in TEST than ever, yet not once
  in the final 229 days. BTC's ADX at TEST start was 17.9 (already sub-threshold). The window's
  last 7.5 months are a single sustained regime as ADX sees it.
- **Turnover falls under the veto** (72.25 → 58.00 full-window), consistent with the veto removing
  in-market days rather than adding switches — cost drag was not what killed this family.
- **Episode structure:** 45 combined veto episodes full-window, lengths min 1 / median 3 / max 16
  days. Median-3-day episodes echo the H-BearShort whipsaw finding (median episode 3 bars) — chop
  episodes on this data are short wherever they are measured.

## 5. What this verdict implies for adjacent ideas

- **MESA/Hilbert Cycle-Presence and HMM Regime-Switching are closed without individual testing** —
  as the pre-registered F-P2 branch dictates, and now with the strongest available evidence: any
  chop classifier, whatever its construction, needs recent in-market chop episodes in the held-out
  window to be validated, and the frozen window's last 7.5 months contain none that either of two
  structurally different classifiers can see. Closure notes with the reopening condition are on all
  four cards plus the family ledger.
- **The T-028 durable findings survive intact:** low-ER chop harm is real (F-H2 re-confirmed on a
  mostly-different day-set), and the ER signal is orthogonal-to-vol at full-window scale. Nothing
  in T-030 contradicts them; T-030 adds that the harm's *harvestable episodes* stop in Oct-2025 on
  this dataset regardless of classifier.
- **The fourth consecutive verdict decided by the mid-2025→Oct-2025 stretch** (H-IVGate, T-028,
  T-029, T-030). The meta-review §7 "TEST-split verdicts are episode-hostage" doubt is now the
  single most-confirmed structural fact about the frozen dataset. Every idea whose value
  proposition is conditional on specific regime episodes faces the same wall; only calendar time
  (the forward dry-run lane) or a window extension dilutes it. This is stated as factual
  implication, not as a selection.
- **The F-P2-style dispersion census generalizes.** It has now stopped two cycles and closed a
  family at zero trial cost. Any future overlay/veto/gate construct — in any family — whose firing
  set can be computed pre-trial should expect an F-P1/F-P2-style census as a standing pre-gate;
  three cycles of precedent define the thresholds.

## 6. Bookkeeping performed by this Reviewer

- `strategy_iteration_log.md`: Engineer's entry heading corrected (25 → 32) with a numbering note;
  Reviewer audit appended under Iteration 32.
- `research_index.md`: banner cycle counter advanced to **10 of 25**; cycle-#10 line marked
  Reviewer-verified and pointed at this brief; row #32 tightened, marked Reviewer-verified
  (exact rerun + independent TA-Lib recomputation).
- `research_metrics.md`: header updated for T-030 (n_trials unchanged at **100** — matches
  `research_index.md`); iteration-count row refreshed (31 counted headings, labels unreliable);
  zero-cost pre-gate-stop tally extended with T-029 and T-030.
- `strategy_research_notes.md`: four durable lessons appended (window-property vs
  threshold-construction; full-window gates masking TEST-split violations; relative-vs-absolute
  harm; autopsy-to-pre-gate ROI).
- `knowledge_base/hypothesis_bank.md`: ADX card updated ASSIGNED → TESTED-REJECTED with Reviewer
  caveats (TEST-split ρ 0.709; positive-mean harm); missing closure notes added to MESA/Hilbert
  and HMM cards with the reopening condition quoted; family-ledger row corrected and the reopening
  condition added.
- Meta-review counter: **10 of 25 — not due.**
- n_trials: **100**, verified consistent across `research_metrics.md`, `research_index.md`, and
  this cycle's report.
