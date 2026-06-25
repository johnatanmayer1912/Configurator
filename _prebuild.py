#!/usr/bin/env python3
"""Pre-build validation for NX-OS Configuration Authority releases."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_DIRS = ("templates", "static", "data", "tests")
REQUIRED_FILES = (
    "VERSION",
    "hardware_profiles.yaml",
    "web_launcher.py",
    "templates/nxos_base.j2",
    "templates/web/index.html",
    "static/roadmap.js",
    "static/option-info.js",
    "data/option_encyclopedia.yaml",
    "data/scenario_templates.yaml",
    "data/config_matrix.yaml",
)
PYTHON_PACKAGES = ("core", "api", "models", "utils")


def check_paths() -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_DIRS:
        if not (ROOT / name).is_dir():
            errors.append(f"Missing directory: {name}")
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"Missing file: {rel}")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        errors.append("VERSION file is empty")
    return errors


def check_python_syntax() -> list[str]:
    errors: list[str] = []
    for pkg in PYTHON_PACKAGES:
        base = ROOT / pkg
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"Syntax error in {path.relative_to(ROOT)}: {exc}")
    for script in ("web_launcher.py", "_prebuild.py"):
        path = ROOT / script
        if path.is_file():
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"Syntax error in {script}: {exc}")
    return errors


def check_imports() -> list[str]:
    errors: list[str] = []
    try:
        from core.scenario_engine import ScenarioEngine  # noqa: F401
        from core.engine import ConfigEngine  # noqa: F401
        from core.catalog_loader import CatalogLoader  # noqa: F401
    except Exception as exc:
        errors.append(f"Import smoke failed: {exc}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_paths())
    errors.extend(check_python_syntax())
    errors.extend(check_imports())
    if errors:
        print("PREBUILD: FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("PREBUILD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
