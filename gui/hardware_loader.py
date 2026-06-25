"""
HardwareLoader — loads hardware profiles from hardware_profiles.yaml.

Falls back to hardcoded NexusModel constants if the YAML file is missing.
"""

from __future__ import annotations

from typing import Optional

from models.nexus_models import NexusModel
from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Hardcoded fallback profiles (mirrors hardware_profiles.yaml structure)
# ---------------------------------------------------------------------------

_FALLBACK_PROFILES: list[dict] = [
    {
        "name": NexusModel.N93180YC_EX,
        "total_ports": 54,
        "port_groups": [
            {"speed": "10/25G", "start": 1, "end": 48, "type": "SFP+"},
            {"speed": "40/100G", "start": 49, "end": 54, "type": "QSFP28"},
        ],
        "vpc_peer_link": ["Ethernet1/53", "Ethernet1/54"],
        "vpc_keepalive": ["Ethernet1/47", "Ethernet1/48"],
    },
    {
        "name": NexusModel.N9336C_FX2,
        "total_ports": 36,
        "port_groups": [
            {"speed": "40/100G", "start": 1, "end": 36, "type": "QSFP28"},
        ],
        "vpc_peer_link": ["Ethernet1/35", "Ethernet1/36"],
        "vpc_keepalive": ["Ethernet1/33", "Ethernet1/34"],
    },
    {
        "name": NexusModel.N9348GC_FXP,
        "total_ports": 54,
        "port_groups": [
            {"speed": "1G", "start": 1, "end": 48, "type": "Base-T"},
            {"speed": "10/25G", "start": 49, "end": 52, "type": "SFP28"},
            {"speed": "40/100G", "start": 53, "end": 54, "type": "QSFP28"},
        ],
        "vpc_peer_link": ["Ethernet1/53", "Ethernet1/54"],
        "vpc_keepalive": ["Ethernet1/47", "Ethernet1/48"],
    },
    {
        "name": NexusModel.GENERIC,
        "total_ports": 0,
        "port_groups": [],
        "vpc_peer_link": [],
        "vpc_keepalive": [],
    },
]


class HardwareLoader:
    """Loads and exposes hardware profile data for supported Nexus models."""

    def __init__(self) -> None:
        # Ordered dict: name -> profile dict
        self._profiles: dict[str, dict] = {}
        self._names: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load profiles from hardware_profiles.yaml.

        Falls back to hardcoded constants if the YAML file cannot be found
        or parsed.
        """
        try:
            # Import here so that resource_path.py (task 1.5) is not required
            # at module import time — only at load() call time.
            from gui.resource_path import resource_path  # noqa: PLC0415
            import yaml  # noqa: PLC0415

            yaml_path = resource_path("hardware_profiles.yaml")
            with open(yaml_path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)

            raw_profiles: list[dict] = data.get("profiles", [])
            if not raw_profiles:
                raise ValueError("No profiles found in hardware_profiles.yaml")

            self._load_from_list(raw_profiles)
            logger.info("HardwareLoader: loaded %d profiles from YAML", len(self._profiles))

        except FileNotFoundError:
            logger.warning(
                "HardwareLoader: hardware_profiles.yaml not found — using hardcoded fallback profiles"
            )
            self._load_from_list(_FALLBACK_PROFILES)

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "HardwareLoader: failed to load hardware_profiles.yaml (%s) — using hardcoded fallback profiles",
                exc,
            )
            self._load_from_list(_FALLBACK_PROFILES)

    def get_profile(self, name: str) -> dict:
        """Return the profile dict for *name*.

        Raises:
            KeyError: if *name* is not a known profile.
        """
        if name not in self._profiles:
            raise KeyError(f"Unknown hardware profile: {name!r}")
        return self._profiles[name]

    def get_all_names(self) -> list[str]:
        """Return all profile names in load order."""
        return list(self._names)

    def get_port_speed(self, name: str, port_index: int) -> str:
        """Return the speed string for a 1-based *port_index* on *name*.

        Returns ``"Unknown"`` if the port index does not fall within any
        defined port group.

        Raises:
            KeyError: if *name* is not a known profile.
        """
        profile = self.get_profile(name)
        for group in profile.get("port_groups", []):
            start: int = group.get("start", 0)
            end: int = group.get("end", 0)
            if start <= port_index <= end:
                return group.get("speed", "Unknown")
        return "Unknown"

    def get_vpc_ports(self, name: str) -> dict:
        """Return ``{"peer_link": [...], "keepalive": [...]}`` for *name*.

        Raises:
            KeyError: if *name* is not a known profile.
        """
        profile = self.get_profile(name)
        return {
            "peer_link": list(profile.get("vpc_peer_link", [])),
            "keepalive": list(profile.get("vpc_keepalive", [])),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_from_list(self, profiles: list[dict]) -> None:
        """Populate internal state from a list of profile dicts."""
        self._profiles = {}
        self._names = []
        for profile in profiles:
            name: Optional[str] = profile.get("name")
            if not name:
                logger.warning("HardwareLoader: skipping profile with missing name: %r", profile)
                continue
            self._profiles[name] = profile
            self._names.append(name)
