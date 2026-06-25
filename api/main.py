import os
import re
import threading
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, field_validator, model_validator, conint, constr
from typing import List, Optional, Dict, Any
from models.device_model import Device, VPCConfig
from models.vlan_model import VLAN
from models.interface_model import Interface
from models.l3_models import SVI, HSRPConfig, StaticRoute
from models.intent_model import BlueprintIntent, IntentOverrides
from pipelines.build_pipeline import ConfigurationPipeline
from core.validator import DeviceValidator, ValidationError
from core.compliance import ComplianceEngine
from core.checkpoint_manager import CheckpointManager
from core.intent_engine import IntentEngine
from core.catalog_loader import CatalogLoader
from core.scenario_engine import ScenarioEngine
from core.renderer import ConfigRenderer
from utils.web_logger import logger
from datetime import datetime
from core.import_wizard import ConfigBuilderEngine
from core.config_remarks import ConfigRemarksEngine, build_cli_blocks
from utils.app_dirs import get_history_dir, get_checkpoints_dir, get_app_dir
from utils.version import get_app_version
from utils.change_package import build_manifest, write_package_artifacts
from core.link_allocator import build_reserved_inventory, validate_link_row, suggest_members, port_budget
from core.po_map_store import load_po_map, save_po_map, ranges_for_model
from core.cable_plan import build_cable_plan, render_cable_plan_md
from core.version_diff import compare_versions
from core.hostname_rules import validate_hostname as validate_hostname_rules, validate_site_code, suggest_hostname

HISTORY_DIR = Path(get_history_dir())
HOSTNAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")


def _is_loopback(host: Optional[str]) -> bool:
    return host in {"127.0.0.1", "::1", "localhost"}


app = FastAPI(title="Configuration Authority System", version=get_app_version())
pipeline = ConfigurationPipeline()
device_validator = DeviceValidator()
compliance = ComplianceEngine()
checkpoints = CheckpointManager()
intent_engine = IntentEngine()
catalog = CatalogLoader()
scenario_engine = ScenarioEngine(catalog)
config_renderer = ConfigRenderer()
config_builder = ConfigBuilderEngine(catalog)
remarks_engine = ConfigRemarksEngine(catalog)


def _auth_token() -> str:
    return os.getenv("CONFIG_AUTH_TOKEN", "")


def _enforce_privileged_access(request: Request) -> None:
    client_host = request.client.host if request.client else None
    if not _is_loopback(client_host):
        raise HTTPException(status_code=403, detail="Access denied.")
    # Token authentication removed for offline use


def _enforce_loopback_only(request: Request) -> None:
    # Loopback restriction removed for offline use
    pass

# --- Pydantic Data Contract ---

class VLANInput(BaseModel):
    id: conint(ge=1, le=4094)  # type: ignore[valid-type]
    name: constr(strip_whitespace=True, min_length=1, max_length=64)  # type: ignore[valid-type]

class HSRPInput(BaseModel):
    group: conint(ge=1, le=4095)  # type: ignore[valid-type]
    vip: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    priority: conint(ge=1, le=255) = 100  # type: ignore[valid-type]
    preempt: bool = True

class SVIInput(BaseModel):
    vlan_id: conint(ge=1, le=4094)  # type: ignore[valid-type]
    ip_address: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    description: Optional[constr(strip_whitespace=True, max_length=120)] = None  # type: ignore[valid-type]
    hsrp: Optional[HSRPInput] = None
    vrf: Optional[constr(strip_whitespace=True, max_length=64)] = None  # type: ignore[valid-type]

class VPCInput(BaseModel):
    domain_id: conint(ge=1, le=1000)  # type: ignore[valid-type]
    role: constr(strip_whitespace=True, min_length=4, max_length=10)  # type: ignore[valid-type]
    keepalive_vrf: constr(strip_whitespace=True, min_length=1, max_length=64)  # type: ignore[valid-type]
    local_keepalive_ip: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    remote_keepalive_ip: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    peer_link_id: conint(ge=1, le=4096)  # type: ignore[valid-type]
    peer_link_interfaces: List[constr(strip_whitespace=True, min_length=4, max_length=32)] = Field(default_factory=list)  # type: ignore[valid-type]
    system_priority: conint(ge=1, le=65535) = 32667  # type: ignore[valid-type]

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"primary", "secondary"}:
            raise ValueError("vPC role must be 'primary' or 'secondary'.")
        return normalized

    @model_validator(mode="after")
    def validate_vpc_shape(self):
        if len(self.peer_link_interfaces) < 1:
            raise ValueError("At least one vPC peer-link interface is required.")
        if self.local_keepalive_ip == self.remote_keepalive_ip:
            raise ValueError("vPC local and remote keepalive IPs must be different.")
        return self

class StaticRouteInput(BaseModel):
    prefix: constr(strip_whitespace=True, min_length=9, max_length=64)  # type: ignore[valid-type]
    next_hop: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    vrf: Optional[constr(strip_whitespace=True, max_length=64)] = None  # type: ignore[valid-type]
    description: Optional[constr(strip_whitespace=True, max_length=120)] = None  # type: ignore[valid-type]

class InterfaceInput(BaseModel):
    name: constr(strip_whitespace=True, min_length=4, max_length=32)  # type: ignore[valid-type]
    mode: constr(strip_whitespace=True, min_length=5, max_length=8) = "access"  # type: ignore[valid-type]
    vlan: Optional[conint(ge=1, le=4094)] = None  # type: ignore[valid-type]
    description: Optional[constr(strip_whitespace=True, max_length=120)] = None  # type: ignore[valid-type]
    shutdown: bool = False
    vpc_id: Optional[conint(ge=1, le=4096)] = None  # type: ignore[valid-type]

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"access", "trunk"}:
            raise ValueError("Interface mode must be 'access' or 'trunk'.")
        return normalized

class DeviceInput(BaseModel):
    hostname: constr(strip_whitespace=True, min_length=1, max_length=63)  # type: ignore[valid-type]
    mgmt_ip: constr(strip_whitespace=True, min_length=9, max_length=64)  # type: ignore[valid-type]
    mgmt_gw: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    model: constr(strip_whitespace=True, min_length=3, max_length=64) = "Generic"  # type: ignore[valid-type]
    vlans: List[VLANInput] = Field(default_factory=list)
    interfaces: List[InterfaceInput] = Field(default_factory=list)
    svis: List[SVIInput] = Field(default_factory=list)
    static_routes: List[StaticRouteInput] = Field(default_factory=list)
    vpc: Optional[VPCInput] = None
    motd: constr(strip_whitespace=True, min_length=5, max_length=240) = "Authorized Access Only"  # type: ignore[valid-type]
    admin_user: constr(strip_whitespace=True, min_length=1, max_length=32) = "admin"  # type: ignore[valid-type]
    admin_password: constr(strip_whitespace=True, max_length=128) = ""  # type: ignore[valid-type]
    nxos_version: constr(strip_whitespace=True, min_length=3, max_length=16) = "9.3"  # type: ignore[valid-type]
    enabled_features: List[str] = Field(default_factory=list)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        if not HOSTNAME_PATTERN.fullmatch(value):
            raise ValueError("Hostname must use alphanumeric characters and hyphens only.")
        return value

    @field_validator("mgmt_ip")
    @classmethod
    def validate_mgmt_ip(cls, value: str) -> str:
        if "/" not in value:
            raise ValueError("Management IP must include CIDR notation (example: 10.10.10.10/24).")
        return value

    @model_validator(mode="after")
    def enforce_admin_password_for_non_default_user(self):
        user = self.admin_user
        password = self.admin_password
        if user and user.lower() != "admin" and not password:
            raise ValueError("Admin password is required when using a custom admin username.")
        return self


class IntentOverridesInput(BaseModel):
    motd: Optional[constr(strip_whitespace=True, min_length=5, max_length=240)] = None  # type: ignore[valid-type]
    admin_user: Optional[constr(strip_whitespace=True, min_length=1, max_length=32)] = None  # type: ignore[valid-type]
    admin_password: Optional[constr(strip_whitespace=True, max_length=128)] = None  # type: ignore[valid-type]
    management_vrf: constr(strip_whitespace=True, min_length=1, max_length=64) = "management"  # type: ignore[valid-type]
    base_access_vlan: conint(ge=1, le=4000) = 10  # type: ignore[valid-type]
    access_vlan_count: conint(ge=1, le=50) = 4  # type: ignore[valid-type]
    interface_count: conint(ge=1, le=128) = 48  # type: ignore[valid-type]


class IntentInput(BaseModel):
    hostname: constr(strip_whitespace=True, min_length=1, max_length=63)  # type: ignore[valid-type]
    site_name: constr(strip_whitespace=True, min_length=2, max_length=64)  # type: ignore[valid-type]
    role: constr(strip_whitespace=True, min_length=4, max_length=10)  # type: ignore[valid-type]
    model: constr(strip_whitespace=True, min_length=3, max_length=64) = "Generic"  # type: ignore[valid-type]
    mgmt_ip: constr(strip_whitespace=True, min_length=9, max_length=64)  # type: ignore[valid-type]
    mgmt_gw: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    redundancy_mode: constr(strip_whitespace=True, min_length=3, max_length=16) = "standalone"  # type: ignore[valid-type]
    security_tier: constr(strip_whitespace=True, min_length=4, max_length=16) = "standard"  # type: ignore[valid-type]
    uplink_ports: List[constr(strip_whitespace=True, min_length=4, max_length=32)] = Field(default_factory=list)  # type: ignore[valid-type]
    overrides: IntentOverridesInput = Field(default_factory=IntentOverridesInput)

    @field_validator("hostname")
    @classmethod
    def validate_intent_hostname(cls, value: str) -> str:
        if not HOSTNAME_PATTERN.fullmatch(value):
            raise ValueError("Hostname must use alphanumeric characters and hyphens only.")
        return value

    @field_validator("role")
    @classmethod
    def validate_intent_role(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"access", "leaf", "spine"}:
            raise ValueError("Intent role must be access, leaf, or spine.")
        return normalized

    @field_validator("redundancy_mode")
    @classmethod
    def validate_redundancy_mode(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"standalone", "vpc"}:
            raise ValueError("Redundancy mode must be standalone or vpc.")
        return normalized

    @field_validator("security_tier")
    @classmethod
    def validate_security_tier(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"standard", "hardened"}:
            raise ValueError("Security tier must be standard or hardened.")
        return normalized

class ScenarioInput(BaseModel):
    scenario_id: constr(strip_whitespace=True, min_length=3, max_length=64)  # type: ignore[valid-type]
    hostname: constr(strip_whitespace=True, min_length=1, max_length=63)  # type: ignore[valid-type]
    site_name: constr(strip_whitespace=True, min_length=2, max_length=64) = "DEFAULT_SITE"  # type: ignore[valid-type]
    mgmt_ip: constr(strip_whitespace=True, min_length=9, max_length=64)  # type: ignore[valid-type]
    mgmt_gw: constr(strip_whitespace=True, min_length=7, max_length=64)  # type: ignore[valid-type]
    generate_pair: bool = False
    overrides: Dict[str, object] = Field(default_factory=dict)

    @field_validator("hostname")
    @classmethod
    def validate_scenario_hostname(cls, value: str) -> str:
        if not HOSTNAME_PATTERN.fullmatch(value):
            raise ValueError("Hostname must use alphanumeric characters and hyphens only.")
        return value


class DiffInput(BaseModel):
    baseline: str = ""
    proposed: str = ""


class ParseDiffInput(BaseModel):
    running_config: str = ""
    proposed: str = ""


class ParseConfigInput(BaseModel):
    running_config: str = ""


class BuilderAnswersInput(BaseModel):
    answers: Dict[str, object] = Field(default_factory=dict)


class OpenFolderInput(BaseModel):
    path: str = ""

# --- Helper Logic ---

def map_to_core(input: DeviceInput) -> Device:
    vlans = [VLAN(v.id, v.name) for v in input.vlans]
    interfaces = [Interface(i.name, i.mode, i.vlan, i.description, i.shutdown, i.vpc_id) for i in input.interfaces]
    svis = []
    for s in input.svis:
        hsrp = HSRPConfig(**s.hsrp.model_dump()) if s.hsrp else None
        svis.append(SVI(vlan_id=s.vlan_id, ip_address=s.ip_address, description=s.description, hsrp=hsrp, vrf=s.vrf))
    
    routes = [StaticRoute(**r.model_dump()) for r in input.static_routes]
    
    vpc = None
    if input.vpc:
        vpc = VPCConfig(**input.vpc.model_dump())

    return Device(
        hostname=input.hostname, mgmt_ip=input.mgmt_ip, mgmt_gw=input.mgmt_gw,
        model=input.model, vlans=vlans, interfaces=interfaces, svis=svis,
        static_routes=routes, vpc=vpc, motd=input.motd,
        admin_user=input.admin_user, admin_password=input.admin_password,
        nxos_version=input.nxos_version, enabled_features=input.enabled_features,
    )


def map_intent_to_core(intent_input: IntentInput):
    intent = BlueprintIntent(
        hostname=intent_input.hostname,
        site_name=intent_input.site_name,
        role=intent_input.role,
        model=intent_input.model,
        mgmt_ip=intent_input.mgmt_ip,
        mgmt_gw=intent_input.mgmt_gw,
        redundancy_mode=intent_input.redundancy_mode,
        security_tier=intent_input.security_tier,
        uplink_ports=intent_input.uplink_ports,
        overrides=IntentOverrides(
            motd=intent_input.overrides.motd,
            admin_user=intent_input.overrides.admin_user,
            admin_password=intent_input.overrides.admin_password,
            management_vrf=intent_input.overrides.management_vrf,
            base_access_vlan=intent_input.overrides.base_access_vlan,
            access_vlan_count=intent_input.overrides.access_vlan_count,
            interface_count=intent_input.overrides.interface_count,
        ),
    )
    device, resolution = intent_engine.resolve(intent)
    scenario_engine.enrich_intent_topology(device, intent)
    return (device, resolution), intent


def _render_preview(device, nxos_version: str, overrides: Optional[dict] = None) -> str:
    metadata = {
        "version": pipeline.version,
        "nxos_version": nxos_version,
        "mode": "vPC Pair" if device.vpc else "Standalone",
        "system": "Configuration Authority System",
    }
    metadata.update(scenario_engine.build_render_metadata(overrides or {}))
    return config_renderer.render_device_config(device, metadata=metadata)


def _model_meta(model_name: str) -> Dict:
    hw = catalog.get_hardware_profile(model_name) or {}
    matrix_row = None
    return {
        "display_name": hw.get("display_name", model_name),
        "device_class": hw.get("device_class", "hybrid"),
        "primary_speed_label": hw.get("primary_speed_label", "Multi"),
        "speed_badges": hw.get("speed_badges", []),
        "total_ports": hw.get("total_ports", 0),
        "port_groups": hw.get("port_groups", []),
    }


def _preview_extras(device, config_preview: str, overrides: Optional[dict], scenario_id: str) -> Dict:
    ov = overrides or {}
    action = remarks_engine.analyze(device, config_preview, ov)
    blocks = build_cli_blocks(device, catalog, ov)
    model = ov.get("model", device.model)
    row = catalog.get_matrix_row(scenario_id) or {}
    return {
        "action_required": action,
        "cli_blocks": blocks,
        "model_meta": _model_meta(model),
        "speed_badges": _model_meta(model).get("speed_badges", []),
        "matrix_row": row,
    }

# --- Endpoints ---

@app.get("/version")
def get_version():
    return {"version": pipeline.version, "status": "operational", "platform": "web"}


@app.get("/catalog")
def get_full_catalog():
    return catalog.full_catalog()


@app.get("/catalog/versions")
def get_catalog_versions():
    return catalog.list_versions()


@app.get("/catalog/scenarios")
def get_catalog_scenarios():
    return catalog.list_scenarios()


@app.get("/catalog/hardware")
def get_catalog_hardware():
    return catalog.list_hardware_profiles()


@app.get("/catalog/features")
def get_catalog_features():
    return {"features": catalog.list_features(), "aliases": catalog.list_aliases()}


@app.get("/catalog/matrix")
def get_catalog_matrix():
    return {
        "matrix": catalog.list_config_matrix(),
        "hardware": catalog.list_hardware_profiles(),
        "placeholders": catalog.list_placeholders(),
    }


@app.post("/scenario/preview")
def preview_scenario(input: ScenarioInput, request: Request):
    # Token authentication removed for offline use
    try:
        applied = scenario_engine.apply_scenario(
            input.scenario_id,
            input.hostname,
            input.site_name,
            input.mgmt_ip,
            input.mgmt_gw,
            overrides=input.overrides,
        )
        device = applied["device"]
        report = device_validator.validate(device)
        findings = compliance.audit(device)
        config_preview = _render_preview(device, applied["nxos_version"], input.overrides)
        extras = _preview_extras(device, config_preview, input.overrides, applied["scenario_id"])
        if applied.get("planner_warnings"):
            extras["planner_warnings"] = applied["planner_warnings"]
        response = {
            "status": report["status"],
            "scenario_id": applied["scenario_id"],
            "scenario_name": applied["scenario_name"],
            "nxos_version": applied["nxos_version"],
            "enabled_features": applied["enabled_features"],
            "summary_lines": applied["resolution"].summary_lines,
            "policy_flags": applied["resolution"].policy_flags,
            "validation_errors": report["errors"],
            "compliance_findings": findings,
            "pair_mode": applied.get("pair_mode", False),
            "config_preview": config_preview,
            "engineer_notes": applied["resolution"].policy_flags,
            **extras,
        }
        if applied.get("pair_mode"):
            secondary = applied["pair"]["secondary"]["device"]
            pair_report = device_validator.validate_vpc_pair(device, secondary)
            response["pair_preview"] = {
                "primary": applied["pair"]["primary"],
                "secondary_hostname": applied["pair"]["secondary"]["hostname"],
                "pair_validation": pair_report,
                "secondary_config_preview": _render_preview(secondary, applied["nxos_version"], input.overrides),
            }
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario preview failed: {e}")
        raise HTTPException(status_code=500, detail="Scenario preview failed.")


@app.post("/scenario/generate")
def generate_scenario(input: ScenarioInput, request: Request):
    # Token authentication removed for offline use
    try:
        applied = scenario_engine.apply_scenario(
            input.scenario_id,
            input.hostname,
            input.site_name,
            input.mgmt_ip,
            input.mgmt_gw,
            overrides=input.overrides,
        )
        device = applied["device"]
        if report := device_validator.validate(device):
            if report["status"] == "fail":
                raise ValidationError(report)

        export_override = input.overrides.get("export_dir") if input.overrides else None
        export_base = ConfigurationPipeline.resolve_export_directory(
            str(export_override) if export_override else None
        )
        is_pair = bool(input.generate_pair and applied.get("pair_mode"))
        batch_ts = datetime.now().strftime("%Y%m%d_%H%M%S") if is_pair else None

        if is_pair:
            secondary = applied["pair"]["secondary"]["device"]
            pair_report = device_validator.validate_vpc_pair(device, secondary)
            if pair_report["status"] == "fail":
                raise ValidationError(pair_report)

        checkpoints.save_checkpoint(device, label="scenario-pre-gen")
        render_meta = scenario_engine.build_render_metadata(input.overrides)
        config_text = _render_preview(device, applied["nxos_version"], input.overrides)
        primary_manifest = pipeline.execute(
            device,
            extra_artifacts={
                "scenario": {
                    "id": applied["scenario_id"],
                    "name": applied["scenario_name"],
                    "nxos_version": applied["nxos_version"],
                    "features": applied["enabled_features"],
                    "site_name": input.site_name,
                },
                "blueprint_summary": "\n".join(applied["resolution"].summary_lines),
            },
            render_metadata=render_meta,
            output_dir=export_base,
            site_name=input.site_name,
            scenario_slug=applied["scenario_id"],
            pair_batch=is_pair,
            batch_timestamp=batch_ts,
        )
        results = [{
            "hostname": device.hostname,
            "message": primary_manifest["message"],
            "config_preview": config_text,
            "files": primary_manifest["files"],
        }]
        all_files = list(primary_manifest["files"])
        export_dir = primary_manifest["output_dir"]
        batch_folder = primary_manifest.get("batch_folder")

        if is_pair:
            secondary = applied["pair"]["secondary"]["device"]
            checkpoints.save_checkpoint(secondary, label="scenario-pre-gen")
            sec_config = _render_preview(secondary, applied["nxos_version"], input.overrides)
            secondary_manifest = pipeline.execute(
                secondary,
                extra_artifacts={
                    "scenario": {
                        "id": applied["scenario_id"],
                        "name": applied["scenario_name"],
                        "nxos_version": applied["nxos_version"],
                        "features": applied["enabled_features"],
                        "vpc_role": "secondary",
                        "site_name": input.site_name,
                    },
                },
                render_metadata=render_meta,
                output_dir=export_base,
                site_name=input.site_name,
                scenario_slug=applied["scenario_id"],
                pair_batch=True,
                batch_timestamp=batch_ts,
            )
            all_files.extend(secondary_manifest["files"])
            results.append({
                "hostname": secondary.hostname,
                "message": secondary_manifest["message"],
                "config_preview": sec_config,
                "files": secondary_manifest["files"],
            })

        hosts_meta: List[Dict] = []
        if device.vpc:
            hosts_meta.append({
                "hostname": device.hostname,
                "vpc_role": "primary",
                "keepalive_local": device.vpc.local_keepalive_ip,
                "keepalive_remote": device.vpc.remote_keepalive_ip,
            })
        else:
            hosts_meta.append({"hostname": device.hostname, "vpc_role": "standalone"})
        if is_pair:
            sec_dev = applied["pair"]["secondary"]["device"]
            hosts_meta.append({
                "hostname": sec_dev.hostname,
                "vpc_role": "secondary",
                "keepalive_local": sec_dev.vpc.local_keepalive_ip if sec_dev.vpc else "",
                "keepalive_remote": sec_dev.vpc.remote_keepalive_ip if sec_dev.vpc else "",
            })

        action = remarks_engine.analyze(device, config_text, input.overrides or {})
        pkg = build_manifest(
            version=pipeline.version,
            site_name=input.site_name,
            scenario_id=applied["scenario_id"],
            scenario_name=applied["scenario_name"],
            nxos_version=applied["nxos_version"],
            hosts=hosts_meta,
            files=all_files,
            output_dir=export_dir,
            batch_folder=batch_folder,
            lab_ready=bool(action.get("lab_ready")),
            summary_lines=applied["resolution"].summary_lines,
            pair_mode=is_pair,
        )
        pkg_files = write_package_artifacts(export_dir, pkg)
        all_files = list(all_files) + pkg_files

        cable_name = _write_cable_plan_artifact(
            export_dir,
            device,
            applied,
            input,
            pair_hostname=applied["pair"]["secondary"]["hostname"] if is_pair else None,
        )
        if cable_name:
            all_files.append(cable_name)

        return {
            "status": "success",
            "results": results,
            "scenario_name": applied["scenario_name"],
            "summary_lines": applied["resolution"].summary_lines,
            "export": {
                "output_dir": export_dir,
                "files": all_files,
                "batch_folder": batch_folder,
                "site_name": input.site_name,
                "scenario_id": applied["scenario_id"],
                "change_package": pkg,
            },
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.report["errors"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario generation failed: {e}")
        raise HTTPException(status_code=500, detail="Scenario generation failed.")

@app.post("/validate")
def validate_device(input: DeviceInput, request: Request):
    # Token authentication removed for offline use
    device = map_to_core(input)
    report = device_validator.validate(device)
    findings = compliance.audit(device)
    report["compliance_findings"] = findings
    return report

@app.post("/generate-config")
def generate_config(input: DeviceInput, request: Request):
    # Token authentication removed for offline use
    device = map_to_core(input)
    try:
        checkpoints.save_checkpoint(device, label="pre-gen")
        manifest = pipeline.execute(device)
        return {"status": "success", "message": manifest["message"], "export": manifest}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.report["errors"])
    except Exception as e:
        logger.error(f"Config generation failed: {e}")
        raise HTTPException(status_code=500, detail="Configuration generation failed due to an internal error.")


@app.post("/intent/preview")
def preview_intent(input: IntentInput, request: Request):
    # Token authentication removed for offline use
    try:
        (device, resolution), _ = map_intent_to_core(input)
        report = device_validator.validate(device)
        findings = compliance.audit(device)
        return {
            "status": report["status"],
            "profile_name": resolution.profile_name,
            "summary_lines": resolution.summary_lines,
            "policy_flags": resolution.policy_flags,
            "validation_errors": report["errors"],
            "compliance_findings": findings,
        }
    except Exception as e:
        logger.error(f"Intent preview failed: {e}")
        raise HTTPException(status_code=500, detail="Intent preview failed due to an internal error.")


@app.post("/intent/generate")
def generate_from_intent(input: IntentInput, request: Request):
    # Token authentication removed for offline use
    try:
        (device, resolution), intent = map_intent_to_core(input)
        checkpoints.save_checkpoint(device, label="intent-pre-gen")
        manifest = pipeline.execute(
            device,
            extra_artifacts={
                "intent": {
                    "hostname": intent.hostname,
                    "site_name": intent.site_name,
                    "role": intent.role,
                    "model": intent.model,
                    "redundancy_mode": intent.redundancy_mode,
                    "security_tier": intent.security_tier,
                    "uplink_ports": intent.uplink_ports,
                },
                "blueprint_summary": "\n".join(resolution.summary_lines),
                "blueprint_policy": resolution.policy_flags,
            },
            site_name=intent.site_name,
            scenario_slug=intent.role,
        )
        return {
            "status": "success",
            "message": manifest["message"],
            "export": manifest,
            "profile_name": resolution.profile_name,
            "summary_lines": resolution.summary_lines,
            "policy_flags": resolution.policy_flags,
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.report["errors"])
    except Exception as e:
        logger.error(f"Intent generation failed: {e}")
        raise HTTPException(status_code=500, detail="Intent generation failed due to an internal error.")

def _vault_entries(base: Path) -> List[str]:
    if not base.exists():
        return []
    entries = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".txt", ".json", ".md"}:
            continue
        rel = p.relative_to(base).as_posix()
        entries.append(rel)
    return sorted(entries, reverse=True)


def _filter_vault_entries(
    files: List[str],
    *,
    hostname: Optional[str] = None,
    site: Optional[str] = None,
    scenario: Optional[str] = None,
    artifact_type: Optional[str] = None,
) -> List[str]:
    out = files
    if hostname:
        hn = hostname.lower()
        out = [f for f in out if hn in f.lower()]
    if site:
        s = site.lower()
        out = [f for f in out if s in f.lower().split("/")[-1]]
    if scenario:
        sc = scenario.lower()
        out = [f for f in out if sc in f.lower()]
    if artifact_type:
        t = artifact_type.lower()
        if t == "config":
            out = [f for f in out if "_config." in f.lower()]
        elif t == "manifest":
            out = [f for f in out if f.endswith("manifest.json")]
        elif t == "package":
            out = [f for f in out if "CHANGE_PACKAGE" in f]
        elif t == "json":
            out = [f for f in out if f.endswith(".json")]
    return out


@app.get("/history")
def get_history(
    request: Request,
    hostname: Optional[str] = None,
    site: Optional[str] = None,
    scenario: Optional[str] = None,
    artifact_type: Optional[str] = None,
):
    # Token authentication removed for offline use
    files = _filter_vault_entries(
        _vault_entries(HISTORY_DIR),
        hostname=hostname,
        site=site,
        scenario=scenario,
        artifact_type=artifact_type,
    )
    return files


@app.get("/system/paths")
def system_paths(request: Request):
    # Token authentication removed for offline use
    return {
        "app_dir": get_app_dir(),
        "vault_dir": str(HISTORY_DIR),
        "checkpoints_dir": get_checkpoints_dir(),
        "version": pipeline.version,
    }


@app.post("/system/open-folder")
def open_folder(body: OpenFolderInput, request: Request):
    # Token authentication removed for offline use
    if ".." in body.path.replace("\\", "/"):
        raise HTTPException(status_code=400, detail="Invalid path.")
    target = Path(body.path).resolve()
    if not target.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found.")
    import sys
    import subprocess
    try:
        if sys.platform == "win32":
            os.startfile(str(target))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(target)], check=False)
        else:
            subprocess.run(["xdg-open", str(target)], check=False)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not open folder: {exc}")
    return {"status": "ok", "path": str(target)}


@app.post("/builder/parse")
def builder_parse(body: ParseConfigInput, request: Request):
    # Token authentication removed for offline use
    return config_builder.analyze_paste(body.running_config)


@app.post("/builder/questions")
def builder_questions(body: BuilderAnswersInput, request: Request):
    # Token authentication removed for offline use
    return {"questions": config_builder.get_questions(body.answers)}


@app.post("/builder/recommend")
def builder_recommend(body: BuilderAnswersInput, request: Request):
    # Token authentication removed for offline use
    return config_builder.recommend(body.answers)

@app.get("/history/{filename}", response_class=PlainTextResponse)
def get_history_content(filename: str, request: Request):
    # Token authentication removed for offline use
    safe_name = Path(filename).as_posix().replace("\\", "/")
    if ".." in safe_name or safe_name.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid artifact name.")
    path = (HISTORY_DIR / safe_name).resolve()
    if not str(path).startswith(str(HISTORY_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid artifact path.")
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found in Vault.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/checkpoints")
def list_checkpoints(request: Request, hostname: Optional[str] = None):
    # Token authentication removed for offline use
    return checkpoints.list_checkpoints(hostname=hostname)


@app.get("/checkpoints/{filename}")
def get_checkpoint(filename: str, request: Request):
    # Token authentication removed for offline use
    safe = Path(filename).name
    path = Path(checkpoints.checkpoint_dir) / safe
    if not path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found.")
    return checkpoints.load_checkpoint(str(path))


@app.get("/util/expand-range")
def expand_range(range_str: str, request: Request):
    # Token authentication removed for offline use
    from utils.range_parser import expand_interface_range
    return {"expanded": expand_interface_range(range_str)}


@app.post("/util/diff-config")
def diff_config(input: DiffInput, request: Request):
    # Token authentication removed for offline use
    diff_text = pipeline.generate_diff(input.baseline, input.proposed)
    return {"diff": diff_text, "lines_added": diff_text.count("\n+")}


@app.post("/util/parse-running-config-diff")
def parse_running_config_diff(input: ParseDiffInput, request: Request):
    """Parse pasted running-config and diff against proposed CLI (read-only validation aid)."""
    # Token authentication removed for offline use
    parsed = config_builder.analyze_paste(input.running_config)
    diff_text = pipeline.generate_diff(input.running_config, input.proposed)
    return {
        "parsed": parsed,
        "diff": diff_text,
        "lines_added": diff_text.count("\n+"),
    }


@app.post("/checkpoints/{filename}/restore-preview")
def restore_checkpoint_preview(filename: str, request: Request):
    """Return checkpoint JSON for wizard restore (does not mutate server state)."""
    # Token authentication removed for offline use
    safe = Path(filename).name
    path = Path(checkpoints.checkpoint_dir) / safe
    if not path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found.")
    data = checkpoints.load_checkpoint(str(path))
    return {"checkpoint": data, "filename": safe}


class LinkValidateInput(BaseModel):
    model: str
    row: Dict[str, Any]
    peer_link_interfaces: List[str] = []
    keepalive_interfaces: List[str] = []
    link_rows: List[Dict[str, Any]] = []
    exclude_po: Optional[int] = None


class CablePlanInput(BaseModel):
    hostname: str
    site_name: str = "DEFAULT_SITE"
    scenario_id: str
    model: str
    overrides: Optional[Dict[str, Any]] = None
    pair_hostname: Optional[str] = None


class PoMapSaveInput(BaseModel):
    default_ranges: Optional[Dict[str, List[int]]] = None
    models: Optional[Dict[str, Dict[str, List[int]]]] = None


def _device_po_dicts(device: Device) -> List[Dict[str, Any]]:
    return [
        {
            "number": po.number,
            "description": po.description,
            "member_interfaces": list(po.member_interfaces),
            "vpc_peer_link": po.vpc_peer_link,
            "vpc_keepalive": po.vpc_keepalive,
        }
        for po in device.port_channels
    ]


def _write_cable_plan_artifact(
    export_dir: str,
    device: Device,
    applied: Dict[str, Any],
    input: ScenarioInput,
    *,
    pair_hostname: Optional[str],
) -> Optional[str]:
    plan = build_cable_plan(
        hostname=device.hostname,
        model=device.model,
        site_name=input.site_name,
        scenario_name=applied.get("scenario_name", ""),
        port_channels=_device_po_dicts(device),
        pair_hostname=pair_hostname,
    )
    md = render_cable_plan_md(plan)
    name = f"{device.hostname}_CABLE_PLAN.md"
    path = Path(export_dir) / name
    path.write_text(md, encoding="utf-8")
    return name


@app.get("/admin/po-map")
def get_po_map(request: Request):
    # Token authentication removed for offline use
    return load_po_map()


@app.post("/admin/po-map")
def post_po_map(body: PoMapSaveInput, request: Request):
    # Token authentication removed for offline use
    return save_po_map(body.model_dump(exclude_none=True))


@app.get("/release/notes")
def release_notes():
    from utils.version import get_app_version
    ver = get_app_version()
    notes_path = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    excerpt = ""
    if notes_path.exists():
        text = notes_path.read_text(encoding="utf-8")
        marker = f"## [{ver}]"
        if marker in text:
            chunk = text.split(marker, 1)[1].split("\n## [", 1)[0]
            excerpt = chunk.strip()[:4000]
    return {"version": ver, "excerpt": excerpt or f"NX-OS Configuration Authority {ver}"}


@app.get("/util/version-diff")
def version_diff(from_id: str, to_id: str, request: Request):
    # Token authentication removed for offline use
    return compare_versions(from_id, to_id, catalog)


@app.post("/util/validate-link")
def validate_link(body: LinkValidateInput, request: Request):
    # Token authentication removed for offline use
    inv = build_reserved_inventory(
        model=body.model,
        peer_link_interfaces=body.peer_link_interfaces,
        keepalive_interfaces=body.keepalive_interfaces,
        link_rows=body.link_rows,
    )
    return validate_link_row(
        body.row,
        inv,
        body.model,
        exclude_self_po=body.exclude_po,
    )


@app.post("/util/suggest-members")
def suggest_link_members(body: LinkValidateInput, request: Request):
    # Token authentication removed for offline use
    hw = catalog.get_hardware_profile(body.model) or {}
    pool = body.row.get("pool", "fiber")
    count = int(body.row.get("count", 2))
    inv = build_reserved_inventory(
        model=body.model,
        peer_link_interfaces=body.peer_link_interfaces,
        keepalive_interfaces=body.keepalive_interfaces,
        link_rows=body.link_rows,
    )
    return {"ports": suggest_members(hw_profile=hw, pool=pool, count=count, inventory=inv)}


@app.post("/util/port-budget")
def get_port_budget(body: LinkValidateInput, request: Request):
    # Token authentication removed for offline use
    hw = catalog.get_hardware_profile(body.model) or {}
    inv = build_reserved_inventory(
        model=body.model,
        peer_link_interfaces=body.peer_link_interfaces,
        keepalive_interfaces=body.keepalive_interfaces,
        link_rows=body.link_rows,
    )
    return port_budget(hw, inv)


@app.post("/util/cable-plan")
def cable_plan_preview(body: CablePlanInput, request: Request):
    # Token authentication removed for offline use
    applied = scenario_engine.apply_scenario(
        body.scenario_id,
        body.hostname,
        body.site_name,
        "10.10.10.10/24",
        "10.10.10.1",
        overrides=body.overrides,
    )
    device = applied["device"]
    plan = build_cable_plan(
        hostname=device.hostname,
        model=device.model,
        site_name=body.site_name,
        scenario_name=applied.get("scenario_name", ""),
        port_channels=_device_po_dicts(device),
        pair_hostname=body.pair_hostname,
    )
    return {"plan": plan, "markdown": render_cable_plan_md(plan)}


@app.get("/util/hostname-hints")
def hostname_hints(request: Request, hostname: str, site: str = "", role: str = "leaf", pair: bool = False):
    # Token authentication removed for offline use
    ok, hints = validate_hostname_rules(hostname, role=role, pair=pair)
    site_ok, site_msg = validate_site_code(site) if site else (True, "")
    return {
        "valid": ok,
        "hints": hints,
        "site_valid": site_ok,
        "site_message": site_msg,
        "suggestion": suggest_hostname(site or "HQ", role, pair),
    }


@app.post("/system/shutdown")
def shutdown_system(request: Request):
    """Stop the local server. Loopback only — no session token required."""
    _enforce_loopback_only(request)
    logger.info("SHUTDOWN REQUEST: Stop button or CLI triggered.")

    def stop_process() -> None:
        time.sleep(0.25)
        shutdown_handler = getattr(request.app.state, "request_shutdown", None)
        if callable(shutdown_handler):
            shutdown_handler()
            return
        os.kill(os.getpid(), 15)

    threading.Thread(target=stop_process, daemon=True).start()
    return {"status": "shutdown_initiated"}
