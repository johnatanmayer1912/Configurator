"""NX-OS template section headers and interface-block indentation."""

import re

from core.engine import ConfigEngine
from core.scenario_engine import ScenarioEngine

# Top-level stanzas whose children must be indented (2 spaces minimum).
INDENTED_PARENTS = re.compile(
    r"^(interface |vlan \d+|vpc domain|vrf context|line (console|vty)|aaa group server)"
)

REQUIRED_SECTIONS = (
    "! Management & Routing",
    "! NTP",
    "! Logging",
    "! vPC Domain",
    "! Port-Channels",
)


def _indentation_errors(cfg: str) -> list[str]:
    """Return lines that break 2-space indent under interface/vlan/vpc/vrf parents."""
    errors: list[str] = []
    lines = cfg.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not INDENTED_PARENTS.match(line):
            i += 1
            continue
        parent = line
        i += 1
        while i < len(lines):
            child = lines[i]
            if child.strip() == "":
                i += 1
                continue
            # Next top-level block
            if not child.startswith(" ") and not child.startswith("\t"):
                break
            # HSRP nested commands use 4 spaces
            if child.startswith("    "):
                i += 1
                continue
            if not child.startswith("  ") or len(child.strip()) == 0:
                errors.append(f"under '{parent.strip()}': '{child}'")
            i += 1
    return errors


def test_vpc_core_keepalive_po_l3_indentation():
    engine = ScenarioEngine()
    cfg = ConfigEngine().build_config(
        engine.apply_scenario(
            "vpc_core_pair", "CORE1-VPC", "HQ", "10.10.10.10/24", "10.10.10.1"
        )["device"]
    )
    block = cfg[cfg.find("interface port-channel2") : cfg.find("interface port-channel20")]
    assert "  vrf member VPC_Keep_Alive" in block
    assert "  ip address 1.1.1.1/24" in block
    assert "  no shutdown" in block
    assert "\nvrf member" not in block.replace("  vrf member", "")


def test_vpc_core_downlink_trunk_indentation():
    engine = ScenarioEngine()
    cfg = ConfigEngine().build_config(
        engine.apply_scenario(
            "vpc_core_pair", "CORE1-VPC", "HQ", "10.10.10.10/24", "10.10.10.1"
        )["device"]
    )
    block = cfg[cfg.find("interface port-channel20") : cfg.find("interface port-channel21")]
    assert "  mtu 9216" in block
    assert "  vpc 20" in block
    assert "\nmtu 9216" not in block


def test_section_headers_present():
    engine = ScenarioEngine()
    ce = ConfigEngine()
    result = engine.apply_scenario(
        "vpc_core_pair", "CORE1-VPC", "HQ", "10.10.10.10/24", "10.10.10.1"
    )
    cfg = ce.build_config(result["device"])
    for section in REQUIRED_SECTIONS:
        assert section in cfg, section


def test_management_ntp_logging_block():
    engine = ScenarioEngine()
    cfg = ConfigEngine().build_config(
        engine.apply_scenario(
            "vpc_core_pair",
            "CORE1-VPC",
            "HQ",
            "10.10.10.10/24",
            "10.10.10.1",
            overrides={"security_tier": "hardened"},
        )["device"]
    )
    mgmt = cfg.split("! Management & Routing")[1].split("! NTP")[0]
    assert "interface mgmt0" in mgmt
    assert "  ip address 10.10.10.10/24" in mgmt
    assert "vrf context management" in mgmt
    assert "  ip route 0.0.0.0/0 10.10.10.1" in mgmt
    ntp = cfg.split("! NTP")[1].split("! Logging")[0]
    assert "ntp server" in ntp
    assert "prefer use-vrf management" in ntp
    log = cfg.split("! Logging")[1].split("!")[0]
    assert "logging source-interface mgmt0" in log
    assert "logging timestamp milliseconds" in log


ALL_SCENARIOS = [
    "vpc_core_pair",
    "vpc_leaf_pair",
    "vpc_access_pair",
    "standalone_leaf",
    "standalone_access",
    "spine_core",
    "mgmt_oob",
]


def test_no_indentation_errors_across_scenarios():
    engine = ScenarioEngine()
    ce = ConfigEngine()
    for scen in ALL_SCENARIOS:
        result = engine.apply_scenario(
            scen, "TEST-SW-01", "HQ", "10.10.10.10/24", "10.10.10.1"
        )
        cfg = ce.build_config(result["device"])
        errs = _indentation_errors(cfg)
        assert not errs, f"{scen}: {errs[:5]}"


def test_vpc_domain_subcommands_indented():
    engine = ScenarioEngine()
    cfg = ConfigEngine().build_config(
        engine.apply_scenario(
            "vpc_core_pair", "CORE1-VPC", "HQ", "10.10.10.10/24", "10.10.10.1"
        )["device"]
    )
    domain = cfg.split("! vPC Domain")[1].split("! L3")[0]
    assert "  peer-switch" in domain
    assert "  role priority" in domain
    assert "  peer-keepalive" in domain
    assert "  peer-gateway" in domain
    assert "  ip arp synchronize" in domain
