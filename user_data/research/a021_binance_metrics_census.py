"""Fixed A-021 BTCUSDT archive census; data quality only, never strategy returns."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from functools import partial

import requests

from a021_binance_metrics_probe import (
    BASE, DAYS, OUT, ROOT, Offline, fetch_raw, inspect_zip, verify_checksum,
)

HISTORY = OUT / 'history_20230901_20260901'


def census_days() -> list[str]:
    start, end = date(2023, 9, 1), date(2026, 9, 1)
    return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days)]


def inspect_day(day: str, offline: bool = False) -> dict:
    folder = OUT if day in DAYS else HISTORY
    filename = f'BTCUSDT-metrics-{day}.zip'
    result = {'date': day, 'raw_path': (folder / filename).relative_to(ROOT).as_posix()}
    session = Offline() if offline else requests.Session()
    try:
        body = fetch_raw(BASE + filename, folder / filename, session)
        checksum = fetch_raw(BASE + filename + '.CHECKSUM', folder / (filename + '.CHECKSUM'), session)
        verify_checksum(body, checksum, filename)
        result.update(inspect_zip(body, day))
        result['archive_sha256'] = hashlib.sha256(body).hexdigest()
        result['checksum_sha256'] = hashlib.sha256(checksum).hexdigest()
        result['status'] = 'INSPECTED'
    except (requests.RequestException, ValueError, OSError, EOFError, zipfile.BadZipFile) as exc:
        result.update(status='ERROR', error=f'{type(exc).__name__}: {exc}')
    finally:
        if not offline:
            session.close()
    return result


def summarize(records: list[dict], days: list[str]) -> dict:
    by_day = {row['date']: row for row in records}
    if len(by_day) != len(records) or set(by_day) != set(days):
        raise ValueError('Missing, extra or duplicate day records')
    if days != sorted(set(days)):
        raise ValueError('Expected dates must be ordered and unique')
    if any(date.fromisoformat(b) - date.fromisoformat(a) != timedelta(days=1)
           for a, b in zip(days, days[1:])):
        raise ValueError('Expected dates must be consecutive')
    complete = observed = missing = run = longest = 0
    run_start = longest_start = longest_end = None
    schemas = set()
    incomplete_days = []
    for day in days:
        row = by_day[day]
        inspected = row['status'] == 'INSPECTED'
        if inspected:
            observed += row['rows']
            missing += row['missing_5m_slots']
            schemas.add(tuple(row['columns']))
        else:
            missing += 288
        clean = (inspected and row['rows'] == 288 and row['missing_5m_slots'] == 0
                 and row['duplicate_timestamps'] == 0 and row['non_increasing_steps'] == 0
                 and not any(row['null_counts'].values()))
        if clean:
            complete += 1
            if run == 0:
                run_start = day
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, run_start, day
        else:
            incomplete_days.append(day)
            run = 0
    return {
        'expected_days': len(days),
        'inspected_days': sum(r['status'] == 'INSPECTED' for r in records),
        'complete_days': complete,
        'observed_rows': observed,
        'missing_5m_slots_including_uninspected_days': missing,
        'missing_slot_note': 'Uninspected days count as unavailable to this census, not proven absent at source.',
        'incomplete_days': incomplete_days,
        'longest_complete_run_days': longest,
        'longest_complete_run_start': longest_start,
        'longest_complete_run_end': longest_end,
        'distinct_schemas': [list(s) for s in sorted(schemas)],
        'continuous_coverage_verified': bool(days) and complete == len(days),
        'coverage_note': 'Timestamp-grid/null coverage only; not numeric-unit or economic validity.',
        'point_in_time_validity_verified': False,
        'strategy_configurations_evaluated': 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    days = census_days()
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(partial(inspect_day, offline=args.offline), days):
            records.append(row)
            if len(records) % 50 == 0 or len(records) == len(days):
                print(f"{len(records)}/{len(days)} days inspected; "
                      f"errors={sum(r['status'] == 'ERROR' for r in records)}", flush=True)
    summary = summarize(records, days)
    report = {'task_id': 'A-021', 'summary': summary, 'records': records}
    # Save only a completed census; individual raw downloads survive interruptions.
    output = HISTORY / 'census_inspection.json'
    HISTORY.mkdir(parents=True, exist_ok=True)
    if output.exists():
        if json.loads(output.read_text(encoding='utf-8')) != report:
            raise ValueError('Census differs from saved report; refusing overwrite')
    else:
        with output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
    print(json.dumps(summary, indent=2))
    if records[-1]['status'] == 'INSPECTED':
        print('Last ten raw records of final day:')
        print('\n'.join(records[-1]['last_10_raw_records']))
    if summary['inspected_days'] != len(days):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
