"""P0 audit remediation regressions — keepalive symmetry, trunk VLANs, upload validation."""

import pytest
from fastapi.testclient import TestClient

from api.main import app, _build_deployment_vpc_config
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine

client = TestClient(app)


class _Sw:
    def __init__(self, hostname, local_ka="", remote_ka=""):
        self.hostname = hostname
        self.local_ka = local_ka
        self.remote_ka = remote_ka
        self.vpc_pl_ints = "Eth1/49-50"
        self.vpc_peer_link_id = 1
        self.keepalive_po_id = 2
        self.vpc_system_priority = 32667
        self.baseline_options = []


@pytest.mark.mandatory
def test_build_deployment_vpc_config_secondary_keepalive_swap():
    primary = _Sw("LEAF1-A")
    secondary = _Sw("LEAF1-B")
    pair = {"domain": 100, "primary": "LEAF1-A", "secondary": "LEAF1-B", "peer_link_ports": "Eth1/49-50"}

    p_vpc = _build_deployment_vpc_config(pair, primary, True, partner_config=secondary)
    s_vpc = _build_deployment_vpc_config(pair, secondary, False, partner_config=primary)

    assert p_vpc.local_keepalive_ip.split("/")[0] != p_vpc.remote_keepalive_ip.split("/")[0]
    assert p_vpc.local_keepalive_ip.split("/")[0] == s_vpc.remote_keepalive_ip.split("/")[0]
    assert p_vpc.remote_keepalive_ip.split("/")[0] == s_vpc.local_keepalive_ip.split("/")[0]
    assert s_vpc.role == "secondary"
    assert s_vpc.role_priority == 8192


@pytest.mark.mandatory
def test_vpc_peer_link_renders_trunk_allowed_vlan():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "local_ka": "10.255.255.1",
            "remote_ka": "10.255.255.2",
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "interface port-channel1" in cfg
    po_start = cfg.find("interface port-channel1")
    po_end = cfg.find("\ninterface ", po_start + 1)
    po_block = cfg[po_start:po_end if po_end > 0 else len(cfg)]
    assert "vpc peer-link" in po_block
    assert "switchport trunk allowed vlan" in po_block


@pytest.mark.mandatory
def test_l3_keepalive_port_channel_has_no_switchport():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "DC-LEAF-01-A",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "local_ka": "10.255.255.1/24",
            "remote_ka": "10.255.255.2",
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    ka_start = cfg.find("interface port-channel2")
    assert ka_start >= 0
    ka_end = cfg.find("\ninterface ", ka_start + 1)
    ka_block = cfg[ka_start:ka_end if ka_end > 0 else len(cfg)]
    assert "no switchport" in ka_block


@pytest.mark.mandatory
def test_config_upload_basic_path_does_not_500():
    """Basic upload path must not crash (P0 fix for ValidationSeverity/add_error)."""
    res = client.post(
        "/config/upload",
        json={
            "config_text": "!",
            "hardware_model": "Nexus 9336C-FX2",
            "nxos_version": "9.3",
            "validation_level": "basic",
        },
    )
    assert res.status_code == 200
    assert "validation_id" in res.json()


@pytest.mark.mandatory
def test_deployment_rejects_empty_switch_list():
    res = client.post("/generate-deployment", json={"switches": [], "vpc_pairs": [], "uplinks": []})
    assert res.status_code == 422
