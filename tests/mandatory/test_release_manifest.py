"""Mandatory pre-release tests — see data/release_qa_manifest.yaml."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "release_qa_manifest.yaml"


@pytest.mark.mandatory
def test_release_qa_manifest_loads():
    assert MANIFEST.is_file(), "data/release_qa_manifest.yaml must exist"
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert data.get("schema_version") >= 1
    assert data.get("stages"), "manifest must define stages"


@pytest.mark.mandatory
def test_release_qa_manifest_paths_exist():
    sys.path.insert(0, str(ROOT / "scripts"))
    from release_qa_manifest import validate_manifest_files

    errors = validate_manifest_files()
    assert not errors, "Manifest references missing files:\n" + "\n".join(errors)


@pytest.mark.mandatory
def test_all_mandatory_stages_have_labels_and_triggers():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for stage in data["stages"]:
        assert stage.get("id"), "stage id required"
        assert stage.get("label"), f"stage {stage.get('id')} needs label"
        assert stage.get("triggers"), f"stage {stage.get('id')} needs triggers"
        assert stage.get("type") in ("pytest", "script"), stage.get("id")


@pytest.mark.mandatory
def test_pre_exe_includes_ui_and_shutdown_blockers():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    pre_exe_ids = {s["id"] for s in data["stages"] if "pre_exe" in (s.get("triggers") or [])}
    required = {
        "release_blockers",
        "mandatory_ui_ux",
        "mandatory_field_vpc",
        "mandatory_generate_api",
        "mandatory_field_gaps",
        "mandatory_api_expanded",
        "mandatory_feature_render",
        "mandatory_baseline_coverage",
        "mandatory_hardware_coverage",
        "mandatory_intent_engine",
        "mandatory_v4_world_class",
        "frozen_bundle_sim",
    }
    missing = required - pre_exe_ids
    assert not missing, f"pre_exe missing stages: {missing}"
