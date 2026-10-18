"""Apply scenario presets to intent/device payloads."""

from typing import Any, Dict, List, Optional

from core.catalog_loader import CatalogLoader
from core.intent_engine import IntentEngine
from core.device_enricher import enrich_device
from core.interface_customizer import apply_interface_customizations, validate_interface_plans
from core.link_resolver import resolve_link_plans
from core.manual_overrides import apply_manual_overrides
from core.vpc_topology import apply_vpc_leaf_topology, apply_vpc_topology
from core.vlan_validator import VLANValidator
from models.device_model import Device, VPCConfig
from models.intent_model import BlueprintIntent, IntentOverrides


class ScenarioEngine:
    """Maps scenario templates to concrete device/intent configurations."""

    def __init__(self, catalog: Optional[CatalogLoader] = None) -> None:
        self.catalog = catalog or CatalogLoader()
        self.intent_engine = IntentEngine(self.catalog)
        self.vlan_validator = VLANValidator(self.catalog)

    def apply_scenario(
        self,
        scenario_id: str,
        hostname: str,
        site_name: str,
        mgmt_ip: str,
        mgmt_gw: str,
        overrides: Optional[Dict[str, Any]] = None,
        secondary_hostname: Optional[str] = None,
        secondary_mgmt_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        scenario = self.catalog.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        defaults = dict(scenario.get("defaults", {}))
        if overrides:
            # Only update with overrides if they are explicitly provided (not None)
            # This ensures user's explicit VLAN choices are respected
            for key, value in overrides.items():
                if value is not None:
                    defaults[key] = value
        defaults["site_name"] = defaults.get("site_name") or site_name

        # Validate VLAN assignments against hardware constraints
        model = defaults.get("model", "Generic")
        base_vlan = defaults.get("base_access_vlan", 10)
        vlan_count = defaults.get("access_vlan_count", 4)
        
        valid, msg = self.vlan_validator.validate_vlan_range(model, base_vlan, vlan_count)
        if not valid:
            # Suggest valid range if validation fails
            suggested_start, suggested_end = self.vlan_validator.suggest_vlan_range(
                model, vlan_count, base_vlan
            )
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"VLAN validation failed for {model}: {msg}. Using suggested range [{suggested_start}-{suggested_end}]")
            defaults["base_access_vlan"] = suggested_start
            defaults["access_vlan_count"] = suggested_end - suggested_start + 1

        hw = self._hardware_for_model(defaults.get("model", "Generic"))
        defaults["downlinks"] = resolve_link_plans(
            scenario_id=scenario_id,
            defaults=defaults,
            catalog=self.catalog,
            hw_profile=hw,
            kind="downlink",
        )
        resolved_uplinks = resolve_link_plans(
            scenario_id=scenario_id,
            defaults=defaults,
            catalog=self.catalog,
            hw_profile=hw,
            kind="uplink",
        )
        wants_vpc = self._wants_vpc(scenario, defaults)
        if resolved_uplinks and wants_vpc:
            defaults["uplinks"] = resolved_uplinks
            defaults["uplink_ports"] = []
        elif resolved_uplinks:
            flat_uplinks: List[str] = []
            for item in resolved_uplinks:
                flat_uplinks.extend(item.get("members") or [])
            defaults["uplink_ports"] = flat_uplinks
            defaults["uplinks"] = []
        else:
            defaults["uplinks"] = []

        nxos_version = defaults.get("nxos_version", "9.3")
        features = self._sanitize_features(defaults.get("features", []))
        features = self._apply_version_feature_caps(features, nxos_version)
        pair_mode = scenario.get("pair_mode", False)

        intent = BlueprintIntent(
            hostname=hostname,
            site_name=site_name,
            role=scenario.get("role", "access"),
            model=defaults.get("model", "Generic"),
            mgmt_ip=mgmt_ip,
            mgmt_gw=mgmt_gw,
            redundancy_mode=scenario.get("redundancy", "standalone"),
            security_tier=defaults.get("security_tier", "standard"),
            uplink_ports=defaults.get("uplink_ports", []),
            overrides=IntentOverrides(
                motd=defaults.get("motd", "Authorized Access Only"),
                base_access_vlan=defaults.get("base_access_vlan", 10),
                access_vlan_count=defaults.get("access_vlan_count", 4),
                interface_count=defaults.get("interface_count", 48),
            ),
        )

        device, resolution = self.intent_engine.resolve(intent)
        self._apply_institutional_baseline(device, defaults)
        self._apply_vpc_config(device, defaults, scenario)
        self._apply_topology(device, defaults, hostname, scenario_id)
        device.nxos_version = nxos_version
        device.enabled_features = list(features)
        apply_manual_overrides(device, defaults)
        enrich_device(device, defaults, vpc_role="primary")

        result: Dict[str, Any] = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.get("name"),
            "device": device,
            "resolution": resolution,
            "intent": intent,
            "nxos_version": nxos_version,
            "enabled_features": features,
            "pair_mode": pair_mode,
        }

        if pair_mode:
            result["pair"] = self._build_vpc_pair(device, defaults, hostname, scenario_id, secondary_hostname, secondary_mgmt_ip)

        vpc_pair_active = bool(device.vpc and pair_mode)
        planner_warnings = validate_interface_plans(device, defaults, vpc_pair=vpc_pair_active)
        if planner_warnings:
            result["planner_warnings"] = planner_warnings

        apply_interface_customizations(device, defaults, vpc_pair=vpc_pair_active)
        if pair_mode and result.get("pair"):
            secondary = result["pair"]["secondary"]["device"]
            apply_interface_customizations(secondary, defaults, vpc_pair=bool(secondary.vpc))
            enrich_device(secondary, defaults, vpc_role="secondary")

        return result

    def build_render_metadata(self, defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Metadata passed to Jinja for optional CLI reference blocks."""
        if defaults.get("inject_cli_reference"):
            return {"cli_reference": self.catalog.list_aliases()}
        return {}

    def _apply_institutional_baseline(self, device: Device, defaults: Dict[str, Any]) -> None:
        raw = defaults.get("baseline_options") or []
        valid = {b["id"] for b in self.catalog.list_baseline_options()}
        device.baseline_options = [str(x) for x in raw if str(x) in valid]
        if defaults.get("network_name") and str(defaults["network_name"]) not in ("", "NETWORK_NAME"):
            device.network_name = str(defaults["network_name"])
        elif defaults.get("site_name"):
            device.network_name = str(defaults["site_name"])
        loc = defaults.get("site_location")
        if loc and str(loc) not in ("", "NET_DEVICE_LOCATION", "LOCATION"):
            device.site_location = str(loc)
        elif defaults.get("site_name"):
            device.site_location = str(defaults["site_name"])
        if defaults.get("snmp_contact"):
            device.snmp_contact = str(defaults["snmp_contact"])
        if defaults.get("spanning_tree_priority") is not None:
            device.spanning_tree_priority = int(defaults["spanning_tree_priority"])

    def _apply_topology(
        self, device: Device, defaults: Dict[str, Any], hostname: str, scenario_id: str
    ) -> None:
        if not device.vpc:
            return
        model = defaults.get("model", device.model)
        hw = self._hardware_for_model(model)
        merged = dict(defaults)
        peer_hostname = defaults.get("peer_hostname") or self._guess_peer_hostname(hostname)
        if scenario_id == "vpc_core_pair":
            apply_vpc_topology(device, merged, hw, peer_hostname=peer_hostname)
        else:
            apply_vpc_leaf_topology(device, merged, hw, peer_hostname=peer_hostname)

    def _resolve_downlinks(self, scenario_id: str, defaults: Dict[str, Any]) -> List[Dict[str, Any]]:
        hw = self._hardware_for_model(defaults.get("model", "Generic"))
        return resolve_link_plans(
            scenario_id=scenario_id,
            defaults=defaults,
            catalog=self.catalog,
            hw_profile=hw,
            kind="downlink",
        )

    @staticmethod
    def _guess_peer_hostname(hostname: str) -> str:
        base = hostname.removesuffix("-A").removesuffix("-B")
        if base.endswith("_VPC"):
            return base[:-4] + "2_VPC"
        if base.endswith("1"):
            return base[:-1] + "2"
        return f"{base}-B"

    def _parse_peer_links(self, defaults: Dict[str, Any], model: str) -> List[str]:
        raw = defaults.get("peer_link_interfaces") or defaults.get("vpc_pl_ints")
        if isinstance(raw, str):
            parsed = [p.strip() for p in raw.split(",") if p.strip()]
            if parsed:
                return parsed
        if isinstance(raw, list) and raw:
            return list(raw)
        hw = self._hardware_for_model(model)
        return list(hw.get("vpc_peer_link") or ["Ethernet1/53", "Ethernet1/54"])

    def _parse_keepalive_ports(self, defaults: Dict[str, Any], model: str) -> List[str]:
        raw = defaults.get("keepalive_interfaces") or defaults.get("vpc_ka_ints")
        if isinstance(raw, str):
            parsed = [p.strip() for p in raw.split(",") if p.strip()]
            if parsed:
                return parsed
        if isinstance(raw, list) and raw:
            return list(raw)
        hw = self._hardware_for_model(model)
        return list(hw.get("vpc_keepalive") or [])

    def _sanitize_features(self, raw: List[Any]) -> List[str]:
        valid = {f["id"] for f in self.catalog.list_features()}
        return [str(x) for x in raw if str(x) in valid]

    def _apply_version_feature_caps(self, features: List[str], nxos_version: str) -> List[str]:
        """Strip unsupported features per NX-OS train; ensure vPC ARP sync on vPC builds."""
        profile = self.catalog.get_version(nxos_version) or {}
        caps = profile.get("features", {})
        out = list(features)
        legacy_only = profile.get("template") == "nxos_legacy.j2"
        if caps.get("vpc_peer_gateway") is False:
            out = [f for f in out if f != "vpc_peer_gateway"]
        if caps.get("vpc_auto_recovery") is False:
            out = [f for f in out if f not in {"vpc_auto_recovery", "vpc_orphan_suspend"}]
        if legacy_only:
            out = [f for f in out if f not in {"vxlan", "nxapi", "bash", "bfd"}]
        if "vpc" in out and "vpc_arp_sync" not in out:
            out.append("vpc_arp_sync")
        return out

    def _wants_vpc(self, scenario: dict, defaults: Dict[str, Any]) -> bool:
        if scenario.get("redundancy") == "vpc":
            return True
        features = defaults.get("features") or []
        return "vpc" in features

    def _apply_vpc_config(self, device: Device, defaults: Dict[str, Any], scenario: dict) -> None:
        if not self._wants_vpc(scenario, defaults):
            device.vpc = None
            return

        model = defaults.get("model", device.model)
        peer_links = self._parse_peer_links(defaults, model)
        keepalive_ports = self._parse_keepalive_ports(defaults, model)
        keepalive_vrf = defaults.get("keepalive_vrf", "management")
        if "baseline_vrf_keepalive" in (defaults.get("baseline_options") or []):
            keepalive_vrf = "VPC_Keep_Alive"

        feature_list = defaults.get("features") or []
        device.vpc = VPCConfig(
            domain_id=int(defaults.get("vpc_domain_id", defaults.get("vpc_domain", 100))),
            role="primary",
            keepalive_vrf=keepalive_vrf,
            local_keepalive_ip=defaults.get("local_keepalive_ip", defaults.get("local_ka", "10.255.255.1")),
            remote_keepalive_ip=defaults.get("remote_keepalive_ip", defaults.get("remote_ka", "10.255.255.2")),
            peer_link_id=int(defaults.get("vpc_peer_link_id", defaults.get("vpc_pl_id", 100))),
            peer_link_interfaces=peer_links,
            keepalive_interfaces=keepalive_ports,
            keepalive_po_id=int(defaults.get("keepalive_po_id", defaults.get("vpc_keepalive_po_id", 2))),
            system_priority=int(defaults.get("vpc_system_priority", 32667)),
            role_priority=int(defaults.get("role_priority_primary", defaults.get("vpc_role_priority_primary", 4096))),
            peer_switch="vpc_peer_switch" in feature_list,
            delay_restore=defaults.get("vpc_delay_restore") if "vpc_delay_restore" in feature_list else None,
        )

    def _hardware_for_model(self, model: str) -> Dict[str, Any]:
        for profile in self.catalog.list_hardware_profiles():
            if profile.get("display_name") == model or model in (profile.get("name") or ""):
                return profile
        return {}

    def _build_vpc_pair(
        self, primary_device: Device, defaults: Dict[str, Any], base_hostname: str, scenario_id: str,
        secondary_hostname: Optional[str] = None, secondary_mgmt_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        import copy

        secondary = copy.deepcopy(primary_device)
        base = base_hostname.removesuffix("-A").removesuffix("-B")
        secondary.hostname = secondary_hostname or f"{base}-B"
        if secondary_mgmt_ip:
            secondary.mgmt_ip = secondary_mgmt_ip
        enrich_device(secondary, defaults, vpc_role="secondary")
        if secondary.vpc:
            sec_priority = int(
                defaults.get("role_priority_secondary", defaults.get("vpc_role_priority_secondary", 2000))
            )
            secondary.vpc = VPCConfig(
                domain_id=secondary.vpc.domain_id,
                role="secondary",
                keepalive_vrf=secondary.vpc.keepalive_vrf,
                local_keepalive_ip=secondary.vpc.remote_keepalive_ip,
                remote_keepalive_ip=secondary.vpc.local_keepalive_ip,
                peer_link_id=secondary.vpc.peer_link_id,
                peer_link_interfaces=list(secondary.vpc.peer_link_interfaces),
                keepalive_interfaces=list(secondary.vpc.keepalive_interfaces),
                keepalive_po_id=secondary.vpc.keepalive_po_id,
                system_priority=secondary.vpc.system_priority,
                role_priority=sec_priority,
                peer_switch=secondary.vpc.peer_switch,
                delay_restore=secondary.vpc.delay_restore,
            )
            merged = dict(defaults)
            merged["downlinks"] = self._resolve_downlinks(scenario_id, defaults)
            hw = self._hardware_for_model(defaults.get("model", secondary.model))
            peer_hostname = primary_device.hostname
            if scenario_id == "vpc_core_pair":
                apply_vpc_topology(secondary, merged, hw, peer_hostname=peer_hostname)
            else:
                apply_vpc_leaf_topology(secondary, merged, hw, peer_hostname=peer_hostname)
        return {
            "primary": {"hostname": primary_device.hostname, "vpc_role": "primary"},
            "secondary": {"hostname": secondary.hostname, "vpc_role": "secondary", "device": secondary},
        }

    def enrich_intent_topology(self, device: Device, intent: BlueprintIntent) -> None:
        """Align Intent API output with wizard-grade vPC topology from hardware profiles."""
        role = intent.role.lower()
        if intent.redundancy_mode.lower() != "vpc" or role not in {"leaf", "spine"}:
            if intent.redundancy_mode.lower() != "vpc":
                device.vpc = None
            return
        scenario_id = "vpc_core_pair" if role == "spine" else "vpc_leaf_pair"
        scenario = self.catalog.get_scenario(scenario_id) or {"redundancy": "vpc", "role": role}
        defaults = {
            "model": intent.model,
            "features": ["vpc", "lacp"],
            "vpc_domain_id": 100 if role == "spine" else 1,
            "vpc_peer_link_id": 100 if role == "spine" else 1,
            "local_keepalive_ip": "10.255.255.1",
            "remote_keepalive_ip": "10.255.255.2",
            "baseline_options": [],
        }
        self._apply_vpc_config(device, defaults, scenario)
        self._apply_topology(device, defaults, intent.hostname, scenario_id)
        enrich_device(device, defaults, vpc_role="primary")
