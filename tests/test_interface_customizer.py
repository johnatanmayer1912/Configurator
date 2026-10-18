"""Interface Planner — vPC port-channels, presets, pair mirroring, edge cases."""

import re

from core.engine import ConfigEngine
from core.interface_customizer import apply_interface_customizations, normalize_interface_name
from core.scenario_engine import ScenarioEngine


def _apply_leaf(plans=None, hostname="DC-LEAF-01-A", **extra):
    overrides = {
        "uplink_options": {"uplink_fiber_pair": False, "uplink_fiber_quad": False},
        **extra,
    }
    if plans:
        overrides["interface_plans"] = plans
    return ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        hostname,
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides,
    )


def _block(cfg: str, name: str) -> str:
    marker = f"interface {name}"
    start = cfg.find(marker)
    assert start >= 0, f"{name} not in config"
    end = cfg.find("\ninterface ", start + 1)
    return cfg[start:end if end > 0 else len(cfg)]


def test_leaf_default_infra_only_no_bulk_access():
    result = ScenarioEngine().apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    device = result["device"]
    access = [i for i in device.interfaces if i.mode == "access"]
    assert len(access) == 0
    cfg = ConfigEngine().build_config(device)
    assert "vpc domain" in cfg
    assert "interface port-channel1" in cfg
    assert "interface port-channel2" in cfg
    assert "interface port-channel30" in cfg
    # Fiber uplink uses Ethernet1/53-54 (vpc_uplink_start/end), not Ethernet1/49-50 (keepalive)
    assert "channel-group 30 mode active" in _block(cfg, "Ethernet1/53")
    assert "Access_Port_" not in cfg


def test_normalize_interface_name():
    assert normalize_interface_name("eth1/5") == "Ethernet1/5"
    assert normalize_interface_name("Ethernet1/12") == "Ethernet1/12"


def test_vpc_access_port_channel_primary_and_secondary_mirrored():
    plans = [
        {
            "interface": "Ethernet1/5",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 250,
            "vlan_name": "SERVERS",
            "description": "Lab_Server_05",
        }
    ]
    result = _apply_leaf(plans)
    pri = result["device"]
    sec = result["pair"]["secondary"]["device"]

    pri_po = next(po for po in pri.port_channels if po.number == 10)
    sec_po = next(po for po in sec.port_channels if po.number == 10)
    assert pri_po.mode == "access"
    assert pri_po.access_vlan == 250
    assert pri_po.vpc_id == 10
    assert pri_po.description == "Lab_Server_05"
    assert sec_po.access_vlan == 250
    assert sec_po.member_interfaces == ["Ethernet1/5"]

    pri_intf = next(i for i in pri.interfaces if i.name == "Ethernet1/5")
    sec_intf = next(i for i in sec.interfaces if i.name == "Ethernet1/5")
    assert pri_intf.channel_group == 10
    assert sec_intf.channel_group == 10

    pri_cfg = ConfigEngine().build_config(pri)
    sec_cfg = ConfigEngine().build_config(sec)

    for cfg in (pri_cfg, sec_cfg):
        po_blk = _block(cfg, "port-channel10")
        assert "switchport mode access" in po_blk
        assert "switchport access vlan 250" in po_blk
        assert "vpc 10" in po_blk
        assert "description Lab_Server_05" in po_blk
        eth_blk = _block(cfg, "Ethernet1/5")
        assert "channel-group 10 mode active" in eth_blk
        assert "Part_Of_vPC10_Access" in eth_blk

    assert any(v.id == 250 and v.name == "SERVERS" for v in pri.vlans)
    assert any(v.id == 250 for v in sec.vlans)


def test_multiple_vpc_port_channels_increment_from_10():
    plans = [
        {
            "interface": "Ethernet1/3",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 100,
            "vlan_name": "FABRIC_100",
        },
        {
            "interface": "Ethernet1/4",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 101,
            "vlan_name": "FABRIC_101",
        },
        {
            "interface": "Ethernet1/6",
            "preset": "trunk_all",
            "vpc_port_channel": True,
            "mode": "trunk",
            "trunk_vlans": "10,20,30",
            "description": "Multi_VLAN_Trunk",
        },
    ]
    result = _apply_leaf(plans)
    nums = sorted(po.number for po in result["device"].port_channels if po.number >= 10)
    assert nums == [10, 11, 12]
    trunk_po = next(po for po in result["device"].port_channels if po.number == 12)
    assert trunk_po.mode == "trunk"
    assert trunk_po.trunk_vlans == "10,20,30"


def test_existing_vlan_name_not_duplicated():
    plans = [
        {
            "interface": "Ethernet1/8",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 100,
            "vlan_name": "CUSTOM_NAME",
        }
    ]
    result = _apply_leaf(plans)
    vlan_100 = [v for v in result["device"].vlans if v.id == 100]
    assert len(vlan_100) == 1
    assert vlan_100[0].name == "FABRIC_100"  # scenario already created FABRIC_100


def test_reserved_peer_link_port_skipped():
    plans = [
        {
            "interface": "Ethernet1/51",  # vpc_peer_link port for Nexus 93180YC-EX
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 999,
        }
    ]
    result = _apply_leaf(plans)
    assert not any(po.number >= 10 for po in result["device"].port_channels)
    pl_intf = next(i for i in result["device"].interfaces if i.name == "Ethernet1/51")
    assert pl_intf.channel_group == 1  # still peer-link


def test_standalone_access_direct_no_vpc_po():
    plans = [
        {
            "interface": "Ethernet1/10",
            "preset": "access_vlan",
            "vpc_port_channel": True,
            "mode": "access",
            "vlan_id": 50,
            "vlan_name": "USERS",
        }
    ]
    result = ScenarioEngine().apply_scenario(
        "standalone_access",
        "ACCESS-01",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"interface_plans": plans},
    )
    device = result["device"]
    assert not any(po.number >= 10 for po in device.port_channels)
    intf = next(i for i in device.interfaces if i.name == "Ethernet1/10")
    assert intf.mode == "access"
    assert intf.vlan == 50


def test_custom_cli_lines_rendered():
    plans = [
        {
            "interface": "Ethernet1/12",
            "preset": "custom",
            "custom_cli": "  switchport mode access\n  switchport access vlan 333\n  description My_Custom",
        }
    ]
    result = _apply_leaf(plans)
    cfg = ConfigEngine().build_config(result["device"])
    blk = _block(cfg, "Ethernet1/12")
    assert "switchport access vlan 333" in blk
    assert "description My_Custom" in blk


def test_bring_up_preset():
    plans = [{"interface": "Ethernet1/20", "preset": "bring_up"}]
    result = _apply_leaf(plans)
    intf = next(i for i in result["device"].interfaces if i.name == "Ethernet1/20")
    assert intf.mode == "bare"
    cfg = ConfigEngine().build_config(result["device"])
    blk = _block(cfg, "Ethernet1/20")
    assert "no shutdown" in blk
    assert "switchport" not in blk


def test_vpc_core_pair_still_no_bulk_access():
    result = ScenarioEngine().apply_scenario(
        "vpc_core_pair",
        "CORE1-VPC",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
    )
    access = [i for i in result["device"].interfaces if i.mode == "access"]
    assert len(access) == 0


def test_pair_secondary_same_po_ids_various_ports():
    """Regression: ports 5, 21, 42 on pair — identical Po numbers and members on A/B."""
    ports = ["Ethernet1/5", "Ethernet1/21", "Ethernet1/42"]
    plans = []
    for idx, port in enumerate(ports):
        plans.append(
            {
                "interface": port,
                "preset": "access_vlan",
                "vpc_port_channel": True,
                "mode": "access",
                "vlan_id": 300 + idx,
                "vlan_name": f"VLAN_{300 + idx}",
                "description": f"Host_{port.split('/')[-1]}",
            }
        )
    result = _apply_leaf(plans)
    pri = result["device"]
    sec = result["pair"]["secondary"]["device"]
    pri_pos = {po.number: po for po in pri.port_channels if po.number >= 10}
    sec_pos = {po.number: po for po in sec.port_channels if po.number >= 10}
    assert pri_pos.keys() == sec_pos.keys() == {10, 11, 12}
    for num in (10, 11, 12):
        assert pri_pos[num].member_interfaces == sec_pos[num].member_interfaces
        assert pri_pos[num].access_vlan == sec_pos[num].access_vlan

    pri_cfg = ConfigEngine().build_config(pri)
    sec_cfg = ConfigEngine().build_config(sec)
    for po in (10, 11, 12):
        assert f"interface port-channel{po}" in pri_cfg
        assert f"interface port-channel{po}" in sec_cfg
        assert re.search(rf"interface port-channel{po}\n  description Host_", pri_cfg)
