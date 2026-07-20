# T-026 Report: A-TransportRepair

## Task ID and hypothesis
**Task ID:** T-026
**Hypothesis:** H-Transport: The OKX fetch failure is client-stack-specific — localized to the `aiohttp`/`ccxt.async_support` layer — and is not a network-level, DNS-level, or exchange-side block. It is therefore repairable from within this environment by configuration (connector, resolver, TLS context, timeout, or proxy-trust settings) without any change to strategy code, data, or the exchange account.

## Objective
Determine why the freqtrade/ccxt async client cannot reach OKX from this environment while `curl` reaches the identical URL successfully, repair it if it is repairable by configuration, and restart the dry-run bot so the forward-evidence lane resumes accruing sample.

## Implementation Notes
- Followed the isolation ladder exact steps as specified in §5.1 and §5.2. 
- Created and executed probe scripts `t026_probe.py` (L0b), `t026_l1.py`, `t026_l2.py`, `t026_l3a.py` through `t026_l3g.py` to test variations cleanly and independently. 
- Transcripts saved to `user_data/research/evidence/T-026/`. 
- No configuration could resolve the `ClientConnectorDNSError` inside `aiohttp` on this environment.
- Because all L3 repair options failed, followed the §6 block path and wrote `research/BLOCKED.md`.
- Monitor edits (§5.5) and Bot restart (§5.6) were skipped per instructions (`only if §5.3 succeeded`).
- Ran §5.4 Authenticity checks successfully as instructed.

## Ladder Results Table

| Variant | Attempts | Outcome | Exception Type | Time-to-failure |
|---|---|---|---|---|
| L0a (curl) | 1 | SUCCESS | None (HTTP 200) | ~0.5s |
| L0b (ccxt async) | 3 | FAIL | ExchangeNotAvailable | ~0.1s |
| L1 (ccxt sync) | 3 | SUCCESS | None | ~4.0s (success) |
| L2 (bare aiohttp) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3g (socket.getaddrinfo) | 3 | SUCCESS | None | ~0.0s |
| L3a (AF_INET) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3b (trust_env) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3c (timeout) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3d (SSL context) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3e (AWS host) | 3 | FAIL | ClientConnectorDNSError | ~0.0s |
| L3f (ccxt timeout/trust) | 3 | FAIL | ExchangeNotAvailable | ~0.1s |

## Diagnosis
The `aiohttp` layer is uniquely implicated. The failure is completely localized to the `aiohttp`/`ccxt.async_support` stack's DNS resolution mechanism, which fails instantly with `ClientConnectorDNSError`.

The following layers are explicitly EXONERATED:
- Network-level connectivity (raw curl succeeded).
- Exchange-side block (raw curl succeeded).
- `ccxt` exchange implementation logic (L1 `ccxt` SYNC path, which uses `requests`/`urllib3`, succeeded).
- System DNS/IPv4 reachability (L3g `socket.getaddrinfo` returned accurate IPv4 records instantly).

Because no configuration variant repaired the `aiohttp` DNS failure, H-Transport is REJECTED.

## §5.4 Authenticity Output
```
--- 1. OHLC Sanity ---
PASS: user_data/data/okx\ADA_USDT-1d.feather
PASS: user_data/data/okx\AVAX_USDT-1d.feather
PASS: user_data/data/okx\BNB_USDT-1d.feather
PASS: user_data/data/okx\BTC_USDT-1d.feather
PASS: user_data/data/okx\DOT_USDT-1d.feather
PASS: user_data/data/okx\ETH_USDT-1d.feather
PASS: user_data/data/okx\LINK_USDT-1d.feather
PASS: user_data/data/okx\SOL_USDT-1d.feather
PASS: user_data/data/okx\UNI_USDT-1d.feather
--- 2. Tick-size conformance ---
PASS: BTC_USDT-1d tickSz 0.1 conformance
--- 3. Provenance ---
PASS: No new bars after 2026-07-11, no provenance required.
--- 4. Overlap immutability ---
PASS: SHA256 manifest unchanged (no download occurred).
  user_data/data/okx\ADA_USDT-1d.feather: 9a86f391b8be18de82bf83e85549743e315121e1b1d6cb580a832cfb1b8a52ee
  user_data/data/okx\AVAX_USDT-1d.feather: a4a8a0fcdc71fccf3885f0a137ebee41f204d30b60289ae66efa83fb121a646b
  user_data/data/okx\BNB_USDT-1d.feather: 1596c77f6573483a6c82e4962d5f62b24078009be8e85c53d4c39e9096abbf9b
  user_data/data/okx\BTC_USDT-1d.feather: b3dac6954cceedf6f77ba3cd6aebc5ff9b8268ed54c08508dd047e7ab6a67bf8
  user_data/data/okx\DOT_USDT-1d.feather: afdd1a9d1880e8a00d2da7affe899f4b8626f55400de936a3f30c1b9743a2244
  user_data/data/okx\ETH_USDT-1d.feather: 26c6336d0743398d253fb71f6aff78ef23b79de01d047461ccd4e316cccedde5
  user_data/data/okx\LINK_USDT-1d.feather: 911240b8dc6b53f5d2618b4fe959e03914fa214f31d7137b5e60c4b6fcafc9c2
  user_data/data/okx\SOL_USDT-1d.feather: bcf88e1e23d6902aa93e3b8d2ddf35695604bb6944a8ce5937de2acfad918f86
  user_data/data/okx\UNI_USDT-1d.feather: b7ac459e71bd18877a702c5235d48b3b9eed61495139dace78eae5bc20cb8e89
--- 5. Cross-source agreement ---
PASS: Last 30 daily closes agree within 0.5% (max diff: 0.05%)
```

## Monitor Edits
Skipped. Not performed as the ladder repair path failed (only applicable if §5.3 succeeded).

## Bot Status
Skipped. Not performed as the ladder repair path failed (only applicable if §5.3 succeeded).

## Recommendations to the Director
- **Suspicious behavior**: The complete failure of `aiohttp` to resolve DNS (even when supplied with explicit `AF_INET` family parameters) suggests an incompatibility between this specific version of `aiohttp` (3.14.1) and the underlying Windows resolver APIs on this environment.
- **Future directions**: Since the problem exists firmly in the async stack's DNS behavior, repairing it without modifying freqtrade code will require environment-level adjustments. This might involve setting specific Windows network stack environment variables (like enforcing `aiohttp`'s `ThreadedResolver` if possible without code changes, though that's difficult), replacing the Python environment, or downgrading/upgrading `aiohttp` globally (F-6 Operator refresh card).
- **F-6 Decision**: The F-6 decision should be formally forced for the next cycle as the async network repair options via configuration have been fully exhausted. 
