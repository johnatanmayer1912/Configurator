import os
import sys
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from models.device_model import Device
from core.catalog_loader import CatalogLoader
from utils.web_logger import logger

class ConfigRenderer:
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS
                template_dir = os.path.join(base_path, "templates")
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                template_dir = os.path.join(base_path, "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.catalog = CatalogLoader()

    def _resolve_template(self, device: Device, template_name: Optional[str]) -> str:
        if template_name:
            return template_name
        version_profile = self.catalog.get_version(device.nxos_version)
        if version_profile and version_profile.get("template"):
            return version_profile["template"]
        return "nxos_base.j2"

    def _feature_flags(self, device: Device) -> dict:
        enabled = set(device.enabled_features or [])
        version_profile = self.catalog.get_version(device.nxos_version) or {}
        version_features = version_profile.get("features", {})

        def on(feature_id: str, default: bool = False) -> bool:
            if enabled:
                return feature_id in enabled
            return default

        def on_vpc_option(feature_id: str, version_key: str) -> bool:
            """vPC sub-options: must be in enabled list AND allowed by NX-OS version profile."""
            if not enabled:
                return version_features.get(version_key, False)
            if feature_id not in enabled:
                return False
            return version_features.get(version_key, True)

        baseline = set(device.baseline_options or [])

        def baseline_on(option_id: str) -> bool:
            return option_id in baseline

        features = {
            "interface_vlan": on("interface_vlan", True),
            "lldp": on("lldp", True),
            "lacp": on("lacp", True),
            "vpc": on("vpc", device.vpc is not None),
            "hsrp": on("hsrp", "hsrp" in enabled),
            "storm_control": on("storm_control", True),
            "vpc_peer_gateway": on_vpc_option("vpc_peer_gateway", "vpc_peer_gateway"),
            "vpc_auto_recovery": on_vpc_option("vpc_auto_recovery", "vpc_auto_recovery"),
            "vpc_arp_sync": on_vpc_option("vpc_arp_sync", "vpc_arp_sync"),
            "hsrp_version": version_features.get("hsrp_version", 2),
            "bfd": on("bfd", False),
            "nxapi": on("nxapi", False),
            "bash": on("bash", False),
            "ntp": on("ntp", bool(device.ntp_servers)),
            "logging": on("logging", bool(device.logging_hosts)),
            "snmp": on("snmp", bool(device.snmp_location)),
            "vpc_orphan_suspend": on_vpc_option("vpc_orphan_suspend", "vpc_auto_recovery"),
            "vpc_peer_switch": on("vpc_peer_switch", device.vpc.peer_switch if device.vpc else False),
            "vpc_delay_restore": on("vpc_delay_restore", bool(device.vpc and device.vpc.delay_restore)),
            "vxlan": on("vxlan", False),
            "baseline_cfs": baseline_on("baseline_cfs"),
            "baseline_copp": baseline_on("baseline_copp"),
            "baseline_no_pwd_check": baseline_on("baseline_no_pwd_check"),
            "baseline_snmp_traps": baseline_on("baseline_snmp_traps"),
            "baseline_spanning_tree": baseline_on("baseline_spanning_tree"),
            "baseline_cli_aliases": baseline_on("baseline_cli_aliases"),
            "baseline_icam": baseline_on("baseline_icam"),
            "baseline_vrf_keepalive": baseline_on("baseline_vrf_keepalive"),
            "baseline_errdisable_recovery": baseline_on("baseline_errdisable_recovery"),
            "baseline_icmp_redirects": baseline_on("baseline_icmp_redirects"),
            "baseline_vpc_delay_restore_vlan": baseline_on("baseline_vpc_delay_restore_vlan"),
            "baseline_no_dns_lookup": baseline_on("baseline_no_dns_lookup"),
            "baseline_exec_timeout": baseline_on("baseline_exec_timeout"),
            "baseline_logging_source": baseline_on("baseline_logging_source"),
            "aaa_tacacs": on("aaa_tacacs", False),
        }
        
        logger.info(f"RENDERER_FEATURE_FLAGS",
                   hostname=device.hostname,
                   vpc_enabled=features["vpc"],
                   lacp_enabled=features["lacp"],
                   lldp_enabled=features["lldp"])
        
        return features

    def render_device_config(
        self, device: Device, template_name: str = None, metadata: dict = None
    ) -> str:
        """Renders NX-OS configuration for the device using version-aware templates."""
        logger.info(f"RENDERER_START",
                   hostname=device.hostname,
                   template_name=template_name,
                   nxos_version=device.nxos_version)
        
        template_file = self._resolve_template(device, template_name)
        logger.info(f"RENDERER_TEMPLATE_RESOLVED",
                   hostname=device.hostname,
                   template_file=template_file)
        
        template = self.env.get_template(template_file)
        meta = dict(metadata or {})
        meta.setdefault("nxos_version", device.nxos_version)
        version_profile = self.catalog.get_version(device.nxos_version) or {}
        if not device.boot_image and version_profile.get("boot_image"):
            meta.setdefault("boot_image", version_profile["boot_image"])
        
        logger.info(f"RENDERER_BEFORE_RENDER",
                   hostname=device.hostname,
                   metadata_keys=list(meta.keys()),
                   device_interfaces_count=len(device.interfaces) if device.interfaces else 0,
                   device_port_channels_count=len(device.port_channels) if device.port_channels else 0,
                   device_uplink_config_count=len(device.uplink_config) if device.uplink_config else 0,
                   device_downlink_config_count=len(device.downlink_config) if device.downlink_config else 0)
        
        try:
            rendered = template.render(
                device=device,
                metadata=meta,
                features=self._feature_flags(device),
            )
            
            logger.info(f"RENDERER_RENDER_COMPLETE",
                       hostname=device.hostname,
                       rendered_length=len(rendered) if rendered else 0,
                       rendered_preview=rendered[:500] if rendered and len(rendered) > 0 else "EMPTY")
            
            return rendered
        except Exception as e:
            logger.error(f"RENDERER_RENDER_ERROR",
                        hostname=device.hostname,
                        error=str(e),
                        error_type=type(e).__name__)
            raise
