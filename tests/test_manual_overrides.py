"""Tests for manual VLAN/interface override merging."""

from core.manual_overrides import apply_manual_overrides
from core.scenario_engine import ScenarioEngine
from models.device_model import Device
from models.vlan_model import VLAN


def test_apply_custom_vlan_and_interface_lines():
    device = Device(
        hostname="TEST",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        model="Generic",
        vlans=[VLAN(10, "EXISTING")],
    )
    apply_manual_overrides(
        device,
        {
            "custom_vlans": [{"id": 99, "name": "EXTRA"}],
            "custom_svis": [{"vlan_id": 99, "ip_address": "192.168.99.1/24"}],
            "interface_lines": "Ethernet1/1 mode access vlan 99\nEthernet1/2 trunk",
        },
    )
    vlan_ids = {v.id for v in device.vlans}
    assert 99 in vlan_ids
    assert 10 in vlan_ids
    assert any(s.vlan_id == 99 for s in device.svis)
    names = {i.name for i in device.interfaces}
    assert "Ethernet1/1" in names
    assert "Ethernet1/2" in names


def test_scenario_engine_applies_manual_overrides():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "standalone_access",
        "ACCESS-01",
        "LAB",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "custom_vlans": [{"id": 500, "name": "GUEST"}],
            "interface_lines": "Ethernet1/47 mode access vlan 500",
        },
    )
    device = result["device"]
    assert any(v.id == 500 for v in device.vlans)
    assert any(i.name == "Ethernet1/47" for i in device.interfaces)


def test_vxlan_scenario_enables_overlay_feature():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vxlan_evpn_leaf",
        "LEAF-01-A",
        "DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"peer_link_interfaces": "Ethernet1/53, Ethernet1/54"},
    )
    assert "vxlan" in result["enabled_features"]
    assert result["device"].vpc is not None
