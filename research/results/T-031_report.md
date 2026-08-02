# T-031_report

**Task ID:** T-031
**Hypothesis:** The funding-rate data axis can be bootstrapped from this environment at zero cost: OKX's public REST v5 API is reachable (proven for candles via raw curl in T-025/T-026/T-027), retains ≥60 days of 8-hour funding-rate history for BTC-USDT-SWAP and ETH-USDT-SWAP, serves that history immutably (identical values on re-fetch), and an append-only recorder run at least every 14 days captures it without gaps.

## 2. Implementation Notes
- Created `user_data/research/funding_recorder.py` mapping OKX's v5 `funding-rate-history` API with sync `requests`.
- Created `user_data/research/verify_funding.py` for independent verification.
- Pagination semantics determined empirically: `before` paginates towards newer records, `after` paginates towards older records. Used `after` to backfill, and `before` was not strictly needed, just checking overlap.
- Records are saved to `user_data/research/data/funding/<instId>.csv`.
- No assumptions made on missing data; fields mapped directly.
- `mock_data.py` was untouched.
- Did not touch any `.feather` file.

## 3. Lookahead/leakage checks performed
- Not applicable for this cycle (no strategy or backtest implemented). Assured that the `funding_recorder.py` fetches only true history and timestamp logic correctly separates `funding_time_ms`.

## 4. Variants attempted
- 0 (0 / 0 budget consumed).

## 5. Backtest results
- N/A

## 6. Walk-forward / out-of-sample results
- N/A

## 7. DSR and any other required statistics
- N/A. `n_trials` remains at **100**.

## 8. Verdict vs. falsification statement
**Verdict: ACCEPT (Outcome A)**
- **F-a (unreachable):** FALSE. Reachable.
- **F-b (retention too shallow):** FALSE. Deepest retrievable funding record is 97 days old.
- **F-c (source unstable):** FALSE. No overlapping records differed.

## 9. Regime behavior
- N/A

## 10. Lessons
- OKX public API retains exactly 97.0 days of funding-rate history. 
- The `after` parameter is used to paginate backwards in time.
- OKX provides `open-interest-volume`, `long-short-account-ratio`, and `taker-volume` free of charge, with data going back to 2026-01-21T16:00:00Z (at 1D granularity).

## 11. Raw output locations
- `research/results/T-031_transcripts/P1_probe_btc.txt`
- `research/results/T-031_transcripts/BTC-USDT-SWAP_first.json`
- `research/results/T-031_transcripts/BTC-USDT-SWAP_last.json`
- `research/results/T-031_transcripts/P6_survey_0.json`
- `research/results/T-031_transcripts/P6_survey_1.json`
- `research/results/T-031_transcripts/P6_survey_2.json`
- `user_data/research/data/funding/*.csv`

## 12. Recommendations to the Director
- The funding rate recorder is fully operational. We should wait 4-6 months to accrue sufficient forward data before running any strategy relying on it.
- The `open-interest`, `long-short-ratio`, and `taker-volume` endpoints returned 1D data spanning over ~6 months. This is a very promising alternate axis since it goes much further back than the 97-day funding rate. A future cycle could backfill and formalize these series.

## 13. Runbook
- To run incremental update:
  `python user_data/research/funding_recorder.py --update`
- **Required cadence:** At least every 14 days (since retention is 97 days, even 30+ day gaps are lossless, but 14 days is safe).
- **Healthy run output:**
  ```
  Updated BTC-USDT-SWAP: 0 new rows
  Updated ETH-USDT-SWAP: 0 new rows
  ...
  ```

---
## Acceptance Checks

**AC1 Probe:** HTTP 200, `code=="0"`, 100 records, transcript saved. Latest record at `1784563200000`. PASS.
**AC2 Backfill:** 9/9 instruments stored.

| Instrument | Record Count | Earliest UTC | Latest UTC | Retention (Days) | Gaps > 8h |
|---|---|---|---|---|---|
| BTC-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| ETH-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| SOL-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| BNB-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| ADA-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| AVAX-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| DOT-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| LINK-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
| UNI-USDT-SWAP | 292 | 2026-04-14T08:00:00Z | 2026-07-20T08:00:00Z | 97.0 | None |
PASS.

**AC3 Authenticity:** 
```
Verification for BTC-USDT-SWAP:
Time UTC | Stored Rate | Fetched Rate | Match
2026-06-03T00:00:00Z | 0.0000865678874748 | 0.0000865678874748 | True
2026-05-30T08:00:00Z | 0.0000272922964657 | 0.0000272922964657 | True
2026-06-10T16:00:00Z | -0.0000087786677452 | -0.0000087786677452 | True
2026-06-06T08:00:00Z | -0.0000337977745229 | -0.0000337977745229 | True
2026-07-19T16:00:00Z | 0.0000422130855567 | 0.0000422130855567 | True
2026-04-27T08:00:00Z | -0.0000629907601197 | -0.0000629907601197 | True
2026-07-05T16:00:00Z | 0.0000211483321941 | 0.0000211483321941 | True
2026-06-22T08:00:00Z | 0.0000287541037749 | 0.0000287541037749 | True
2026-06-04T00:00:00Z | 0.0000987113820589 | 0.0000987113820589 | True
2026-04-22T00:00:00Z | -0.0000183064589195 | -0.0000183064589195 | True

Verification for ETH-USDT-SWAP:
Time UTC | Stored Rate | Fetched Rate | Match
2026-06-17T00:00:00Z | 0.0000309117993428 | 0.0000309117993428 | True
2026-05-29T16:00:00Z | 0.0000700212118699 | 0.0000700212118699 | True
2026-07-12T16:00:00Z | -0.0000149280788989 | -0.0000149280788989 | True
2026-06-15T16:00:00Z | -0.0000409078153245 | -0.0000409078153245 | True
2026-05-16T16:00:00Z | 0.0000711006759472 | 0.0000711006759472 | True
2026-04-24T00:00:00Z | -0.0000335490466586 | -0.0000335490466586 | True
2026-05-19T16:00:00Z | 0.0000782644134814 | 0.0000782644134814 | True
2026-04-23T08:00:00Z | -0.0000378413703615 | -0.0000378413703615 | True
2026-06-24T16:00:00Z | 0.0000357666052303 | 0.0000357666052303 | True
2026-06-21T00:00:00Z | 0.0000311233669537 | 0.0000311233669537 | True
```
PASS.

**AC4 Idempotency:** Second run added 0 rows. 
Hashes:
BTC-USDT-SWAP.csv: D819918F4069E24C9ABCF618A6776E178BCF8B4FE7C97B3E0EB52ABE4E424049
ETH-USDT-SWAP.csv: E15B9BC8FF15C73B30C40BCE29E04943678CBDEAF464D1E4998FAB0856AD7CBC
SOL-USDT-SWAP.csv: E6F6CB4C54062804AD1EF1CF28ECAFD8EB7233FDE8EF221D4163F5F9D5EE90E1
BNB-USDT-SWAP.csv: CA00F12E8263B781B448D0F4199A5B98557354C42059E559B0580C4C71C141B4
ADA-USDT-SWAP.csv: A5DBC2BAB4E16D1700093F110CA099FF4616C1FD727AC7216E4E25E75BB52F2A
AVAX-USDT-SWAP.csv: BBA4B8B9D6B2129DCC9AA474FC0D2B5D4DE34F96D96B22A23B1EF07F05356D93
DOT-USDT-SWAP.csv: A94088FDFC0E99DA25EC4DE837293AC74B37E8A44F83CD7CFD1D1DFD4CB9F250
LINK-USDT-SWAP.csv: 9640022989583299E4923DE1D2EBBA1CAD9F0F637C427706251F141157A7ED0F
UNI-USDT-SWAP.csv: 906A2E0BEB3A24F0BBF9FF921FC9EAB5201172BE92B8288C216D0CDAC0B5D19C
(Pre and post update hashes are identical). PASS.

**AC5 No synthetic paths:** Code exclusively fetches from real API, parsed through JSON, appending to CSV. No `mock_data.py` modified. PASS.

**AC6 No-touch manifest:** Feathers identical before and after. PASS.

**AC7 Forward-lane preflight:**
Last heartbeat was >24h old, so restarted exactly as requested.
Fresh bot heartbeat: PID=16124 at 2026-07-20 08:39:08,665.
Startup log confirmed: `Dry run is enabled. All trades are simulated.`
PASS.

**AC8 Survey table:**
| Endpoint | HTTP Status | Earliest Retrievable Timestamp | Granularity |
|---|---|---|---|
| `contracts/open-interest-volume?ccy=BTC&period=1D` | 200 | 2026-01-21T16:00:00Z | 1D |
| `contracts/long-short-account-ratio?ccy=BTC&period=1D` | 200 | 2026-01-21T16:00:00Z | 1D |
| `taker-volume?ccy=BTC&instType=CONTRACTS&period=1D` | 200 | 2026-01-21T16:00:00Z | 1D |
PASS.

**AC9 Budget / n_trials:** `n_trials` = 100 in all bookkeeping files. Constraints respected. PASS.
