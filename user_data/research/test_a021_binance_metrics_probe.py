"""Synthetic fixtures exercise preservation and integrity, never estimate market returns."""
import hashlib
import importlib
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


def module():
    spec = importlib.util.find_spec('a021_binance_metrics_probe')
    assert spec is not None, 'A021 probe implementation is missing'
    return importlib.import_module('a021_binance_metrics_probe')


class Response:
    status_code = 200
    headers = {'Last-Modified': 'example'}
    content = b'raw fixture'


class Session:
    def get(self, url, **kwargs):
        return Response()


class Offline:
    def get(self, *args, **kwargs):
        raise AssertionError('Unexpected network access')


def archive(text, name='BTCUSDT-metrics-2025-01-01.csv'):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as out:
        out.writestr(name, text)
    return stream.getvalue()


def test_fetch_preserves_raw_and_reuses_cache_without_network(tmp_path):
    path = tmp_path / 'sample.zip'
    m = module()
    assert m.fetch_raw('https://example.test/sample.zip', path, Session()) == b'raw fixture'
    assert path.read_bytes() == b'raw fixture'
    metadata = json.loads(path.with_name(path.name + '.meta.json').read_text())
    assert metadata['sha256'] == hashlib.sha256(b'raw fixture').hexdigest()
    assert m.fetch_raw('https://example.test/sample.zip', path, Offline()) == b'raw fixture'


def test_modified_cache_is_rejected_without_overwrite(tmp_path):
    m = module()
    path = tmp_path / 'sample.zip'
    m.fetch_raw('https://example.test/sample.zip', path, Session())
    path.write_bytes(b'damaged')
    with pytest.raises(ValueError, match='hash'):
        m.fetch_raw('https://example.test/sample.zip', path, Offline())
    assert path.read_bytes() == b'damaged'


def test_orphan_cache_is_not_refetched(tmp_path):
    path = tmp_path / 'sample.zip'
    path.write_bytes(b'preserve me')
    with pytest.raises(ValueError, match='metadata'):
        module().fetch_raw('https://example.test/sample.zip', path, Offline())
    assert path.read_bytes() == b'preserve me'


def test_http_error_body_is_preserved_but_not_accepted(tmp_path):
    class Failed(Session):
        def get(self, *args, **kwargs):
            response = Response()
            response.status_code = 404
            response.content = b'not found'
            return response
    path = tmp_path / 'missing.zip'
    with pytest.raises(ValueError, match='HTTP 404'):
        module().fetch_raw('https://example.test/missing.zip', path, Failed())
    assert path.read_bytes() == b'not found'


def test_checksum_requires_digest_and_exact_filename():
    m = module()
    digest = hashlib.sha256(b'abc').hexdigest()
    m.verify_checksum(b'abc', (digest + '  sample.zip\n').encode(), 'sample.zip')
    for checksum in [digest + '  other.zip', '0' * 64 + '  sample.zip']:
        with pytest.raises(ValueError):
            m.verify_checksum(b'abc', checksum.encode(), 'sample.zip')


def test_inspection_reports_gaps_duplicates_nulls_and_raw_tail():
    text = ('create_time,symbol,sum_open_interest\n'
            '2025-01-01 00:00:00,BTCUSDT,10\n'
            '2025-01-01 00:10:00,BTCUSDT,\n'
            '2025-01-01 00:10:00,BTCUSDT,12\n')
    result = module().inspect_zip(archive(text), '2025-01-01')
    assert result['rows'] == 3
    assert result['duplicate_timestamps'] == 1
    assert result['missing_5m_slots'] == 286
    assert result['null_counts']['sum_open_interest'] == 1
    assert result['last_10_raw_records'] == text.splitlines()[1:]


@pytest.mark.parametrize('text', [
    'create_time,symbol\n2025-01-01 00:00:00,ETHUSDT\n',
    'create_time,symbol\n2025-01-02 00:00:00,BTCUSDT\n',
    'create_time,symbol\n2025-01-01 00:01:00,BTCUSDT\n',
    'wrong,symbol\n2025-01-01 00:00:00,BTCUSDT\n',
])
def test_inspection_rejects_wrong_symbol_day_grid_or_schema(text):
    with pytest.raises(ValueError):
        module().inspect_zip(archive(text), '2025-01-01')


def test_zip_member_name_is_validated_without_extraction():
    with pytest.raises(ValueError, match='member'):
        module().inspect_zip(archive('x', '../escape.csv'), '2025-01-01')
