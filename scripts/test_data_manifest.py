#!/usr/bin/env python3
"""Regression tests for the data integrity gate (scripts/data_manifest.py).

Runs standalone or under pytest:

    python scripts/test_data_manifest.py
    pytest scripts/test_data_manifest.py -q

Every test builds its own throwaway data tree in a temp directory. Nothing here
touches user_data/data/ or the committed manifest.

The conditions covered are the ones that actually happened in this project's
history, plus the ones that would let them recur:

  clean tree                -> passes
  MODIFIED file             -> fails (T-023 / T-025: fabricated bars written into feathers)
  MISSING file              -> fails (data silently dropped)
  UNTRACKED file            -> fails (fabricated file added alongside real ones)
  missing manifest          -> fails closed, never silently passes
  unreadable manifest       -> fails closed
  bypass env var            -> passes but is flagged, never silent
  excluded names            -> manifest does not hash itself
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "dm_under_test", Path(__file__).resolve().parent / "data_manifest.py")
dm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dm)


class Tree:
    """A throwaway data tree with its own manifest."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="dm_test_"))
        self.data = self.root / "data"
        (self.data / "okx" / "futures").mkdir(parents=True)
        self.write("okx/BTC_USDT-1d.feather", b"\x00BTC-daily-bars\x00" * 64)
        self.write("okx/ETH_USDT-1d.feather", b"\x00ETH-daily-bars\x00" * 64)
        self.write("okx/futures/BTC_USDT_USDT-1h-funding_rate.feather", b"funding" * 32)
        self.write("voo_daily.csv", b"date,close\n2020-01-01,300\n")
        self.manifest = self.data / "MANIFEST.json"

    def write(self, rel: str, blob: bytes):
        p = self.data / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(blob)
        return p

    def build(self, note=""):
        return dm.build(self.data, self.manifest, note=note)

    def compare(self):
        return dm.compare(self.data, self.manifest)

    def verify(self, raise_on_mismatch=True):
        return dm.verify(self.data, self.manifest, raise_on_mismatch=raise_on_mismatch)

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def _tree():
    t = Tree()
    t.build()
    return t


def test_clean_tree_passes():
    t = _tree()
    try:
        r = t.compare()
        assert r["ok"], r
        assert r["checked_count"] == 4
        assert not r["modified"] and not r["missing"] and not r["extra"]
        assert t.verify()["ok"]
    finally:
        t.close()


def test_modified_file_fails():
    """T-023 / T-025 failure mode: bars fabricated into an existing feather."""
    t = _tree()
    try:
        p = t.data / "okx" / "BTC_USDT-1d.feather"
        p.write_bytes(p.read_bytes() + b"\x00FABRICATED-BAR\x00")
        r = t.compare()
        assert not r["ok"]
        assert len(r["modified"]) == 1
        assert r["modified"][0]["file"] == "okx/BTC_USDT-1d.feather"
        assert r["modified"][0]["recorded_sha256"] != r["modified"][0]["actual_sha256"]
        assert not r["missing"] and not r["extra"]
        try:
            t.verify()
            raise AssertionError("verify() should have raised on a modified file")
        except dm.DataIntegrityError as exc:
            assert "MODIFIED" in str(exc)
    finally:
        t.close()


def test_missing_file_fails():
    t = _tree()
    try:
        (t.data / "okx" / "ETH_USDT-1d.feather").unlink()
        r = t.compare()
        assert not r["ok"]
        assert r["missing"] == ["okx/ETH_USDT-1d.feather"]
        try:
            t.verify()
            raise AssertionError("verify() should have raised on a missing file")
        except dm.DataIntegrityError as exc:
            assert "MISSING" in str(exc)
    finally:
        t.close()


def test_untracked_file_fails():
    """A file present on disk but ABSENT from the manifest must fail.

    Without this, fabricated data could be introduced as a NEW file rather than
    an edit to an existing one, and the gate would pass.
    """
    t = _tree()
    try:
        t.write("okx/FAKE_USDT-1d.feather", b"entirely fabricated series")
        r = t.compare()
        assert not r["ok"], "untracked file must fail verification"
        assert r["extra"] == ["okx/FAKE_USDT-1d.feather"]
        assert not r["modified"] and not r["missing"]
        try:
            t.verify()
            raise AssertionError("verify() should have raised on an untracked file")
        except dm.DataIntegrityError as exc:
            assert "UNTRACKED" in str(exc), str(exc)
    finally:
        t.close()


def test_untracked_in_new_subdirectory_fails():
    """Same, but hidden one level deeper than any recorded file."""
    t = _tree()
    try:
        t.write("okx/5m/BTC_USDT-5m.feather", b"sub-hourly fabrication")
        r = t.compare()
        assert not r["ok"]
        assert r["extra"] == ["okx/5m/BTC_USDT-5m.feather"]
    finally:
        t.close()


def test_missing_manifest_fails_closed():
    t = _tree()
    try:
        t.manifest.unlink()
        for fn in (t.compare, t.verify):
            try:
                fn()
                raise AssertionError(f"{fn.__name__}() must fail closed without a manifest")
            except dm.DataIntegrityError as exc:
                assert "no data manifest" in str(exc)
    finally:
        t.close()


def test_unreadable_manifest_fails_closed():
    t = _tree()
    try:
        t.manifest.write_text("{ this is not json", encoding="utf-8")
        try:
            t.compare()
            raise AssertionError("must fail closed on an unreadable manifest")
        except dm.DataIntegrityError as exc:
            assert "unreadable" in str(exc)
    finally:
        t.close()


def test_bypass_passes_but_is_flagged():
    t = _tree()
    os.environ[dm.BYPASS_ENV] = "1"
    try:
        (t.data / "okx" / "BTC_USDT-1d.feather").write_bytes(b"tampered")
        r = t.verify()
        assert r["ok"] and r["bypassed"], "bypass must not raise, but must be marked"
    finally:
        os.environ.pop(dm.BYPASS_ENV, None)
        t.close()


def test_bypass_absent_by_default():
    t = _tree()
    try:
        assert dm.BYPASS_ENV not in os.environ or os.environ[dm.BYPASS_ENV] != "1"
        assert t.verify()["bypassed"] is False
    finally:
        t.close()


def test_manifest_does_not_hash_itself():
    t = _tree()
    try:
        recorded = json.loads(t.manifest.read_text(encoding="utf-8"))["files"]
        assert "MANIFEST.json" not in recorded
        assert t.compare()["ok"], "a rebuilt manifest must not invalidate itself"
    finally:
        t.close()


def test_rebuild_after_legitimate_change_clears_the_failure():
    t = _tree()
    try:
        p = t.data / "okx" / "BTC_USDT-1d.feather"
        p.write_bytes(p.read_bytes() + b"\x00genuine-new-bar\x00")
        assert not t.compare()["ok"]
        t.build(note="legitimate top-up, verified against exchange")
        r = t.compare()
        assert r["ok"]
        assert json.loads(t.manifest.read_text(encoding="utf-8"))["note"].startswith("legitimate")
    finally:
        t.close()


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main() -> int:
    failed = []
    for fn in TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001 - a test harness reports everything
            failed.append((fn.__name__, exc))
            print(f"  FAIL  {fn.__name__}: {type(exc).__name__}: {exc}")
    print()
    print(f"{len(TESTS) - len(failed)}/{len(TESTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
