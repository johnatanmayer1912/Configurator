"""Config Builder — questionnaire engine (customize-your-switch flow)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.config_parser import ParsedConfig, parse_running_config
from core.catalog_loader import CatalogLoader


QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "start_mode",
        "title": "How would you like to start?",
        "help": "Paste an existing config and we'll detect settings, or start fresh.",
        "type": "choice",
        "required": True,
        "options": [
            {"value": "paste", "label": "I have a running-config to analyze", "icon": "paste"},
            {"value": "fresh", "label": "Brand-new switch — guide me step by step", "icon": "new"},
        ],
    },
    {
        "id": "running_config",
        "title": "Paste your running-config",
        "help": "We'll extract hostname, VLANs, vPC, mgmt, and features automatically.",
        "type": "textarea",
        "required": True,
        "show_if": {"start_mode": "paste"},
    },
    {
        "id": "device_role",
        "title": "What is this switch's role?",
        "help": "Drives port layout, VLANs, and L3 services.",
        "type": "choice",
        "required": True,
        "options": [
            {"value": "access", "label": "Access / IDF closet switch"},
            {"value": "leaf", "label": "Data center leaf / ToR"},
            {"value": "spine", "label": "Spine / core layer"},
            {"value": "mgmt", "label": "Out-of-band management only"},
        ],
    },
    {
        "id": "redundancy",
        "title": "Redundancy model?",
        "help": "vPC pair generates primary + secondary configs in one build folder.",
        "type": "choice",
        "required": True,
        "options": [
            {"value": "standalone", "label": "Standalone — single switch"},
            {"value": "vpc", "label": "vPC pair — dual-homed leaf"},
        ],
        "hide_if": {"device_role": "mgmt"},
        "hide_if_any": {"device_role": ["spine"]},
    },
    {
        "id": "environment",
        "title": "Environment & security posture?",
        "type": "choice",
        "required": True,
        "options": [
            {"value": "lab", "label": "Lab / staging — standard tier"},
            {"value": "production", "label": "Production — hardened (no NX-API/bash, syslog enforced)"},
        ],
    },
    {
        "id": "fabric",
        "title": "VXLAN / EVPN overlay?",
        "type": "choice",
        "required": True,
        "options": [
            {"value": "no", "label": "No — traditional VLANs only"},
            {"value": "yes", "label": "Yes — VXLAN leaf foundation (lab validate first)"},
        ],
        "show_if": {"device_role": "leaf"},
    },
    {
        "id": "site_name",
        "title": "Site name",
        "help": "Used in export filenames and folder names (e.g. HQ_DC, DR_SITE).",
        "type": "text",
        "required": True,
        "placeholder": "HQ_DC",
    },
    {
        "id": "hostname",
        "title": "Switch hostname",
        "type": "text",
        "required": True,
        "placeholder": "DC-LEAF-01-A",
    },
    {
        "id": "mgmt_ip",
        "title": "Management IP (with CIDR)",
        "type": "text",
        "required": True,
        "placeholder": "10.10.10.10/24",
    },
    {
        "id": "mgmt_gw",
        "title": "Management default gateway",
        "type": "text",
        "required": True,
        "placeholder": "10.10.10.1",
    },
    {
        "id": "confirm_build",
        "title": "Ready to apply?",
        "help": "We'll pre-fill the main wizard. Review on Step 5, then Build & Save.",
        "type": "confirm",
        "required": True,
    },
]


class ConfigBuilderEngine:
    """Dynamic questionnaire + recommendation for the Config Builder."""

    def __init__(self, catalog: Optional[CatalogLoader] = None) -> None:
        self.catalog = catalog or CatalogLoader()

    def get_questions(self, answers: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        answers = answers or {}
        visible = []
        for q in QUESTIONS:
            if not self._question_visible(q, answers):
                continue
            enriched = dict(q)
            enriched["prefill"] = self._prefill(q["id"], answers)
            visible.append(enriched)
        return visible

    def _question_visible(self, q: Dict[str, Any], answers: Dict[str, Any]) -> bool:
        show_if = q.get("show_if")
        if show_if:
            for key, val in show_if.items():
                if answers.get(key) != val:
                    return False
        hide_if = q.get("hide_if")
        if hide_if:
            for key, val in hide_if.items():
                if answers.get(key) == val:
                    return False
        hide_if_any = q.get("hide_if_any")
        if hide_if_any:
            for key, vals in hide_if_any.items():
                if answers.get(key) in vals:
                    return False
        return True

    def _prefill(self, qid: str, answers: Dict[str, Any]) -> Any:
        parsed = self._parsed_from_answers(answers)
        if qid == "device_role" and parsed:
            return parsed.detect_role()
        if qid == "redundancy" and parsed:
            return "vpc" if parsed.has_vpc else "standalone"
        if qid == "environment":
            return answers.get("environment") or "lab"
        if qid == "fabric" and parsed:
            return "yes" if "vxlan" in parsed.features else "no"
        if qid == "hostname" and parsed and parsed.hostname:
            return parsed.hostname
        if qid == "mgmt_ip" and parsed and parsed.mgmt_ip:
            return parsed.mgmt_ip
        if qid == "mgmt_gw" and parsed and parsed.mgmt_gw:
            return parsed.mgmt_gw
        if qid == "site_name":
            return answers.get("site_name") or "HQ_DC"
        return answers.get(qid, "")

    def _parsed_from_answers(self, answers: Dict[str, Any]) -> Optional[ParsedConfig]:
        raw = answers.get("running_config") or answers.get("_parsed_config_text")
        if not raw:
            return None
        return parse_running_config(raw)

    def analyze_paste(self, text: str) -> Dict[str, Any]:
        parsed = parse_running_config(text)
        return {
            "parsed": parsed.to_dict(),
            "summary": self._detection_summary(parsed),
            "suggested_answers": {
                "device_role": parsed.detect_role(),
                "redundancy": "vpc" if parsed.has_vpc else "standalone",
                "fabric": "yes" if "vxlan" in parsed.features else "no",
                "hostname": parsed.hostname,
                "mgmt_ip": parsed.mgmt_ip,
                "mgmt_gw": parsed.mgmt_gw,
                "environment": "production"
                if "bash" not in parsed.features and "nxapi" not in parsed.features
                else "lab",
            },
        }

    def _detection_summary(self, parsed: ParsedConfig) -> List[str]:
        lines = []
        if parsed.hostname:
            lines.append(f"Hostname: {parsed.hostname}")
        if parsed.mgmt_ip:
            lines.append(f"Management: {parsed.mgmt_ip}")
        if parsed.features:
            lines.append(f"Features: {', '.join(parsed.features)}")
        if parsed.vlans:
            lines.append(f"VLANs: {len(parsed.vlans)} detected")
        if parsed.vpc_domain_id:
            lines.append(f"vPC domain: {parsed.vpc_domain_id}")
        if parsed.vpc_peer_link_interfaces:
            lines.append(f"Peer-link: {', '.join(parsed.vpc_peer_link_interfaces)}")
        if parsed.access_port_count:
            lines.append(f"Access ports (approx): {parsed.access_port_count}")
        if not lines:
            lines.append("No strong signals — we'll use your answers to build a baseline.")
        return lines

    def recommend(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        parsed = self._parsed_from_answers(answers)
        role = answers.get("device_role") or (parsed.detect_role() if parsed else "access")
        redundancy = answers.get("redundancy", "standalone")
        fabric = answers.get("fabric", "no")
        env = answers.get("environment", "lab")

        scenario_id = self._pick_scenario(role, redundancy, fabric)
        scenario = self.catalog.get_scenario(scenario_id) or {}
        defaults = dict(scenario.get("defaults", {}))

        features = list(defaults.get("features", []))
        if fabric == "yes" and redundancy != "vpc" and scenario_id == "standalone_leaf":
            if "vxlan" not in features:
                features.append("vxlan")
        tier = "hardened" if env == "production" else "standard"

        overrides: Dict[str, Any] = {
            "security_tier": tier,
            "features": features,
        }

        if parsed:
            if parsed.ntp_servers:
                overrides["ntp_server"] = ", ".join(parsed.ntp_servers)
            if parsed.logging_hosts:
                overrides["logging_host"] = ", ".join(parsed.logging_hosts)
            if parsed.snmp_location:
                overrides["snmp_location"] = parsed.snmp_location
            if parsed.vpc_domain_id:
                overrides["vpc_domain_id"] = parsed.vpc_domain_id
            if parsed.vpc_peer_link_interfaces:
                overrides["peer_link_interfaces"] = ", ".join(parsed.vpc_peer_link_interfaces)
            if parsed.local_keepalive_ip:
                overrides["local_keepalive_ip"] = parsed.local_keepalive_ip
            if parsed.remote_keepalive_ip:
                overrides["remote_keepalive_ip"] = parsed.remote_keepalive_ip
            if parsed.vlans:
                overrides["custom_vlans"] = parsed.vlans[:20]
            if parsed.interface_lines:
                overrides["interface_lines"] = "\n".join(parsed.interface_lines[:48])
            if parsed.motd:
                overrides["motd"] = parsed.motd

        wizard = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.get("name", scenario_id),
            "site_name": answers.get("site_name") or "HQ_DC",
            "hostname": answers.get("hostname") or (parsed.hostname if parsed else "NXOS-SW-01"),
            "mgmt_ip": answers.get("mgmt_ip") or (parsed.mgmt_ip if parsed else "10.10.10.10/24"),
            "mgmt_gw": answers.get("mgmt_gw") or (parsed.mgmt_gw if parsed else "10.10.10.1"),
            "generate_pair": redundancy == "vpc" and scenario.get("pair_mode", False),
            "overrides": overrides,
        }

        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.get("name"),
            "wizard": wizard,
            "summary": self._recommendation_summary(scenario, wizard, parsed),
            "detection": parsed.to_dict() if parsed else None,
        }

    def _pick_scenario(self, role: str, redundancy: str, fabric: str) -> str:
        if role == "mgmt":
            return "mgmt_oob"
        if role == "spine":
            return "vpc_core_pair" if redundancy == "vpc" else "spine_core"
        if fabric == "yes" and role == "leaf":
            return "vxlan_evpn_leaf" if redundancy == "vpc" else "standalone_leaf"
        if role == "access":
            return "vpc_access_pair" if redundancy == "vpc" else "standalone_access"
        if redundancy == "vpc":
            return "vpc_leaf_pair"
        if role == "leaf":
            return "standalone_leaf"
        return "standalone_access"

    def _recommendation_summary(
        self, scenario: dict, wizard: dict, parsed: Optional[ParsedConfig]
    ) -> List[str]:
        lines = [
            f"Scenario: {scenario.get('name', wizard['scenario_id'])}",
            f"Site: {wizard['site_name']} · Hostname: {wizard['hostname']}",
            f"Security: {wizard['overrides'].get('security_tier', 'standard')}",
        ]
        if wizard.get("generate_pair"):
            lines.append("Output: vPC pair (primary + secondary in one build folder)")
        if parsed:
            lines.append(f"Imported {parsed.raw_line_count} lines from running-config")
        lines.append("Next: review the main wizard, Validate, then Build & Save.")
        return lines
