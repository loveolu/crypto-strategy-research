# Review Brief: T-027 / A-ResolverRepair

**Date:** 2026-07-19
**Task:** T-027 / A-ResolverRepair
**Reviewer Verdict:** ACCEPTED (Ops/Infrastructure)

## 1. Verdict and decisive reasons
**ACCEPTED.** The assignment was executed flawlessly. The `aiodns` uninstall successfully decoupled the async loop from `c-ares`, restoring `freqtrade`'s network connection via the Windows OS resolver (`ThreadedResolver`).
- `aiohttp` probe succeeded perfectly.
- `freqtrade download-data` downloaded authentic new bars for all 9 assets.
- `curl` verification passed for all newly fetched bars.
- `dryrun_monitor.py` was restored to an honest freshness check and cleanly evaluated the state without synthesizing data.
- The bot successfully detached and resumed heartbeats.

This cycle breaks the four-cycle blockage on the forward-evidence lane and confirms T-026's misdiagnosis (that the environment was unrepairable).

## 2. Audit findings worth remembering
- **Integrity Clean:** The Engineer successfully ran the entire procedure honestly. The cross-checks and transcripts reconcile with the report.
- **Spec Adherence:** The procedure was followed precisely. The pre-checks, falsification checks, real network requests, and authenticity assertions were executed in the prescribed order.
- **Budget Compliance:** 0 DSR trials spent (`n_trials=99`). 22 network attempts out of 30 allocated.
- **Testing Constraints (`pytest`):** The Engineer correctly noted that `test_dryrun_monitor.py` was structurally broken for `pytest` due to top-level imperative `sys.exit()` calls. This was patched to allow test collection. Future scripts should ensure all testable assertions are wrapped in proper `test_` functions.

## 3. Engineer's "Recommendations to the Director"
1. **Forward Lane Restored:** The forward-evidence lane is fully restored. The dry-run bot is accruing valid out-of-sample data on OKX. *(Reviewer confirms).*
2. **`pytest` Structure:** The `pytest` execution for `test_dryrun_monitor.py` was structurally incompatible out-of-the-box. Future pytest checks should ensure test scripts are valid pytest functions, not just imperative execution scripts.
3. **C1 Coverage Trigger Fired:** The C1 trigger currently fails (10% coverage) due to the extended downtime between 2026-07-09 and 2026-07-19. This will heal naturally as the bot remains up, but the recommendation to "register Task Scheduler keepalive to prevent recurrence" stands. *(Reviewer confirms this is correct behavior for the C1 trigger).*

## 4. Observations from the data
- The expected signal for the `TrendVolTarget` champion and portfolio remains FLAT (0 entries fired) through the 2026-07-08 to 2026-07-18 window. The M1 Mechanical Parity check correctly confirmed flat-parity across all bars.

## 5. What this verdict implies for adjacent ideas
- The forward-evidence lane (H-ForwardParity) is officially UNBLOCKED and accruing sample. The Director can safely rely on the bot remaining operational and data being pulled authentically.
- The `F-6` hypothesis (buying a paid-vendor feed) is formally rejected and no longer relevant.
