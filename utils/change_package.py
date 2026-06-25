"""Change-window export package — manifest, README, device JSON, rollback notes."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.device_model import Device


def device_to_dict(device: Device) -> Dict[str, Any]:
    return asdict(device)


def write_device_json(target_dir: str, prefix: str, device: Device) -> str:
    name = f"{prefix}_device.json"
    path = os.path.join(target_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(device_to_dict(device), fh, indent=2)
    return name


def build_manifest(
    *,
    version: str,
    site_name: str,
    scenario_id: str,
    scenario_name: str,
    nxos_version: str,
    hosts: List[Dict[str, Any]],
    files: List[str],
    output_dir: str,
    batch_folder: Optional[str] = None,
    lab_ready: bool = True,
    summary_lines: Optional[List[str]] = None,
    policy_flags: Optional[Dict[str, str]] = None,
    pair_mode: bool = False,
) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "product": "NX-OS Configuration Authority",
        "app_version": version,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "site_name": site_name,
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "nxos_version": nxos_version,
        "pair_mode": pair_mode,
        "batch_folder": batch_folder,
        "output_dir": output_dir,
        "lab_ready": lab_ready,
        "summary_lines": summary_lines or [],
        "policy_flags": policy_flags or {},
        "hosts": hosts,
        "files": files,
    }


def render_change_package_md(manifest: Dict[str, Any]) -> str:
    lines = [
        "# NX-OS Change Package",
        "",
        f"**Generated:** {manifest.get('generated_at', '')}",
        f"**Application:** {manifest.get('product', '')} v{manifest.get('app_version', '')}",
        f"**Site:** {manifest.get('site_name', '')}",
        f"**Scenario:** {manifest.get('scenario_name', '')} (`{manifest.get('scenario_id', '')}`)",
        f"**NX-OS train:** {manifest.get('nxos_version', '')}",
        f"**Lab ready:** {'Yes' if manifest.get('lab_ready') else 'Review Action Required first'}",
        "",
        "## Files in this folder",
        "",
    ]
    for f in manifest.get("files", []):
        lines.append(f"- `{f}`")
    lines.extend([
        "",
        "## Switches",
        "",
    ])
    for h in manifest.get("hosts", []):
        role = h.get("vpc_role", "standalone")
        lines.append(f"- **{h.get('hostname', '')}** ({role})")
        if h.get("keepalive_local") and h.get("keepalive_remote"):
            lines.append(
                f"  - Keepalive: local `{h['keepalive_local']}` → remote `{h['keepalive_remote']}`"
            )
    if manifest.get("pair_mode"):
        lines.extend([
            "",
            "## vPC pair notes",
            "",
            "- Paste **primary** config on switch A first, then **secondary** on switch B.",
            "- Secondary hostname uses `-B` suffix; keepalive IPs are swapped automatically.",
            "- After paste: `show vpc brief`, `show interface status`, `copy run start` only after lab sign-off.",
        ])
    lines.extend([
        "",
        "## Rollback reminder",
        "",
        "- Keep the pasted running-config backup before applying this build.",
        "- Use **Compare** on Review step or `_diff.txt` artifacts to review deltas.",
        "",
        "## Post-paste checklist",
        "",
        "1. `show running-config | sec vpc`",
        "2. `show vpc brief`",
        "3. `show interface status err-disabled`",
        "4. `show ip route vrf management`",
        "",
    ])
    return "\n".join(lines)


def write_package_artifacts(target_dir: str, manifest: Dict[str, Any]) -> List[str]:
    os.makedirs(target_dir, exist_ok=True)
    written: List[str] = []
    manifest_name = "manifest.json"
    readme_name = "CHANGE_PACKAGE.md"
    manifest_path = os.path.join(target_dir, manifest_name)
    readme_path = os.path.join(target_dir, readme_name)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    written.append(manifest_name)
    with open(readme_path, "w", encoding="utf-8") as fh:
        fh.write(render_change_package_md(manifest))
    written.append(readme_name)
    return written
