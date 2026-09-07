"""A-021: fixed five-day archive probe; no strategy imports or outcome evaluation.

Raw bytes and HTTP metadata are immutable. A partial cache fails closed rather
than refetching. Run --offline to replay evidence without network access.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'user_data/research/data/binance_metrics_a021'
DAYS = ('2023-01-01', '2024-01-01', '2025-01-01', '2025-08-01', '2026-08-01')
BASE = 'https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/'


def fetch_raw(url: str, path: Path, session) -> bytes:
    """Save the complete response before validation; never repair/overwrite cache."""
    metadata_path = path.with_name(path.name + '.meta.json')
    if path.exists() or metadata_path.exists():
        if not path.exists() or not metadata_path.exists():
            raise ValueError(f'Incomplete raw/metadata pair: {path}')
        body = path.read_bytes()
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        if metadata['url'] != url:
            raise ValueError(f'Cached URL mismatch: {path}')
        if metadata['sha256'] != hashlib.sha256(body).hexdigest():
            raise ValueError(f'Cached hash mismatch: {path}')
    else:
        response = session.get(url, timeout=30)
        body = response.content
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents concurrent writers from replacing evidence.
        with path.open('xb') as stream:
            stream.write(body)
        metadata = {
            'url': url,
            'fetched_at_utc': datetime.now(timezone.utc).isoformat(),
            'status': response.status_code,
            'headers': dict(response.headers),
            'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest(),
        }
        with metadata_path.open('x', encoding='utf-8') as stream:
            json.dump(metadata, stream, indent=2)
    if metadata['status'] != 200:
        raise ValueError(f"HTTP {metadata['status']}: preserved at {path}")
    return body


def verify_checksum(body: bytes, checksum: bytes, filename: str) -> None:
    fields = checksum.decode('ascii').split()
    if len(fields) != 2 or fields[1].lstrip('*') != filename:
        raise ValueError('Checksum filename/format mismatch')
    if fields[0].lower() != hashlib.sha256(body).hexdigest():
        raise ValueError('Checksum digest mismatch')


def inspect_zip(body: bytes, day: str) -> dict:
    """Report observed schema/quality; the five-minute grid is an explicit check."""
    expected_name = f'BTCUSDT-metrics-{day}.csv'
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        members = archive.infolist()
        if len(members) != 1 or members[0].filename != expected_name:
            raise ValueError('Unexpected ZIP member')
        if members[0].file_size > 5_000_000:
            raise ValueError('ZIP member exceeds probe size limit')
        text = archive.read(members[0]).decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    if not {'create_time', 'symbol'} <= set(columns):
        raise ValueError(f'Unsupported timestamp/symbol schema: {columns}')
    if len(columns) != len(set(columns)):
        raise ValueError('Duplicate column names')
    rows = list(reader)
    if not rows:
        raise ValueError('Empty metrics file')
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Malformed CSV row width')
    timestamps = [datetime.fromisoformat(row['create_time']) for row in rows]
    start = datetime.fromisoformat(day)
    end = start + timedelta(days=1)
    for row, stamp in zip(rows, timestamps):
        if row['symbol'] != 'BTCUSDT':
            raise ValueError('Unexpected symbol')
        if stamp.tzinfo is not None or not start <= stamp < end:
            raise ValueError('Unexpected timestamp day/timezone')
        if (stamp - start).total_seconds() % 300:
            raise ValueError('Timestamp outside five-minute grid')
    unique = set(timestamps)
    null_tokens = {'', 'nan', 'null', 'none', 'na'}
    return {
        'date': day,
        'member': expected_name,
        'columns': columns,
        'rows': len(rows),
        'first_timestamp': min(timestamps).isoformat(),
        'last_timestamp': max(timestamps).isoformat(),
        'timezone_note': 'Raw create_time is naive; UTC semantics require source confirmation.',
        'duplicate_timestamps': len(timestamps) - len(unique),
        'non_increasing_steps': sum(b <= a for a, b in zip(timestamps, timestamps[1:])),
        'missing_5m_slots': 288 - len(unique),
        'null_counts': {key: sum(row[key].strip().lower() in null_tokens for row in rows)
                        for key in columns},
        'last_10_raw_records': text.splitlines()[1:][-10:],
    }


class Offline:
    def get(self, *args, **kwargs):
        raise ValueError('Offline replay requires all raw files and metadata to exist')


def run(session) -> dict:
    results = []
    for day in DAYS:
        filename = f'BTCUSDT-metrics-{day}.zip'
        body = fetch_raw(BASE + filename, OUT / filename, session)
        checksum = fetch_raw(BASE + filename + '.CHECKSUM', OUT / (filename + '.CHECKSUM'), session)
        verify_checksum(body, checksum, filename)
        result = inspect_zip(body, day)
        result['archive_sha256'] = hashlib.sha256(body).hexdigest()
        result['checksum_sha256'] = hashlib.sha256(checksum).hexdigest()
        result['raw_path'] = (OUT / filename).relative_to(ROOT).as_posix()
        results.append(result)
        print(f"{day}: {result['rows']} rows, {result['missing_5m_slots']} missing 5m slots", flush=True)
    return {
        'task_id': 'A-021',
        'status': 'SAMPLE_CONTENT_INSPECTED_NOT_FULL_COVERAGE',
        'raw_versioning_status': 'Check git independently; script does not commit artifacts.',
        'strategy_configurations_evaluated': 0,
        'point_in_time_validity_verified': False,
        'continuous_coverage_verified': False,
        'records': results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    if args.offline:
        report = run(Offline())
    else:
        with requests.Session() as session:
            session.headers['User-Agent'] = 'freqtrade-research/A-021'
            report = run(session)
    # A replay prints the same evidence without modifying any saved artifact.
    output = OUT / 'sample_inspection.json'
    if output.exists():
        if json.loads(output.read_text(encoding='utf-8')) != report:
            raise ValueError('Inspection differs from saved report; refusing overwrite')
    else:
        with output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
