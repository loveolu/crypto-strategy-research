"""Coverage tests use synthetic day summaries, not fabricated market observations."""
import hashlib
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


def module():
    assert importlib.util.find_spec('a021_binance_metrics_census') is not None, 'Census missing'
    return importlib.import_module('a021_binance_metrics_census')


def test_fixed_window_includes_leap_day_and_excludes_end():
    days = module().census_days()
    assert len(days) == 1096
    assert days[0] == '2023-09-01' and days[-1] == '2026-08-31'
    assert '2024-02-29' in days and '2026-09-01' not in days
    assert days == sorted(set(days))


def good(day):
    return {'date': day, 'status': 'INSPECTED', 'rows': 288,
            'missing_5m_slots': 0, 'duplicate_timestamps': 0,
            'non_increasing_steps': 0, 'null_counts': {'sum_open_interest': 0},
            'columns': ['create_time', 'symbol', 'sum_open_interest']}


def test_missing_or_dirty_days_break_complete_run():
    days = ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04']
    rows = [good(d) for d in days]
    rows[1] = {'date': days[1], 'status': 'ERROR', 'error': 'HTTP 404'}
    report = module().summarize(rows, days)
    assert report['complete_days'] == 3
    assert report['longest_complete_run_days'] == 2
    assert report['longest_complete_run_start'] == '2025-01-03'
    assert report['missing_5m_slots_including_uninspected_days'] == 288
    assert report['observed_rows'] == 864
    assert report['continuous_coverage_verified'] is False
    rows[2]['null_counts']['sum_open_interest'] = 1
    assert module().summarize(rows, days)['longest_complete_run_days'] == 1


def test_summary_refuses_dropped_or_duplicate_day_records():
    for records in [[], [good('2025-01-01'), good('2025-01-01')]]:
        with pytest.raises(ValueError):
            module().summarize(records, ['2025-01-01'])


def test_all_days_complete_is_not_point_in_time_verification():
    days = ['2025-01-01', '2025-01-02']
    report = module().summarize([good(d) for d in days], days)
    assert report['continuous_coverage_verified'] is True
    assert report['point_in_time_validity_verified'] is False
    assert report['strategy_configurations_evaluated'] == 0


def test_daily_fetch_rejects_bad_checksum_and_preserves_failure(monkeypatch):
    m = module()
    # Only replace HTTP/cache I/O. The real day worker must validate its checksum.
    def fetch(url, path, session):
        return b'0' * 64 + b'  wrong.zip' if url.endswith('CHECKSUM') else b'bad zip'
    monkeypatch.setattr(m, 'fetch_raw', fetch)
    result = m.inspect_day('2025-01-01', offline=True)
    assert result['status'] == 'ERROR'
    assert 'Checksum' in result['error']


def test_corrupt_zip_is_a_reported_day_error_not_an_aborted_census(monkeypatch):
    m = module()
    checksum = (hashlib.sha256(b'bad zip').hexdigest()
                + '  BTCUSDT-metrics-2025-01-01.zip').encode()
    monkeypatch.setattr(m, 'fetch_raw', lambda url, path, session:
                        checksum if url.endswith('CHECKSUM') else b'bad zip')
    result = m.inspect_day('2025-01-01', offline=True)
    assert result['status'] == 'ERROR'
    assert 'BadZipFile' in result['error']
