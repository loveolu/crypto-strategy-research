"""Synthetic validity fixtures are not exchange data or trading evidence."""
import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


def module():
    assert importlib.util.find_spec('a021_oi_validity_view') is not None, 'OI view missing'
    return importlib.import_module('a021_oi_validity_view')


def fixture():
    return pd.DataFrame({'sum_open_interest': [10., 12., 15., 18., 20., 24.],
                         'sum_open_interest_value': [100.] * 6},
                        index=pd.date_range('2025-01-01', periods=6, freq='5min'))


def build(frame):
    return module().build_oi_view(frame, pd.Timestamp('2025-01-01'),
                                  pd.Timestamp('2025-01-01 00:30'), lookback_bars=2)


def test_valid_change_requires_full_warmup_and_preserves_values():
    raw = fixture()
    view = build(raw)
    assert view['window_valid'].tolist() == [False, False, True, True, True, True]
    assert view['oi_change'].iloc[2] == pytest.approx(.5)
    assert view['oi_change'].iloc[:2].isna().all()
    pd.testing.assert_series_equal(view['sum_open_interest'], raw['sum_open_interest'])


@pytest.mark.parametrize('bad', [0., -1., np.nan, np.inf, -np.inf])
def test_bad_interior_or_endpoint_blocks_until_full_window_recovers(bad):
    raw = fixture()
    raw.iloc[2, 0] = bad
    view = build(raw)
    assert view['window_valid'].tolist() == [False, False, False, False, False, True]
    assert view['oi_change'].iloc[:5].isna().all()
    assert view['oi_change'].iloc[5] == pytest.approx(24 / 18 - 1)


def test_zero_oi_value_blocks_even_when_oi_units_are_positive():
    raw = fixture()
    raw.iloc[2, 1] = 0
    assert build(raw)['window_valid'].tolist() == [False, False, False, False, False, True]


def test_missing_timestamp_stays_nan_and_blocks_cross_gap_change():
    view = build(fixture().drop(pd.Timestamp('2025-01-01 00:10')))
    assert len(view) == 6
    assert view['record_present'].tolist() == [True, True, False, True, True, True]
    assert pd.isna(view['sum_open_interest'].iloc[2])
    assert view['window_valid'].tolist() == [False, False, False, False, False, True]


def test_sorting_changes_no_raw_values_or_derived_results():
    raw = fixture()
    reversed_raw = raw.iloc[::-1].copy()
    pd.testing.assert_frame_equal(build(raw), build(reversed_raw))
    pd.testing.assert_frame_equal(reversed_raw, raw.iloc[::-1])


def test_future_changes_do_not_change_prior_view():
    raw = fixture()
    modified = raw.copy()
    modified.iloc[4:] = 0
    pd.testing.assert_frame_equal(build(raw).iloc[:4], build(modified).iloc[:4])


def test_duplicate_timestamps_are_rejected_not_deduplicated():
    raw = fixture()
    with pytest.raises(ValueError, match='duplicate'):
        build(pd.concat([raw, raw.iloc[:1]]))


def test_off_grid_out_of_range_or_aware_labels_are_rejected():
    for shift in [pd.Timedelta(minutes=1), pd.Timedelta(minutes=-5)]:
        raw = fixture()
        raw.index += shift
        with pytest.raises(ValueError):
            build(raw)
    raw = fixture().tz_localize('UTC')
    with pytest.raises(ValueError):
        build(raw)


def test_entirely_missing_source_does_not_manufacture_measurements():
    view = build(fixture().iloc[:0])
    assert len(view) == 6
    assert not view['record_present'].any()
    assert view['sum_open_interest'].isna().all()
    assert view['oi_change'].isna().all()
