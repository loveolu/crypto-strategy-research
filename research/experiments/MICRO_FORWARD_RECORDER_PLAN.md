# OKX one-minute forward recorder

Created 2026-09-04 PDT after CRYPTO-EXP-028/030 showed that 29 days is enough
to screen microstructure hypotheses but not enough for candidate-grade evidence.

## Contract

- Record nine liquid OKX USDT perpetuals at one-minute resolution.
- Persist only complete, finalized UTC days: exactly 1,440 timestamps per partition.
- Store one immutable CSV partition per instrument/day under
  `user_data/research/data/okx_micro_forward/`.
- On rerun, retain original provenance and reject any changed overlapping OHLCV.
- Use atomic partition/status writes and append-only request/error audit records.
- Daily host invocation: `run_micro_forward_recorder.ps1`, intended for 00:20 local
  time so the prior UTC day is finalized.

## Research gate

Do not use this forward archive to promote a strategy until at least 365 complete
common days exist. At that point use rolling chronological walk-forward validation,
measured execution costs, delay/cost/concentration robustness, and the cumulative
multiple-testing adjustment. Until then it is data collection, not evidence of a
tradeable edge.

## Launch note

The first in-session collection attempt for 2026-09-03 was correctly audited as
9/9 failures because the managed sandbox forbade outbound sockets (`WinError 10013`).
No partial candle partition was written. The collector and pagination behavior are
covered by offline tests; a host-context scheduled task is the intended runtime.

Two non-escalated `schtasks /Create` attempts from the managed process returned
`ERROR: The system cannot find the path specified` even though `schtasks.exe`,
PowerShell, Python and the wrapper path all exist. Therefore the task is explicitly
**NOT REGISTERED** as of 2026-09-04 16:12 PDT. Do not describe collection as active
until a queryable task or another live process handle exists and a complete partition
has been written successfully.
