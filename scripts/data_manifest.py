#!/usr/bin/env python3
"""SHA-256 integrity manifest for everything under user_data/data/.

Why this exists
---------------
Three cycles in this project's history wrote fabricated market data straight into
the feather files and reported results computed on it (T-023, T-025) or reported
a hand-typed number the script never produced (T-019). The manifest turns "the
data is authentic" from a claim an agent makes in prose into a check that either
passes or fails.

It does NOT prove the data came from the exchange — only re-fetching does that
(see `research/strategy_research_notes.md`, "Data provenance and reserved
holdout", and note the OKX `1Dutc` bar-type requirement). What it proves is that
the data has not changed since a human committed the manifest. Combined with git,
that makes every data change an explicit, reviewable, attributable event: to
change data you must rebuild the manifest, and the rebuild shows up in the diff.

Usage
-----
    python scripts/data_manifest.py build      # hash the tree, write the manifest
    python scripts/data_manifest.py verify     # check tree against manifest
    python scripts/data_manifest.py verify --json
    python scripts/data_manifest.py status     # verify, but never exit nonzero

Exit codes: 0 clean, 1 mismatch, 2 manifest missing or unreadable.

After `build`, COMMIT THE MANIFEST. `user_data/*` is gitignored, so it needs
`git add -f user_data/data/MANIFEST.json`. An uncommitted manifest protects
nothing.

Legitimate data updates
-----------------------
A real data top-up changes files, so verify() will fail — that is intended. The
sequence is: update the data, confirm it is genuine (re-fetch and compare), run
`build`, and commit the manifest in the same commit as the data with an
explanation. Do not set the bypass variable to make a failure go away.

Bypass (for bootstrapping only): FREQTRADE_SKIP_DATA_VERIFY=1 disables the
import-time check in validator.py. Any run using it is not evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "user_data" / "data"
MANIFEST_PATH = DATA_DIR / "MANIFEST.json"

#: Never hashed: the manifest itself, and OS/editor droppings that are not data.
EXCLUDE_NAMES = {"MANIFEST.json", ".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIXES = {".tmp", ".lock", ".swp", ".pyc"}
EXCLUDE_DIRS = {"__pycache__", ".ipynb_checkpoints"}

BYPASS_ENV = "FREQTRADE_SKIP_DATA_VERIFY"
MANIFEST_VERSION = 1


class DataIntegrityError(RuntimeError):
    """Raised when the data tree does not match the committed manifest."""


def _included(p: Path) -> bool:
    if not p.is_file():
        return False
    if p.name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    return not any(part in EXCLUDE_DIRS for part in p.parts)


def sha256_file(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def scan(data_dir: Path = DATA_DIR) -> dict[str, dict]:
    """Hash every included file. Keys are POSIX paths relative to data_dir."""
    out: dict[str, dict] = {}
    for p in sorted(data_dir.rglob("*")):
        if _included(p):
            rel = p.relative_to(data_dir).as_posix()
            out[rel] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    return out


def build(data_dir: Path = DATA_DIR, manifest_path: Path = MANIFEST_PATH,
          note: str | None = None) -> dict:
    files = scan(data_dir)
    manifest = {
        "version": MANIFEST_VERSION,
        "algorithm": "sha256",
        "root": data_dir.relative_to(REPO_ROOT).as_posix(),
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_count": len(files),
        "total_bytes": sum(v["bytes"] for v in files.values()),
        "note": note or "",
        "files": files,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    return manifest


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> dict:
    if not manifest_path.exists():
        raise DataIntegrityError(
            f"no data manifest at {manifest_path}. Run "
            f"`python scripts/data_manifest.py build` and commit the result "
            f"(git add -f {manifest_path.relative_to(REPO_ROOT).as_posix()}).")
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"data manifest unreadable: {exc}") from exc


def compare(data_dir: Path = DATA_DIR, manifest_path: Path = MANIFEST_PATH) -> dict:
    """Compare the tree against the manifest. Never raises on mismatch."""
    manifest = load_manifest(manifest_path)
    recorded = manifest.get("files", {})
    actual = scan(data_dir)

    modified, missing, extra = [], [], []
    for rel, rec in sorted(recorded.items()):
        if rel not in actual:
            missing.append(rel)
        elif actual[rel]["sha256"] != rec["sha256"]:
            modified.append({
                "file": rel,
                "recorded_sha256": rec["sha256"][:16],
                "actual_sha256": actual[rel]["sha256"][:16],
                "recorded_bytes": rec.get("bytes"),
                "actual_bytes": actual[rel]["bytes"],
            })
    for rel in sorted(actual):
        if rel not in recorded:
            extra.append(rel)

    return {
        "ok": not (modified or missing or extra),
        "built_utc": manifest.get("built_utc"),
        "checked_count": len(actual),
        "recorded_count": len(recorded),
        "modified": modified,
        "missing": missing,
        "extra": extra,
    }


def verify(data_dir: Path = DATA_DIR, manifest_path: Path = MANIFEST_PATH,
           raise_on_mismatch: bool = True) -> dict:
    """Verify the data tree. Raises DataIntegrityError on mismatch by default.

    Honours FREQTRADE_SKIP_DATA_VERIFY=1, which returns a result marked
    `bypassed` so callers can record that the check did not actually run.
    """
    if os.environ.get(BYPASS_ENV) == "1":
        return {"ok": True, "bypassed": True, "modified": [], "missing": [], "extra": [],
                "checked_count": 0, "recorded_count": 0, "built_utc": None}

    result = compare(data_dir, manifest_path)
    result["bypassed"] = False
    if not result["ok"] and raise_on_mismatch:
        raise DataIntegrityError(format_failure(result))
    return result


def format_failure(r: dict) -> str:
    lines = ["DATA INTEGRITY CHECK FAILED — user_data/data does not match the committed manifest.", ""]
    if r["modified"]:
        lines.append(f"  MODIFIED ({len(r['modified'])}):")
        for m in r["modified"][:20]:
            lines.append(f"    {m['file']}")
            lines.append(f"        sha256 {m['recorded_sha256']}… -> {m['actual_sha256']}…"
                         f"   bytes {m['recorded_bytes']:,} -> {m['actual_bytes']:,}")
        if len(r["modified"]) > 20:
            lines.append(f"    … and {len(r['modified']) - 20} more")
    if r["missing"]:
        lines.append(f"  MISSING ({len(r['missing'])}): " + ", ".join(r["missing"][:20]))
    if r["extra"]:
        lines.append(f"  UNTRACKED ({len(r['extra'])}): " + ", ".join(r["extra"][:20]))
    lines += [
        "",
        "  Every result computed against this tree is unverifiable until resolved.",
        "",
        "  If this change is legitimate: confirm the data is genuine (re-fetch and compare —",
        "  note OKX daily candles need bar=1Dutc), then run",
        "      python scripts/data_manifest.py build",
        "  and commit the manifest together with the data, explaining the change.",
        "",
        f"  Do NOT set {BYPASS_ENV}=1 to silence this. A run with the check bypassed is not evidence.",
    ]
    return "\n".join(lines)


def _cmd_build(args) -> int:
    m = build(note=args.note or "")
    print(f"manifest written: {MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()}")
    print(f"  files hashed : {m['file_count']}")
    print(f"  total bytes  : {m['total_bytes']:,}")
    print(f"  built (UTC)  : {m['built_utc']}")
    print()
    print("COMMIT IT — user_data/* is gitignored:")
    print(f"  git add -f {MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()}")
    return 0


def _cmd_verify(args) -> int:
    try:
        r = compare()
    except DataIntegrityError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(r, indent=2))
    elif r["ok"]:
        print(f"OK: {r['checked_count']} files match the manifest "
              f"(built {r['built_utc']}).")
    else:
        print(format_failure(r))
    if args.never_fail:
        return 0
    return 0 if r["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="hash the data tree and write the manifest")
    b.add_argument("--note", default="", help="reason for the rebuild, stored in the manifest")
    b.set_defaults(func=_cmd_build)

    v = sub.add_parser("verify", help="check the data tree against the manifest")
    v.add_argument("--json", action="store_true")
    v.add_argument("--never-fail", action="store_true", help=argparse.SUPPRESS)
    v.set_defaults(func=_cmd_verify)

    s = sub.add_parser("status", help="like verify, but always exits 0")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=_cmd_verify, never_fail=True)

    args = ap.parse_args(argv)
    if not hasattr(args, "never_fail"):
        args.never_fail = False
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
