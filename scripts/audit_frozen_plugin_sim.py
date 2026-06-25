#!/usr/bin/env python3
"""Validate offline EXE bundle assets (Configurator — no NST plugin registry)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mirrors NXOS_Configurator_Web_*.spec datas=
BUNDLE_PATHS = (
    "templates",
    "static",
    "data",
    "hardware_profiles.yaml",
    "VERSION",
    "docs",
)


def main() -> int:
    missing: list[str] = []
    for rel in BUNDLE_PATHS:
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
    critical_static = (
        "static/roadmap.js",
        "static/port-map-editor.js",
        "static/option-info.js",
        "static/app.js",
        "static/config-studio.js",
        "static/builder.js",
        "static/interface-planner.js",
        # v5 feature assets — must ship in offline bundle
        "static/vpc-link-planner.js",
        "static/fabric-questionnaire.js",
        "static/topology-view.js",
        "static/wizard-enhancements.js",
        "static/admin-po-map.js",
        "static/styles.css",
        "static/favicon.svg",
        "templates/web/index.html",
        "templates/web/admin.html",
        "templates/nxos_base.j2",
        "data/option_encyclopedia.yaml",
        "data/po_allocation_map.yaml",
    )
    for rel in critical_static:
        if not (ROOT / rel).is_file():
            missing.append(rel)

    print("=== Configurator frozen bundle simulation ===")
    print(f"  root: {ROOT}")
    print(f"  bundle_entries: {len(BUNDLE_PATHS)}")
    print(f"  missing: {len(missing)}")
    for item in missing:
        print(f"    - {item}")

    if missing:
        print("  VERDICT: FAIL — bundle assets missing")
        return 1
    print("  VERDICT: PASS — all bundle assets present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
