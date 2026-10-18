#!/usr/bin/env python3
"""Cursor hook: remind agents to sync mandatory QA when code changes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCH_PREFIXES = (
    'modules/',
    'tests/',
    'utils/',
    'vlan_checker_web.py',
    '_prebuild.py',
    'scripts/',
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = payload.get('file_path') or payload.get('path') or ''
    norm = str(file_path).replace('\\', '/')

    if not any(norm.endswith(p.rstrip('/')) or p in norm for p in WATCH_PREFIXES):
        return 0

    manifest = ROOT / 'qa/mandatory/MANIFEST.yaml'
    msg = (
        'NLAP mandatory QA gate: if this change adds/fixes behavior, extend '
        'tests/mandatory/, update qa/mandatory/MANIFEST.yaml, and '
        '.cursor/skills/nlap-release-council/QUESTIONNAIRE.md. '
        'Before release run: python scripts/run_mandatory_qa.py'
    )
    print(json.dumps({'user_message': msg}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
