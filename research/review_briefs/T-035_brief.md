# T-035 Review Brief — Independent Reviewer

**Task:** T-035 / H-FearGreed (Crypto Fear & Greed Index ≥75 Extreme-Greed champion veto,
six-step zero-cost pre-gate ladder, would-have-been DSR trial #101)
**Engineer verdict:** REJECTED (Step 3 — Lead/lag pre-gate)
**Reviewer verdict:** **REJECT CONFIRMED.** Every headline number independently reproduced from
raw data; no fabrication; no lookahead bias; one non-outcome-changing code defect found and
disclosed; budget and bookkeeping compliant.
**n_trials:** 100 (unchanged, zero DSR trials spent — confirmed in `research_metrics.md` header).

---

## 1. Verdict and decisive reasons

The Engineer's REJECT verdict is upheld on independent audit with one disclosed but
non-outcome-changing defect.

- **Recomputation.** Rebuilt the entire pre-gate chain directly from
  `user_data/research/data/fear_greed/fng_raw.json` (3,089 records; first/last 3 records
  byte-match the report) and the committed `BTC_USDT-1d.feather`/`ETH_USDT-1d.feather`.
  Reproduced exactly: **Step 1** coverage 99.8706% (3086/3090 calendar days, 2018-02-01 to
  2026-07-18) — PASS. **Step 2** correlation vs rv30 = −0.1382, vs roc30 = 0.7011, both below
  the 0.90 redundancy bar — PASS. **Step 3** avg |positive-lag| correlation (F&G leading) =
  0.0076 (forward 5d returns) / 0.0127 (forward rv30 change) vs avg |negative-lag| (F&G lagging)
  = 0.1405 / 0.0136 — FAIL, exactly as reported.
- **No lookahead bias.** `fwd_5d_ret`/`fwd_rv30_diff` use `shift(-5)`, which is the correct
  construction for a forward-looking correlation *target* in a diagnostic pre-gate (not a
  trading signal being computed on unclosed data) — not a leakage defect. `rv30`/`roc30`/`core`
  are built strictly from past OHLCV.
- **One code defect found, disclosed, and shown not to change today's verdict.**
  `NEXT_TASK.md`'s Step 3 falsification condition is an OR across the two forward series
  ("...for at least one of the two forward series..."), but `phase_feargreed.py:116` codes an
  **AND**: `if (avg_pos_ret <= avg_neg_ret) and (avg_pos_rv <= avg_neg_rv)`. On this data both
  conditions independently hold (0.0076 ≤ 0.1405 and 0.0127 ≤ 0.0136), so AND and OR agree and
  the REJECT stands — but the coded gate is strictly weaker than specified and could pass a
  hypothetical dataset where only one series lags, which the spec intends to reject. This is a
  process finding for future Engineers/Reviewers, not a defect in this cycle's conclusion.
- **Full spec adherence otherwise.** Falsification steps evaluated in the exact specified order
  (1→2→3), execution stopped at the first failure (steps 4-7 correctly never run); exactly the
  Extreme-Greed ≥75 construction was tested, no threshold search or alternative (e.g.
  Extreme-Fear contrarian) construction attempted; `best_strategy_so_far.py`/
  `TrendVolTarget.py` untouched; exactly 2 of the ≤3 allowed new files created (script + raw
  JSON cache — the 3rd, a standalone strategy file, was correctly never created since step 7
  was never reached).
- **Bookkeeping boundary respected.** The Engineer updated `research_metrics.md`'s header and
  `strategy_iteration_log.md` as required (deliverables 4-5), and correctly left
  `research/research_index.md` and `knowledge_base/hypothesis_bank.md` untouched (Reviewer-only
  bookkeeping per deliverable 6).
- **requests, not aiohttp, used for the fetch** — correctly avoiding the project's documented
  `aiodns`/`AsyncResolver` DNS defect (T-026/T-027 history); the raw JSON was saved verbatim
  before any processing, satisfying the mandatory auditability requirement given this project's
  three prior data-fabrication incidents (T-019, T-023, T-025). No evidence of fabrication in
  this cycle — the raw file independently reproduces the report's own printed samples.

## 2. Audit findings worth remembering

- **This is the first genuinely non-OHLCV, non-price-derived data axis this project has ever
  successfully fetched and tested** (COT, DVOL, ADX/ER/MESA/HMM were all price- or
  positioning/vol-derived). It passed both zero-cost gates that matter most for "is this real,
  new information" (reachability, redundancy) before failing on the gate that matters for
  "is this actionable" (lead/lag) — a clean, informative negative result, not an
  environment/data blocker.
- **A standing project note was factually wrong and is now corrected.** Prior to this cycle,
  `research/research_index.md`'s lessons section listed "sentiment" among data axes "confirmed
  unreachable in this environment." This appears to have been an inference from the earlier
  blocked funding-rate/order-book/on-chain pivot, never independently verified for sentiment
  specifically — the free, unauthenticated `alternative.me` endpoint used here worked on the
  first attempt with 99.87% coverage. Corrected in `research_index.md` and `research_metrics.md`
  this cycle; flagged as a general caution (see `strategy_research_notes.md` addition) against
  writing off a data axis without confirming the specific endpoint was actually tried.
- **Sixth consecutive doomed hypothesis stopped at zero DSR-trial cost** (following EWMA,
  BearShort, CointPair, SizingBand, IVGate/IVSizing, ERScale/ADXGate) — the reusable
  reachability→redundancy→lead/lag→episode-floor→harm-census→TEST-concentration ladder
  continues to catch failures cheaply.

## 3. Engineer's "Recommendations to the Director" (carried forward verbatim)

> I recommend abandoning the Fear & Greed Index as a leading indicator. Its extreme reactivity
> to past returns makes it useless for anticipatory vetoing.
>
> The failure here reiterates that "sentiment" is often just a delayed shadow of price
> momentum. I recommend prioritizing structural, non-OHLCV data that reflects actual capital
> constraints or mechanics (if reachable) over broad retail sentiment indexes.
>
> Since sentiment data appears purely reactive, any future exploration of sentiment indicators
> should first establish leading characteristics before testing trading mechanisms.

The Reviewer notes this cycle only falsifies the *anticipatory-veto* framing of this specific
index. It does not test (and the Engineer does not claim to have tested) whether a *reactive/
confirmation* use of F&G — e.g., using an already-lagging indicator to confirm a move already
underway, rather than to anticipate one — could still carry information the champion's own
signals lack. The Director should treat "sentiment is reactive" as established by this cycle's
evidence, and "sentiment is therefore useless for this project" as the Engineer's inference
beyond that evidence.

## 4. Observations from the data / open questions

- The redundancy pre-gate result is itself informative: F&G correlates fairly strongly with
  `roc30` (0.70) — a level, not just a leading/lagging property — while staying below the 0.90
  bar. This means F&G carries meaningfully overlapping (but not redundant) information with the
  champion's own trend-momentum term, consistent with it being *reactive* to the same price
  moves ROC30 already captures, rather than an independent signal.
- Step 3's negative-lag correlation for returns (0.1405) is an order of magnitude larger than
  its positive-lag counterpart (0.0076) — a large, unambiguous margin, not a borderline call.
  The rv30-change comparison (0.0136 vs 0.0127) is much closer, but still resolves the same
  direction. The verdict is not sensitive to the AND/OR code defect noted above precisely
  because both series independently clear the reject bar, one by a wide margin.
- No episode-count, harm-census, or TEST-concentration data exists for this hypothesis (steps
  4-6 were never reached) — unlike the DVOL and regime-classifier families, there is no
  in-market-episode census available for F&G to compare against those families' findings.

## 5. What this verdict implies for adjacent ideas

- **The sentiment axis is closed for anticipatory-veto constructions on this data**, on the
  same class of evidence (lead/lag) that separated the DVOL axis's two mechanisms (DVOL passed
  lead/lag and was closed later on harvestability/harm grounds instead; F&G fails lead/lag
  directly and never reaches those later gates). This is a stronger, earlier closure than
  DVOL's.
- **This does not close a reactive/contrarian framing of F&G**, nor any other sentiment source
  this project has not yet fetched (the Engineer's report and this brief both note this
  explicitly; selecting whether to pursue it is the Director's call, not this Reviewer's).
- **The corrected "sentiment is reachable" fact is now durable project knowledge** — any future
  Director considering data-axis options should read `research_index.md`'s corrected line
  rather than the pre-existing (wrong) "BLOCKED" claim.

## 6. Bookkeeping performed by this review

- `research/strategy_iteration_log.md`: Independent Reviewer audit block appended under the
  existing Iteration 39 heading (no renumbering).
- `research/research_metrics.md`: Data-axis status table updated — corrected the stale
  "sentiment BLOCKED" claim and added a Fear & Greed row with full findings; header entry was
  already added by the Engineer per deliverable 4.
- `research/research_index.md`: new row #37 added to the hypotheses-tested table; new item #27
  added to "Lessons from empirical testing"; corrected the stale "sentiment... unreachable" line
  under "New data axes still BLOCKED"; cycles-since-meta-review counter advanced to 16 of 25
  (not due).
- `knowledge_base/hypothesis_bank.md`: "Crypto Fear & Greed Sentiment Filter" card status updated
  from ASSIGNED to TESTED — REJECTED, with full verdict detail and citations.
- `research/strategy_research_notes.md`: durable lessons added (non-OHLCV provenance does not
  imply leading/anticipatory information; zero-cost pre-gate ladders keep paying for themselves,
  6-for-6 now; boolean gate logic must be transcribed literally from spec, not paraphrased;
  data-axis "BLOCKED" claims must be tied to a specific attempted endpoint, not inferred).
- **Meta-review check:** cycle counter is 16 of 25 since meta-review #1 — not due (threshold 25).

---

## T-035 audit-status note (2026-08-01)

**Relocated from `research/research_index.md` on 2026-08-02 by operator instruction, content
unchanged.** It was written there by the Reviewer who established the finding; it is moved here,
verbatim, because `research_index.md` is loaded into the Director's mandatory context every cycle
and that file's own "Where detail lives" section directs per-cycle detail to
`research/review_briefs/`. The index now carries a one-line pointer to this section. The finding,
its authorship and its standing are unaltered by the move.

> **T-035 audit-status note (2026-08-01).** The T-035 raw artifact
> (`user_data/research/data/fear_greed/fng_raw.json`) is **permanently lost**. It was never
> committed, sat outside manifest coverage, and was overwritten on 2026-08-01 by an unguarded
> re-fetch. **Restoration was tested and is impossible** — back-solving from the current byte rate
> implies ~3,233 records against the 3,101 held, so the current file is not a superset and the API
> response shape changed. **Do not attempt restoration.**
> **T-035's verdict stands.** The Reviewer's contemporaneous audit reproduced every figure correctly
> at the time, and on 2026-08-01 all six re-derived **exactly** from the current file (coverage
> 99.87%, corr −0.1382 / 0.7011, lead/lag 0.0076/0.1405 and 0.0127/0.0136, Step-3 FAIL) — every
> statistic is anchored to the BTC date range, which the added records postdate. **What is lost is
> byte-level provenance of the input**, not reproducibility of the computation: the numbers can be
> re-derived, but the raw response can no longer be proven to be what the Engineer fetched.
