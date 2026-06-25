"""Post-processing device models after scenario/intent resolution."""

import ipaddress
import re
from typing import List, Optional

from models.device_model import Device
from models.l3_models import HSRPConfig, SVI


def _vip_from_cidr(cidr: str, last_octet: int = 1) -> str:
    network = ipaddress.ip_interface(cidr).network
    base = str(network.network_address).split(".")
    if len(base) == 4:
        base[3] = str(last_octet)
        return ".".join(base)
    return str(network.network_address)


def apply_hsrp(device: Device, vpc_role: str = "primary") -> None:
    """Attach HSRP to SVIs when hsrp feature is enabled."""
    if "hsrp" not in (device.enabled_features or []):
        return
    priority = 110 if vpc_role == "primary" else 100
    updated: List[SVI] = []
    for idx, svi in enumerate(device.svis):
        if svi.hsrp:
            updated.append(svi)
            continue
        group = svi.vlan_id
        vip = _vip_from_cidr(svi.ip_address, 1)
        updated.append(
            SVI(
                vlan_id=svi.vlan_id,
                ip_address=svi.ip_address,
                description=svi.description,
                vrf=svi.vrf,
                hsrp=HSRPConfig(group=group, vip=vip, priority=priority, preempt=True),
            )
        )
    device.svis = updated


def apply_security_tier(device: Device, tier: str) -> None:
    """Adjust features and defaults for standard vs hardened tier."""
    device.security_tier = tier
    features = set(device.enabled_features or [])
    if tier == "hardened":
        features -= {"nxapi", "bash"}
        features.add("storm_control")
        features.add("logging")
        features.add("ntp")
        if not device.logging_hosts:
            device.logging_hosts = ["10.255.255.254"]
    device.enabled_features = sorted(features)


def apply_management_baseline(device: Device, overrides: dict) -> None:
    """Apply NTP/logging/SNMP from UI overrides."""
    ntp = overrides.get("ntp_servers") or overrides.get("ntp_server")
    if isinstance(ntp, str) and ntp.strip():
        device.ntp_servers = [s.strip() for s in ntp.split(",") if s.strip()]
    elif isinstance(ntp, list):
        device.ntp_servers = ntp

    log = overrides.get("logging_hosts") or overrides.get("logging_host")
    if isinstance(log, str) and log.strip():
        device.logging_hosts = [s.strip() for s in log.split(",") if s.strip()]
    elif isinstance(log, list):
        device.logging_hosts = log

    if overrides.get("snmp_location"):
        device.snmp_location = str(overrides["snmp_location"])
    if overrides.get("site_location"):
        loc = str(overrides["site_location"])
        if loc not in ("NET_DEVICE_LOCATION", "LOCATION"):
            device.site_location = loc
    elif overrides.get("site_name") and not device.site_location:
        device.site_location = str(overrides["site_name"])
    if overrides.get("network_name"):
        nn = str(overrides["network_name"])
        if nn != "NETWORK_NAME":
            device.network_name = nn
    elif overrides.get("site_name") and (not device.network_name or device.network_name == "NETWORK_NAME"):
        device.network_name = str(overrides["site_name"])
    if overrides.get("snmp_trap_host_1"):
        device.snmp_trap_host_1 = str(overrides["snmp_trap_host_1"])
    if overrides.get("snmp_trap_host_2"):
        device.snmp_trap_host_2 = str(overrides["snmp_trap_host_2"])
    if overrides.get("snmp_v3_user"):
        device.snmp_v3_user = str(overrides["snmp_v3_user"])
    if overrides.get("boot_image"):
        device.boot_image = str(overrides["boot_image"])
    if overrides.get("tacacs_server_1"):
        device.tacacs_server_1 = str(overrides["tacacs_server_1"]).strip()
    if overrides.get("tacacs_key"):
        device.tacacs_key = str(overrides["tacacs_key"]).strip()
    if overrides.get("spectrum_user"):
        device.spectrum_user = bool(overrides["spectrum_user"])

    if overrides.get("admin_user"):
        device.admin_user = str(overrides["admin_user"])
    pwd = overrides.get("admin_password")
    if pwd:
        device.admin_password = str(pwd)
        device.create_local_user = True

    if "ntp" in (device.enabled_features or []) and not device.ntp_servers:
        device.ntp_servers = ["10.255.255.254"]
    if "logging" in (device.enabled_features or []) and not device.logging_hosts:
        device.logging_hosts = ["10.255.255.254"]


def apply_fabric_defaults(device: Device, overrides: Optional[dict] = None) -> None:
    """VXLAN/EVPN foundation — lab defaults when overlay feature enabled."""
    if "vxlan" not in (device.enabled_features or []):
        return
    ov = overrides or {}
    device.fabric_bgp_asn = int(ov.get("fabric_bgp_asn", device.fabric_bgp_asn or 65001))
    device.fabric_loopback = str(ov.get("fabric_loopback", device.fabric_loopback or "10.255.0.1/32"))
    device.fabric_vni = int(ov.get("fabric_vni", device.fabric_vni or 10000))


def enrich_device(device: Device, overrides: Optional[dict] = None, vpc_role: str = "primary") -> Device:
    """Full post-processing pipeline for scenario-generated devices."""
    overrides = overrides or {}
    tier = overrides.get("security_tier", getattr(device, "security_tier", "standard"))
    apply_security_tier(device, tier)
    apply_management_baseline(device, overrides)
    apply_fabric_defaults(device, overrides)
    apply_hsrp(device, vpc_role)
    return device
