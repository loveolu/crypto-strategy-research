import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "user_data" / "research"))

from market_structure_readiness import audit_archive, main


def _write_series(root: Path, metric: str, coin: str, stamps: list[int]) -> None:
    path = root / metric / f"{coin}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp_ms", "currency", "value"])
        writer.writeheader()
        for stamp in stamps:
            writer.writerow({"timestamp_ms": stamp, "currency": coin, "value": 1})


def test_audit_requires_complete_aligned_daily_history(tmp_path: Path) -> None:
    day = 86_400_000
    stamps = [1_700_000_000_000 + day * i for i in range(365)]
    for metric in ("oi", "flow"):
        for coin in ("BTC", "ETH"):
            _write_series(tmp_path, metric, coin, stamps)

    ready = audit_archive(tmp_path, ("oi", "flow"), ("BTC", "ETH"), 365)
    assert ready["ready_for_feature_research"] is True
    assert ready["common_complete_days"] == 365
    assert ready["series_checked"] == 4
    assert ready["issues"] == []

    _write_series(tmp_path, "flow", "ETH", stamps[:-1])
    short = audit_archive(tmp_path, ("oi", "flow"), ("BTC", "ETH"), 365)
    assert short["ready_for_feature_research"] is False
    assert short["common_complete_days"] == 364
    assert any("minimum 365" in issue for issue in short["issues"])


def test_audit_rejects_duplicates_gaps_and_missing_series(tmp_path: Path) -> None:
    day = 86_400_000
    stamps = [1_700_000_000_000, 1_700_000_000_000, 1_700_000_000_000 + 2 * day]
    _write_series(tmp_path, "oi", "BTC", stamps)

    result = audit_archive(tmp_path, ("oi",), ("BTC", "ETH"), 2)
    btc = next(row for row in result["series"] if row["currency"] == "BTC")
    assert result["ready_for_feature_research"] is False
    assert btc["duplicate_timestamps"] == 1
    assert btc["missing_daily_intervals"] == 1
    assert any("missing series" in issue for issue in result["issues"])


def test_cli_writes_machine_readable_evidence(tmp_path: Path) -> None:
    day = 86_400_000
    _write_series(tmp_path, "oi", "BTC", [1_700_000_000_000 + day * i for i in range(2)])
    output = tmp_path / "summary.json"
    exit_code = main([
        "--root", str(tmp_path), "--metrics", "oi", "--currencies", "BTC",
        "--minimum-days", "3", "--output", str(output),
    ])
    assert exit_code == 2
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["ready_for_feature_research"] is False
    assert saved["common_complete_days"] == 2
