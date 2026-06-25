"""Tests for device enricher, HSRP, and risk analyzer."""

from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine
from core.engine import ConfigEngine
from core.device_enricher import apply_hsrp, apply_security_tier
from core.risk_analyzer import RiskAnalyzer
from models.device_model import Device
from models.vlan_model import VLAN
from models.l3_models import SVI


def test_hsrp_applied_when_feature_enabled():
    device = Device(
        hostname="T", mgmt_ip="10.0.0.1/24", mgmt_gw="10.0.0.254", model="Generic",
        vlans=[VLAN(10, "TEN")],
        svis=[SVI(vlan_id=10, ip_address="10.10.0.2/24")],
        enabled_features=["hsrp"],
    )
    apply_hsrp(device, "primary")
    assert device.svis[0].hsrp is not None
    assert device.svis[0].hsrp.vip == "10.10.0.1"
    assert device.svis[0].hsrp.priority == 110


def test_hardened_tier_strips_nxapi():
    device = Device(
        hostname="T", mgmt_ip="10.0.0.1/24", mgmt_gw="10.0.0.254", model="Generic",
        enabled_features=["nxapi", "bash", "lldp"],
    )
    apply_security_tier(device, "hardened")
    assert "nxapi" not in device.enabled_features
    assert "bash" not in device.enabled_features
    assert "logging" in device.enabled_features


def test_vpc_leaf_hsrp_in_config():
    engine = ScenarioEngine(CatalogLoader())
    result = engine.apply_scenario(
        "vpc_leaf_pair", "LEAF-A", "HQ", "10.10.10.10/24", "10.10.10.1",
        overrides={"peer_link_interfaces": "Ethernet1/53, Ethernet1/54"},
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "hsrp 100" in cfg or "hsrp 10" in cfg
    assert "role priority 4096" in cfg
    assert "orphan-port suspend" in cfg
    assert "ntp server" in cfg
    assert "feature interface-vlanfeature" not in cfg


def test_risk_analyzer_ignores_no_shutdown():
    analyzer = RiskAnalyzer()
    lines = ["interface Eth1/1", " no shutdown", "vlan 10", " name TEST"]
    result = analyzer.analyze(lines)
    shutdown_findings = [f for f in result["findings"] if "shutdown" in f["command"].lower()]
    assert len(shutdown_findings) == 0
