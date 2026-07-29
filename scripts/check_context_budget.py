#!/usr/bin/env python3
"""Enforce the Research Director's mandatory context budget.

The Director loads a fixed set of files before selecting a hypothesis. Prior to
2026-07-28 that set was ~360 KB (~90k tokens), rising to ~680 KB if the two topic
files the prompt named as examples were opened. This script makes the budget a
hard, checkable constraint instead of a hope.

Exit codes:
    0  mandatory set within budget
    1  over budget
    2  a mandatory file or marker is missing (treated as a failure: an
       unmeasurable budget is not a satisfied one)

Usage:
    python scripts/check_context_budget.py            # check, print breakdown
    python scripts/check_context_budget.py --budget-kb 32
    python scripts/check_context_budget.py --json

The MANDATORY list below must stay in sync with the "Research Director — context
loading" section of PROJECT_OPERATOR_MANUAL.md, which is the human-readable
authority. If you change one, change the other.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BUDGET_KB = 40
BYTES_PER_TOKEN_APPROX = 4  # rough English/markdown approximation, not a tokenizer run

MARKER_BEGIN = "<!-- DIRECTOR-MANDATORY-BEGIN -->"
MARKER_END = "<!-- DIRECTOR-MANDATORY-END -->"

#: Per-file cap for review briefs (PROJECT_OPERATOR_MANUAL.md, "Independent
#: Reviewer output standard"). The latest brief is mandatory Director context, so
#: an oversized brief taxes every future hypothesis selection.
REVIEW_BRIEF_CAP = 4 * 1024
REVIEW_BRIEFS_DIR = "research/review_briefs"

#: (path, region) where region is None for the whole file, "markers" to count only
#: the bytes between MARKER_BEGIN and MARKER_END, or "latest-brief" to resolve the
#: newest file in REVIEW_BRIEFS_DIR at check time.
MANDATORY: list[tuple[str, str | None]] = [
    ("PROJECT_OPERATOR_MANUAL.md", "markers"),
    ("research/research_index.md", None),
    ("knowledge_base/hypothesis_bank.md", "markers"),
    ("research/STANDING_DIRECTIVES.md", None),
    (REVIEW_BRIEFS_DIR, "latest-brief"),
]

#: Files the Director may open per-cycle but which must NOT be in the mandatory set.
#: Reported for context so the size that was moved off-budget stays visible.
ON_DEMAND = [
    "knowledge_base/master_index.md",
    "knowledge_base/archive/closed_families.md",
    "research/archive/index_narrative_pre_2026-07-28.md",
    "research/current_champion.md",
]


def latest_brief() -> Path | None:
    """Newest file in the review-briefs directory, by mtime."""
    d = REPO_ROOT / REVIEW_BRIEFS_DIR
    if not d.is_dir():
        return None
    briefs = [p for p in d.glob("*.md") if p.is_file()]
    return max(briefs, key=lambda p: p.stat().st_mtime) if briefs else None


def measure(rel: str, region: str | None) -> tuple[int, str | None]:
    """Return (bytes, error). Bytes are UTF-8 encoded length of the counted region."""
    if region == "latest-brief":
        fp = latest_brief()
        if fp is None:
            return 0, f"no review brief found in {rel}"
        return len(fp.read_text(encoding="utf-8").encode("utf-8")), None
    fp = REPO_ROOT / rel
    if not fp.exists():
        return 0, f"missing file: {rel}"
    text = fp.read_text(encoding="utf-8")
    if region is None:
        return len(text.encode("utf-8")), None
    if region == "markers":
        if MARKER_BEGIN not in text:
            return 0, f"{rel}: {MARKER_BEGIN} not found"
        if MARKER_END not in text:
            return 0, f"{rel}: {MARKER_END} not found"
        start = text.index(MARKER_BEGIN)
        end = text.index(MARKER_END)
        if end < start:
            return 0, f"{rel}: END marker precedes BEGIN marker"
        return len(text[start:end].encode("utf-8")), None
    return 0, f"{rel}: unknown region spec {region!r}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budget-kb", type=float, default=DEFAULT_BUDGET_KB,
                    help=f"budget in KB (default {DEFAULT_BUDGET_KB})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    budget = int(args.budget_kb * 1024)
    rows, errors, total = [], [], 0

    warnings: list[str] = []
    for rel, region in MANDATORY:
        n, err = measure(rel, region)
        if err:
            errors.append(err)
        total += n
        if region == "latest-brief":
            lb = latest_brief()
            label = f"{REVIEW_BRIEFS_DIR}/{lb.name}" if lb else rel
            desc = f"latest brief (cap {REVIEW_BRIEF_CAP:,} B)"
            if n > REVIEW_BRIEF_CAP:
                warnings.append(
                    f"{label} is {n:,} B, {n - REVIEW_BRIEF_CAP:,} B over the "
                    f"{REVIEW_BRIEF_CAP:,} B review-brief cap "
                    f"(PROJECT_OPERATOR_MANUAL.md, 'Independent Reviewer output standard')")
        else:
            label = rel
            desc = "marked region" if region == "markers" else "whole file"
        rows.append({"file": label, "region": desc, "bytes": n})

    on_demand_rows = []
    for rel in ON_DEMAND:
        fp = REPO_ROOT / rel
        on_demand_rows.append({"file": rel,
                               "bytes": fp.stat().st_size if fp.exists() else 0,
                               "exists": fp.exists()})

    over = total > budget
    result = {
        "budget_bytes": budget,
        "total_bytes": total,
        "over_budget": over,
        "headroom_bytes": budget - total,
        "approx_tokens": total // BYTES_PER_TOKEN_APPROX,
        "mandatory": rows,
        "on_demand": on_demand_rows,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Research Director mandatory context budget")
        print("=" * 62)
        for r in sorted(rows, key=lambda x: -x["bytes"]):
            pct = 100.0 * r["bytes"] / budget if budget else 0
            print(f"  {r['bytes']:8,d} B  {pct:5.1f}% of budget  {r['file']}  [{r['region']}]")
        print("-" * 62)
        print(f"  {total:8,d} B  {100.0*total/budget:5.1f}% of budget  TOTAL"
              f"  (~{total // BYTES_PER_TOKEN_APPROX:,} tokens)")
        print(f"  budget {budget:,} B ({args.budget_kb:g} KB), "
              f"headroom {budget - total:,} B")
        print()
        print("Off-budget (on-demand only — must NOT be loaded every cycle):")
        for r in on_demand_rows:
            flag = "" if r["exists"] else "   (missing)"
            print(f"  {r['bytes']:8,d} B  {r['file']}{flag}")
        if warnings:
            print()
            print("WARNINGS:")
            for w in warnings:
                print(f"  ! {w}")
        if errors:
            print()
            print("ERRORS:")
            for e in errors:
                print(f"  ! {e}")

    if errors:
        if not args.json:
            print("\nFAIL: mandatory set could not be fully measured.")
        return 2
    if over:
        if not args.json:
            print(f"\nFAIL: mandatory context is {total - budget:,} B over the "
                  f"{args.budget_kb:g} KB budget.")
            print("Fix by compacting a mandatory file or demoting one to on-demand in")
            print("PROJECT_OPERATOR_MANUAL.md — not by raising the budget.")
        return 1
    if not args.json:
        print("\nOK: mandatory context within budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
