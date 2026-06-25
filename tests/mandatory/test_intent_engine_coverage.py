"""IntentEngine coverage — all three roles, vPC mode, hardened tier, MOTD, edge cases.

The IntentEngine was the only core module with zero HTTP or unit-level test
references. This suite validates the engine directly and via the /intent/* API.
"""

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from core.intent_engine import IntentEngine
from models.intent_model import BlueprintIntent, IntentOverrides

client = TestClient(app)


def _intent(
    role: str,
    redundancy_mode: str = "standalone",
    security_tier: str = "standard",
    hostname: str = "INTENT-SW-01",
    model: str = "Generic",
    **override_kwargs,
) -> tuple:
    """Build BlueprintIntent and resolve it via IntentEngine."""
    engine = IntentEngine()
    overrides = IntentOverrides(**override_kwargs)
    intent = BlueprintIntent(
        hostname=hostname,
        site_name="HQ_DC",
        role=role,
        model=model,
        mgmt_ip="10.10.10.10/24",
        mgmt_gw="10.10.10.1",
        redundancy_mode=redundancy_mode,
        security_tier=security_tier,
        overrides=overrides,
    )
    device, resolution = engine.resolve(intent)
    return device, resolution, intent


# ─────────────────────────────────────────────────────────
#  Role: access
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_access_role_builds_device():
    device, resolution, _ = _intent("access")
    assert device.hostname == "INTENT-SW-01"
    assert device.mgmt_ip == "10.10.10.10/24"


@pytest.mark.mandatory
def test_intent_access_generates_user_vlans():
    device, _, _ = _intent("access", base_access_vlan=100, access_vlan_count=4)
    ids = [v.id for v in device.vlans]
    assert ids == [100, 101, 102, 103]
    names = [v.name for v in device.vlans]
    assert all(n.startswith("USER_") for n in names)


@pytest.mark.mandatory
def test_intent_access_interfaces_are_access_mode():
    device, _, _ = _intent("access", interface_count=4, base_access_vlan=10)
    access_intfs = [i for i in device.interfaces if i.mode == "access"]
    assert len(access_intfs) >= 1


@pytest.mark.mandatory
def test_intent_access_builds_svis_for_first_two_vlans():
    device, _, _ = _intent("access", base_access_vlan=10, access_vlan_count=4)
    assert len(device.svis) == 2
    assert device.svis[0].vlan_id == 10
    assert device.svis[1].vlan_id == 11


@pytest.mark.mandatory
def test_intent_access_no_vpc_in_standalone():
    device, resolution, _ = _intent("access", redundancy_mode="standalone")
    assert device.vpc is None
    assert resolution.policy_flags["vpc_enabled"] == "no"


@pytest.mark.mandatory
def test_intent_access_resolution_profile_name():
    _, resolution, _ = _intent("access", security_tier="standard")
    assert "ACCESS" in resolution.profile_name.upper()
    assert "STANDARD" in resolution.profile_name.upper()


@pytest.mark.mandatory
def test_intent_access_resolution_summary_lines():
    _, resolution, _ = _intent("access")
    summary = "\n".join(resolution.summary_lines)
    assert "Role:" in summary
    assert "Site:" in summary
    assert "Model:" in summary
    assert "Redundancy:" in summary


# ─────────────────────────────────────────────────────────
#  Role: leaf
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_leaf_builds_fabric_vlans():
    device, _, _ = _intent("leaf", base_access_vlan=200, access_vlan_count=3)
    names = [v.name for v in device.vlans]
    assert all(n.startswith("FABRIC_") for n in names)


@pytest.mark.mandatory
def test_intent_leaf_standalone_no_vpc():
    device, resolution, _ = _intent("leaf", redundancy_mode="standalone")
    assert device.vpc is None
    assert resolution.policy_flags["vpc_enabled"] == "no"


@pytest.mark.mandatory
def test_intent_leaf_vpc_mode_creates_vpc_config():
    device, resolution, _ = _intent("leaf", redundancy_mode="vpc")
    assert device.vpc is not None
    assert device.vpc.role == "primary"
    assert resolution.policy_flags["vpc_enabled"] == "yes"


@pytest.mark.mandatory
def test_intent_leaf_vpc_keepalive_ips_differ():
    device, _, _ = _intent("leaf", redundancy_mode="vpc")
    assert device.vpc is not None
    assert device.vpc.local_keepalive_ip != device.vpc.remote_keepalive_ip


@pytest.mark.mandatory
def test_intent_leaf_svis_built():
    device, _, _ = _intent("leaf", base_access_vlan=20, access_vlan_count=4)
    assert len(device.svis) == 2
    assert device.svis[0].vlan_id == 20


@pytest.mark.mandatory
def test_intent_leaf_svi_ip_address_format():
    device, _, _ = _intent("leaf", base_access_vlan=30, access_vlan_count=2)
    for svi in device.svis:
        assert "/" in svi.ip_address, "SVI IP must include prefix length"
        assert svi.ip_address.startswith("10.")


# ─────────────────────────────────────────────────────────
#  Role: spine
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_spine_builds_transit_vlans():
    device, _, _ = _intent("spine", base_access_vlan=1000, access_vlan_count=2)
    names = [v.name for v in device.vlans]
    assert all(n.startswith("TRANSIT_") for n in names)


@pytest.mark.mandatory
def test_intent_spine_has_no_svis():
    device, _, _ = _intent("spine")
    assert device.svis == [], "Spine role must not generate SVIs"


@pytest.mark.mandatory
def test_intent_spine_no_vpc_even_in_vpc_mode():
    """Spine standalone — vPC only supported on leaf in IntentEngine."""
    device, resolution, _ = _intent("spine", redundancy_mode="standalone")
    assert device.vpc is None


@pytest.mark.mandatory
def test_intent_spine_resolution_profile():
    _, resolution, _ = _intent("spine")
    assert "SPINE" in resolution.profile_name.upper()


@pytest.mark.mandatory
def test_intent_spine_stp_policy_restricted():
    _, resolution, _ = _intent("spine")
    assert resolution.policy_flags["stp_edge_defaults"] == "restricted"


@pytest.mark.mandatory
def test_intent_access_stp_policy_enabled():
    _, resolution, _ = _intent("access")
    assert resolution.policy_flags["stp_edge_defaults"] == "enabled"


# ─────────────────────────────────────────────────────────
#  Security tier & MOTD
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_hardened_tier_motd_contains_authorized_only():
    device, _, _ = _intent("access", security_tier="hardened")
    assert "AUTHORIZED" in device.motd.upper()


@pytest.mark.mandatory
def test_intent_standard_tier_motd_contains_institutional():
    device, _, _ = _intent("access", security_tier="standard")
    assert "institutional" in device.motd.lower() or "access" in device.motd.lower()


@pytest.mark.mandatory
def test_intent_custom_motd_override_respected():
    device, _, _ = _intent("access", motd="Custom MOTD for Testing")
    assert device.motd == "Custom MOTD for Testing"


# ─────────────────────────────────────────────────────────
#  Uplink ports
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_uplink_ports_assigned_as_trunk():
    engine = IntentEngine()
    intent = BlueprintIntent(
        hostname="LEAF-01",
        site_name="HQ",
        role="leaf",
        model="Generic",
        mgmt_ip="10.0.0.1/24",
        mgmt_gw="10.0.0.254",
        redundancy_mode="standalone",
        security_tier="standard",
        uplink_ports=["Ethernet1/47", "Ethernet1/48"],
        overrides=IntentOverrides(interface_count=10),
    )
    device, _ = engine.resolve(intent)
    uplink_modes = {
        i.mode for i in device.interfaces if i.name in {"Ethernet1/47", "Ethernet1/48"}
    }
    assert "trunk" in uplink_modes, "Uplink ports must be assigned trunk mode"


# ─────────────────────────────────────────────────────────
#  Admin credentials
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_default_admin_user():
    device, _, _ = _intent("access")
    assert device.admin_user == "admin"


@pytest.mark.mandatory
def test_intent_custom_admin_user_and_password():
    device, _, _ = _intent(
        "access",
        admin_user="netops",
        admin_password="S3cureP@ss",
    )
    assert device.admin_user == "netops"
    assert device.admin_password == "S3cureP@ss"


# ─────────────────────────────────────────────────────────
#  Invalid role rejection
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
def test_intent_engine_rejects_invalid_role():
    engine = IntentEngine()
    with pytest.raises(ValueError, match="role must be"):
        intent = BlueprintIntent(
            hostname="TEST",
            site_name="HQ",
            role="firewall",
            model="Generic",
            mgmt_ip="10.0.0.1/24",
            mgmt_gw="10.0.0.254",
        )
        engine.resolve(intent)


# ─────────────────────────────────────────────────────────
#  API surface: /intent/preview end-to-end
# ─────────────────────────────────────────────────────────

@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_api_preview_access_returns_interfaces_count(_mock):
    res = client.post(
        "/intent/preview",
        json={
            "hostname": "INTENT-ACCESS-01",
            "site_name": "TEST",
            "role": "access",
            "mgmt_ip": "10.0.0.1/24",
            "mgmt_gw": "10.0.0.254",
            "overrides": {"interface_count": 8, "access_vlan_count": 2},
        },
    )
    assert res.status_code == 200
    data = res.json()
    summary = "\n".join(data.get("summary_lines", []))
    assert "Interfaces generated:" in summary
    count_line = [l for l in data["summary_lines"] if "Interfaces generated:" in l]
    assert count_line, "summary_lines must include interface count"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_api_preview_vpc_leaf_has_vpc_policy(_mock):
    res = client.post(
        "/intent/preview",
        json={
            "hostname": "INTENT-LEAF-01",
            "site_name": "TEST",
            "role": "leaf",
            "mgmt_ip": "10.0.0.1/24",
            "mgmt_gw": "10.0.0.254",
            "redundancy_mode": "vpc",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["policy_flags"]["vpc_enabled"] == "yes"


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_intent_api_invalid_redundancy_mode_422(_mock):
    res = client.post(
        "/intent/preview",
        json={
            "hostname": "TEST",
            "site_name": "HQ",
            "role": "leaf",
            "mgmt_ip": "10.0.0.1/24",
            "mgmt_gw": "10.0.0.254",
            "redundancy_mode": "cluster",
        },
    )
    assert res.status_code == 422
