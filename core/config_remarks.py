"""Action Required remarks — lab-ready vs production-only (no false-positive token scan)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from core.catalog_loader import CatalogLoader
from models.device_model import Device

_ATTENTION_RE = re.compile(r"! ATTENTION:\s*(.+)", re.IGNORECASE)
_COMMENT_ONLY_RE = re.compile(r"^\s*!")

# Lines that are engineer guidance — never treat as unresolved config.
_IGNORE_ATTENTION_PREFIXES = (
    "configure snmp trap hosts",
    "confirm boot image",
    "replace net_device_location",
)


class ConfigRemarksEngine:
    """Detect unresolved placeholders from the explicit registry only."""

    def __init__(self, catalog: Optional[CatalogLoader] = None) -> None:
        self.catalog = catalog or CatalogLoader()

    def analyze(
        self,
        device: Device,
        config_text: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        overrides = overrides or {}
        lab: List[Dict[str, Any]] = []
        production: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for spec in self.catalog.list_placeholders():
            pid = spec["id"]
            token = spec.get("token", "")
            phase = spec.get("phase", "production")
            if self._is_resolved(device, overrides, spec):
                continue
            if token and token not in config_text:
                continue
            remark = self._remark(spec)
            bucket = lab if phase == "lab" else production
            if pid not in seen:
                bucket.append(remark)
                seen.add(pid)

        for line in config_text.splitlines():
            m = _ATTENTION_RE.search(line)
            if not m:
                continue
            hint = m.group(1).strip()
            hint_lower = hint.lower()
            if any(hint_lower.startswith(p) for p in _IGNORE_ATTENTION_PREFIXES):
                continue
            rid = f"attention_{hash(hint) % 10000}"
            if rid in seen:
                continue
            if any(r.get("message", "").lower() == hint_lower for r in production + lab):
                continue
            production.append({
                "id": rid,
                "severity": "recommended",
                "field": "",
                "message": hint,
                "wizard_step": 4,
                "cli_line_hint": line.strip(),
                "phase": "production",
            })
            seen.add(rid)

        if device.admin_password and device.create_local_user:
            production.append({
                "id": "plaintext_password",
                "severity": "recommended",
                "field": "admin_password",
                "message": "Local user password is in plaintext CLI — use TACACS+ in production.",
                "wizard_step": 4,
                "phase": "production",
            })

        remarks = lab + production
        lab_pending = len([r for r in lab if r.get("severity") == "required"])
        prod_pending = len(production)

        return {
            "remarks": remarks,
            "lab_remarks": lab,
            "production_remarks": production,
            "pending_count": lab_pending,
            "production_pending_count": prod_pending,
            "lab_ready": lab_pending == 0,
            "resolved_count": max(0, len(self.catalog.list_placeholders()) - len(seen)),
        }

    def _remark(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": spec["id"],
            "severity": spec.get("severity", "required"),
            "field": spec.get("field", ""),
            "token": spec.get("token", ""),
            "message": spec.get("message", ""),
            "wizard_step": spec.get("wizard_step", 4),
            "cli_line_hint": spec.get("token", ""),
            "phase": spec.get("phase", "production"),
        }

    def _is_resolved(self, device: Device, overrides: Dict[str, Any], spec: Dict[str, Any]) -> bool:
        field = spec.get("field", "")
        val = overrides.get(field)
        if val is None or val == "":
            val = getattr(device, field, None)

        if field == "mgmt_ip":
            return bool(val) and "/" in str(val) and "MGMT_IP" not in str(val).upper()
        if field == "mgmt_gw":
            return bool(val) and str(val) not in {"", "MGMT_GATEWAY"}
        if field == "site_location":
            bad = {"", "NET_DEVICE_LOCATION", "LOCATION"}
            return bool(val) and str(val) not in bad
        if field == "network_name":
            return bool(val) and str(val) not in {"", "NETWORK_NAME"}
        if field == "snmp_trap_host_1":
            return bool(val) and "SNMP_SERVER" not in str(val).upper()
        if field == "snmp_trap_host_2":
            return bool(val) and "SNMP_SERVER" not in str(val).upper()
        if field == "snmp_v3_user":
            return bool(val) and str(val) not in {"", "USER_NAME"}
        if field == "boot_image":
            return bool(val) and "BOOT_IMAGE" not in str(val).upper()
        if field == "nxos_version":
            return bool(device.nxos_version)
        return bool(val)


def build_cli_blocks(
    device: Device,
    catalog: Optional[CatalogLoader] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Structured CLI snippets per enabled feature/baseline/downlink."""
    catalog = catalog or CatalogLoader()
    overrides = overrides or {}
    blocks: List[Dict[str, Any]] = []
    enabled = set(device.enabled_features or [])
    baseline = set(device.baseline_options or [])

    for feat in catalog.list_features():
        if feat["id"] not in enabled:
            continue
        cli = feat.get("cli")
        if cli:
            blocks.append({
                "id": feat["id"],
                "label": feat.get("label", feat["id"]),
                "category": feat.get("category", "feature"),
                "snippet": cli.strip(),
            })

    for opt in catalog.list_baseline_options():
        if opt["id"] not in baseline:
            continue
        cli = opt.get("cli")
        if cli:
            blocks.append({
                "id": opt["id"],
                "label": opt.get("label", opt["id"]),
                "category": "baseline",
                "snippet": cli.strip(),
            })

    downlink_opts = overrides.get("downlink_options") or {}
    for preset in catalog.list_downlink_presets():
        if not downlink_opts.get(preset["id"], preset.get("default", False)):
            continue
        members = ", ".join(preset.get("members") or [])
        snippet = (
            f"interface port-channel{preset.get('po_id')}\n"
            f"  description {preset.get('description')}\n"
            f"  switchport mode trunk\n"
            f"  mtu {preset.get('mtu', 9216)}\n"
            f"  vpc {preset.get('vpc_id')}\n"
            f"! Members: {members}"
        )
        blocks.append({
            "id": preset["id"],
            "label": preset.get("label", preset["id"]),
            "category": "downlink",
            "snippet": snippet,
        })

    if device.vpc:
        pl = ", ".join(device.vpc.peer_link_interfaces)
        ka = ", ".join(device.vpc.keepalive_interfaces)
        blocks.append({
            "id": "vpc_domain",
            "label": "vPC Domain",
            "category": "vpc",
            "snippet": (
                f"vpc domain {device.vpc.domain_id}\n"
                f"  peer-keepalive destination {device.vpc.remote_keepalive_ip} "
                f"source {device.vpc.local_keepalive_ip} vrf {device.vpc.keepalive_vrf}\n"
                f"! Peer-link: {pl}\n"
                f"! Keepalive: {ka}"
            ),
        })

    return blocks
