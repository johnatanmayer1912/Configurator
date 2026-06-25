"""Baseline options coverage — all 14 institutional baseline options must render.

Each test enables one option via scenario overrides and asserts the
corresponding NX-OS CLI line is present in the rendered config.
"""

import pytest

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine


def _render_with_baseline(baseline_ids: list, scenario_id: str = "vpc_core_pair",
                           hostname: str = "CORE-01", **extra_overrides) -> str:
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        scenario_id,
        hostname,
        "HQ_DC",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"baseline_options": baseline_ids, **extra_overrides},
    )
    return ConfigEngine().build_config(result["device"])


# ─────────────────────────────────────────────────────────
#  CFS Ethernet Distribute
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_cfs_renders():
    cfg = _render_with_baseline(["baseline_cfs"])
    assert "cfs eth distribute" in cfg


@pytest.mark.mandatory
def test_baseline_cfs_absent_when_not_enabled():
    cfg = _render_with_baseline([])
    assert "cfs eth distribute" not in cfg


# ─────────────────────────────────────────────────────────
#  CoPP Strict
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_copp_renders():
    cfg = _render_with_baseline(["baseline_copp"])
    assert "copp profile strict" in cfg


# ─────────────────────────────────────────────────────────
#  No Password Strength Check
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_no_pwd_check_renders():
    cfg = _render_with_baseline(["baseline_no_pwd_check"])
    assert "no password strength-check" in cfg


# ─────────────────────────────────────────────────────────
#  SNMP Trap Baseline
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_snmp_traps_renders_rmon_events():
    cfg = _render_with_baseline(["baseline_snmp_traps"])
    assert "rmon event" in cfg
    assert "snmp-server enable traps" in cfg


@pytest.mark.mandatory
def test_baseline_snmp_traps_includes_callhome():
    cfg = _render_with_baseline(["baseline_snmp_traps"])
    assert "callhome" in cfg


# ─────────────────────────────────────────────────────────
#  Spanning-Tree Root Priority
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_spanning_tree_renders():
    cfg = _render_with_baseline(["baseline_spanning_tree"], spanning_tree_priority=8192)
    assert "spanning-tree vlan" in cfg
    assert "8192" in cfg


# ─────────────────────────────────────────────────────────
#  CLI Aliases
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_cli_aliases_renders():
    cfg = _render_with_baseline(["baseline_cli_aliases"])
    assert "cli alias name wr" in cfg
    assert "cli alias name shint" in cfg
    assert "cli alias name shintd" in cfg


# ─────────────────────────────────────────────────────────
#  ICAM Monitor Scale
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_icam_renders():
    cfg = _render_with_baseline(["baseline_icam"])
    assert "icam monitor scale" in cfg


# ─────────────────────────────────────────────────────────
#  Dedicated Keepalive VRF (vPC-only option)
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_vrf_keepalive_renders_in_vpc_scenario():
    cfg = _render_with_baseline(
        ["baseline_vrf_keepalive"],
        scenario_id="vpc_core_pair",
    )
    assert "vrf context" in cfg, "vrf context must be present for keepalive vrf baseline"


# ─────────────────────────────────────────────────────────
#  Errdisable Recovery
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_errdisable_recovery_renders():
    cfg = _render_with_baseline(["baseline_errdisable_recovery"])
    assert "errdisable recovery interval 300" in cfg
    assert "errdisable recovery cause link-flap" in cfg


@pytest.mark.mandatory
def test_baseline_errdisable_absent_when_not_enabled():
    cfg = _render_with_baseline([])
    assert "errdisable recovery interval" not in cfg


# ─────────────────────────────────────────────────────────
#  Disable ICMP Redirects
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_icmp_redirects_renders():
    cfg = _render_with_baseline(["baseline_icmp_redirects"])
    assert "no ip icmp redirect" in cfg


@pytest.mark.mandatory
def test_baseline_icmp_redirects_absent_when_not_enabled():
    cfg = _render_with_baseline([])
    assert "no ip icmp redirect" not in cfg


# ─────────────────────────────────────────────────────────
#  vPC Delay Restore SVI (vPC-only option)
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_vpc_delay_restore_vlan_renders_in_vpc_domain():
    cfg = _render_with_baseline(
        ["baseline_vpc_delay_restore_vlan"],
        scenario_id="vpc_core_pair",
    )
    assert "delay restore interface-vlan 150" in cfg, (
        "delay restore interface-vlan must appear in vpc domain when baseline option enabled"
    )


@pytest.mark.mandatory
def test_baseline_vpc_delay_restore_vlan_absent_when_not_enabled():
    cfg = _render_with_baseline([], scenario_id="vpc_core_pair")
    assert "delay restore interface-vlan 150" not in cfg


# ─────────────────────────────────────────────────────────
#  Disable DNS Lookup
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_no_dns_lookup_renders():
    cfg = _render_with_baseline(["baseline_no_dns_lookup"])
    assert "no ip domain-lookup" in cfg


@pytest.mark.mandatory
def test_baseline_dns_lookup_present_when_option_disabled():
    cfg = _render_with_baseline([])
    assert "ip domain-lookup" in cfg


# ─────────────────────────────────────────────────────────
#  Idle Session Timeout (exec-timeout)
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_exec_timeout_renders():
    cfg = _render_with_baseline(["baseline_exec_timeout"])
    assert "exec-timeout 15 0" in cfg
    assert "line console" in cfg
    assert "line vty" in cfg


@pytest.mark.mandatory
def test_baseline_exec_timeout_absent_when_not_enabled():
    cfg = _render_with_baseline([])
    assert "exec-timeout" not in cfg


# ─────────────────────────────────────────────────────────
#  Syslog Source Interface
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_baseline_logging_source_renders_when_logging_configured():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "standalone_access",
        "ACCESS-01",
        "HQ",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "baseline_options": ["baseline_logging_source"],
            "features": ["interface_vlan", "lacp", "logging"],
            "logging_hosts": ["10.1.1.100"],
        },
    )
    cfg = ConfigEngine().build_config(result["device"])
    assert "logging source-interface mgmt0" in cfg


# ─────────────────────────────────────────────────────────
#  Mutual-exclusion: all 14 options together
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_all_baseline_options_coexist_without_error():
    """All 14 baseline options enabled simultaneously must not crash the renderer."""
    all_opts = [
        "baseline_cfs", "baseline_copp", "baseline_no_pwd_check",
        "baseline_snmp_traps", "baseline_spanning_tree", "baseline_cli_aliases",
        "baseline_icam", "baseline_vrf_keepalive", "baseline_errdisable_recovery",
        "baseline_icmp_redirects", "baseline_vpc_delay_restore_vlan",
        "baseline_no_dns_lookup", "baseline_exec_timeout", "baseline_logging_source",
    ]
    cfg = _render_with_baseline(
        all_opts,
        scenario_id="vpc_core_pair",
        spanning_tree_priority=8192,
        features=["vpc", "lacp", "interface_vlan", "logging"],
        logging_hosts=["10.1.1.100"],
    )
    assert "hostname CORE-01" in cfg
    assert "cfs eth distribute" in cfg
    assert "copp profile strict" in cfg
    assert "icam monitor scale" in cfg
    assert "errdisable recovery" in cfg
