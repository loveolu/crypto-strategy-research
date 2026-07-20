# Blocked Report for T-026

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

## Transcript Filenames
All present in `user_data/research/evidence/T-026/`:
- L0a_curl.txt
- L0b_ccxt_async.txt
- L1_ccxt_sync.txt
- L2_bare_aiohttp.txt
- L3a_family_af_inet.txt
- L3b_trust_env.txt
- L3c_timeout.txt
- L3d_ssl_context.txt
- L3e_aws_host.txt
- L3f_ccxt_async_tweaked.txt
- L3g_socket_getaddrinfo.txt

## L0a Curl Transcript
```
Sun Jul 19 04:57:10 UTC 2026
{"code":"0","msg":"","data":[["1784419200000","64834","64967.9","64620","64719.2","393.08768811","25469405.273798826","25469405.273798826","0"],["1784332800000","63937.3","64872.7","63886.6","64833.9","1809.65919575","116409762.485911622","116409762.485911622","1"],["1784246400000","63830.9","64391.9","62536.4","63937.3","5902.50964255","373677161.766383119","373677161.766383119","1"],["1784160000000","64760.3","64998.6","63750","63830.8","4209.46222691","270848592.20798104","270848592.20798104","1"],["1784073600000","65037.4","65600","64486","64760.3","5769.9185297","375175262.75635538","375175262.75635538","1"]]}
HTTP_CODE=200 TIME_TOTAL=0.485351
Sun Jul 19 04:57:11 UTC 2026
```

## Diagnosis
The `aiohttp` layer is uniquely implicated. The failure is completely localized to the `aiohttp`/`ccxt.async_support` stack, specifically its DNS resolution mechanism, which instantly fails with `ClientConnectorDNSError` on every configuration variant tested. 

The following layers are explicitly EXONERATED:
- Network-level connectivity (raw curl succeeded).
- Exchange-side block (raw curl succeeded).
- `ccxt` exchange implementation logic (L1 `ccxt` SYNC path, which uses `requests`/`urllib3`, succeeded).
- System DNS/IPv4 reachability (L3g `socket.getaddrinfo` returned accurate IPv4 records instantly).

Because no configuration variant repaired the `aiohttp` DNS failure, H-Transport is REJECTED. The environment remains blocked from fetching forward data via the async freqtrade pipeline.
