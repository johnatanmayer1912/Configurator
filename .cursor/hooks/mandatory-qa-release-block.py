#!/usr/bin/env python3
"""Cursor hook: remind before PyInstaller / release commands to run mandatory QA."""
from __future__ import annotations

import json
import re
import sys

RELEASE_PATTERNS = [
    re.compile(r'PyInstaller', re.I),
    re.compile(r'build_v5[\d.]*\.spec', re.I),
    re.compile(r'verify_offline_bundle', re.I),
    re.compile(r'smoke_release', re.I),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    command = payload.get('command') or payload.get('cmd') or ''
    if not any(p.search(command) for p in RELEASE_PATTERNS):
        return 0

    msg = (
        'RELEASE GATE: Run mandatory QA before building EXE:\n'
        '  python scripts/run_mandatory_qa.py --manifest-check\n'
        '  python scripts/run_mandatory_qa.py\n'
        '  python -m pytest tests/ -q\n'
        '  python _prebuild.py\n'
        'Council: .cursor/skills/nlap-release-council/'
    )
    # Advisory only — do not block; user may intentionally skip in dev
    print(json.dumps({'user_message': msg}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
