"""Append-safe daily recorder for public OKX Rubik market-structure data."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parent / "data" / "market_structure"
CURRENCIES = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
BASE_URL = "https://www.okx.com/api/v5/rubik/stat"
METRICS = {
    "open_interest_volume": {
        "path": "contracts/open-interest-volume",
        "params": {},
        "values": ["open_interest_usd", "volume_usd"],
    },
    "long_short_account_ratio": {
        "path": "contracts/long-short-account-ratio",
        "params": {},
        "values": ["long_short_account_ratio"],
    },
    "taker_volume": {
        "path": "taker-volume",
        "params": {"instType": "CONTRACTS"},
        "values": ["taker_buy_volume_usd", "taker_sell_volume_usd"],
    },
}


def parse_rows(
    metric: str,
    currency: str,
    rows: list[list[str]],
    fetched_at_utc: str,
    source_url: str,
) -> pd.DataFrame:
    """Normalize one OKX array-shaped response using the declared metric schema."""
    value_columns = METRICS[metric]["values"]
    parsed = []
    for row in rows:
        if len(row) != len(value_columns) + 1:
            raise ValueError(f"unexpected {metric} row width: {len(row)}")
        timestamp_ms = int(row[0])
        record = {
            "timestamp_ms": timestamp_ms,
            "timestamp_utc": pd.Timestamp(timestamp_ms, unit="ms", tz="UTC").isoformat(),
            "currency": currency,
        }
        record.update({name: float(value) for name, value in zip(value_columns, row[1:])})
        record.update({"fetched_at_utc": fetched_at_utc, "source_url": source_url})
        parsed.append(record)
    return pd.DataFrame(parsed)


def merge_rows(old: pd.DataFrame, new: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    """Merge new timestamps while rejecting revisions to already stored values."""
    if old.empty:
        return new.sort_values("timestamp_ms").reset_index(drop=True)
    if new.empty:
        return old.sort_values("timestamp_ms").reset_index(drop=True)
    old_by_time = old.set_index("timestamp_ms")
    new_by_time = new.set_index("timestamp_ms")
    overlap = old_by_time.index.intersection(new_by_time.index)
    for timestamp in overlap:
        for column in value_columns:
            before = float(old_by_time.loc[timestamp, column])
            after = float(new_by_time.loc[timestamp, column])
            if not np.isclose(before, after, rtol=0.0, atol=1e-12):
                raise ValueError(
                    f"immutable overlap changed at {timestamp} column {column}: {before} != {after}"
                )
    additions = new.loc[~new["timestamp_ms"].isin(old["timestamp_ms"])]
    return pd.concat([old, additions], ignore_index=True).sort_values("timestamp_ms").reset_index(drop=True)


def finalized_daily_rows(rows: pd.DataFrame, fetched_at_utc: str) -> pd.DataFrame:
    """Exclude the current/incomplete UTC day and any future-labelled rows."""
    cutoff_ms = int(pd.Timestamp(fetched_at_utc).floor("1D").timestamp() * 1000)
    return rows.loc[rows["timestamp_ms"] < cutoff_ms].copy()


def _append_audit(record: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / "fetch_log.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary_path = Path(temporary)
    try:
        frame.to_csv(temporary_path, index=False)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _fetch(metric: str, currency: str) -> tuple[pd.DataFrame, dict]:
    spec = METRICS[metric]
    url = f"{BASE_URL}/{spec['path']}"
    params = {"ccy": currency, "period": "1D", **spec["params"]}
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    last_error = None
    for attempt in range(1, 4):
        try:
            time.sleep(0.35)
            response = requests.get(url, params=params, timeout=30)
            body = response.content
            payload = response.json()
            audit = {
                "fetched_at_utc": fetched_at,
                "metric": metric,
                "currency": currency,
                "url": response.url,
                "http_status": response.status_code,
                "api_code": payload.get("code"),
                "rows_received": len(payload.get("data", [])),
                "response_sha256": hashlib.sha256(body).hexdigest(),
                "attempt": attempt,
            }
            _append_audit(audit)
            if response.status_code != 200 or payload.get("code") != "0":
                raise RuntimeError(f"OKX returned HTTP {response.status_code}, code {payload.get('code')}")
            parsed = parse_rows(metric, currency, payload["data"], fetched_at, response.url)
            return finalized_daily_rows(parsed, fetched_at), audit
        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = error
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"failed {metric}/{currency} after 3 attempts: {last_error}")


def collect() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    for metric, spec in METRICS.items():
        for currency in CURRENCIES:
            try:
                new, audit = _fetch(metric, currency)
                path = DATA_DIR / metric / f"{currency}.csv"
                old = pd.read_csv(path) if path.exists() else pd.DataFrame()
                merged = merge_rows(old, new, spec["values"])
                _atomic_csv(merged, path)
                results.append(
                    {
                        "metric": metric,
                        "currency": currency,
                        "rows": int(len(merged)),
                        "new_rows": int(len(merged) - len(old)),
                        "earliest_utc": merged["timestamp_utc"].iloc[0],
                        "latest_utc": merged["timestamp_utc"].iloc[-1],
                        "response_sha256": audit["response_sha256"],
                    }
                )
            except Exception as error:
                errors.append({"metric": metric, "currency": currency, "error": str(error)})
    status = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expected_series": len(METRICS) * len(CURRENCIES),
        "successful_series": len(results),
        "failed_series": len(errors),
        "results": results,
        "errors": errors,
    }
    status_path = DATA_DIR / "status.json"
    descriptor, temporary = tempfile.mkstemp(prefix=".status.", suffix=".tmp", dir=DATA_DIR)
    os.close(descriptor)
    temporary_path = Path(temporary)
    try:
        temporary_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary_path, status_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    status = collect()
    print(json.dumps(status, indent=2))
    return 0 if status["failed_series"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
