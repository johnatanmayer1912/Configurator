"""Load YAML catalogs for NX-OS versions, scenarios, and feature options."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _data_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "data"
    return Path(__file__).resolve().parent.parent / "data"


def _load_yaml(name: str) -> dict:
    path = _data_root() / name
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class CatalogLoader:
    """Read-only catalog access for UI and scenario engine."""

    def __init__(self) -> None:
        self._versions = _load_yaml("nxos_versions.yaml")
        self._scenarios = _load_yaml("scenario_templates.yaml")
        self._features = _load_yaml("feature_options.yaml")
        self._baseline = _load_yaml("institutional_baseline.yaml")
        self._matrix = _load_yaml("config_matrix.yaml")
        self._placeholders = _load_yaml("placeholder_fields.yaml")
        self._hints = _load_yaml("field_hints.yaml")
        self._encyclopedia = _load_yaml("option_encyclopedia.yaml")
        self._interface_presets = _load_yaml("interface_presets.yaml")
        self._hardware_path = self._resolve_hardware_path()

    @staticmethod
    def _resolve_hardware_path() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / "hardware_profiles.yaml"
        return Path(__file__).resolve().parent.parent / "hardware_profiles.yaml"

    def list_versions(self) -> List[Dict[str, Any]]:
        return self._versions.get("versions", [])

    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        for item in self.list_versions():
            if item.get("id") == version_id:
                return item
        return None

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return self._scenarios.get("scenarios", [])

    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        for item in self.list_scenarios():
            if item.get("id") == scenario_id:
                return item
        return None

    def list_features(self) -> List[Dict[str, Any]]:
        return self._features.get("features", [])

    def list_aliases(self) -> List[Dict[str, Any]]:
        return self._features.get("aliases", [])

    def list_baseline_options(self) -> List[Dict[str, Any]]:
        return self._baseline.get("baseline_options", [])

    def list_downlink_presets(self) -> List[Dict[str, Any]]:
        return self._baseline.get("downlink_presets", [])

    def list_uplink_presets(self) -> List[Dict[str, Any]]:
        return self._baseline.get("uplink_presets", [])

    def list_config_matrix(self) -> List[Dict[str, Any]]:
        return self._matrix.get("matrix", [])

    def get_matrix_row(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        for row in self.list_config_matrix():
            if row.get("scenario_id") == scenario_id:
                return row
        return None

    def list_placeholders(self) -> List[Dict[str, Any]]:
        return self._placeholders.get("placeholders", [])

    def get_hardware_profile(self, model: str) -> Optional[Dict[str, Any]]:
        for profile in self.list_hardware_profiles():
            if profile.get("display_name") == model or model in (profile.get("name") or ""):
                return profile
        return None

    def list_hardware_profiles(self) -> List[Dict[str, Any]]:
        if not self._hardware_path.exists():
            return []
        with open(self._hardware_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        profiles = []
        for profile in data.get("profiles", []):
            profiles.append(
                {
                    "display_name": profile.get("display_name", profile.get("name")),
                    "name": profile.get("name"),
                    "device_class": profile.get("device_class", "hybrid"),
                    "primary_speed_label": profile.get("primary_speed_label", "Multi"),
                    "speed_badges": profile.get("speed_badges", []),
                    "total_ports": profile.get("total_ports", 0),
                    "vpc_peer_link": profile.get("vpc_peer_link", []),
                    "vpc_keepalive": profile.get("vpc_keepalive", []),
                    "port_groups": profile.get("port_groups", []),
                }
            )
        return profiles

    def get_field_hints(self) -> Dict[str, Any]:
        return self._hints

    def list_interface_presets(self) -> List[Dict[str, Any]]:
        return self._interface_presets.get("presets", [])

    def get_interface_po_start(self) -> int:
        return int(self._interface_presets.get("vpc_po_start", 10))

    def get_option_help(self) -> Dict[str, Any]:
        return self._encyclopedia.get("options", {})

    def full_catalog(self) -> Dict[str, Any]:
        return {
            "versions": self.list_versions(),
            "scenarios": self.list_scenarios(),
            "features": self.list_features(),
            "aliases": self.list_aliases(),
            "baseline_options": self.list_baseline_options(),
            "downlink_presets": self.list_downlink_presets(),
            "uplink_presets": self.list_uplink_presets(),
            "config_matrix": self.list_config_matrix(),
            "placeholders": self.list_placeholders(),
            "hardware": self.list_hardware_profiles(),
            "field_hints": self._hints.get("fields", {}),
            "wizard_tips": self._hints.get("wizard_tips", {}),
            "option_help": self.get_option_help(),
            "interface_presets": self.list_interface_presets(),
            "interface_po_start": self.get_interface_po_start(),
        }
