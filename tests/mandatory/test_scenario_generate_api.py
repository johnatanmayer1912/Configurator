"""F-002 — /scenario/generate integration (pair export, vault files, keepalive swap)."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

LEAF_PAIR_PAYLOAD = {
    "scenario_id": "vpc_leaf_pair",
    "hostname": "DC-LEAF-01-A",
    "site_name": "HQ_DC",
    "mgmt_ip": "10.10.10.10/24",
    "mgmt_gw": "10.10.10.1",
    "generate_pair": True,
    "overrides": {
        "model": "Nexus 93180YC-EX",
        "nxos_version": "9.3",
        "local_keepalive_ip": "10.255.255.1",
        "remote_keepalive_ip": "10.255.255.2",
    },
}


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_scenario_generate_pair_writes_two_configs(_mock, tmp_path):
    payload = {**LEAF_PAIR_PAYLOAD, "overrides": {**LEAF_PAIR_PAYLOAD["overrides"], "export_dir": str(tmp_path)}}
    res = client.post("/scenario/generate", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert len(data["results"]) == 2
    hosts = {r["hostname"] for r in data["results"]}
    assert hosts == {"DC-LEAF-01-A", "DC-LEAF-01-B"}

    export = data.get("export") or {}
    assert export.get("batch_folder")
    out_dir = export["output_dir"]
    assert os.path.isdir(out_dir)
    files = export.get("files") or []
    assert len(files) >= 2
    config_files = [f for f in files if f.endswith("_config.txt")]
    assert len(config_files) >= 2

    pri_cfg = data["results"][0]["config_preview"]
    sec_cfg = data["results"][1]["config_preview"]
    assert "feature vpc" in pri_cfg
    assert "interface port-channel10" not in pri_cfg or "vpc domain" in pri_cfg
    assert "10.255.255.1" in pri_cfg or "10.255.255.2" in pri_cfg
    assert sec_cfg and "DC-LEAF-01-B" in sec_cfg or "DC-LEAF-01-B" in data["results"][1]["hostname"]


@pytest.mark.mandatory
@patch("api.main._enforce_privileged_access")
def test_scenario_generate_single_no_batch_folder(_mock, tmp_path):
    payload = {
        **LEAF_PAIR_PAYLOAD,
        "generate_pair": False,
        "overrides": {**LEAF_PAIR_PAYLOAD["overrides"], "export_dir": str(tmp_path)},
    }
    res = client.post("/scenario/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["hostname"] == "DC-LEAF-01-A"
