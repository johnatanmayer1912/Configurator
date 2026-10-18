#!/usr/bin/env python3
"""Cursor hook: block release builds until mandatory QA manifest is valid."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.mandatory_qa_registry import validate_manifest_sync  # noqa: E402


def main() -> int:
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    ok, errors = validate_manifest_sync()
    if ok:
        print(json.dumps({
            'user_message': (
                'Mandatory QA manifest OK. Before EXE ship also run: '
                'python scripts/run_mandatory_qa.py && python _prebuild.py'
            )
        }))
        return 0

    detail = '; '.join(errors[:5])
    print(json.dumps({
        'user_message': f'MANDATORY QA MANIFEST OUT OF SYNC — fix before release: {detail}',
        'permission': 'deny',
    }))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
