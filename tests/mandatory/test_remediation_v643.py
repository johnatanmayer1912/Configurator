"""v6.43.0 P0/P1 + Product/UX remediation regressions."""

import re

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from api.main import app
from core.deployment_builder import apply_custom_uplinks_for_switch, resolve_deployment_export_base
from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine
from core.vpc_topology import apply_vpc_topology
from core.catalog_loader import CatalogLoader
from models.device_model import Device, VPCConfig
from models.interface_model import Interface
from utils.app_dirs import get_history_dir

client = TestClient(app)


@pytest.mark.mandatory
def test_nxos_base_vpc_domain_after_port_channels():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "nxos_version": "9.3",
            "local_ka": "10.255.255.1/24",
            "remote_ka": "10.255.255.2",
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    po_pos = cfg.find("interface port-channel")
    vpc_m = re.search(r"^vpc domain ", cfg, re.MULTILINE)
    assert po_pos >= 0
    assert vpc_m is not None
    assert po_pos < vpc_m.start()


@pytest.mark.mandatory
def test_unified_api_preview_mode():
    res = client.post(
        "/api/v1/config/generate",
        json={
            "mode": "preview",
            "device": {
                "hostname": "SW1",
                "mgmt_ip": "10.0.0.1/24",
                "mgmt_gw": "10.0.0.254",
                "model": "Nexus 9336C-FX2",
                "nxos_version": "9.3",
            },
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body.get("preview") is True
    assert "hostname SW1" in body.get("cli", "")


@pytest.mark.mandatory
def test_config_templates_crud():
    res = client.post(
        "/config/templates",
        json={
            "name": "pytest_fabric",
            "description": "test",
            "switches": [{"hostname": "SW1", "model": "Nexus 9336C-FX2", "role": "leaf"}],
            "vpc_pairs": [],
            "uplinks": [],
        },
    )
    assert res.status_code == 200
    tid = res.json()["id"]
    got = client.get(f"/config/templates/{tid}")
    assert got.status_code == 200
    assert got.json()["template"]["name"] == "pytest_fabric"


@pytest.mark.mandatory
def test_uplink_from_ports_to_ports():
    device = Device(
        hostname="LEAF1",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        model="Nexus 9336C-FX2",
        interfaces=[],
    )
    uplinks = [
        {
            "from": "LEAF1",
            "to": "SPINE1",
            "from_ports": "E1/49",
            "to_ports": "E1/1",
            "po_id": 10,
        }
    ]
    apply_custom_uplinks_for_switch(device, "LEAF1", uplinks, {"LEAF1", "SPINE1"})
    assert any(i.name == "Ethernet1/49" for i in device.interfaces)


@pytest.mark.mandatory
def test_resolve_deployment_export_base_custom_dir():
    history = Path(get_history_dir())
    custom = history / "custom_batch"
    custom.mkdir(parents=True, exist_ok=True)
    base = resolve_deployment_export_base(str(custom), history, preview=True)
    assert "custom_batch" in str(base)


@pytest.mark.mandatory
def test_routed_keepalive_topology():
    catalog = CatalogLoader()
    hw = catalog.get_hardware_profile("Nexus 9336C-FX2")
    device = Device(
        hostname="CORE1",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        model="Nexus 9336C-FX2",
        vpc=VPCConfig(
            domain_id=100,
            role="primary",
            keepalive_vrf="keepalive",
            local_keepalive_ip="10.255.255.1",
            remote_keepalive_ip="10.255.255.2",
            peer_link_id=1,
            peer_link_interfaces=["Ethernet1/49", "Ethernet1/50"],
            keepalive_interfaces=["Ethernet1/51"],
        ),
        interfaces=[],
    )
    defaults = {"baseline_options": ["baseline_keepalive_routed"]}
    apply_vpc_topology(device, defaults, hw, peer_hostname="CORE2")
    assert device.vpc.keepalive_routed_direct is True
    ka = next(i for i in device.interfaces if i.name == "Ethernet1/51")
    assert ka.ip_address is not None
    assert "10.255.255.1" in ka.ip_address
