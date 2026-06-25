"""Read application version from VERSION file."""

import os
import sys
from functools import lru_cache


@lru_cache(maxsize=1)
def get_app_version() -> str:
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(sys._MEIPASS, "VERSION"))
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(base, "VERSION"))
    for path in candidates:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read().strip()
    return "2.8.0"
