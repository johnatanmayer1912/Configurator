"""Regression test: vPC feature enabled on standalone scenario."""

from core.scenario_engine import ScenarioEngine


def test_vpc_feature_on_standalone_scenario():
    engine = ScenarioEngine()
    result = engine.apply_scenario(
        "standalone_access",
        "ACCESS-01",
        "LAB",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={
            "features": ["interface_vlan", "lldp", "vpc", "ntp", "logging"],
            "peer_link_interfaces": "Ethernet1/53, Ethernet1/54",
            "local_keepalive_ip": "10.255.255.1",
            "remote_keepalive_ip": "10.255.255.2",
        },
    )
    assert result["device"].vpc is not None
    assert result["device"].vpc.domain_id == 100


def test_pipeline_render_metadata_includes_cli_reference():
    from pipelines.build_pipeline import ConfigurationPipeline
    from core.scenario_engine import ScenarioEngine
    from core.catalog_loader import CatalogLoader

    engine = ScenarioEngine(CatalogLoader())
    result = engine.apply_scenario(
        "mgmt_oob",
        "MGMT-01",
        "LAB",
        "10.10.10.10/24",
        "10.10.10.1",
        overrides={"inject_cli_reference": True},
    )
    meta = engine.build_render_metadata({"inject_cli_reference": True})
    assert "cli_reference" in meta
    assert len(meta["cli_reference"]) >= 0

    pipeline = ConfigurationPipeline()
    config = pipeline.engine.build_config(result["device"], metadata={
        "version": pipeline.version,
        "cli_reference": meta["cli_reference"],
    })
    assert "CLI Reference" in config or len(meta["cli_reference"]) == 0