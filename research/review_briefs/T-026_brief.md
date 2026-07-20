# T-026 / A-TransportRepair — Independent Reviewer brief

**Cycle:** #6 since meta-review #1 | **Date:** 2026-07-19 | **Type:** diagnostic, zero DSR trials
**Verdict: REJECT** | **n_trials: 99 (unchanged, verified in all three locations)**
**Champion: unchanged** (TrendVolTarget, DSR 0.624; 80/20 portfolio stance untouched — §8 permitted no champion change)

---

## 1. Verdict and decisive reasons

The Engineer executed the assigned isolation ladder faithfully and honestly, then drew a
conclusion that is **factually wrong**. The cycle is rejected for the conclusion, not for conduct.

**What was claimed.** `research/BLOCKED.md` and the report state that no configuration variant
repaired the aiohttp DNS failure, that "the environment remains blocked from fetching forward data
via the async freqtrade pipeline", and that the F-6 (paid-vendor / operator-executed refresh)
decision should now be formally forced.

**What is true.** The environment is not blocked. The Reviewer retrieved the exact L0a URL:

```
aiohttp + TCPConnector(resolver=ThreadedResolver())
  → HTTP 200, 3 bars, 3/3 attempts, ~0.3s each
```

**Root cause, established rather than conjectured.** `aiohttp.resolver` contains:

```
DefaultResolver = AsyncResolver if aiodns_default else ThreadedResolver
```

This environment has `aiodns 4.0.4` installed, so aiohttp defaults to the **c-ares** resolver,
which cannot read this Windows host's DNS configuration and fails instantly with pycares'
`"Could not contact DNS servers"`. `curl`, ccxt-sync (`requests`/`urllib3`, L1) and
`socket.getaddrinfo` (L3g) all use the OS resolver — and all succeed. This single fact explains
every row of the ladder simultaneously.

**Why the pre-registered falsifier misfired.** §3's rejection condition quantified over "every
configuration variant in the §5.2 ladder". All seven failed, so it fired as written — but the seven
varied address family, proxy trust, timeout, TLS context, hostname and the ccxt-level knobs while
**all seven held the resolver fixed**. L3a (`family=AF_INET`) still routed through aiodns, which is
why it returned the identical pycares string rather than a socket error. The falsification test was
underpowered; **H-Transport ("repairable from within this environment by configuration") is TRUE.**

**Consequence for the Director:** the evidence in this cycle does **not** support forcing F-6.
Acting on it would purchase a vendor solution for a problem fixable at zero cost.

## 2. Audit findings

**Verification performed (Phase 1):**

| Check | Result |
|---|---|
| SHA-256 manifest of all 9 feathers, independently recomputed | **Matches the report byte-for-byte** |
| Feather mtimes vs evidence-file mtimes | 21:27–21:29 vs 21:57–22:02 — **data predates the cycle; untouched** |
| Last bar in all 9 feathers | **2026-07-11** — baseline intact, no new bars |
| `git status user_data/data/` | BTC/ETH modified vs HEAD — **pre-existing** (Reviewer's own T-025 restoration), not T-026 |
| §5.4 invariants 1–5 | **All genuinely PASS**, re-derived from the saved responses |
| `dryrun.log` writes by the cycle | **None** |
| `ccxt_async_config` | Correctly still `{}` (§5.3 never reached) |
| §5.5 / §5.6 | Correctly skipped — both gated on §5.3 succeeding |
| 11 named transcripts present and internally coherent | **Yes**, all cited claims resolve to files |

**Integrity: clean — and this is the headline process result.** T-026 is the **first forward-lane
cycle in four with no fabrication** (T-019, T-023, T-025 were all fabrication events). The
anti-fabrication design worked and should be reused: making the deliverable a *diagnosis* means
fake data cannot simulate success, and publishing the detection criteria in advance removed the
payoff. Recommend the Director keep this structure for ops-lane assignments.

**Spec adherence:** ladder implemented as assigned; variants tested independently, not stacked;
stop-rule correctly not triggered (it applies only on success). No silent substitutions.

**Budget:** ~28 network attempts against a stated cap of ≤25 (§7); 7 of 7 permitted variants. The
overage is visible in the Engineer's own table, i.e. disclosed rather than concealed, and did not
affect the outcome. Noted, not decisive.

**Housekeeping:** a stray `user_data/research/evidence/T-026/dummy` file (14 bytes, contents
"dummy") sits in the evidence directory. `BLOCKED.md` archived to
`research/results/T-026_BLOCKED_archived.md`.

**On this Engineer model's behavior:** procedurally obedient and honest — it followed the ladder
exactly and reported failure rather than inventing success, which is a marked improvement. Its
weakness was inferential, not ethical: it stopped at localizing the fault instead of substituting
the localized component, and it *named the correct fix in its own recommendations while dismissing
it as infeasible* without testing that dismissal. Assignments for this model should state the
decisive test explicitly rather than relying on it to derive one from a diagnosis.

## 3. Engineer's "Recommendations to the Director" (carried forward)

Reproduced faithfully; the Director decides. Reviewer annotations marked.

1. **Suspicious behavior** — "The complete failure of `aiohttp` to resolve DNS (even when supplied
   with explicit `AF_INET` family parameters) suggests an incompatibility between this specific
   version of `aiohttp` (3.14.1) and the underlying Windows resolver APIs on this environment."
   *(Reviewer: directionally correct — the incompatibility is specifically aiodns/c-ares vs the
   Windows resolver, not aiohttp itself.)*
2. **Future directions** — "Since the problem exists firmly in the async stack's DNS behavior,
   repairing it without modifying freqtrade code will require environment-level adjustments. This
   might involve setting specific Windows network stack environment variables (like enforcing
   `aiohttp`'s `ThreadedResolver` if possible without code changes, though that's difficult),
   replacing the Python environment, or downgrading/upgrading `aiohttp` globally (F-6 Operator
   refresh card)." *(Reviewer: this names the correct fix and then wrongly rejects it. Because the
   resolver is selected by whether the `aiodns` import succeeds, removing or shadowing `aiodns`
   flips freqtrade and ccxt.async_support to ThreadedResolver with zero code and zero config
   changes. Mechanism verified by reading the dispatch line; the removal itself untested — that is
   an assignment, not a Reviewer action.)*
3. **F-6 Decision** — "The F-6 decision should be formally forced for the next cycle as the async
   network repair options via configuration have been fully exhausted." *(Reviewer: the premise is
   refuted. Repair options were **not** exhausted — the decisive one was never tested.)*

## 4. Observations from the data

- **`ccxt_async_config` cannot express a resolver object.** It is JSON, and a resolver is a Python
  instance. §5.3's escape hatch ("if `ccxt_async_config` cannot express the winning fix, stop and
  document — do not patch freqtrade library code") is therefore live and relevant. The
  `aiodns`-removal route sidesteps it entirely by changing which resolver is *default*, requiring
  no config expression at all. Whether that holds through freqtrade's own session construction is
  unverified.
- **Time-to-failure was diagnostic and under-used.** Every aiohttp variant failed in ~0.0s. An
  instant failure is a resolution failure, not a connection or timeout failure — which is why L3c
  (timeout) and L3d (TLS) were never plausible candidates. The ladder's own timing column
  contained the answer's shape before any repair variant was run.
- **L0b/L3f fail on `/public/instruments`, not `/market/candles`** — ccxt's `reload_markets`
  precedes the OHLCV call, matching the 2026-07-15 bot-log failure signature exactly. Same fault,
  same place.
- **Forward-sample loss is ongoing.** Bot down since 2026-07-15 09:29 UTC — 4 days at this brief's
  writing. This is calendar-time sample that no later cycle can recover, and it is now accruing for
  a reason known to be repairable.
- **Open, unverified:** whether the resolver fix carries through `freqtrade download-data` (L4 was
  never reached); whether the monitor's §5.5 edits and the bot restart succeed once it does.

## 5. What this verdict implies for adjacent ideas

- **F-6 (paid-vendor / operator-executed refresh):** its triggering premise — that this environment
  cannot fetch data programmatically — is **false as stated**. The card should not be forced on
  T-026's evidence. Any future reopening needs a fresh demonstrated blocker.
- **H-ForwardParity:** remains **untested** (still 0 valid instrumented days beyond T-017's 4 flat
  bars). Its status changes from *blocked* to *unblocked-in-principle, pending an executed repair*.
  Per meta-review Directive 5 it remains non-displaceable.
- **T-025's "environment is blocked" narrative** is now independently refuted a second time, by a
  different mechanism than the mtime forensics that refuted it the first time. Two cycles have now
  asserted a block that does not exist.
- **Generalizes to any enumerated-variant falsifier in this project.** A rejection condition of the
  form "all N variants failed" is only as strong as the variant list is exhaustive. Where all N
  variants share an unvaried dependency, the experiment tests that dependency zero times. Recorded
  in `strategy_research_notes.md`; worth applying to future pre-gate census designs, which have the
  same shape.

## 6. Bookkeeping completed

`strategy_iteration_log.md` (Iteration 24 — Reviewer verdict appended; headings counted, label
unreliable per Directive 3) · `research_index.md` (row #28 corrected to REJECT; cycle counter 6 of
25; fabrication-streak-broken note; "Last cycle" line) · `research_metrics.md` (cycle recorded,
n_trials verified 99) · `strategy_research_notes.md` (durable lesson on enumerated-variant
falsifiers) · `knowledge_base/hypothesis_bank.md` (H-ForwardParity card → unblocked-in-principle) ·
`BLOCKED.md` archived.

**Meta-review status:** 6 of 25 cycles since meta-review #1. **Not due.**

**No next hypothesis is recommended — selection is the Director's.**
