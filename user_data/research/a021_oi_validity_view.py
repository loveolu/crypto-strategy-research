"""Offline OI validity view. No execution-time assumption or strategy evaluation."""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = 'b03e93705'
CENSUS_PATH = ('user_data/research/data/binance_metrics_a021/'
               'history_20230901_20260901/census_inspection.json')
OUTPUT = ROOT / 'user_data/research/data/binance_metrics_a021_derived'
OI_FIELDS = ['sum_open_interest', 'sum_open_interest_value']


def build_oi_view(raw: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp,
                  lookback_bars: int = 288) -> pd.DataFrame:
    if not isinstance(raw.index, pd.DatetimeIndex) or raw.index.tz is not None:
        raise ValueError('Require naive source timestamp labels, not assumed UTC availability')
    if raw.index.has_duplicates:
        raise ValueError('Reject duplicate timestamps, including identical duplicates')
    if raw.index.hasnans or start.tzinfo is not None or end.tzinfo is not None or end <= start:
        raise ValueError('Invalid time interval or missing timestamp')
    if isinstance(lookback_bars, bool) or not isinstance(lookback_bars, int) or lookback_bars < 1:
        raise ValueError('lookback_bars must be a positive integer')
    if not set(OI_FIELDS) <= set(raw.columns):
        raise ValueError('Missing OI fields')
    step = pd.Timedelta(minutes=5)
    if start.value % step.value or end.value % step.value:
        raise ValueError('Range boundaries must be on the five-minute grid')
    grid = pd.date_range(start, end, freq=step, inclusive='left')
    if not raw.index.isin(grid).all():
        raise ValueError('Off-grid or out-of-range source timestamp')
    view = raw.sort_index().reindex(grid).copy()
    view['record_present'] = grid.isin(raw.index)
    numeric = view[OI_FIELDS].apply(pd.to_numeric, errors='raise')
    valid = view['record_present'] & np.isfinite(numeric).all(axis=1) & numeric.gt(0).all(axis=1)
    view['observation_valid'] = valid
    window = lookback_bars + 1
    view['window_valid'] = valid.rolling(window, min_periods=window).sum().eq(window)
    safe_oi = numeric['sum_open_interest'].where(valid)
    view['oi_change'] = (safe_oi / safe_oi.shift(lookback_bars) - 1).where(view['window_valid'])
    return view


def load_committed_oi() -> tuple[pd.DataFrame, str]:
    # Read the immutable census manifest from Git, not a potentially edited working copy.
    census_bytes = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{CENSUS_PATH}'], cwd=ROOT)
    census = json.loads(census_bytes)
    if len(census['records']) != 1096 or any(r['status'] != 'INSPECTED' for r in census['records']):
        raise ValueError('Committed census is incomplete')
    frames = []
    for record in census['records']:
        path = ROOT / record['raw_path']
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != record['archive_sha256']:
            raise ValueError(f'Raw archive hash mismatch: {path}')
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            frame = pd.read_csv(io.BytesIO(archive.read(record['member'])),
                                usecols=['create_time', *OI_FIELDS])
        if len(frame) != record['rows']:
            raise ValueError(f'Row count mismatch: {path}')
        frame['source_archive'] = path.name
        frame['source_row'] = np.arange(len(frame))
        frame.index = pd.DatetimeIndex(pd.to_datetime(frame.pop('create_time')))
        frames.append(frame)
    return pd.concat(frames), hashlib.sha256(census_bytes).hexdigest()


def main() -> None:
    raw, manifest_hash = load_committed_oi()
    view = build_oi_view(raw, pd.Timestamp('2023-09-01'), pd.Timestamp('2026-09-01'))
    report = {
        'task_id': 'A-021',
        'source_commit': SOURCE_COMMIT,
        'source_census_sha256': manifest_hash,
        'lookback_bars': 288,
        'required_consecutive_observations': 289,
        'timestamp_semantics': 'Naive source labels retained; not approved execution/availability times.',
        'expected_grid_rows': len(view),
        'source_rows': len(raw),
        'absent_grid_slots': int((~view['record_present']).sum()),
        'present_invalid_oi_rows': int((view['record_present'] & ~view['observation_valid']).sum()),
        'valid_24h_windows': int(view['window_valid'].sum()),
        'invalid_or_warmup_24h_windows': int((~view['window_valid']).sum()),
        'per_calendar_year': {
            str(year): {'grid_rows': len(group), 'valid_24h_windows': int(group['window_valid'].sum()),
                        'invalid_or_warmup': int((~group['window_valid']).sum())}
            for year, group in view.groupby(view.index.year)},
        'source_values_interpolated_or_filled': False,
        'execution_timing_verified': False,
        'strategy_configurations_evaluated': 0,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    table_path = OUTPUT / 'oi_24h_validity.parquet'
    if table_path.exists():
        pd.testing.assert_frame_equal(pd.read_parquet(table_path), view, check_freq=False)
    else:
        # Exclusive open prevents accidental replacement, including concurrent runs.
        with table_path.open('xb') as stream:
            view.to_parquet(stream, index=True)
    report['derived_parquet_sha256'] = hashlib.sha256(table_path.read_bytes()).hexdigest()
    report_path = OUTPUT / 'eligibility_report.json'
    if report_path.exists():
        if json.loads(report_path.read_text(encoding='utf-8')) != report:
            raise ValueError('Derived report changed; refusing overwrite')
    else:
        with report_path.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
