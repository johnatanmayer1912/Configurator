#!/usr/bin/env python3
"""Run mandatory QA for on-change (fast) or pre-release (full) triggers.

Usage:
  python scripts/run_mandatory_qa.py --on-change    # after code edits (pre-commit)
  python scripts/run_mandatory_qa.py --pre-release # before VERSION bump
  python scripts/run_mandatory_qa.py --pre-exe     # alias for enterprise_qa_gate.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"FAIL: {label}")
        return False
    print(f"PASS: {label}")
    return True


def run_trigger(trigger: str) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from release_qa_manifest import load_manifest, stages_for_trigger, validate_manifest_files

    manifest_errors = validate_manifest_files()
    if manifest_errors:
        print("MANIFEST VALIDATION: FAIL")
        for err in manifest_errors:
            print(f"  - {err}")
        return 1

    ok = True
    stages = stages_for_trigger(trigger)
    if not stages:
        print(f"No stages configured for trigger: {trigger}")
        return 1

    print(f"QA trigger: {trigger} ({len(stages)} stages) — {load_manifest().get('product')}")

    has_full_suite = False
    pytest_paths: list[str] = []

    for stage in stages:
        sid = stage.get("id", "unknown")
        label = stage.get("label", sid)
        blocker = stage.get("blocker", True)
        stype = stage.get("type")

        if stype == "pytest":
            paths = stage.get("paths") or []
            if any(p.replace("\\", "/") in ("tests/", "tests") for p in paths):
                has_full_suite = True
                continue
            for p in paths:
                if p not in pytest_paths:
                    pytest_paths.append(p)
            continue

        if stype == "script":
            for script in stage.get("command") or []:
                ok &= _run([sys.executable, script], f"{label} ({script})")
                if not ok and blocker:
                    return 1

    if pytest_paths and not has_full_suite:
        ok &= _run(
            [sys.executable, "-m", "pytest", *pytest_paths, "-q", "--tb=short"],
            f"Mandatory pytest ({trigger})",
        )

    if has_full_suite:
        ok &= _run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"], "Full pytest suite")

    print("\n" + "=" * 60)
    if ok:
        print(f"MANDATORY QA ({trigger}): PASS")
        return 0
    print(f"MANDATORY QA ({trigger}): FAIL")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mandatory QA by trigger")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--on-change", action="store_true", help="Fast gate after code edits")
    group.add_argument("--pre-release", action="store_true", help="Before VERSION bump")
    group.add_argument("--pre-exe", action="store_true", help="Before offline exe build")
    args = parser.parse_args()

    if args.on_change:
        return run_trigger("on_change")
    if args.pre_release:
        return run_trigger("pre_release")
    return run_trigger("pre_exe")


if __name__ == "__main__":
    sys.exit(main())
