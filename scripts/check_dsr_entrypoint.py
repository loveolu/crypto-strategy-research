#!/usr/bin/env python3
"""Fail if research code imports freqtrade_dsr directly.

`validator.deflated_sharpe()` is the only sanctioned entry point for the Deflated
Sharpe Ratio. It reads research/trial_sharpe_ledger.csv, supplies the real
cross-trial variance when the ledger holds enough rows, and attaches
PROXY_DSR_WARNING when it does not.

Calling `freqtrade_dsr.deflated_sharpe_ratio()` directly bypasses all of that and
silently takes `trial_sharpe_var=None`, which falls back to the Lo (2002)
estimator proxy. That proxy scales as ~1/(n_obs-1), making the selection hurdle a
function of TRADE FREQUENCY rather than search intensity: at n_trials=30 it is
0.2174 at 92 observations and 0.0207 at 10,000. Every DSR in this project's
history was computed that way, and nothing announced it.

Exit codes:
    0  clean
    1  a non-exempt file imports freqtrade_dsr directly
    2  the research directory is missing

Usage:
    python scripts/check_dsr_entrypoint.py
    python scripts/check_dsr_entrypoint.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = REPO_ROOT / "user_data" / "research"

#: The sanctioned wrapper. It is SUPPOSED to import freqtrade_dsr.
WRAPPER = "validator.py"

#: Frozen reproduction scripts (ARCHIVE_COST_NOTE.md rule 1). They predate the
#: wrapper and must keep reproducing their archived numbers, proxy hurdle and all.
#: This list is CLOSED — it is not a place to add new files.
FROZEN_EXEMPT = re.compile(r"^phase\d+[a-z0-9_]*\.py$")

PATTERN = re.compile(
    r"^\s*(?:from\s+freqtrade_dsr\s+import|import\s+freqtrade_dsr)\b"
    r"|^\s*from\s+freqtrade_dsr\b",
    re.MULTILINE)

#: Bare-name imports of the underlying functions, e.g. via sys.path manipulation.
BARE = re.compile(
    r"^\s*from\s+\S*freqtrade_dsr\S*\s+import\s+.*"
    r"(deflated_sharpe_ratio|evaluate_freqtrade|expected_max_sharpe)",
    re.MULTILINE)


def scan() -> tuple[list[dict], list[dict]]:
    """Return (violations, exempt_hits)."""
    violations, exempt = [], []
    for fp in sorted(RESEARCH_DIR.rglob("*.py")):
        rel = fp.relative_to(REPO_ROOT).as_posix()
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = []
        for m in list(PATTERN.finditer(text)) + list(BARE.finditer(text)):
            line_no = text[:m.start()].count("\n") + 1
            hits.append({"line": line_no, "text": text.splitlines()[line_no - 1].strip()})
        if not hits:
            continue
        rec = {"file": rel, "hits": sorted(hits, key=lambda h: h["line"])}
        if fp.name == WRAPPER or FROZEN_EXEMPT.match(fp.name):
            exempt.append(rec)
        else:
            violations.append(rec)
    return violations, exempt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not RESEARCH_DIR.is_dir():
        print(f"FAIL: {RESEARCH_DIR} does not exist", file=sys.stderr)
        return 2

    violations, exempt = scan()

    if args.json:
        print(json.dumps({"violations": violations, "exempt": exempt}, indent=2))
    else:
        print("DSR entry-point check")
        print("=" * 62)
        print(f"  sanctioned wrapper : user_data/research/{WRAPPER}")
        n_frozen = sum(1 for e in exempt if not e["file"].endswith(WRAPPER))
        print(f"  frozen exempt      : {n_frozen} phase*.py script(s)")
        print(f"  (validator.py loads freqtrade_dsr via importlib, so it never matches"
              f" the import patterns; it is the wrapper by design.)")
        for e in exempt:
            if not e["file"].endswith(WRAPPER):
                print(f"      exempt  {e['file']}  (line {e['hits'][0]['line']})")
        print()
        if violations:
            print(f"  VIOLATIONS: {len(violations)}")
            for v in violations:
                for h in v["hits"]:
                    print(f"      {v['file']}:{h['line']}  {h['text']}")
            print()
            print("  Use validator.deflated_sharpe(returns, n_trials) instead. Importing")
            print("  freqtrade_dsr directly takes trial_sharpe_var=None silently, which")
            print("  makes the DSR hurdle a function of trade frequency rather than of")
            print("  search intensity, and emits no warning.")
            print()
            print("  The frozen exemption covers phase*.py ONLY and is closed. A new")
            print("  script is not frozen and does not qualify.")
        else:
            print("  VIOLATIONS: 0")

    if violations:
        if not args.json:
            print("\nFAIL")
        return 1
    if not args.json:
        print("\nOK: no research file imports freqtrade_dsr directly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
