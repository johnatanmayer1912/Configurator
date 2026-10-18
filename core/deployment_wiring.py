"""
Cross-switch uplink wiring for multi-switch deployments.

Pass 2 of generate_deployment: after every Device exists in device_by_hostname,
wire core/spine downlinks to leaf uplinks (order-independent).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from models.device_model import Device
from models.interface_model import Interface

logger = logging.getLogger(__name__)


def _ensure_trunk_iface(device: Device, port_name: str, description: str, po_id: int) -> None:
    for iface in device.interfaces:
        if iface.name == port_name:
            iface.description = description
            iface.channel_group = po_id
            iface.channel_mode = "active"
            iface.mode = "trunk"
            return
    new_iface = Interface(
        name=port_name,
        description=description,
        mode="trunk",
        shutdown=False,
    )
    new_iface.channel_group = po_id
    new_iface.channel_mode = "active"
    device.interfaces.append(new_iface)


def _wire_leaf_pair_to_core(
    core_device: Device,
    core_hostname: str,
    leaf_device: Device,
    leaf_hostname: str,
    port_idx: int,
    po_id: int,
    leaf_uplink_start: int,
    leaf_uplink_end: int,
) -> int:
    """Configure one leaf's uplink PO on leaf + downlink pair on core. Returns next port_idx."""
    desc1 = f"to {leaf_hostname} port {leaf_uplink_start}"
    desc2 = f"to {leaf_hostname} port {leaf_uplink_end}"

    core_device.downlink_config = core_device.downlink_config or []
    leaf_device.uplink_config = leaf_device.uplink_config or []

    for uplink_port_idx, core_port_offset, desc in (
        (leaf_uplink_start, 0, desc1),
        (leaf_uplink_end, 1, desc2),
    ):
        uplink_port = f"Ethernet1/{uplink_port_idx}"
        core_port = f"Ethernet1/{port_idx + core_port_offset}"

        leaf_device.uplink_config.append({
            "interface": uplink_port,
            "description": f"to {core_hostname}",
            "mode": "trunk",
            "port_channel": po_id,
        })
        _ensure_trunk_iface(leaf_device, uplink_port, f"to {core_hostname}", po_id)

        core_device.downlink_config.append({
            "interface": core_port,
            "description": desc,
            "mode": "trunk",
            "port_channel": po_id,
            "channel_group": f"{po_id} mode active",
        })
        _ensure_trunk_iface(core_device, core_port, desc, po_id)

    return port_idx + 2


def wire_core_leaf_downlinks(
    device_by_hostname: Dict[str, Device],
    switch_configs: List[Any],
    catalog: Any,
    request_id: str = "",
) -> None:
    """
    Apply core/spine → leaf uplink wiring using a complete hostname index.

    Safe to call after all switches are built (two-pass deployment).
    """
    for switch_config in switch_configs:
        hw_profile = catalog.get_hardware_profile(switch_config.model)
        if not hw_profile:
            continue

        device_class = hw_profile.get("device_class")
        if device_class not in ("core", "spine") and not (
            getattr(switch_config, "role", None) in ("core", "spine")
        ):
            continue

        core_device = device_by_hostname.get(switch_config.hostname)
        if not core_device:
            continue

        downlink_10g_start = hw_profile.get("downlink_10g_start", 1)
        downlink_10g_end = hw_profile.get("downlink_10g_end", 10)
        downlink_1g_start = hw_profile.get("downlink_1g_start", 11)
        downlink_1g_end = hw_profile.get("downlink_1g_end", 20)

        leaf_switches = [
            s for s in switch_configs
            if s.model
            and catalog.get_hardware_profile(s.model)
            and catalog.get_hardware_profile(s.model).get("device_class") in ("leaf_1g", "leaf_10g")
        ]

        core_device.downlink_config = core_device.downlink_config or []

        leaf_10g = [
            s for s in leaf_switches
            if catalog.get_hardware_profile(s.model).get("device_class") == "leaf_10g"
        ]
        port_idx = downlink_10g_start
        po_id = 20
        for leaf in leaf_10g:
            if port_idx > downlink_10g_end:
                break
            leaf_device = device_by_hostname.get(leaf.hostname)
            if not leaf_device:
                logger.warning(
                    "LEAF_DEVICE_NOT_FOUND pass2 hostname=%s core=%s request_id=%s",
                    leaf.hostname,
                    switch_config.hostname,
                    request_id,
                )
                continue
            leaf_hw = catalog.get_hardware_profile(leaf.model) or {}
            port_idx = _wire_leaf_pair_to_core(
                core_device,
                switch_config.hostname,
                leaf_device,
                leaf.hostname,
                port_idx,
                po_id,
                leaf_hw.get("vpc_uplink_start", 53),
                leaf_hw.get("vpc_uplink_end", 54),
            )
            po_id += 1

        leaf_1g = [
            s for s in leaf_switches
            if catalog.get_hardware_profile(s.model).get("device_class") == "leaf_1g"
        ]
        port_idx = downlink_1g_start
        po_id = 21
        for leaf in leaf_1g:
            if port_idx > downlink_1g_end:
                break
            leaf_device = device_by_hostname.get(leaf.hostname)
            if not leaf_device:
                logger.warning(
                    "LEAF_DEVICE_NOT_FOUND_1G pass2 hostname=%s core=%s request_id=%s",
                    leaf.hostname,
                    switch_config.hostname,
                    request_id,
                )
                continue
            leaf_hw = catalog.get_hardware_profile(leaf.model) or {}
            port_idx = _wire_leaf_pair_to_core(
                core_device,
                switch_config.hostname,
                leaf_device,
                leaf.hostname,
                port_idx,
                po_id,
                leaf_hw.get("vpc_uplink_start", 51),
                leaf_hw.get("vpc_uplink_end", 52),
            )
            po_id += 1

        logger.info(
            "CORE_DOWNLINK_WIRED pass2 core=%s downlinks=%s request_id=%s",
            switch_config.hostname,
            len(core_device.downlink_config or []),
            request_id,
        )


def validate_all_vpc_pairs(
    device_by_hostname: Dict[str, Device],
    vpc_pairs: List[Dict[str, Any]],
    device_validator: Any,
) -> List[str]:
    """Validate every vPC pair after all devices are built. Returns error strings."""
    errors: List[str] = []
    for pair in vpc_pairs or []:
        primary = device_by_hostname.get(pair.get("primary"))
        secondary = device_by_hostname.get(pair.get("secondary"))
        if not primary or not secondary:
            continue
        if not primary.vpc or not secondary.vpc:
            continue
        report = device_validator.validate_vpc_pair(primary, secondary)
        if report["status"] != "pass":
            domain = pair.get("domain", "?")
            errors.append(f"vPC domain {domain}: {'; '.join(report['errors'])}")
    return errors
