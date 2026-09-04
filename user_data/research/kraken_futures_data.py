"""Download and validate public Kraken Futures chart candles."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "user_data" / "research" / "data" / "kraken_futures"
SYMBOLS = {
    "BTC": "PF_XBTUSD",
    "ETH": "PF_ETHUSD",
    "SOL": "PF_SOLUSD",
    "XRP": "PF_XRPUSD",
    "ADA": "PF_ADAUSD",
    "AVAX": "PF_AVAXUSD",
    "DOT": "PF_DOTUSD",
    "LINK": "PF_LINKUSD",
}
BASE = "https://futures.kraken.com/api/charts/v1/trade"


def parse_candles(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    frame["date"] = pd.to_datetime(frame.pop("time"), unit="ms", utc=True)
    frame = frame.set_index("date")[["open", "high", "low", "close", "volume"]]
    return frame.astype(float)


def merge_candle_pages(pages: list[pd.DataFrame]) -> pd.DataFrame:
    if not pages:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    return pd.concat(pages).sort_index().loc[lambda x: ~x.index.duplicated(keep="first")]


def download(symbol: str, resolution: str, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, list[dict]]:
    cursor = int(start.timestamp())
    end_seconds = int(end.timestamp())
    step = {"4h": 14_400, "1d": 86_400}[resolution]
    pages = []
    provenance = []
    while cursor <= end_seconds:
        url = f"{BASE}/{symbol}/{resolution}"
        response = requests.get(url, params={"from": cursor, "to": end_seconds}, timeout=30)
        body = response.content
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("candles", [])
        provenance.append(
            {
                "url": response.url,
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "rows": len(rows),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
        )
        if not rows:
            break
        page = parse_candles(rows)
        pages.append(page)
        next_cursor = int(page.index.max().timestamp()) + step
        if next_cursor <= cursor:
            raise RuntimeError("Kraken pagination did not advance")
        cursor = next_cursor
        if not payload.get("more_candles", False):
            break
        time.sleep(0.25)
    frame = merge_candle_pages(pages).loc[start:end]
    validate_candles(frame, expected_frequency=resolution)
    return frame, provenance


def validate_candles(frame: pd.DataFrame, expected_frequency: str | None = None) -> None:
    if frame.empty:
        raise ValueError("no candles returned")
    if not frame.index.is_monotonic_increasing or not frame.index.is_unique:
        raise ValueError("candle timestamps are not sorted and unique")
    if expected_frequency and len(frame) > 1:
        expected = pd.Timedelta(expected_frequency)
        if not frame.index.to_series().diff().dropna().eq(expected).all():
            raise ValueError(f"candle spacing is not uniformly {expected_frequency}")
    if frame.isna().any().any():
        raise ValueError("candle data contains missing values")
    if not ((frame["high"] >= frame[["open", "close"]].max(axis=1)).all()
            and (frame["low"] <= frame[["open", "close"]].min(axis=1)).all()
            and (frame["high"] >= frame["low"]).all()
            and (frame["volume"] >= 0).all()):
        raise ValueError("invalid OHLCV relationship")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2023-01-22")
    parser.add_argument("--end", default="2026-09-01")
    args = parser.parse_args()
    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {"source": BASE, "start": start.isoformat(), "end": end.isoformat(), "series": []}
    for instrument, symbol in SYMBOLS.items():
        for resolution in ("4h", "1d"):
            frame, provenance = download(symbol, resolution, start, end)
            path = OUTPUT / f"{instrument}-{symbol}-{resolution}.feather"
            frame.reset_index().to_feather(path)
            manifest["series"].append(
                {
                    "instrument": instrument,
                    "symbol": symbol,
                    "resolution": resolution,
                    "rows": len(frame),
                    "first": frame.index.min().isoformat(),
                    "last": frame.index.max().isoformat(),
                    "file": str(path.relative_to(ROOT)),
                    "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "requests": provenance,
                }
            )
            print(f"{instrument} {resolution}: {len(frame)} rows")
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
