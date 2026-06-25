"""Multi-site hostname and site-code validation (C10)."""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
SITE_CODE_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,31}$", re.IGNORECASE)

ROLE_SUFFIX = {
    "spine": ("-VPC", "-CORE"),
    "leaf": ("-A", "-LEAF"),
    "access": ("-SW", "-IDF"),
}


def validate_hostname(value: str, *, role: Optional[str] = None, pair: bool = False) -> Tuple[bool, List[str]]:
    hints: List[str] = []
    v = (value or "").strip()
    if not v:
        return False, ["Hostname is required."]
    if "_" in v:
        hints.append("Use hyphens instead of underscores (NX-OS convention).")
        v = v.replace("_", "-")
    if not HOSTNAME_RE.match(v):
        return False, ["Hostname: letters, numbers, hyphens; 1–63 chars; no leading/trailing hyphen."]
    if role and pair and not (v.endswith("-A") or v.endswith("-B")):
        hints.append("vPC pair primary often ends with -A (secondary auto gets -B).")
    if role == "spine" and "VPC" not in v.upper() and "CORE" not in v.upper():
        hints.append("Core switches often include CORE or VPC in the hostname.")
    return True, hints


def validate_site_code(value: str) -> Tuple[bool, str]:
    v = (value or "").strip()
    if not v:
        return False, "Site code is required for exports."
    if not SITE_CODE_RE.match(v):
        return False, "Site code: 2–32 chars, letters, numbers, hyphen, underscore."
    return True, ""


def suggest_hostname(site: str, role: str, pair: bool = False) -> str:
    base = re.sub(r"[^A-Za-z0-9]", "", site.upper())[:8] or "SITE"
    if role == "spine":
        return f"{base}-CORE1-VPC"
    if role == "leaf":
        return f"{base}-LEAF-01-A" if pair else f"{base}-LEAF-01"
    if role == "access":
        return f"{base}-ACCESS-01-A" if pair else f"{base}-ACCESS-01"
    return f"{base}-SW-01"
