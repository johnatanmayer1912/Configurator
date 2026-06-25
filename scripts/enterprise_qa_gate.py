#!/usr/bin/env python3
"""Enterprise QA gate — manifest-driven, run before offline exe build.

See data/release_qa_manifest.yaml and docs/06-quality-assurance/MANDATORY_RELEASE_TESTS.md
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], label: str) -> bool:
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(f"FAIL: {label}")
        return False
    print(f"PASS: {label}")
    return True


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from release_qa_manifest import load_manifest, stages_for_trigger, validate_manifest_files

    manifest_errors = validate_manifest_files()
    if manifest_errors:
        print("MANIFEST VALIDATION: FAIL")
        for err in manifest_errors:
            print(f"  - {err}")
        return 1

    manifest = load_manifest()
    stages = stages_for_trigger("pre_exe")
    print(f"Enterprise QA gate — {manifest.get('product')} (pre_exe, {len(stages)} stages)")

    ok = True
    for stage in stages:
        sid = stage.get("id", "unknown")
        label = stage.get("label", sid)
        blocker = stage.get("blocker", True)
        stype = stage.get("type")
        prefix = "RELEASE BLOCKER" if blocker else "CHECK"

        if stype == "pytest":
            paths = stage.get("paths") or []
            for p in paths:
                step_label = f"{prefix}: {label} ({p})"
                ok &= run([sys.executable, "-m", "pytest", p, "-q", "--tb=short"], step_label)
                if not ok and blocker:
                    print("\n" + "=" * 60)
                    print(f"ENTERPRISE QA GATE: FAIL at stage {sid}")
                    return 1
        elif stype == "script":
            for script in stage.get("command") or []:
                step_label = f"{prefix}: {label} ({script})"
                ok &= run([sys.executable, script], step_label)
                if not ok and blocker:
                    print("\n" + "=" * 60)
                    print(f"ENTERPRISE QA GATE: FAIL at stage {sid}")
                    return 1

    print("\n" + "=" * 60)
    if ok:
        print("ENTERPRISE QA GATE: PASS")
        return 0
    print("ENTERPRISE QA GATE: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
