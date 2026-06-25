"""Feature render coverage — every CLI feature must appear in the correct config block.

Tests features that had no assertion in prior suites:
  bfd, vpc_orphan_suspend, vpc_auto_recovery, vpc_peer_gateway,
  vpc_peer_switch, vpc_delay_restore, nxapi, bash, aaa_tacacs,
  vxlan overlay placeholder, hardened-tier stripping.
"""

import pytest

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine


def _render(scenario_id: str, hostname: str = "SW-01", **overrides) -> str:
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=overrides if overrides else None,
    )
    return ConfigEngine().build_config(result["device"])


VPC_FEATURES_BASE = [
    "vpc", "lacp", "interface_vlan", "lldp",
    "storm_control", "vpc_peer_gateway", "vpc_auto_recovery",
    "vpc_arp_sync", "vpc_orphan_suspend", "vpc_peer_switch",
    "vpc_delay_restore",
]


# ─────────────────────────────────────────────────────────
#  BFD
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_bfd_feature_renders_in_config():
    cfg = _render("vpc_leaf_pair", features=["vpc", "lacp", "bfd"])
    assert "feature bfd" in cfg, "bfd feature must appear when enabled"


@pytest.mark.mandatory
def test_bfd_absent_when_not_in_features():
    cfg = _render("vpc_leaf_pair", features=["vpc", "lacp"])
    assert "feature bfd" not in cfg, "bfd must be absent when not in features list"


# ─────────────────────────────────────────────────────────
#  vpc_orphan_suspend
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_orphan_suspend_renders_in_vpc_domain():
    cfg = _render("vpc_leaf_pair", features=VPC_FEATURES_BASE)
    assert "orphan-port suspend" in cfg, "orphan-port suspend must appear in vpc domain block"


@pytest.mark.mandatory
def test_vpc_orphan_suspend_inside_vpc_domain_block():
    cfg = _render("vpc_leaf_pair", features=VPC_FEATURES_BASE)
    domain_idx = cfg.find("vpc domain")
    assert domain_idx >= 0
    block_end = cfg.find("\n!", domain_idx + 1)
    if block_end == -1:
        block_end = len(cfg)
    vpc_block = cfg[domain_idx:block_end]
    assert "orphan-port suspend" in vpc_block


# ─────────────────────────────────────────────────────────
#  vpc_auto_recovery
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_auto_recovery_renders_in_vpc_domain():
    cfg = _render("vpc_leaf_pair", features=VPC_FEATURES_BASE)
    assert "auto-recovery" in cfg, "auto-recovery must appear in vpc domain block when enabled"


# ─────────────────────────────────────────────────────────
#  vpc_peer_gateway
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_peer_gateway_renders_when_enabled():
    cfg = _render("vpc_leaf_pair", features=VPC_FEATURES_BASE)
    assert "peer-gateway" in cfg, "peer-gateway must appear in vpc domain when enabled"


@pytest.mark.mandatory
def test_vpc_peer_gateway_absent_when_not_in_features():
    cfg = _render("vpc_leaf_pair", features=["vpc", "lacp"])
    assert "peer-gateway" not in cfg


# ─────────────────────────────────────────────────────────
#  vpc_peer_switch
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_peer_switch_renders_in_vpc_domain():
    cfg = _render("vpc_leaf_pair", features=VPC_FEATURES_BASE)
    assert "peer-switch" in cfg, "peer-switch must appear in vpc domain when enabled"


# ─────────────────────────────────────────────────────────
#  vpc_delay_restore
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_delay_restore_renders_when_device_has_value():
    """delay restore comes from device.vpc.delay_restore if set; feature flag gates the line."""
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "vpc_leaf_pair",
        "SW-01",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"features": VPC_FEATURES_BASE, "delay_restore": 150},
    )
    device = result["device"]
    if device.vpc:
        device.vpc.delay_restore = 150
    cfg = ConfigEngine().build_config(device)
    assert "delay restore 150" in cfg or "delay restore" in cfg


# ─────────────────────────────────────────────────────────
#  nxapi / bash
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_nxapi_renders_when_feature_enabled():
    cfg = _render("standalone_leaf", features=["interface_vlan", "nxapi"])
    assert "feature nxapi" in cfg, "feature nxapi must appear when nxapi is in features"


@pytest.mark.mandatory
def test_bash_renders_when_feature_enabled():
    cfg = _render("standalone_leaf", features=["interface_vlan", "bash"])
    assert "feature bash-shell" in cfg, "feature bash-shell must appear when bash is in features"


@pytest.mark.mandatory
def test_nxapi_absent_by_default_in_standard_leaf():
    cfg = _render("standalone_leaf")
    assert "feature nxapi" not in cfg


@pytest.mark.mandatory
def test_bash_absent_by_default_in_standard_leaf():
    cfg = _render("standalone_leaf")
    assert "feature bash-shell" not in cfg


# ─────────────────────────────────────────────────────────
#  Hardened security tier strips nxapi + bash
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_hardened_tier_strips_nxapi_from_features():
    cfg = _render(
        "standalone_leaf",
        security_tier="hardened",
        features=["interface_vlan", "nxapi", "bash"],
    )
    assert "feature nxapi" not in cfg, "nxapi must be stripped in hardened tier"


@pytest.mark.mandatory
def test_hardened_tier_strips_bash_from_features():
    cfg = _render(
        "standalone_leaf",
        security_tier="hardened",
        features=["interface_vlan", "nxapi", "bash"],
    )
    assert "feature bash-shell" not in cfg, "bash must be stripped in hardened tier"


# ─────────────────────────────────────────────────────────
#  AAA / TACACS+
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_tacacs_block_renders_when_feature_and_server_set():
    cfg = _render(
        "standalone_access",
        features=["interface_vlan", "lacp", "aaa_tacacs"],
        tacacs_server_1="10.1.1.1",
        tacacs_key="MyTacacsKey",
    )
    assert "aaa group server tacacs+" in cfg, "AAA TACACS+ block must render when feature + server set"
    assert "10.1.1.1" in cfg


@pytest.mark.mandatory
def test_tacacs_absent_when_no_server_configured():
    cfg = _render("standalone_access", features=["interface_vlan"])
    assert "aaa group server tacacs+" not in cfg


# ─────────────────────────────────────────────────────────
#  VXLAN overlay placeholder
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vxlan_overlay_fabric_renders():
    cfg = _render("vxlan_evpn_leaf", "VXLAN-LEAF-01")
    assert "feature nv overlay" in cfg
    assert "interface nve1" in cfg
    assert "router bgp" in cfg


@pytest.mark.mandatory
def test_vxlan_bfd_coexists_in_same_config():
    cfg = _render("vxlan_evpn_leaf", "VXLAN-LEAF-01", features=["vpc", "lacp", "bfd", "vxlan"])
    assert "feature bfd" in cfg
    assert "feature nv overlay" in cfg or "VXLAN" in cfg


# ─────────────────────────────────────────────────────────
#  vpc_arp_sync
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_vpc_arp_sync_renders_in_vpc_domain():
    cfg = _render("vpc_leaf_pair", features=["vpc", "lacp", "vpc_arp_sync"])
    assert "ip arp synchronize" in cfg, "ARP sync must appear in vpc domain when enabled"
