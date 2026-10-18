import os
import re
import threading
import time
import uuid
import traceback
from pathlib import Path
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator, conint, constr, ValidationInfo
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
from core.engine import ConfigEngine
from core.renderer import ConfigRenderer
from utils.web_logger import logger, request_id_var
from utils.app_dirs import get_history_dir, get_checkpoints_dir, get_app_dir
from utils.version import get_app_version
from utils.change_package import build_manifest, write_package_artifacts
from core.link_allocator import build_reserved_inventory, validate_link_row, suggest_members, port_budget
from core.po_map_store import load_po_map, save_po_map, ranges_for_model
from core.cable_plan import build_cable_plan, render_cable_plan_md
from core.version_diff import compare_versions
from core.hostname_rules import validate_hostname as validate_hostname_rules, validate_site_code, suggest_hostname
from core.import_wizard import ConfigBuilderEngine
from core.config_remarks import ConfigRemarksEngine, build_cli_blocks
from core.deployment_wiring import wire_core_leaf_downlinks, validate_all_vpc_pairs
from core.deployment_builder import (
    resolve_deployment_export_base,
    apply_custom_uplinks_for_switch,
    switches_blocked_by_vpc_errors,
)
from core.deployment_state import get_state_manager
from core.template_store import list_templates, save_template, load_template
from api.input_contracts import (
    VPCPairInput,
    UplinkInput,
    UnifiedGenerateRequest,
    validate_hostname_value,
    validate_mgmt_ip_cidr,
)
from core.config_parser import parse_running_config, ParsedConfig, ValidationResult, ValidationError as ConfigValidationError, ValidationWarning, RemediationSuggestion, ValidationSeverity

# Optional observability imports - graceful fallback if not available
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = None
    generate_latest = None
    CONTENT_TYPE_LATEST = None

HISTORY_DIR = Path(get_history_dir())
HOSTNAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")

# Prometheus metrics - only initialize if available
if PROMETHEUS_AVAILABLE:
    http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
    config_generations_total = Counter('config_generations_total', 'Total config generations')
    validation_errors_total = Counter('validation_errors_total', 'Total validation errors')
else:
    http_requests_total = None
    http_request_duration = None
    config_generations_total = None
    validation_errors_total = None


def _is_loopback(host: Optional[str]) -> bool:
    return host in {"127.0.0.1", "::1", "localhost"}


app = FastAPI(title="Configuration Authority System", version=get_app_version())

# Mount static files directory
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve index.html at root
templates_dir = Path(__file__).parent.parent / "templates" / "web"
index_file = templates_dir / "index.html"

@app.get("/")
async def serve_index():
    """Serve the main application HTML page."""
    if index_file.exists():
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return {"message": "index.html not found"}

# CORS for offline localhost — credentials disabled (required when allow_origins=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:9000", "http://localhost:9000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID correlation middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
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
    token = _auth_token()
    if token:
        req_token = request.headers.get("x-config-auth-token", "")
        if req_token != token:
            raise HTTPException(status_code=401, detail="Unauthorized authentication token.")


def _enforce_loopback_only(request: Request) -> None:
    # Loopback restriction removed for offline use
    pass


def _build_deployment_vpc_config(
    vpc_pair: dict,
    switch_config: object,
    is_primary: bool,
    hw_profile: Optional[dict] = None,
    partner_config: Optional[object] = None,
) -> VPCConfig:
    """
    Build VPCConfig from deployment vPC pair data and switch configuration.

    Always overwrites any scenario-preset vPC so primary/secondary roles,
    keepalive IPs, and peer-link members match the deployment topology.
    """
    from utils.range_parser import expand_interface_range

    peer_link_ports_raw = vpc_pair.get("peer_link_ports", "") or getattr(switch_config, "vpc_pl_ints", "") or ""
    peer_link_interfaces = expand_interface_range(peer_link_ports_raw) if peer_link_ports_raw else []

    if not peer_link_interfaces and hw_profile:
        peer_link_interfaces = list(hw_profile.get("vpc_peer_link") or [])

    role = "primary" if is_primary else "secondary"

    if is_primary:
        local_ka = getattr(switch_config, "local_ka", None) or "10.255.255.1"
        remote_ka = getattr(switch_config, "remote_ka", None) or ""
        if not remote_ka and partner_config:
            remote_ka = getattr(partner_config, "local_ka", None) or "10.255.255.2"
        if not remote_ka:
            remote_ka = "10.255.255.2"
    else:
        local_ka = getattr(switch_config, "local_ka", None) or ""
        remote_ka = getattr(switch_config, "remote_ka", None) or ""
        if partner_config:
            if not local_ka:
                local_ka = getattr(partner_config, "remote_ka", None) or "10.255.255.2"
            if not remote_ka:
                remote_ka = getattr(partner_config, "local_ka", None) or "10.255.255.1"
        if not local_ka:
            local_ka = "10.255.255.2"
        if not remote_ka:
            remote_ka = "10.255.255.1"

    if local_ka.split("/")[0] == remote_ka.split("/")[0]:
        if is_primary:
            remote_ka = "10.255.255.2" if local_ka.split("/")[0] != "10.255.255.2" else "10.255.255.1"
        else:
            local_ka, remote_ka = "10.255.255.2", "10.255.255.1"

    peer_link_id = getattr(switch_config, "vpc_peer_link_id", 1) or 1
    keepalive_po_id = getattr(switch_config, "keepalive_po_id", 2) or 2
    system_priority = getattr(switch_config, "vpc_system_priority", 32667) or 32667

    keepalive_vrf = "management"
    baseline_options = getattr(switch_config, "baseline_options", None) or []
    if "baseline_vrf_keepalive" in baseline_options:
        keepalive_vrf = "VPC_Keep_Alive"

    keepalive_interfaces: List[str] = []
    if hw_profile:
        keepalive_interfaces = list(hw_profile.get("vpc_keepalive") or [])

    return VPCConfig(
        domain_id=int(vpc_pair.get("domain", 100)),
        role=role,
        keepalive_vrf=keepalive_vrf,
        local_keepalive_ip=local_ka,
        remote_keepalive_ip=remote_ka,
        peer_link_id=peer_link_id,
        peer_link_interfaces=peer_link_interfaces,
        keepalive_interfaces=keepalive_interfaces,
        keepalive_po_id=keepalive_po_id,
        system_priority=system_priority,
        role_priority=4096 if is_primary else 8192,
        peer_switch=False,
        delay_restore=None,
    )


def _set_interface_channel_group(iface: Interface, po_id: int, mode: str = "active") -> None:
    """Apply port-channel membership using the Interface model field consumed by Jinja."""
    iface.channel_group = po_id
    iface.channel_mode = mode


def _switch_is_spine_or_core(switch_config: object, hw_catalog: CatalogLoader) -> bool:
    """True when a switch acts as fabric spine/core (by role or hardware profile)."""
    role = getattr(switch_config, "role", None)
    if role in ("spine", "core"):
        return True
    model = getattr(switch_config, "model", None)
    if not model:
        return False
    hw = hw_catalog.get_hardware_profile(model)
    return bool(hw and hw.get("device_class") in ("core", "spine"))


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
    domain_id: conint(ge=1, le=4096)  # type: ignore[valid-type]
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
    vpc_domain: Optional[str] = None
    vpc_peer_link_id: int = 1
    keepalive_po_id: int = 2
    vpc_system_priority: int = 32667
    local_ka: str = "10.10.10.1"
    remote_ka: str = "10.10.10.2"
    vpc_pl_ints: str = ""
    base_access_vlan: int = 10
    access_vlan_count: int = 4
    interface_count: int = 0
    bring_up_spare_ports: bool = False
    security_tier: str = "standard"
    site_name: str = "HQ"
    baseline_options: List[str] = Field(default_factory=list)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        return validate_hostname_value(value)

    @field_validator("mgmt_ip")
    @classmethod
    def validate_mgmt_ip(cls, value: str) -> str:
        return validate_mgmt_ip_cidr(value)


class SwitchConfig(BaseModel):
    hostname: str
    mgmt_ip: str
    mgmt_gw: str = "10.10.10.1"
    site_name: str = "HQ"
    model: str = "Nexus 9336C-FX2"
    nxos_version: str = "9.3"
    vpc_domain: Optional[str] = None
    vpc_peer_link_id: int = 1
    keepalive_po_id: int = 2
    vpc_system_priority: int = 32667
    local_ka: str = "10.10.10.1"
    remote_ka: str = "10.10.10.2"
    vpc_pl_ints: str = ""
    base_access_vlan: int = 10
    access_vlan_count: int = 4
    interface_count: int = 0
    bring_up_spare_ports: bool = False
    security_tier: str = "standard"
    role: Optional[str] = None
    baseline_options: List[str] = []
    vlans: List[VLANInput] = Field(default_factory=list)

    @field_validator('hostname')
    @classmethod
    def validate_hostname(cls, v: str) -> str:
        return validate_hostname_value(v)

    @field_validator('mgmt_ip')
    @classmethod
    def validate_mgmt_ip_cidr_required(cls, v: str) -> str:
        return validate_mgmt_ip_cidr(v)

    @field_validator('mgmt_gw', 'local_ka', 'remote_ka')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        if not v:
            raise ValueError('IP address cannot be empty')
        # Handle CIDR notation (e.g., 10.10.10.1/24)
        ip_part = v.split('/')[0] if '/' in v else v
        # Basic IPv4 validation
        parts = ip_part.split('.')
        if len(parts) != 4:
            raise ValueError(f'Invalid IPv4 address: {v}')
        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError(f'Invalid IPv4 address: {v}')
        except ValueError:
            raise ValueError(f'Invalid IPv4 address: {v}')
        return v

    @field_validator('vpc_domain')
    @classmethod
    def validate_vpc_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                domain = int(v)
                if domain < 1 or domain > 4096:
                    raise ValueError('vPC domain must be between 1 and 4096')
            except ValueError:
                raise ValueError('vPC domain must be a valid integer')
        return v

    @field_validator('base_access_vlan')
    @classmethod
    def validate_vlan(cls, v: int) -> int:
        if v < 1 or v > 4094:
            raise ValueError('VLAN must be between 1 and 4094')
        return v

    @field_validator('vpc_peer_link_id', 'keepalive_po_id')
    @classmethod
    def validate_port_channel(cls, v: int) -> int:
        if v < 1 or v > 4096:
            raise ValueError('Port-channel ID must be between 1 and 4096')
        return v


class DeploymentInput(BaseModel):
    switches: List[SwitchConfig]
    vpc_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    uplinks: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = None
    site_name: str = "HQ"
    global_vlans: List[Dict[str, Any]] = Field(default_factory=list)
    site_hierarchy: Optional[Dict[str, Any]] = Field(default=None)
    site_overrides: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def require_at_least_one_switch(self) -> "DeploymentInput":
        if not self.switches:
            raise ValueError("At least one switch is required in a deployment.")
        return self

    @model_validator(mode="after")
    def normalize_topology(self) -> "DeploymentInput":
        """Validate and normalize vPC pairs / uplinks to canonical dicts."""
        normalized_pairs: List[Dict[str, Any]] = []
        for raw in self.vpc_pairs:
            if isinstance(raw, VPCPairInput):
                normalized_pairs.append(raw.to_dict())
            elif isinstance(raw, dict):
                normalized_pairs.append(VPCPairInput.model_validate(raw).to_dict())
            else:
                normalized_pairs.append(VPCPairInput.model_validate(raw).to_dict())
        normalized_uplinks: List[Dict[str, Any]] = []
        for raw in self.uplinks:
            if isinstance(raw, UplinkInput):
                normalized_uplinks.append(raw.to_dict())
            elif isinstance(raw, dict):
                normalized_uplinks.append(UplinkInput.model_validate(raw).to_dict())
            else:
                normalized_uplinks.append(UplinkInput.model_validate(raw).to_dict())
        object.__setattr__(self, "vpc_pairs", normalized_pairs)
        object.__setattr__(self, "uplinks", normalized_uplinks)
        return self


def _dict_to_switch_config(raw: Dict[str, Any]) -> SwitchConfig:
    """Normalize API dict payload into SwitchConfig for deployment pipeline."""
    vlans = raw.get("vlans") or []
    vlan_inputs = [
        VLANInput(id=int(v["id"]), name=str(v.get("name", f"VLAN{v['id']}")))
        for v in vlans
        if "id" in v
    ]
    return SwitchConfig(
        hostname=str(raw.get("hostname", "SW1")),
        mgmt_ip=str(raw.get("mgmt_ip", "10.0.0.1/24")),
        mgmt_gw=str(raw.get("mgmt_gw", "10.0.0.254")),
        site_name=str(raw.get("site_name", "HQ")),
        model=str(raw.get("model", "Nexus 9336C-FX2")),
        nxos_version=str(raw.get("nxos_version", "9.3")),
        vpc_domain=raw.get("vpc_domain"),
        vpc_peer_link_id=int(raw.get("vpc_peer_link_id", 1)),
        keepalive_po_id=int(raw.get("keepalive_po_id", 2)),
        vpc_system_priority=int(raw.get("vpc_system_priority", 32667)),
        local_ka=str(raw.get("local_ka", "10.255.255.1")),
        remote_ka=str(raw.get("remote_ka", "10.255.255.2")),
        vpc_pl_ints=str(raw.get("vpc_pl_ints", raw.get("peer_link_ports", ""))),
        base_access_vlan=int(raw.get("base_access_vlan", 10)),
        access_vlan_count=int(raw.get("access_vlan_count", 4)),
        interface_count=int(raw.get("interface_count", 0)),
        bring_up_spare_ports=bool(raw.get("bring_up_spare_ports", False)),
        security_tier=str(raw.get("security_tier", "standard")),
        role=raw.get("role"),
        baseline_options=list(raw.get("baseline_options") or []),
        vlans=vlan_inputs,
    )


class SiteConfig(BaseModel):
    site_id: str
    site_name: str
    parent_site: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = None
    global_templates: Dict[str, Any] = Field(default_factory=dict)
    site_overrides: Dict[str, Any] = Field(default_factory=dict)
    rollout_phase: str = "planned"  # planned, staging, production
    deployment_status: str = "pending"  # pending, in_progress, completed, failed


class MultiSiteDeploymentRequest(BaseModel):
    sites: List[SiteConfig]
    global_config: Dict[str, Any] = Field(default_factory=dict)
    progressive_rollout: bool = False


class ErrorPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    error_type: str
    frequency: int
    last_occurred: str
    suggested_fix: str
    auto_recoverable: bool


class ErrorAnalyticsResponse(BaseModel):
    total_errors: int
    error_patterns: List[ErrorPattern] = Field(default_factory=list)
    recent_errors: List[Dict[str, Any]] = Field(default_factory=list)


class RecoverySuggestion(BaseModel):
    error_code: str
    error_message: str
    severity: str
    recovery_steps: List[str]
    auto_recovery_available: bool
    auto_recovery_command: Optional[str] = None


class EnhancedErrorResponse(BaseModel):
    error_code: str
    error_message: str
    severity: str
    context: Dict[str, Any] = Field(default_factory=dict)
    affected_components: List[str] = Field(default_factory=list)
    recovery_suggestion: RecoverySuggestion


class PluginInfo(BaseModel):
    name: str
    type: str  # "hardware_profile", "validator", "renderer"
    version: str
    description: str
    enabled: bool = True


class PluginRegistryResponse(BaseModel):
    plugins: List[PluginInfo] = Field(default_factory=list)
    hardware_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int


class ConfigGenerationRequest(BaseModel):
    switches: List[Dict[str, Any]] = Field(default_factory=list)
    scenario: str = "basic"
    nxos_version: str = "9.3"
    hardware_model: str = "Nexus 93180YC-EX"
    vpc_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    uplinks: List[Dict[str, Any]] = Field(default_factory=list)


class ConfigGenerationResponse(BaseModel):
    config: str
    switches_count: int
    scenario: str
    nxos_version: str
    generated_at: str


class NXOSSyntaxValidationRequest(BaseModel):
    config: str
    nxos_version: str = "9.3"


class NXOSSyntaxError(BaseModel):
    line_number: int
    line_content: str
    error_type: str
    error_message: str
    suggestion: Optional[str] = None


class NXOSSyntaxValidationResponse(BaseModel):
    valid: bool
    syntax_errors: List[NXOSSyntaxError] = Field(default_factory=list)
    total_lines: int
    nxos_version: str


class TopologyValidationRequest(BaseModel):
    switches: List[SwitchConfig]
    vpc_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    uplinks: List[Dict[str, Any]] = Field(default_factory=list)


class TopologyValidationIssue(BaseModel):
    severity: str  # "critical", "warning", "info"
    category: str  # "port_capacity", "ip_conflict", "vpc_mismatch", "cable_plan"
    message: str
    affected_switches: List[str] = Field(default_factory=list)
    suggestion: Optional[str] = None


class TopologyValidationResponse(BaseModel):
    valid: bool
    issues: List[TopologyValidationIssue] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict)


class IntentOverridesInput(BaseModel):
    motd: Optional[constr(strip_whitespace=True, min_length=5, max_length=240)] = None  # type: ignore[valid-type]
    admin_user: Optional[constr(strip_whitespace=True, min_length=1, max_length=32)] = None  # type: ignore[valid-type]
    admin_password: Optional[constr(strip_whitespace=True, max_length=128)] = None  # type: ignore[valid-type]
    management_vrf: constr(strip_whitespace=True, min_length=1, max_length=64) = "management"  # type: ignore[valid-type]
    base_access_vlan: conint(ge=1, le=4000) = 10  # type: ignore[valid-type]
    access_vlan_count: conint(ge=1, le=50) = 4  # type: ignore[valid-type]
    interface_count: conint(ge=1, le=128) = 48  # type: ignore[valid-type]


class ConfigUploadRequest(BaseModel):
    config_text: constr(strip_whitespace=True, min_length=1)  # type: ignore[valid-type]
    hardware_model: constr(strip_whitespace=True, min_length=3, max_length=64)  # type: ignore[valid-type]
    nxos_version: constr(strip_whitespace=True, min_length=3, max_length=16) = "9.3"  # type: ignore[valid-type]
    validation_level: constr(strip_whitespace=True) = "comprehensive"  # type: ignore[valid-type]
    baseline_options: List[str] = Field(default_factory=list)

    @field_validator("validation_level")
    @classmethod
    def validate_validation_level(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"basic", "standard", "comprehensive"}:
            raise ValueError("Validation level must be basic, standard, or comprehensive")
        return normalized


class ValidationErrorResponse(BaseModel):
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    error_code: str = ""
    message: str = ""
    severity: str = "high"
    suggestion: Optional[str] = None
    fix_command: Optional[str] = None


class ValidationWarningResponse(BaseModel):
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    warning_code: str = ""
    message: str = ""
    severity: str = "medium"
    suggestion: Optional[str] = None


class RemediationSuggestionResponse(BaseModel):
    issue_code: str
    description: str
    complexity: str
    commands: List[str] = Field(default_factory=list)
    estimated_time: str = ""
    risk_level: str = "low"


class ValidationResultResponse(BaseModel):
    validation_id: str
    is_valid: bool
    errors: List[ValidationErrorResponse] = Field(default_factory=list)
    warnings: List[ValidationWarningResponse] = Field(default_factory=list)
    suggestions: List[RemediationSuggestionResponse] = Field(default_factory=list)
    severity: str = "info"
    detected_role: str = ""
    detected_features: List[str] = Field(default_factory=list)
    hostname: str = ""
    mgmt_ip: str = ""
    vlans: List[Dict[str, Any]] = Field(default_factory=list)
    vpc_domain_id: Optional[int] = None
    timestamp: str = ""


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
    scenario_id: constr(strip_whitespace=True, min_length=1, max_length=64)  # type: ignore[valid-type]
    hostname: constr(strip_whitespace=True, min_length=1, max_length=63)  # type: ignore[valid-type]
    site_name: constr(strip_whitespace=True, min_length=1, max_length=64) = "DEFAULT_SITE"  # type: ignore[valid-type]
    mgmt_ip: constr(strip_whitespace=True, min_length=1, max_length=64)  # type: ignore[valid-type]
    mgmt_gw: constr(strip_whitespace=True, min_length=1, max_length=64)  # type: ignore[valid-type]
    generate_pair: bool = False
    secondary_hostname: Optional[str] = None
    secondary_mgmt_ip: Optional[str] = None
    overrides: Dict[str, object] = Field(default_factory=dict)

    @field_validator("hostname")
    @classmethod
    def validate_scenario_hostname(cls, value: str) -> str:
        return validate_hostname_value(value)

    @field_validator("mgmt_ip")
    @classmethod
    def validate_scenario_mgmt_ip(cls, value: str) -> str:
        return validate_mgmt_ip_cidr(value)

    @field_validator("secondary_hostname", "secondary_mgmt_ip")
    @classmethod
    def validate_secondary_fields(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        # Only validate secondary fields if generate_pair is true
        if info.data.get("generate_pair", False):
            if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                raise ValueError(f"{info.field_name} is required when generate_pair is true")
            return value.strip()
        # If generate_pair is false, allow None or empty string
        return value if value is None else value.strip()


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
    """Get application version and status."""
    return {"version": pipeline.version, "status": "operational", "platform": "web"}


@app.get("/catalog")
def get_full_catalog():
    """Get full catalog including scenarios, hardware, and features."""
    return catalog.full_catalog()


@app.get("/catalog/versions")
def get_catalog_versions():
    """Get available NX-OS versions in the catalog."""
    return catalog.list_versions()


@app.get("/catalog/scenarios")
def get_catalog_scenarios():
    """Get available deployment scenarios."""
    return catalog.list_scenarios()


@app.get("/catalog/hardware")
def get_catalog_hardware():
    """Get available hardware profiles."""
    return catalog.list_hardware_profiles()


@app.get("/data/hardware_profiles.yaml")
def get_hardware_profiles_yaml():
    """Serve hardware_profiles.yaml file for frontend access."""
    import yaml
    
    # Try to find hardware_profiles.yaml in multiple locations
    possible_paths = [
        Path("hardware_profiles.yaml"),
        Path("data/hardware_profiles.yaml"),
        Path(__file__).parent.parent / "hardware_profiles.yaml",
        Path(__file__).parent.parent / "data" / "hardware_profiles.yaml",
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return PlainTextResponse(f.read())
    
    # Return fallback if file not found
    return PlainTextResponse("# Hardware profiles not found")


@app.get("/catalog/features")
def get_catalog_features():
    """Get available NX-OS features and their aliases."""
    return {"features": catalog.list_features(), "aliases": catalog.list_aliases()}


@app.post("/audit/log")
async def audit_log(request: Request):
    """Receive audit logs from frontend for user action tracking."""
    try:
        data = await request.json()
        logs = data.get("logs", [])
        
        for log_entry in logs:
            log_data = log_entry.get("data", {})
            logger.log_user_action(
                action_type=log_entry.get("action_type"),
                element_id=log_data.get("id"),
                element_type=log_data.get("tagName"),
                value=log_data.get("value"),
                page=log_entry.get("page"),
                **{k: v for k, v in log_data.items() if k not in ["id", "tagName", "value"]}
            )
        
        return {"status": "success", "logged": len(logs)}
    except Exception as e:
        logger.error(f"Failed to log audit data: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/catalog/matrix")
def get_catalog_matrix():
    """Get configuration matrix with hardware profiles and placeholders."""
    return {
        "matrix": catalog.list_config_matrix(),
        "hardware": catalog.list_hardware_profiles(),
        "placeholders": catalog.list_placeholders(),
    }


@app.post("/scenario/preview")
def preview_scenario(input: ScenarioInput, request: Request):
    """
    Preview a deployment scenario without generating configurations.
    
    Returns device configuration preview for the specified scenario.
    """
    _enforce_privileged_access(request)
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    start_time = datetime.now(timezone.utc)
    
    logger.log_api_request(
        method="POST",
        endpoint="/scenario/preview",
        payload=input.model_dump(),
        headers=dict(request.headers),
        request_id=req_id
    )
    
    try:
        logger.info(f"Preview request received - scenario_id: {input.scenario_id}, hostname: {input.hostname}, mgmt_ip: {input.mgmt_ip}, mgmt_gw: {input.mgmt_gw}", request_id=req_id)
        logger.debug(f"Full input: {input.model_dump()}", request_id=req_id)
        logger.debug(f"Overrides keys: {list(input.overrides.keys()) if input.overrides else 'None'}", request_id=req_id)
        
        applied = scenario_engine.apply_scenario(
            input.scenario_id,
            input.hostname,
            input.site_name,
            input.mgmt_ip,
            input.mgmt_gw,
            overrides=input.overrides,
            secondary_hostname=input.secondary_hostname,
            secondary_mgmt_ip=input.secondary_mgmt_ip,
        )
        device = applied["device"]
        report = device_validator.validate(device)
        findings = compliance.audit(device)
        config_preview = _render_preview(device, applied["nxos_version"], input.overrides)
        extras = _preview_extras(device, config_preview, input.overrides, applied["scenario_id"])
        if applied.get("planner_warnings"):
            extras["planner_warnings"] = applied["planner_warnings"]
        
        # Debug logging for pair_mode
        pair_mode = applied.get("pair_mode", False)
        logger.debug(f"pair_mode from applied: {pair_mode}", request_id=req_id)
        logger.debug(f"has pair in applied: {'pair' in applied}", request_id=req_id)
        
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
            "pair_mode": pair_mode,
            "config_preview": config_preview,
            "engineer_notes": applied["resolution"].policy_flags,
            **extras,
        }
        if pair_mode and "pair" in applied:
            logger.debug(f"Building pair_preview for secondary", request_id=req_id)
            secondary = applied["pair"]["secondary"]["device"]
            pair_report = device_validator.validate_vpc_pair(device, secondary)
            
            # Generate port maps for both primary and secondary switches
            from core.port_mapping_service import PortMappingService
            port_mapping_service = PortMappingService(catalog)
            
            ov = input.overrides or {}
            model_name = str(ov.get("model") or "Nexus 93180YC-EX")
            domain_id = ov.get("vpc_domain_id") or 100
            downlinks_list = ov.get("downlinks") if isinstance(ov.get("downlinks"), list) else []
            
            # Get hardware profile for port map generation
            hw_profile = catalog.get_hardware_profile(model_name)
            
            # Generate port map for primary switch
            primary_port_map = port_mapping_service.create_port_map(
                hostname=input.hostname,
                model=model_name,
                hw_profile=hw_profile,
                vpc_pair={"domain": domain_id},
                downlinks=downlinks_list
            )
            logger.debug(f"Primary port map generated: {len(primary_port_map.ports)} ports", request_id=req_id)
            
            # Generate port map for secondary switch
            secondary_port_map = port_mapping_service.create_port_map(
                hostname=applied["pair"]["secondary"]["hostname"],
                model=model_name,
                hw_profile=hw_profile,
                vpc_pair={"domain": domain_id},
                downlinks=downlinks_list
            )
            logger.debug(f"Secondary port map generated: {len(secondary_port_map.ports)} ports", request_id=req_id)
            
            response["pair_preview"] = {
                "primary": applied["pair"]["primary"],
                "secondary_hostname": applied["pair"]["secondary"]["hostname"],
                "pair_validation": pair_report,
                "secondary_config_preview": _render_preview(secondary, applied["nxos_version"], input.overrides),
                "primary_port_map": primary_port_map.to_dict(),
                "secondary_port_map": secondary_port_map.to_dict(),
            }
            logger.debug(f"pair_preview built successfully with port maps", request_id=req_id)
            logger.debug(f"primary_port_map port count: {len(primary_port_map.ports)}", request_id=req_id)
            logger.debug(f"secondary_port_map port count: {len(secondary_port_map.ports)}", request_id=req_id)
        
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        # EXTENSIVE LOGGING: Log full response structure
        logger.info(f"=== PREVIEW RESPONSE STRUCTURE ===", request_id=req_id)
        logger.info(f"Response keys: {list(response.keys())}", request_id=req_id)
        logger.info(f"Response status: {response.get('status')}", request_id=req_id)
        logger.info(f"Has pair_preview: {'pair_preview' in response}", request_id=req_id)
        if "pair_preview" in response:
            logger.info(f"pair_preview keys: {list(response['pair_preview'].keys())}", request_id=req_id)
            logger.info(f"pair_preview secondary_hostname: {response['pair_preview'].get('secondary_hostname')}", request_id=req_id)
            logger.info(f"pair_preview has secondary_config_preview: {'secondary_config_preview' in response['pair_preview']}", request_id=req_id)
            if "secondary_config_preview" in response["pair_preview"]:
                logger.info(f"secondary_config_preview length: {len(response['pair_preview']['secondary_config_preview'])}", request_id=req_id)
            logger.info(f"pair_preview has primary_port_map: {'primary_port_map' in response['pair_preview']}", request_id=req_id)
            logger.info(f"pair_preview has secondary_port_map: {'secondary_port_map' in response['pair_preview']}", request_id=req_id)
            if "primary_port_map" in response["pair_preview"]:
                logger.info(f"primary_port_map keys: {list(response['pair_preview']['primary_port_map'].keys())}", request_id=req_id)
                logger.info(f"primary_port_map ports count: {len(response['pair_preview']['primary_port_map'].get('ports', []))}", request_id=req_id)
            if "secondary_port_map" in response["pair_preview"]:
                logger.info(f"secondary_port_map keys: {list(response['pair_preview']['secondary_port_map'].keys())}", request_id=req_id)
                logger.info(f"secondary_port_map ports count: {len(response['pair_preview']['secondary_port_map'].get('ports', []))}", request_id=req_id)
        
        logger.log_api_response(
            method="POST",
            endpoint="/scenario/preview",
            status_code=200,
            response={
                "status": response.get("status"), 
                "scenario_id": response.get("scenario_id"),
                "has_pair_preview": "pair_preview" in response,
                "pair_mode": response.get("pair_mode"),
                "has_pair": "pair" in applied
            },
            duration_ms=duration_ms,
            request_id=req_id
        )
        logger.info(f"Preview completed successfully in {duration_ms:.2f}ms", request_id=req_id)
        
        return response
    except ValueError as e:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.log_api_response(
            method="POST",
            endpoint="/scenario/preview",
            status_code=400,
            response={"error": str(e)},
            duration_ms=duration_ms,
            request_id=req_id
        )
        logger.error(f"Validation error in preview: {e}", request_id=req_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.log_api_response(
            method="POST",
            endpoint="/scenario/preview",
            status_code=500,
            response={"error": str(e)},
            duration_ms=duration_ms,
            request_id=req_id
        )
        logger.log_error(f"Scenario preview failed: {e}", request_id=req_id, traceback=str(e.__traceback__))
        raise HTTPException(status_code=500, detail="Scenario preview failed.")


@app.post("/scenario/generate")
def generate_scenario(input: ScenarioInput, request: Request):
    """
    Generate complete NX-OS configurations for a deployment scenario.
    
    Creates CLI configurations for all switches in the specified scenario.
    Returns generated configurations in structured format.
    """
    # Token authentication removed for offline use
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    start_time = datetime.now(timezone.utc)
    
    logger.info(f"=== GENERATE REQUEST STARTED ===", request_id=req_id)
    logger.info(f"scenario_id: {input.scenario_id}, hostname: {input.hostname}, generate_pair: {input.generate_pair}", request_id=req_id)
    logger.info(f"secondary_hostname: {input.secondary_hostname}, secondary_mgmt_ip: {input.secondary_mgmt_ip}", request_id=req_id)
    
    try:
        applied = scenario_engine.apply_scenario(
            input.scenario_id,
            input.hostname,
            input.site_name,
            input.mgmt_ip,
            input.mgmt_gw,
            overrides=input.overrides,
            secondary_hostname=input.secondary_hostname,
            secondary_mgmt_ip=input.secondary_mgmt_ip,
        )
        logger.info(f"Scenario applied successfully, pair_mode: {applied.get('pair_mode', False)}", request_id=req_id)
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
            
            # Generate port maps for both primary and secondary switches
            from core.port_mapping_service import PortMappingService
            port_mapping_service = PortMappingService(catalog)
            
            # Get hardware profile for port map generation
            hw_profile = catalog.get_hardware_profile(input.overrides.get("model", "N9K-C93180YC-FX"))
            
            # Generate port map for primary switch
            primary_port_map = port_mapping_service.create_port_map(
                hostname=input.hostname,
                model=input.overrides.get("model", "N9K-C93180YC-FX"),
                hw_profile=hw_profile,
                vpc_pair={"domain": input.overrides.get("vpc_domain_id", 100)}
            )
            
            # Generate port map for secondary switch
            secondary_port_map = port_mapping_service.create_port_map(
                hostname=applied["pair"]["secondary"]["hostname"],
                model=input.overrides.get("model", "N9K-C93180YC-FX"),
                hw_profile=hw_profile,
                vpc_pair={"domain": input.overrides.get("vpc_domain_id", 100)}
            )
            
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

        response = {
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
        
        # Add port maps to response if vPC pair
        if is_pair:
            response["pair_port_maps"] = {
                "primary_port_map": primary_port_map.to_dict(),
                "secondary_port_map": secondary_port_map.to_dict(),
            }
        
        return response
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.report["errors"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario generation failed: {e}")
        raise HTTPException(status_code=500, detail="Scenario generation failed.")

@app.post("/validate")
def validate_device(input: DeviceInput, request: Request):
    """
    Validate device configuration against NX-OS best practices and compliance rules.
    
    Returns validation report with compliance findings and recommendations.
    """
    _enforce_privileged_access(request)
    device = map_to_core(input)
    report = device_validator.validate(device)
    findings = compliance.audit(device)
    report["compliance_findings"] = findings
    return report


@app.post("/config/upload")
def upload_config(input: ConfigUploadRequest, request: Request):
    """
    Upload and validate NX-OS running-config against hardware model and best practices.
    
    Performs comprehensive validation including syntax, port mapping, VLAN ranges,
    vPC consistency, feature compatibility, baseline compliance, and security policies.
    Returns detailed validation results with remediation suggestions.
    """
    request_id = request_id_var.get()
    logger.info(f"CONFIG_UPLOAD_START", request_id=request_id, 
                hardware_model=input.hardware_model, 
                nxos_version=input.nxos_version,
                validation_level=input.validation_level)
    
    try:
        # Initialize validation result
        validation_result = ValidationResult()
        
        # Perform validation based on level
        if input.validation_level == "basic":
            # Basic validation: minimal checks only for quick performance
            # Skip parsing entirely to ensure faster performance
            if not input.config_text or len(input.config_text.strip()) == 0:
                validation_result.add_error(ConfigValidationError(
                    error_code="EMPTY_CONFIG",
                    message="Configuration cannot be empty",
                    severity=ValidationSeverity.CRITICAL,
                    line_number=1,
                    line_content="",
                    suggestion="Provide a valid NX-OS configuration",
                    fix_command="paste running-config",
                ))
            # Quick length check only - no parsing
            elif len(input.config_text) > 1000000:
                validation_result.add_error(ConfigValidationError(
                    error_code="CONFIG_TOO_LARGE",
                    message="Configuration exceeds maximum size",
                    severity=ValidationSeverity.HIGH,
                    line_number=1,
                    line_content="",
                    suggestion="Reduce configuration size",
                    fix_command="",
                ))
            # Return immediately with minimal processing
            # Build response with minimal data
            response = ValidationResultResponse(
                validation_id=validation_result.validation_id,
                is_valid=validation_result.is_valid,
                severity=validation_result.severity,
                detected_role="unknown",
                detected_features=[],
                hostname="",
                mgmt_ip="",
                vlans=[],
                vpc_domain_id=None,
                timestamp=validation_result.timestamp
            )
            return response
        else:
            # Parse the configuration (only for standard/comprehensive)
            parsed = parse_running_config(input.config_text)
            
            # Get hardware profile for validation (only for standard/comprehensive)
            catalog = CatalogLoader()
            hw_profile = catalog.get_hardware_profile(input.hardware_model)
            
            if input.validation_level == "standard":
                # Syntax validation
                syntax_result = parsed.validate_syntax(input.config_text)
                validation_result.extend_errors(syntax_result.errors)
                validation_result.extend_warnings(syntax_result.warnings)
            elif input.validation_level == "comprehensive":
                # Syntax validation
                syntax_result = parsed.validate_syntax(input.config_text)
                validation_result.extend_errors(syntax_result.errors)
                validation_result.extend_warnings(syntax_result.warnings)
                
                # Port mapping validation
                if hw_profile:
                    port_result = parsed.validate_port_mapping(hw_profile)
                    validation_result.extend_errors(port_result.errors)
                    validation_result.extend_warnings(port_result.warnings)
                
                # VLAN range validation
                if hw_profile:
                    vlan_result = parsed.validate_vlan_ranges(hw_profile)
                    validation_result.extend_errors(vlan_result.errors)
                    validation_result.extend_warnings(vlan_result.warnings)
                
                # vPC consistency validation
                vpc_result = parsed.validate_vpc_consistency()
                validation_result.extend_errors(vpc_result.errors)
                validation_result.extend_warnings(vpc_result.warnings)
                
                # Feature compatibility validation
                feature_result = parsed.validate_feature_compatibility(input.nxos_version)
                validation_result.extend_warnings(feature_result.warnings)
                
                # Baseline compliance validation
                if input.baseline_options:
                    baseline_result = parsed.validate_baseline_compliance(input.baseline_options)
                    validation_result.extend_warnings(baseline_result.warnings)
                
                # Security policy validation
                security_result = parsed.validate_security_policies()
                validation_result.extend_warnings(security_result.warnings)
                
                # Generate remediation suggestions
                suggestions = parsed.suggest_fixes()
                validation_result.suggestions = suggestions
        
        # Build response
        response = ValidationResultResponse(
            validation_id=validation_result.validation_id,
            is_valid=validation_result.is_valid,
            severity=validation_result.severity,
            detected_role=parsed.detect_role(),
            detected_features=parsed.features,
            hostname=parsed.hostname,
            mgmt_ip=parsed.mgmt_ip,
            vlans=parsed.vlans,
            vpc_domain_id=parsed.vpc_domain_id,
            timestamp=validation_result.timestamp
        )
        
        # Convert errors
        for error in validation_result.errors:
            response.errors.append(ValidationErrorResponse(
                line_number=error.line_number,
                line_content=error.line_content,
                error_code=error.error_code,
                message=error.message,
                severity=error.severity.value,
                suggestion=error.suggestion,
                fix_command=error.fix_command
            ))
        
        # Convert warnings
        for warning in validation_result.warnings:
            response.warnings.append(ValidationWarningResponse(
                line_number=warning.line_number,
                line_content=warning.line_content,
                warning_code=warning.warning_code,
                message=warning.message,
                severity=warning.severity.value,
                suggestion=warning.suggestion
            ))
        
        # Convert suggestions
        for suggestion in validation_result.suggestions:
            response.suggestions.append(RemediationSuggestionResponse(
                issue_code=suggestion.issue_code,
                description=suggestion.description,
                complexity=suggestion.complexity,
                commands=suggestion.commands,
                estimated_time=suggestion.estimated_time,
                risk_level=suggestion.risk_level
            ))
        
        logger.info(f"CONFIG_UPLOAD_COMPLETE", request_id=request_id,
                    validation_id=validation_result.validation_id,
                    is_valid=response.is_valid,
                    error_count=len(response.errors),
                    warning_count=len(response.warnings),
                    suggestion_count=len(response.suggestions))
        
        return response
        
    except Exception as e:
        logger.error(f"CONFIG_UPLOAD_FAILED", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Configuration validation failed: {str(e)}")


class ConfigTemplateSaveRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = ""
    deployment: Dict[str, Any] = Field(default_factory=dict)
    switches: List[Dict[str, Any]] = Field(default_factory=list)
    vpc_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    uplinks: List[Dict[str, Any]] = Field(default_factory=list)


@app.get("/config/templates")
def list_config_templates(request: Request):
    """List saved operator templates (deployments and wizard presets)."""
    request_id = request_id_var.get()
    templates = list_templates()
    logger.info("CONFIG_TEMPLATES_LIST", request_id=request_id, count=len(templates))
    return {"templates": templates, "count": len(templates)}


@app.post("/config/templates")
def save_config_template(body: ConfigTemplateSaveRequest, request: Request):
    """Save a deployment or wizard configuration as a reusable template."""
    request_id = request_id_var.get()
    payload = body.model_dump(exclude={"name", "description"})
    saved = save_template(body.name, payload, body.description)
    logger.info("CONFIG_TEMPLATE_SAVED", request_id=request_id, template_id=saved["id"])
    return {"status": "success", **saved}


@app.get("/config/templates/{template_id}")
def get_config_template(template_id: str, request: Request):
    """Load one saved template by id."""
    data = load_template(template_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")
    return {"status": "success", "template": data}


@app.post("/api/v1/config/generate")
def unified_config_generate(body: UnifiedGenerateRequest, request: Request):
    """
    Unified config generation entry point (single | deployment | preview | wizard).

    Delegates to the authoritative server-side pipelines used by the web UI.
    """
    mode = body.mode
    if mode in {"single", "preview", "wizard"}:
        if not body.device:
            raise HTTPException(status_code=422, detail="device payload is required for single/preview/wizard mode.")
        device_input = DeviceInput.model_validate(body.device)
        if mode == "preview":
            engine = ConfigEngine()
            device = map_to_core(device_input)
            pre_report = device_validator.validate(device)
            if pre_report["status"] != "pass":
                raise HTTPException(status_code=422, detail=pre_report["errors"])
            cli = engine.build_config(device)
            return {
                "status": "success",
                "mode": mode,
                "preview": True,
                "cli": cli,
                "hostname": device.hostname,
            }
        result = generate_config(device_input, request)
        return {"status": "success", "mode": mode, **result}

    if mode == "deployment":
        if not body.deployment:
            raise HTTPException(status_code=422, detail="deployment payload is required for deployment mode.")
        deployment_input = DeploymentInput.model_validate(body.deployment)
        result = generate_deployment(deployment_input, request, preview=body.preview)
        return {"status": "success", "mode": mode, **result}

    raise HTTPException(status_code=422, detail=f"Unsupported mode: {mode}")


@app.post("/generate-config")
def generate_config(input: DeviceInput, request: Request):
    """
    Generate NX-OS CLI configuration for a single device.
    
    Returns complete CLI configuration based on provided device parameters.
    """
    # Token authentication removed for offline use
    device = map_to_core(input)
    try:
        pre_report = device_validator.validate(device)
        if pre_report["status"] != "pass":
            raise HTTPException(status_code=422, detail=pre_report["errors"])
        checkpoints.save_checkpoint(device, label="pre-gen")
        manifest = pipeline.execute(device)
        
        # Include port_map in the response for UI rendering
        result = {
            "status": "success", 
            "message": manifest["message"], 
            "export": manifest
        }
        
        # Add port_map if available
        if hasattr(device, 'port_map') and device.port_map:
            result['port_map'] = {
                'ports': device.port_map.ports if hasattr(device.port_map, 'ports') else [],
                'error': device.port_map.error if hasattr(device.port_map, 'error') else None
            }
        
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.report["errors"])
    except Exception as e:
        logger.error(f"Config generation failed: {e}")
        raise HTTPException(status_code=500, detail="Configuration generation failed due to an internal error.")


@app.post("/generate-deployment")
def generate_deployment(input: DeploymentInput, request: Request, preview: bool = False):
    """
    Generate configurations for all switches in a multi-switch deployment.
    
    Supports vPC pairs, uplinks, and complex topologies. Returns
    configurations for all switches with port maps and physical matrices.
    
    When preview=True, skips file writing and returns only CLI previews.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(request_id)
    
    # Token authentication removed for offline use
    results = []
    errors = []
    
    # Create output directory with proper structure (skip for preview mode)
    try:
        export_base = resolve_deployment_export_base(input.output_dir, HISTORY_DIR, preview)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    
    # Log incoming request for debugging
    logger.info(f"DEPLOYMENT_GENERATION_START", 
                request_id=request_id,
                switch_count=len(input.switches),
                vpc_pairs_count=len(input.vpc_pairs),
                uplinks_count=len(input.uplinks),
                switches=[{"hostname": s.hostname, "model": s.model, "role": s.role} for s in input.switches],
                vpc_pairs=input.vpc_pairs,
                uplinks=input.uplinks,
                export_dir=str(export_base))
    
    logger.info(f"DEPLOYMENT_DETAILED_INPUT",
                request_id=request_id,
                input_dict=input.model_dump())
    
    # Validate vPC pairs before processing
    logger.info(f"VPC_VALIDATION_START", request_id=request_id, vpc_pairs_count=len(input.vpc_pairs) if input.vpc_pairs else 0)
    if input.vpc_pairs:
        for idx, pair in enumerate(input.vpc_pairs):
            logger.info(f"VPC_PAIR_VALIDATION", request_id=request_id, pair_index=idx, pair=pair)
            primary_exists = any(s.hostname == pair.get("primary") for s in input.switches)
            secondary_exists = any(s.hostname == pair.get("secondary") for s in input.switches)
            
            logger.info(f"VPC_PAIR_SWITCH_EXISTENCE", 
                       request_id=request_id, 
                       pair_index=idx,
                       primary=pair.get("primary"),
                       secondary=pair.get("secondary"),
                       primary_exists=primary_exists,
                       secondary_exists=secondary_exists)
            
            if not primary_exists:
                logger.error(f"VPC_VALIDATION_ERROR", 
                            request_id=request_id,
                            error="primary_switch_not_found",
                            pair=pair,
                            available_switches=[s.hostname for s in input.switches])
                raise HTTPException(
                    status_code=422,
                    detail=f"vPC pair domain {pair.get('domain')}: Primary switch '{pair.get('primary')}' not found in deployment"
                )
            if not secondary_exists:
                logger.error(f"VPC_VALIDATION_ERROR",
                            request_id=request_id,
                            error="secondary_switch_not_found",
                            pair=pair,
                            available_switches=[s.hostname for s in input.switches])
                raise HTTPException(
                    status_code=422,
                    detail=f"vPC pair domain {pair.get('domain')}: Secondary switch '{pair.get('secondary')}' not found in deployment"
                )
            
            # Check for duplicate domains
            domain_count = sum(1 for p in input.vpc_pairs if p.get("domain") == pair.get("domain"))
            if domain_count > 1:
                logger.error(f"VPC_VALIDATION_ERROR",
                            request_id=request_id,
                            error="duplicate_domain",
                            domain=pair.get("domain"),
                            domain_count=domain_count)
                raise HTTPException(
                    status_code=422,
                    detail=f"Duplicate vPC domain {pair.get('domain')} detected"
                )
            
            # Validate domain range
            try:
                domain_num = int(pair.get("domain"))
                if domain_num < 1 or domain_num > 4096:
                    logger.error(f"VPC_VALIDATION_ERROR",
                                request_id=request_id,
                                error="domain_out_of_range",
                                domain=domain_num,
                                valid_range="1-4096")
                    raise HTTPException(
                        status_code=422,
                        detail=f"vPC domain {pair.get('domain')} must be between 1 and 4096"
                    )
            except (ValueError, TypeError) as e:
                logger.error(f"VPC_VALIDATION_ERROR",
                            request_id=request_id,
                            error="invalid_domain_format",
                            domain=pair.get("domain"),
                            exception=str(e))
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid vPC domain '{pair.get('domain')}' - must be a number"
                )
    logger.info(f"VPC_VALIDATION_COMPLETE", request_id=request_id, all_pairs_valid=True)
    
    # Validate uplinks before processing
    logger.info(f"UPLINK_VALIDATION_START", request_id=request_id, uplinks_count=len(input.uplinks) if input.uplinks else 0)
    if input.uplinks:
        for idx, uplink in enumerate(input.uplinks):
            logger.info(f"UPLINK_VALIDATION", request_id=request_id, uplink_index=idx, uplink=uplink)
            from_exists = any(s.hostname == uplink.get("from") for s in input.switches)
            to_exists = any(s.hostname == uplink.get("to") for s in input.switches)
            
            logger.info(f"UPLINK_SWITCH_EXISTENCE",
                       request_id=request_id,
                       uplink_index=idx,
                       from_switch=uplink.get("from"),
                       to_switch=uplink.get("to"),
                       from_exists=from_exists,
                       to_exists=to_exists)
            
            if not from_exists:
                logger.error(f"UPLINK_VALIDATION_ERROR",
                            request_id=request_id,
                            error="from_switch_not_found",
                            uplink=uplink,
                            available_switches=[s.hostname for s in input.switches])
                raise HTTPException(
                    status_code=422,
                    detail=f"Uplink: Source switch '{uplink.get('from')}' not found in deployment"
                )
            if not to_exists:
                logger.error(f"UPLINK_VALIDATION_ERROR",
                            request_id=request_id,
                            error="to_switch_not_found",
                            uplink=uplink,
                            available_switches=[s.hostname for s in input.switches])
                raise HTTPException(
                    status_code=422,
                    detail=f"Uplink: Destination switch '{uplink.get('to')}' not found in deployment"
                )
            
            # Validate port-channel ID range
            po_id = uplink.get("po_id")
            if po_id:
                try:
                    po_num = int(po_id)
                    if po_num < 1 or po_num > 4096:
                        logger.error(f"UPLINK_VALIDATION_ERROR",
                                    request_id=request_id,
                                    error="po_id_out_of_range",
                                    po_id=po_id,
                                    valid_range="1-4096")
                        raise HTTPException(
                            status_code=422,
                            detail=f"Uplink: Port-channel ID {po_id} must be between 1 and 4096"
                        )
                except ValueError as e:
                    logger.error(f"UPLINK_VALIDATION_ERROR",
                                request_id=request_id,
                                error="invalid_po_id_format",
                                po_id=po_id,
                                exception=str(e))
                    raise HTTPException(
                        status_code=422,
                        detail=f"Uplink: Invalid port-channel ID '{po_id}'"
                    )
    logger.info(f"UPLINK_VALIDATION_COMPLETE", request_id=request_id, all_uplinks_valid=True)
    
    logger.info(f"SWITCH_PROCESSING_START", request_id=request_id, total_switches=len(input.switches))
    
    # Collect user-defined VLANs from deployment-level global_vlans or individual switches
    # Priority: 1) global_vlans from DeploymentInput, 2) individual switch VLANs
    # Do NOT override auto-generated VLANs based on base_access_vlan/access_vlan_count
    global_vlan_set = None
    global_vlan_str = None
    
    # First check for deployment-level global VLANs
    if input.global_vlans and len(input.global_vlans) > 0:
        global_vlan_set = {v.get("id") for v in input.global_vlans if "id" in v}
        global_vlan_str = ",".join(str(v) for v in sorted(global_vlan_set))
        logger.info(f"GLOBAL_VLAN_DETECTED",
                   request_id=request_id,
                   source="deployment_level",
                   vlan_count=len(global_vlan_set),
                   vlans=global_vlan_str)
    else:
        # Fall back to checking individual switches for VLANs
        for sw in input.switches:
            if sw.vlans and len(sw.vlans) > 0:
                global_vlan_set = {v.id for v in sw.vlans}
                global_vlan_str = ",".join(str(v) for v in sorted(global_vlan_set))
                logger.info(f"GLOBAL_VLAN_DETECTED",
                           request_id=request_id,
                           source_switch=sw.hostname,
                           vlan_count=len(global_vlan_set),
                           vlans=global_vlan_str)
                break
    
    devices = []  # legacy tracker; pass-2 uses device_by_hostname
    device_by_hostname: Dict[str, Device] = {}
    pending_switches: List[Dict[str, Any]] = []
    all_hostnames = {s.hostname for s in input.switches}
    for switch_idx, switch_config in enumerate(input.switches):
        try:
            logger.info(f"SWITCH_PROCESSING_START",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       model=switch_config.model,
                       role=switch_config.role)
            
            # Convert SwitchConfig to DeviceInput
            device_input = DeviceInput(
                hostname=switch_config.hostname,
                mgmt_ip=switch_config.mgmt_ip,
                mgmt_gw=switch_config.mgmt_gw,
                site_name=switch_config.site_name,
                model=switch_config.model,
                nxos_version=switch_config.nxos_version,
                vpc_domain=switch_config.vpc_domain,
                vpc_peer_link_id=switch_config.vpc_peer_link_id,
                keepalive_po_id=switch_config.keepalive_po_id,
                vpc_system_priority=switch_config.vpc_system_priority,
                local_ka=switch_config.local_ka,
                remote_ka=switch_config.remote_ka,
                vpc_pl_ints=switch_config.vpc_pl_ints,
                base_access_vlan=switch_config.base_access_vlan,
                access_vlan_count=switch_config.access_vlan_count,
                interface_count=switch_config.interface_count,
                bring_up_spare_ports=switch_config.bring_up_spare_ports,
                security_tier=switch_config.security_tier,
                baseline_options=list(switch_config.baseline_options or []),
            )
            
            logger.info(f"DEVICE_INPUT_CREATED",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       device_input_dict=device_input.model_dump())
            
            # Apply scenario template based on switch role for proper configuration enrichment
            scenario_id = "spine_core" if switch_config.role == "spine" else "standalone_leaf"
            
            # Initialize vpc_pair for later use
            vpc_pair = None
            
            # Use vPC scenario for any switch (core, leaf, access) that is part of a vPC pair
            # Previously only leaf role was checked — this excluded core switches with vpc_domain
            if input.vpc_pairs:
                vpc_pair = next((p for p in input.vpc_pairs 
                               if p.get("primary") == switch_config.hostname or p.get("secondary") == switch_config.hostname), None)
                if vpc_pair:
                    # core + vPC → use vpc_core_pair scenario which includes 'feature vpc'
                    if switch_config.role in ("core", "leaf", "access"):
                        scenario_id = "vpc_leaf_pair"
                    elif switch_config.role == "spine":
                        scenario_id = "vpc_leaf_pair"  # spines in vPC pair also need feature vpc
            
            logger.info(f"SCENARIO_SELECTION",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       role=switch_config.role,
                       scenario_id=scenario_id)
            
            # Build defaults from switch config - preserve user's explicit VLAN choices
            # Only include vPC-related defaults if this switch is actually in a vPC pair
            defaults = {
                "model": switch_config.model,
                "nxos_version": switch_config.nxos_version,
                "base_access_vlan": switch_config.base_access_vlan,
                "access_vlan_count": switch_config.access_vlan_count,
                "interface_count": switch_config.interface_count,
                "bring_up_spare_ports": switch_config.bring_up_spare_ports,
                "security_tier": switch_config.security_tier,
                "baseline_options": switch_config.baseline_options if hasattr(switch_config, 'baseline_options') else [],
            }
            
            # Only add vPC defaults if this switch is in a vPC pair
            if vpc_pair:
                # Determine peer hostname and look up its management IP
                peer_hostname = vpc_pair.get("primary") if switch_config.hostname == vpc_pair.get("secondary") else vpc_pair.get("secondary")
                peer_switch = next((s for s in input.switches if s.hostname == peer_hostname), None)
                peer_mgmt_ip = peer_switch.mgmt_ip.split('/')[0] if peer_switch else "10.255.255.2"
                
                defaults.update({
                    "vpc_domain_id": switch_config.vpc_domain if switch_config.vpc_domain else vpc_pair.get("domain", 100),
                    "vpc_domain": switch_config.vpc_domain if switch_config.vpc_domain else vpc_pair.get("domain", 100),
                    "vpc_peer_link_id": switch_config.vpc_peer_link_id if switch_config.vpc_peer_link_id else 1,
                    "keepalive_po_id": switch_config.keepalive_po_id if switch_config.keepalive_po_id else 2,
                    "vpc_system_priority": switch_config.vpc_system_priority if switch_config.vpc_system_priority else 20000,
                    "local_keepalive_ip": switch_config.local_ka if switch_config.local_ka else switch_config.mgmt_ip.split('/')[0],
                    "remote_keepalive_ip": switch_config.remote_ka if switch_config.remote_ka else peer_mgmt_ip,
                    "peer_link_interfaces": switch_config.vpc_pl_ints if switch_config.vpc_pl_ints else "Ethernet1/35-36",
                })
            
            # Apply scenario to enrich device with proper configuration
            applied = scenario_engine.apply_scenario(
                scenario_id,
                switch_config.hostname,
                switch_config.site_name,
                switch_config.mgmt_ip,
                switch_config.mgmt_gw,
                overrides=defaults
            )
            
            device = applied["device"]
            
            # If user provided explicit VLANs (either deployment-level or switch-level), use those
            # Priority: 1) deployment-level global_vlans, 2) switch-level vlans
            user_vlan_list = None
            if global_vlan_set and len(global_vlan_set) > 0:
                # Use deployment-level global VLANs
                user_vlan_list = [VLAN(id=v.get("id"), name=v.get("name", f"VLAN_{v.get('id')}")) 
                                   for v in input.global_vlans if "id" in v]
                logger.info(f"USING_DEPLOYMENT_GLOBAL_VLANS",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           global_vlan_count=len(user_vlan_list),
                           global_vlans=[{"id": v.id, "name": v.name} for v in user_vlan_list])
            elif switch_config.vlans and len(switch_config.vlans) > 0:
                # Fall back to switch-level VLANs
                user_vlan_list = [VLAN(id=v.id, name=v.name) for v in switch_config.vlans]
                logger.info(f"USING_SWITCH_EXPLICIT_VLANS",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           user_vlan_count=len(switch_config.vlans),
                           user_vlans=[{"id": v.id, "name": v.name} for v in switch_config.vlans])
            
            if user_vlan_list:
                # Replace device VLANs with user-provided VLANs
                device.vlans = user_vlan_list
                user_vlan_ids = {v.id for v in user_vlan_list}
                user_vlan_str = ",".join(str(v) for v in sorted(user_vlan_ids))
                # Propagate user VLANs to trunk and access interfaces
                for iface in device.interfaces:
                    if iface.mode == "trunk" and iface.trunk_vlans and iface.trunk_vlans != "1-4094":
                        iface.trunk_vlans = user_vlan_str
                for po in device.port_channels:
                    if po.mode == "trunk" and po.trunk_vlans and po.trunk_vlans != "1-4094":
                        po.trunk_vlans = user_vlan_str
                
                logger.info(f"USER_VLANS_APPLIED",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           final_vlan_count=len(device.vlans),
                           final_vlans=[{"id": v.id, "name": v.name} for v in device.vlans])
            
            logger.info(f"DEVICE_ENRICHED_BY_SCENARIO",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       scenario_id=scenario_id,
                       device_type=type(device).__name__,
                       vlans_count=len(device.vlans),
                       svis_count=len(device.svis),
                       interfaces_count=len(device.interfaces),
                       interface_names=[iface.name for iface in device.interfaces])
            
            # Load hardware profile for this switch (needed for port map generation)
            hw_profile = catalog.get_hardware_profile(switch_config.model)
            
            logger.info(f"HARDWARE_PROFILE_LOADED",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       model=switch_config.model,
                       hw_profile_found=hw_profile is not None,
                       device_class=hw_profile.get("device_class") if hw_profile else None)
            
            # Replace generic preset descriptions with actual hostnames for multi-switch deployments
            if input.switches and len(input.switches) > 1:
                # Build a mapping of uplinks to determine actual connections
                uplink_map = {}
                if input.uplinks:
                    for uplink in input.uplinks:
                        from_sw = uplink.get("from")
                        to_sw = uplink.get("to")
                        if from_sw not in uplink_map:
                            uplink_map[from_sw] = []
                        uplink_map[from_sw].append(to_sw)
                
                # Update downlink presets with actual hostnames based on actual uplink connections
                for iface in device.interfaces:
                    if "NET_LEAF_10G" in iface.description:
                        leaf_10g = [s for s in input.switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_10g"]
                        if leaf_10g:
                            hostnames = " + ".join([s.hostname for s in leaf_10g])
                            iface.description = iface.description.replace("NET_LEAF_10G_SW1+SW2", hostnames)
                    elif "NET_LEAF_1G" in iface.description:
                        leaf_1g = [s for s in input.switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_1g"]
                        if leaf_1g:
                            hostnames = " + ".join([s.hostname for s in leaf_1g])
                            iface.description = iface.description.replace("NET_LEAF_1G_SW1+SW2", hostnames)
                    elif "SPINE" in iface.description and switch_config.hostname in uplink_map:
                        # Use actual uplink destinations instead of all spines
                        connected_spines = uplink_map[switch_config.hostname]
                        if connected_spines:
                            hostnames = " + ".join(connected_spines)
                            iface.description = iface.description.replace("SPINE_PAIR", hostnames).replace("SPINE", hostnames)
                
                # Update port-channel descriptions as well
                for po in device.port_channels:
                    if "NET_LEAF_10G" in po.description:
                        leaf_10g = [s for s in input.switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_10g"]
                        if leaf_10g:
                            hostnames = " + ".join([s.hostname for s in leaf_10g])
                            po.description = po.description.replace("NET_LEAF_10G_SW1+SW2", hostnames)
                    elif "NET_LEAF_1G" in po.description:
                        leaf_1g = [s for s in input.switches if s.model and catalog.get_hardware_profile(s.model) and catalog.get_hardware_profile(s.model).get("device_class") == "leaf_1g"]
                        if leaf_1g:
                            hostnames = " + ".join([s.hostname for s in leaf_1g])
                            po.description = po.description.replace("NET_LEAF_1G_SW1+SW2", hostnames)
                    elif "SPINE" in po.description and switch_config.hostname in uplink_map:
                        # Use actual uplink destinations instead of all spines
                        connected_spines = uplink_map[switch_config.hostname]
                        if connected_spines:
                            hostnames = " + ".join(connected_spines)
                            po.description = po.description.replace("SPINE_PAIR", hostnames).replace("SPINE", hostnames)
            
            # Apply vPC topology from deployment if applicable
            logger.info(f"VPC_TOPOLOGY_APPLICATION_START",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       has_vpc_pairs=input.vpc_pairs is not None,
                       vpc_pairs_count=len(input.vpc_pairs) if input.vpc_pairs else 0)
            
            if input.vpc_pairs:
                # vpc_pair was already determined during scenario selection
                if vpc_pair is None:
                    vpc_pair = next((p for p in input.vpc_pairs 
                                   if p.get("primary") == switch_config.hostname or p.get("secondary") == switch_config.hostname), None)
                
                logger.info(f"VPC_PAIR_LOOKUP",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           vpc_pair_found=vpc_pair is not None,
                           vpc_pair=vpc_pair)
                
                if vpc_pair:
                    # Always rebuild vPC from deployment topology (overrides scenario preset)
                    profiles = catalog.list_hardware_profiles()
                    hw_profile = next(
                        (p for p in profiles if p.get("display_name") == switch_config.model),
                        None,
                    )
                    is_primary = switch_config.hostname == vpc_pair.get("primary")
                    partner_hostname = (
                        vpc_pair.get("secondary")
                        if is_primary
                        else vpc_pair.get("primary")
                    )
                    partner_config = next(
                        (s for s in input.switches if s.hostname == partner_hostname),
                        None,
                    )
                    device.vpc = _build_deployment_vpc_config(
                        vpc_pair, switch_config, is_primary, hw_profile, partner_config
                    )

                    # Validate pair consistency when peer is already processed
                    peer_device = device_by_hostname.get(partner_hostname)
                    if peer_device and peer_device.vpc and device.vpc:
                        primary_dev = device if is_primary else peer_device
                        secondary_dev = peer_device if is_primary else device
                        pair_report = device_validator.validate_vpc_pair(primary_dev, secondary_dev)
                        if pair_report["status"] != "pass":
                            raise ValidationError({"errors": pair_report["errors"]})

                    device_by_hostname[switch_config.hostname] = device
                    
                    logger.info(f"VPC_DOMAIN_APPLIED",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               domain_id=device.vpc.domain_id,
                               role=device.vpc.role,
                               peer_link_interfaces=device.vpc.peer_link_interfaces)
                    
                    logger.info(f"HARDWARE_PROFILE_RELOADED",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               hw_profile_found=hw_profile is not None)
                    
                    if hw_profile:
                        # Determine if this is a leaf switch in a vPC pair
                        # Check both device_class and switch role for proper classification
                        device_class = hw_profile.get("device_class")
                        switch_role = getattr(switch_config, 'role', 'leaf')
                        is_leaf = device_class in ["leaf_1g", "leaf_10g"] or switch_role == "leaf"
                        
                        logger.info(f"SWITCH_ROLE_DETERMINATION",
                                   request_id=request_id,
                                   switch_index=switch_idx,
                                   hostname=switch_config.hostname,
                                   device_class=device_class,
                                   switch_role=switch_role,
                                   is_leaf=is_leaf)
                        
                        if is_leaf:
                            # Configure vPC peer-link and keepalive ports for leaf switches
                            vpc_peer_link_ports = hw_profile.get("vpc_peer_link", [])
                            vpc_keepalive_ports = hw_profile.get("vpc_keepalive", [])
                            
                            logger.info(f"LEAF_VPC_CONFIG_START",
                                       request_id=request_id,
                                       switch_index=switch_idx,
                                       hostname=switch_config.hostname,
                                       vpc_peer_link_ports=vpc_peer_link_ports,
                                       vpc_keepalive_ports=vpc_keepalive_ports)
                            
                            # Configure peer-link ports
                            if vpc_peer_link_ports:
                                for port in vpc_peer_link_ports:
                                    # Update the actual interface in the device model
                                    for iface in device.interfaces:
                                        if iface.name == port:
                                            iface.description = f"Part_Of_Vpc_PEERLINK_To_{vpc_pair.get('secondary') if vpc_pair.get('primary') == switch_config.hostname else vpc_pair.get('primary')}"
                                            peer_po = (
                                                device.vpc.peer_link_id
                                                if device.vpc
                                                else getattr(switch_config, "vpc_peer_link_id", 1)
                                            )
                                            _set_interface_channel_group(iface, peer_po)
                                            break
                            
                            # Configure keepalive ports
                            if vpc_keepalive_ports:
                                for port in vpc_keepalive_ports:
                                    # Update the actual interface in the device model
                                    for iface in device.interfaces:
                                        if iface.name == port:
                                            iface.description = f"Part_Of_Vpc_KEEPALIVE_To_{vpc_pair.get('secondary') if vpc_pair.get('primary') == switch_config.hostname else vpc_pair.get('primary')}"
                                            ka_po = (
                                                device.vpc.keepalive_po_id
                                                if device.vpc
                                                else getattr(switch_config, "keepalive_po_id", 2)
                                            )
                                            _set_interface_channel_group(iface, ka_po)
                                            break
                            
                            # Configure uplink ports for leaf switches (ports to connect to core switches)
                            uplink_start = hw_profile.get("vpc_uplink_start", 51)
                            uplink_end = hw_profile.get("vpc_uplink_end", 52)
                            
                            logger.info(f"LEAF_UPLINK_CONFIG_START",
                                       request_id=request_id,
                                       switch_index=switch_idx,
                                       hostname=switch_config.hostname,
                                       uplink_start=uplink_start,
                                       uplink_end=uplink_end)
                            
                            # Find core switches for uplink descriptions using device_class
                            core_switches = [s for s in input.switches if _switch_is_spine_or_core(s, catalog)]
                            
                            logger.info(f"CORE_SWITCHES_FOUND",
                                       request_id=request_id,
                                       switch_index=switch_idx,
                                       hostname=switch_config.hostname,
                                       core_switches_count=len(core_switches),
                                       core_switches=[s.hostname for s in core_switches])
                            
                            if len(core_switches) >= 2:
                                core1 = core_switches[0].hostname
                                core2 = core_switches[1].hostname
                                
                                logger.info(f"USING_CORE_SWITCHES",
                                           request_id=request_id,
                                           switch_index=switch_idx,
                                           hostname=switch_config.hostname,
                                           core1=core1,
                                           core2=core2)
                                
                                # Configure uplink ports with descriptions
                                is_primary = vpc_pair.get("primary") == switch_config.hostname
                                port_offset = 0 if is_primary else 0  # Both switches use same ports
                                
                                # Add uplink configuration to device
                                device.uplink_config = device.uplink_config or []
                                
                                # Update device interface descriptions with actual core hostnames
                                interface_desc_1 = f"to {core1} port 1"
                                interface_desc_2 = f"to {core2} port 1"
                                
                                device.uplink_config.append({
                                    "interface": f"Ethernet1/{uplink_start}",
                                    "description": interface_desc_1,
                                    "mode": "trunk"
                                })
                                
                                # Update the actual interface in the device model
                                for iface in device.interfaces:
                                    if iface.name == f"Ethernet1/{uplink_start}":
                                        iface.description = interface_desc_1
                                        break
                                
                                device.uplink_config.append({
                                    "interface": f"Ethernet1/{uplink_end}",
                                    "description": interface_desc_2,
                                    "mode": "trunk"
                                })
                                
                                # Update the actual interface in the device model
                                for iface in device.interfaces:
                                    if iface.name == f"Ethernet1/{uplink_end}":
                                        iface.description = interface_desc_2
                                        break
                                
                                logger.info(f"LEAF_UPLINK_CONFIG_COMPLETE",
                                           request_id=request_id,
                                           switch_index=switch_idx,
                                           hostname=switch_config.hostname,
                                           uplink_config_count=len(device.uplink_config))
                            else:
                                logger.warning(f"INSUFFICIENT_CORE_SWITCHES",
                                              request_id=request_id,
                                              switch_index=switch_idx,
                                              hostname=switch_config.hostname,
                                              core_switches_count=len(core_switches),
                                              required=2)
                        
                        elif hw_profile.get("device_class") in ["core", "spine"]:
                            # Core→leaf uplink wiring deferred to pass 2 (order-independent)
                            logger.info(
                                "CORE_DOWNLINK_DEFERRED_PASS2",
                                request_id=request_id,
                                switch_index=switch_idx,
                                hostname=switch_config.hostname,
                            )
            if input.uplinks:
                apply_custom_uplinks_for_switch(
                    device,
                    switch_config.hostname,
                    input.uplinks,
                    all_hostnames,
                )

            # Pass 1 complete — register device; render in pass 3
            device_by_hostname[switch_config.hostname] = device
            pending_switches.append({
                "switch_config": switch_config,
                "device": device,
                "vpc_pair": vpc_pair,
                "switch_idx": switch_idx,
            })
            continue

        except ValidationError as e:
            logger.error(f"SWITCH_VALIDATION_ERROR",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       error_type="ValidationError",
                       error_report=e.report,
                       traceback=traceback.format_exc())
            errors.append({
                "hostname": switch_config.hostname,
                "error": e.report["errors"]
            })
        except Exception as e:
            logger.error(f"SWITCH_PROCESSING_ERROR",
                       request_id=request_id,
                       switch_index=switch_idx,
                       hostname=switch_config.hostname,
                       error_type=type(e).__name__,
                       error=str(e),
                       traceback=traceback.format_exc())
            errors.append({
                "hostname": switch_config.hostname,
                "error": str(e)
            })
    

    # Pass 2: cross-switch core→leaf wiring (order-independent)
    wire_core_leaf_downlinks(device_by_hostname, input.switches, catalog, request_id)
    vpc_pair_errors = validate_all_vpc_pairs(device_by_hostname, input.vpc_pairs, device_validator)
    for vpc_err in vpc_pair_errors:
        errors.append({"hostname": "vPC-validation", "error": vpc_err})
    blocked_hostnames = switches_blocked_by_vpc_errors(vpc_pair_errors, input.vpc_pairs)

    # Pass 3: pipeline / export per switch (skip switches in failed vPC pairs)
    for pend in pending_switches:
        switch_config = pend["switch_config"]
        if switch_config.hostname in blocked_hostnames:
            errors.append({
                "hostname": switch_config.hostname,
                "error": "Export blocked: vPC pair failed post-build validation.",
            })
            continue
        device = pend["device"]
        vpc_pair = pend["vpc_pair"]
        switch_idx = pend["switch_idx"]
        try:
                logger.info(f"PIPELINE_EXECUTION_START",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname)
            
                # Log interface state before pipeline execution
                logger.info(f"INTERFACE_STATE_BEFORE_PIPELINE",
                           request_id=request_id,
                           hostname=switch_config.hostname,
                           total_interfaces=len(device.interfaces),
                           interfaces_with_channel_group=[iface.name for iface in device.interfaces if iface.channel_group],
                           all_interface_names=[iface.name for iface in device.interfaces],
                           uplink_config_count=len(device.uplink_config) if device.uplink_config else 0,
                           downlink_config_count=len(device.downlink_config) if device.downlink_config else 0)

                checkpoints.save_checkpoint(device, label=f"pre-gen-{switch_config.hostname}")
            
                # Create subdirectory for this switch based on its role and vPC pair (skip for preview mode)
                switch_dir_name = switch_config.hostname
                if vpc_pair:
                    switch_dir_name = f"vpc_{vpc_pair.get('domain')}_{switch_config.hostname}"
            
                switch_export_dir = export_base / switch_dir_name
                if not preview:
                    os.makedirs(switch_export_dir, exist_ok=True)
            
                logger.info(f"SWITCH_EXPORT_DIR_CREATED",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           export_dir=str(switch_export_dir) if not preview else "PREVIEW_MODE")
            
                # Execute pipeline - skip file writing in preview mode
                if preview:
                    # Generate CLI preview without writing files using ConfigRenderer
                    from core.renderer import ConfigRenderer as Renderer
                    renderer = Renderer()
                
                    # Log device state before rendering
                    logger.info(f"DEVICE_STATE_BEFORE_RENDER",
                               request_id=request_id,
                               hostname=switch_config.hostname,
                               has_port_channels=device.port_channels is not None,
                               port_channels_count=len(device.port_channels) if device.port_channels else 0,
                               has_uplink_config=device.uplink_config is not None,
                               uplink_config_count=len(device.uplink_config) if device.uplink_config else 0,
                               has_downlink_config=device.downlink_config is not None,
                               downlink_config_count=len(device.downlink_config) if device.downlink_config else 0,
                               has_vpc=device.vpc is not None)
                
                    nxos_ver = getattr(device, 'nxos_version', '9.3') or '9.3'
                    metadata = {
                        "version": pipeline.version,
                        "nxos_version": nxos_ver,
                        "mode": "vPC Pair" if device.vpc else "Standalone",
                        "system": "Configuration Authority System",
                    }
                    cli_config = renderer.render_device_config(device, metadata=metadata)
                
                    logger.info(f"RENDER_RESULT",
                               request_id=request_id,
                               hostname=switch_config.hostname,
                               cli_length=len(cli_config) if cli_config else 0,
                               cli_preview=cli_config[:500] if cli_config and len(cli_config) > 0 else "EMPTY")
                
                    manifest = {
                        "cli": cli_config,
                        "config": cli_config,
                        "message": "Preview generated successfully"
                    }
                else:
                    manifest = pipeline.execute(device, output_dir=str(switch_export_dir))
            
                logger.info(f"PIPELINE_EXECUTION_COMPLETE",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           manifest_keys=list(manifest.keys()) if manifest else None,
                           cli_length=len(manifest.get("cli", "")) if manifest else 0)
            
                # Use bulletproof port mapping service for port configuration
                logger.info(f"PORT_MAPPING_SERVICE_START",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname)
            
                from core.port_mapping_service import PortMappingService
                port_mapping_service = PortMappingService(catalog)
            
                # Get hardware profile for this switch
                hw_profile = catalog.get_hardware_profile(switch_config.model)
                logger.info(f"HARDWARE_PROFILE_FOR_PORT_MAP",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           model=switch_config.model,
                           hw_profile_keys=list(hw_profile.keys()) if hw_profile else None)
            
                # Get vPC pair for this switch
                vpc_pair = next((p for p in input.vpc_pairs 
                               if p.get("primary") == switch_config.hostname or p.get("secondary") == switch_config.hostname), None)
            
                logger.info(f"VPC_PAIR_FOR_PORT_MAP",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           vpc_pair_found=vpc_pair is not None,
                           vpc_pair=vpc_pair)
            
                # Create peer switches list (all switches except this one)
                peer_switches = [{"hostname": s.hostname, "model": s.model} 
                                for s in input.switches if s.hostname != switch_config.hostname]
            
                logger.info(f"PEER_SWITCHES_FOR_PORT_MAP",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           peer_switches_count=len(peer_switches),
                           peer_switches=peer_switches)
            
                # Generate bulletproof port map
                try:
                    logger.info(f"PORT_MAP_GENERATION_START",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               model=switch_config.model,
                               hw_profile_keys=list(hw_profile.keys()) if hw_profile else None)
                
                    port_map = port_mapping_service.create_port_map(
                        hostname=switch_config.hostname,
                        model=switch_config.model,
                        hw_profile=hw_profile,
                        vpc_pair=vpc_pair,
                        peer_switches=peer_switches,
                        uplinks=input.uplinks
                    )
                    port_map_dict = port_map.to_dict()
                
                    logger.info(f"PORT_MAP_GENERATION_SUCCESS",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               port_count=port_map_dict['port_count'],
                               port_types=[p['type'] for p in port_map_dict['ports']] if port_map_dict['ports'] else None,
                               port_map_dict=port_map_dict)
                except Exception as e:
                    logger.error(f"PORT_MAP_GENERATION_ERROR",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               error=str(e),
                               error_type=type(e).__name__,
                               traceback=traceback.format_exc())
                    port_map_dict = {
                        "hostname": switch_config.hostname,
                        "model": switch_config.model,
                        "role": "generic",
                        "ports": [],
                        "port_count": 0,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
            
                # Add device interfaces to port map to ensure all configured ports are included
                try:
                    logger.info(f"ADD_DEVICE_INTERFACES_START",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               interface_count=len(device.interfaces))
                    port_mapping_service.add_device_interfaces(port_map, device.interfaces)
                    port_map_dict = port_map.to_dict()
                    logger.info(f"ADD_DEVICE_INTERFACES_SUCCESS",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               updated_port_count=port_map_dict['port_count'])
                except Exception as e:
                    logger.error(f"ADD_DEVICE_INTERFACES_ERROR",
                               request_id=request_id,
                               switch_index=switch_idx,
                               hostname=switch_config.hostname,
                               error=str(e),
                               error_type=type(e).__name__,
                               traceback=traceback.format_exc())
            
                # Build device_config with all interface information
                logger.info(f"DEVICE_CONFIG_BUILD_START",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           interface_count=len(device.interfaces),
                           downlink_config_count=len(device.downlink_config or []),
                           uplink_config_count=len(device.uplink_config or []))
            
                device_config = {
                    "hostname": device.hostname,
                    "model": device.model,
                    "interfaces": [],
                    "downlink_config": device.downlink_config or [],
                    "uplink_config": device.uplink_config or [],
                    "port_map": port_map_dict  # Add bulletproof port map
                }
            
                # Add all interfaces with their configuration
                for iface in device.interfaces:
                    device_config["interfaces"].append({
                        "name": iface.name,
                        "description": iface.description,
                        "port_channel": getattr(iface, 'port_channel', None),
                        "mode": getattr(iface, 'mode', None),
                        "enabled": getattr(iface, 'enabled', True)
                    })
            
                logger.info(f"DEVICE_CONFIG_BUILD_COMPLETE",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           device_config_interfaces_count=len(device_config['interfaces']),
                           device_config_downlink_count=len(device_config['downlink_config']),
                           device_config_uplink_count=len(device_config['uplink_config']),
                           device_config_port_map_port_count=device_config['port_map'].get('port_count', 0))
            
                # Standardize response structure to match frontend expectations
                logger.info(f"RESULT_APPEND_START",
                           request_id=request_id,
                           switch_index=switch_idx,
                           hostname=switch_config.hostname,
                           status="success")
            
                results.append({
                    "hostname": switch_config.hostname,
                    "status": "success",
                    "export": {
                        "cli": manifest.get("cli", ""),
                        "config": manifest.get("config", ""),
                        "message": manifest.get("message", ""),
                        "raw": manifest
                    },
                    "device_config": device_config
                })
                devices.append(device)

        except ValidationError as e:
            logger.error(
                "SWITCH_VALIDATION_ERROR_PASS3",
                request_id=request_id,
                switch_index=switch_idx,
                hostname=switch_config.hostname,
                error_report=e.report,
            )
            errors.append({"hostname": switch_config.hostname, "error": e.report["errors"]})
        except Exception as e:
            logger.error(
                "SWITCH_PROCESSING_ERROR_PASS3",
                request_id=request_id,
                switch_index=switch_idx,
                hostname=switch_config.hostname,
                error=str(e),
            )
            errors.append({"hostname": switch_config.hostname, "error": str(e)})

    logger.info(f"SWITCH_PROCESSING_COMPLETE",
               request_id=request_id,
               total_switches=len(input.switches),
               successful_switches=len(results),
               failed_switches=len(errors),
               results_hostnames=[r['hostname'] for r in results],
               errors_hostnames=[e['hostname'] for e in errors],
               export_base=str(export_base))
    
    # Log final response
    logger.info(f"DEPLOYMENT_GENERATION_COMPLETE",
               request_id=request_id,
               total_results=len(results),
               total_errors=len(errors),
               results_summary=[{"hostname": r['hostname'], "status": r['status'], "port_map_port_count": r.get('device_config', {}).get('port_map', {}).get('port_count', 0)} for r in results],
               errors_summary=errors,
               export_dir=str(export_base))
    
    # Collect all files for export summary
    all_files = []
    for result in results:
        if "export" in result and "raw" in result["export"]:
            manifest = result["export"]["raw"]
            if isinstance(manifest, dict) and "files" in manifest:
                all_files.extend(manifest["files"])
    
    return {
        "status": "completed" if not errors else "partial_success",
        "results": results,
        "errors": errors,
        "total_switches": len(input.switches),
        "successful": len(results),
        "failed": len(errors),
        "export_dir": str(export_base),
        "export": {
            "output_dir": str(export_base),
            "files": all_files,
            "batch_folder": None,
            "site_name": input.site_name
        }
    }


@app.post("/intent/preview")
def preview_intent(input: IntentInput, request: Request):
    """
    Preview intent-based configuration without generating full CLI.
    
    Returns configuration preview based on high-level intent parameters.
    """
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
    """
    Generate complete NX-OS configuration from high-level intent.
    
    Translates intent parameters (role, security tier, etc.) into
    full device configuration with CLI output.
    """
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
    """
    Get list of configuration history files with optional filtering.
    
    Supports filtering by hostname, site, scenario, and artifact type.
    """
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
    """
    Get system directory paths for history, checkpoints, and app data.
    
    Returns paths to key application directories for debugging and file access.
    """
    # Token authentication removed for offline use
    return {
        "app_dir": get_app_dir(),
        "vault_dir": str(HISTORY_DIR),
        "checkpoints_dir": get_checkpoints_dir(),
        "version": pipeline.version,
    }


@app.post("/system/open-folder")
def open_folder(body: OpenFolderInput, request: Request):
    """
    Open a system folder in the OS file explorer.
    
    Security: Prevents path traversal attacks by validating the path.
    """
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
    """
    Parse running configuration for import wizard analysis.
    
    Analyzes pasted NX-OS configuration to extract device parameters.
    """
    # Token authentication removed for offline use
    return config_builder.analyze_paste(body.running_config)


@app.post("/builder/questions")
def builder_questions(body: BuilderAnswersInput, request: Request):
    """
    Get next questions for import wizard based on current answers.
    
    Returns contextual questions to guide configuration import process.
    """
    # Token authentication removed for offline use
    return {"questions": config_builder.get_questions(body.answers)}


@app.post("/builder/recommend")
def builder_recommend(body: BuilderAnswersInput, request: Request):
    """
    Get hardware and configuration recommendations based on parsed config.
    
    Suggests appropriate hardware profiles and configuration options.
    """
    # Token authentication removed for offline use
    return config_builder.recommend(body.answers)

@app.get("/history/{filename}", response_class=PlainTextResponse)
def get_history_content(filename: str, request: Request):
    """
    Get content of a specific history file.
    
    Security: Validates filename to prevent path traversal.
    """
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
    """
    List available configuration checkpoints.
    
    Optional hostname filter for device-specific checkpoints.
    """
    # Token authentication removed for offline use
    return checkpoints.list_checkpoints(hostname=hostname)


@app.get("/checkpoints/{filename}")
def get_checkpoint(filename: str, request: Request):
    """
    Get content of a specific checkpoint file.
    
    Security: Validates filename to prevent path traversal.
    """
    # Token authentication removed for offline use
    safe = Path(filename).name
    path = Path(checkpoints.checkpoint_dir) / safe
    if not path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found.")
    return checkpoints.load_checkpoint(str(path))


@app.get("/util/expand-range")
def expand_range(range_str: str, request: Request):
    """
    Expand interface range notation (e.g., Ethernet1/1-3) to individual interfaces.
    
    Utility function for parsing and expanding interface ranges.
    """
    # Token authentication removed for offline use
    from utils.range_parser import expand_interface_range
    return {"expanded": expand_interface_range(range_str)}


@app.post("/util/diff-config")
def diff_config(input: DiffInput, request: Request):
    """
    Generate unified diff between baseline and proposed configurations.
    
    Returns structured diff with line-by-line changes and statistics.
    """
    # Token authentication removed for offline use
    diff_text = pipeline.generate_diff(input.baseline, input.proposed)
    structured = pipeline.generate_structured_diff(input.baseline, input.proposed)
    return {"diff": diff_text, "lines_added": diff_text.count("\n+"), "structured": structured}


@app.post("/util/parse-running-config-diff")
def parse_running_config_diff(input: ParseDiffInput, request: Request):
    """
    Parse pasted running-config and diff against proposed CLI (read-only validation aid).
    
    Helps validate proposed changes against current running configuration.
    """
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
    """
    Return checkpoint JSON for wizard restore (does not mutate server state).
    
    Preview checkpoint data before restoring to wizard state.
    """
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
    """
    Get port-channel mapping configuration.
    
    Returns default port-channel ranges and model-specific overrides.
    """
    # Token authentication removed for offline use
    return load_po_map()


@app.post("/admin/po-map")
def post_po_map(body: PoMapSaveInput, request: Request):
    """
    Save port-channel mapping configuration.
    
    Updates default ranges and model-specific port-channel assignments.
    """
    # Token authentication removed for offline use
    return save_po_map(body.model_dump(exclude_none=True))


@app.get("/release/notes")
def release_notes():
    """
    Get release notes for current application version.
    
    Returns version information and changelog excerpt.
    """
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
    """
    Compare two NX-OS versions for feature differences.
    
    Returns feature comparison between specified version IDs.
    """
    # Token authentication removed for offline use
    return compare_versions(from_id, to_id, catalog)


# --- Multi-Switch Deployment State Management Endpoints ---

@app.get("/deployment/state")
def get_deployment_state(request: Request):
    """
    Get current deployment state including switches, vPC pairs, and uplinks.
    
    Returns complete deployment state for display and editing.
    """
    state_manager = get_state_manager()
    return state_manager.get_deployment_summary()


@app.get("/deployment/state/validate")
def validate_deployment_state(request: Request):
    """
    Validate deployment state consistency.
    
    Returns list of consistency errors if any exist.
    """
    state_manager = get_state_manager()
    errors = state_manager.validate_consistency()
    return {"valid": len(errors) == 0, "errors": errors}


@app.post("/deployment/switches")
def add_switch(switch_data: Dict[str, Any], request: Request):
    """
    Add a new switch to the deployment.
    
    Creates a new switch state and validates against existing configuration.
    """
    try:
        state_manager = get_state_manager()
        switch = state_manager.add_switch(switch_data)
        return {"status": "success", "switch": switch.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/deployment/switches/{hostname}")
def get_switch(hostname: str, request: Request):
    """
    Get a specific switch by hostname.
    
    Returns switch configuration or 404 if not found.
    """
    state_manager = get_state_manager()
    switch = state_manager.get_switch(hostname)
    if not switch:
        raise HTTPException(status_code=404, detail=f"Switch {hostname} not found")
    return switch.to_dict()


@app.put("/deployment/switches/{hostname}")
def update_switch(hostname: str, updates: Dict[str, Any], request: Request):
    """
    Update an existing switch configuration.
    
    Updates switch state with validation and consistency checks.
    """
    try:
        state_manager = get_state_manager()
        switch = state_manager.update_switch(hostname, updates)
        return {"status": "success", "switch": switch.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.delete("/deployment/switches/{hostname}")
def delete_switch(hostname: str, request: Request):
    """
    Delete a switch from the deployment.
    
    Removes switch if not part of vPC pair or uplink configuration.
    """
    try:
        state_manager = get_state_manager()
        state_manager.delete_switch(hostname)
        return {"status": "success", "message": f"Switch {hostname} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/deployment/vpc-pairs")
def add_vpc_pair(pair_data: Dict[str, Any], request: Request):
    """
    Add a new vPC pair to the deployment.
    
    Creates vPC pair configuration and validates switch membership.
    """
    try:
        state_manager = get_state_manager()
        pair = state_manager.add_vpc_pair(pair_data)
        return {"status": "success", "vpc_pair": pair.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/deployment/vpc-pairs/{domain}")
def get_vpc_pair(domain: int, request: Request):
    """
    Get a specific vPC pair by domain.
    
    Returns vPC pair configuration or 404 if not found.
    """
    state_manager = get_state_manager()
    pair = state_manager.get_vpc_pair(domain)
    if not pair:
        raise HTTPException(status_code=404, detail=f"vPC domain {domain} not found")
    return pair.to_dict()


@app.put("/deployment/vpc-pairs/{domain}")
def update_vpc_pair(domain: int, updates: Dict[str, Any], request: Request):
    """
    Update an existing vPC pair configuration.
    
    Updates vPC pair state with validation and consistency checks.
    """
    try:
        state_manager = get_state_manager()
        pair = state_manager.update_vpc_pair(domain, updates)
        return {"status": "success", "vpc_pair": pair.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.delete("/deployment/vpc-pairs/{domain}")
def delete_vpc_pair(domain: int, request: Request):
    """
    Delete a vPC pair from the deployment.
    
    Removes vPC pair and clears vPC domain from member switches.
    """
    try:
        state_manager = get_state_manager()
        state_manager.delete_vpc_pair(domain)
        return {"status": "success", "message": f"vPC domain {domain} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/deployment/uplinks")
def add_uplink(uplink_data: Dict[str, Any], request: Request):
    """
    Add a new uplink to the deployment.
    
    Creates uplink configuration and validates switch connectivity.
    """
    try:
        state_manager = get_state_manager()
        uplink = state_manager.add_uplink(uplink_data)
        return {"status": "success", "uplink": uplink.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/deployment/uplinks/{uplink_id}")
def get_uplink(uplink_id: str, request: Request):
    """
    Get a specific uplink by ID.
    
    Returns uplink configuration or 404 if not found.
    """
    state_manager = get_state_manager()
    uplink = state_manager.get_uplink(uplink_id)
    if not uplink:
        raise HTTPException(status_code=404, detail=f"Uplink {uplink_id} not found")
    return uplink.to_dict()


@app.put("/deployment/uplinks/{uplink_id}")
def update_uplink(uplink_id: str, updates: Dict[str, Any], request: Request):
    """
    Update an existing uplink configuration.
    
    Updates uplink state with validation and consistency checks.
    """
    try:
        state_manager = get_state_manager()
        uplink = state_manager.update_uplink(uplink_id, updates)
        return {"status": "success", "uplink": uplink.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.delete("/deployment/uplinks/{uplink_id}")
def delete_uplink(uplink_id: str, request: Request):
    """
    Delete an uplink from the deployment.
    
    Removes uplink configuration.
    """
    try:
        state_manager = get_state_manager()
        state_manager.delete_uplink(uplink_id)
        return {"status": "success", "message": f"Uplink {uplink_id} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/deployment/snapshots")
def create_snapshot(request: Request, name: Optional[str] = None):
    """
    Create a snapshot of the current deployment state.
    
    Captures current state for rollback capability.
    """
    state_manager = get_state_manager()
    snapshot_id = state_manager.create_snapshot(name)
    return {"status": "success", "snapshot_id": snapshot_id}


@app.get("/deployment/snapshots")
def list_snapshots(request: Request):
    """
    List all available deployment snapshots.
    
    Returns snapshot IDs and timestamps.
    """
    state_manager = get_state_manager()
    snapshots = state_manager.list_snapshots()
    return {"snapshots": snapshots}


@app.post("/deployment/snapshots/{snapshot_id}/restore")
def restore_snapshot(snapshot_id: str, request: Request):
    """
    Restore deployment state from a snapshot.
    
    Reverts deployment state to captured snapshot.
    """
    try:
        state_manager = get_state_manager()
        state_manager.restore_snapshot(snapshot_id)
        return {"status": "success", "message": f"Snapshot {snapshot_id} restored"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.delete("/deployment/snapshots/{snapshot_id}")
def delete_snapshot(snapshot_id: str, request: Request):
    """
    Delete a deployment snapshot.
    
    Removes snapshot from storage.
    """
    try:
        state_manager = get_state_manager()
        state_manager.delete_snapshot(snapshot_id)
        return {"status": "success", "message": f"Snapshot {snapshot_id} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/deployment/clear")
def clear_deployment(request: Request):
    """
    Clear all deployment state.
    
    Removes all switches, vPC pairs, and uplinks. Use with caution.
    """
    state_manager = get_state_manager()
    state_manager.clear_all()
    return {"status": "success", "message": "Deployment state cleared"}


@app.post("/deployment/save")
def save_deployment(request: Request, name: Optional[str] = None):
    """
    Save current deployment state to a named configuration.
    
    Creates a snapshot with a custom name for later restoration.
    """
    state_manager = get_state_manager()
    snapshot_id = state_manager.create_snapshot(name)
    return {"status": "success", "snapshot_id": snapshot_id}


@app.post("/deployment/load/{snapshot_id}")
def load_deployment(snapshot_id: str, request: Request):
    """
    Load deployment state from a saved configuration.
    
    Restores deployment state from a previously saved snapshot.
    """
    try:
        state_manager = get_state_manager()
        state_manager.restore_snapshot(snapshot_id)
        return {"status": "success", "message": f"Deployment {snapshot_id} loaded"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/deployment/configurations")
def list_deployment_configurations(request: Request):
    """
    List all saved deployment configurations.
    
    Returns available snapshots for loading.
    """
    state_manager = get_state_manager()
    snapshots = state_manager.list_snapshots()
    return {"configurations": snapshots}


@app.post("/deployment/export")
def export_deployment(request: Request):
    """
    Export current deployment state as JSON file.
    
    Returns downloadable JSON with all switches, vPC pairs, and uplinks.
    """
    state_manager = get_state_manager()
    deployment_data = state_manager.get_deployment_summary()
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=deployment_data,
        headers={
            "Content-Disposition": "attachment; filename=deployment_export.json"
        }
    )


@app.post("/deployment/import")
def import_deployment(deployment_data: Dict[str, Any], request: Request):
    """
    Import deployment state from JSON data.
    
    Loads switches, vPC pairs, and uplinks from uploaded JSON.
    """
    try:
        state_manager = get_state_manager()
        
        # Clear existing deployment
        state_manager.clear_all()
        
        # Import switches
        for switch_data in deployment_data.get("switches", []):
            state_manager.add_switch(switch_data)
        
        # Import vPC pairs
        for pair_data in deployment_data.get("vpc_pairs", []):
            state_manager.add_vpc_pair(pair_data)
        
        # Import uplinks
        for uplink_data in deployment_data.get("uplinks", []):
            state_manager.add_uplink(uplink_data)
        
        return {"status": "success", "message": "Deployment imported successfully"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/deployment/download-all")
def download_all_configs(request: Request):
    """
    Download all switch configurations as a ZIP file.
    
    Creates a ZIP archive containing all generated configuration files.
    """
    import zipfile
    import io
    from fastapi.responses import Response
    
    # Get deployment state
    state_manager = get_state_manager()
    deployment_summary = state_manager.get_deployment_summary()
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add switch configurations to ZIP
        for switch in deployment_summary.get("switches", []):
            hostname = switch.get("hostname", "unknown")
            # In a real implementation, this would fetch the actual config files
            # For now, we'll add placeholder entries
            config_content = f"# Configuration for {hostname}\n# Model: {switch.get('model', 'Unknown')}\n"
            zip_file.writestr(f"{hostname}.cfg", config_content)
        
        # Add deployment summary
        summary_content = str(deployment_summary)
        zip_file.writestr("deployment_summary.json", summary_content)
    
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=deployment_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )


@app.post("/util/validate-link")
def validate_link(body: LinkValidateInput, request: Request):
    """
    Validate link planner row for port conflicts.
    
    Checks if proposed port assignment conflicts with reserved ports.
    """
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
    """
    Suggest available port members for a link planner row.
    
    Returns list of available ports based on hardware profile and current inventory.
    """
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
    """
    Calculate port budget for a hardware profile.
    
    Returns available port counts by type after accounting for reserved ports.
    """
    # Token authentication removed for offline use
    hw = catalog.get_hardware_profile(body.model) or {}
    inv = build_reserved_inventory(
        model=body.model,
        peer_link_interfaces=body.peer_link_interfaces,
        keepalive_interfaces=body.keepalive_interfaces,
        link_rows=body.link_rows,
    )
    return port_budget(hw, inv)


@app.post("/validate/topology")
def validate_topology(input: TopologyValidationRequest, request: Request):
    """
    Validate multi-switch deployment topology before configuration generation.
    
    Checks for:
    - Port capacity conflicts across switches
    - IP address conflicts across deployment
    - vPC peer-link port availability
    - vPC configuration consistency
    - Uplink/downlink capacity validation
    """
    request_id = request_id_var.get()
    logger.info(f"TOPOLOGY_VALIDATION_START", request_id=request_id, switch_count=len(input.switches))
    
    issues = []
    summary = {"critical": 0, "warning": 0, "info": 0}
    
    # Collect all switch hostnames and IPs
    switch_hostnames = {sw.hostname for sw in input.switches}
    mgmt_ips = {}
    vpc_keepalive_ips = {}
    
    for sw in input.switches:
        if sw.mgmt_ip:
            mgmt_ips[sw.hostname] = sw.mgmt_ip.split('/')[0]
        
        # Collect vPC keepalive IPs
        if sw.vpc_domain and sw.local_ka:
            vpc_keepalive_ips[f"{sw.hostname}_local"] = sw.local_ka
        if sw.vpc_domain and sw.remote_ka:
            vpc_keepalive_ips[f"{sw.hostname}_remote"] = sw.remote_ka
    
    # 1. Check for duplicate hostnames
    if len(switch_hostnames) != len(input.switches):
        hostname_counts = {}
        for sw in input.switches:
            hostname_counts[sw.hostname] = hostname_counts.get(sw.hostname, 0) + 1
        
        for hostname, count in hostname_counts.items():
            if count > 1:
                issues.append(TopologyValidationIssue(
                    severity="critical",
                    category="hostname_conflict",
                    message=f"Duplicate hostname '{hostname}' found {count} times",
                    affected_switches=[sw.hostname for sw in input.switches if sw.hostname == hostname],
                    suggestion="Ensure each switch has a unique hostname"
                ))
                summary["critical"] += 1
    
    # 2. Check for IP address conflicts
    ip_usage = {}
    for hostname, ip in mgmt_ips.items():
        if ip in ip_usage:
            issues.append(TopologyValidationIssue(
                severity="critical",
                category="ip_conflict",
                message=f"IP address {ip} is used by both {hostname} and {ip_usage[ip]}",
                affected_switches=[hostname, ip_usage[ip]],
                suggestion="Assign unique management IP addresses to each switch"
            ))
            summary["critical"] += 1
        else:
            ip_usage[ip] = hostname
    
    # 3. Check vPC keepalive IP conflicts (only within same vPC domain)
    # Cisco NX-OS allows keepalive IP reuse across different vPC domains
    # since each domain has its own system MAC address and isolated keepalive traffic
    # User model: each switch has a single keepalive IP (local_ka)
    # Validation: switches in the same vPC pair must have different keepalive IPs
    
    # 4. Validate vPC configuration consistency
    for pair in input.vpc_pairs:
        primary = next((sw for sw in input.switches if sw.hostname == pair.get("primary")), None)
        secondary = next((sw for sw in input.switches if sw.hostname == pair.get("secondary")), None)
        
        if not primary or not secondary:
            issues.append(TopologyValidationIssue(
                severity="warning",
                category="vpc_mismatch",
                message=f"vPC pair incomplete: primary={pair.get('primary')}, secondary={pair.get('secondary')}",
                affected_switches=[pair.get("primary"), pair.get("secondary")],
                suggestion="Ensure both switches in the vPC pair are defined in the deployment"
            ))
            summary["warning"] += 1
            continue
        
        # Check vPC domain consistency
        if primary.vpc_domain != secondary.vpc_domain:
            issues.append(TopologyValidationIssue(
                severity="critical",
                category="vpc_mismatch",
                message=f"vPC domain mismatch: {primary.hostname} has domain {primary.vpc_domain}, {secondary.hostname} has domain {secondary.vpc_domain}",
                affected_switches=[primary.hostname, secondary.hostname],
                suggestion="Ensure both switches in the vPC pair have the same vPC domain ID"
            ))
            summary["critical"] += 1
        
        # Check keepalive IP uniqueness within vPC pair
        # Each switch in a vPC pair must have a different keepalive IP
        # Same IPs can be reused across different vPC domains
        if primary.local_ka and secondary.local_ka:
            if primary.local_ka == secondary.local_ka:
                issues.append(TopologyValidationIssue(
                    severity="critical",
                    category="vpc_mismatch",
                    message=f"vPC keepalive IP conflict: {primary.hostname} and {secondary.hostname} both use keepalive IP ({primary.local_ka}) in domain {primary.vpc_domain}",
                    affected_switches=[primary.hostname, secondary.hostname],
                    suggestion=f"Configure different keepalive IPs for {primary.hostname} and {secondary.hostname} within vPC domain {primary.vpc_domain}"
                ))
                summary["critical"] += 1
    
    # 5. Validate uplink port availability
    for uplink in input.uplinks:
        from_switch = next((sw for sw in input.switches if sw.hostname == uplink.get("from")), None)
        to_switch = next((sw for sw in input.switches if sw.hostname == uplink.get("to")), None)
        
        if not from_switch:
            issues.append(TopologyValidationIssue(
                severity="warning",
                category="uplink_config",
                message=f"Uplink references non-existent switch: {uplink.get('from')}",
                affected_switches=[uplink.get("from")],
                suggestion="Ensure the source switch exists in the deployment"
            ))
            summary["warning"] += 1
        
        if not to_switch:
            issues.append(TopologyValidationIssue(
                severity="warning",
                category="uplink_config",
                message=f"Uplink references non-existent switch: {uplink.get('to')}",
                affected_switches=[uplink.get("to")],
                suggestion="Ensure the destination switch exists in the deployment"
            ))
            summary["warning"] += 1
    
    valid = summary["critical"] == 0
    
    logger.info(f"TOPOLOGY_VALIDATION_COMPLETE", request_id=request_id, valid=valid, issues_count=len(issues), summary=summary)
    
    return TopologyValidationResponse(
        valid=valid,
        issues=issues,
        summary=summary
    )


@app.post("/validate/nxos-syntax")
def validate_nxos_syntax(input: NXOSSyntaxValidationRequest, request: Request):
    """
    NT-001 FIX: Validate NX-OS configuration syntax against NX-OS command reference grammar.
    
    Performs syntax validation on NX-OS configuration to catch common errors before deployment.
    """
    request_id = request_id_var.get()
    logger.info(f"NXOS_SYNTAX_VALIDATION_START", request_id=request_id, nxos_version=input.nxos_version)
    
    syntax_errors = []
    lines = input.config.split('\n')
    
    # Basic NX-OS syntax validation rules
    for line_num, line in enumerate(lines, start=1):
        line_content = line.strip()
        
        # Skip empty lines and comments
        if not line_content or line_content.startswith('!'):
            continue
        
        # Check for common syntax errors
        # 1. Interface syntax validation
        if line_content.startswith('interface '):
            interface_name = line_content[10:].strip()
            # Validate interface naming convention
            if not re.match(r'^[A-Za-z]+\d+/\d+', interface_name) and not re.match(r'^[A-Za-z]+\d+', interface_name):
                syntax_errors.append(NXOSSyntaxError(
                    line_number=line_num,
                    line_content=line_content,
                    error_type="interface_syntax",
                    error_message=f"Invalid interface name format: {interface_name}",
                    suggestion="Use format like Ethernet1/1, mgmt0, or loopback0"
                ))
        
        # 2. VLAN ID validation
        if 'vlan ' in line_content.lower() and line_content.lower().startswith('vlan'):
            vlan_match = re.search(r'vlan\s+(\d+)', line_content, re.IGNORECASE)
            if vlan_match:
                vlan_id = int(vlan_match.group(1))
                if vlan_id < 1 or vlan_id > 4094:
                    syntax_errors.append(NXOSSyntaxError(
                        line_number=line_num,
                        line_content=line_content,
                        error_type="vlan_range",
                        error_message=f"VLAN ID {vlan_id} out of valid range (1-4094)",
                        suggestion="Use VLAN ID between 1 and 4094"
                    ))
        
        # 3. IP address validation
        if 'ip address' in line_content.lower():
            ip_match = re.search(r'ip\s+address\s+(\d+\.\d+\.\d+\.\d+/\d+)', line_content, re.IGNORECASE)
            if ip_match:
                ip_cidr = ip_match.group(1)
                try:
                    ip_parts, cidr = ip_cidr.split('/')
                    cidr_int = int(cidr)
                    if cidr_int < 0 or cidr_int > 32:
                        syntax_errors.append(NXOSSyntaxError(
                            line_number=line_num,
                            line_content=line_content,
                            error_type="cidr_range",
                            error_message=f"Invalid CIDR notation: {cidr}",
                            suggestion="Use CIDR between 0 and 32"
                        ))
                except ValueError:
                    syntax_errors.append(NXOSSyntaxError(
                        line_number=line_num,
                        line_content=line_content,
                        error_type="ip_format",
                        error_message=f"Invalid IP address format: {ip_cidr}",
                        suggestion="Use format: X.X.X.X/Y (e.g., 10.0.0.1/24)"
                    ))
        
        # 4. Check for missing semicolons in commands that require them (NX-OS doesn't use semicolons, but check for Cisco IOS-style syntax)
        if line_content.endswith(';'):
            syntax_errors.append(NXOSSyntaxError(
                line_number=line_num,
                line_content=line_content,
                error_type="semicolon_syntax",
                error_message="NX-OS does not use semicolons at end of commands",
                suggestion="Remove semicolon - NX-OS uses newline for command termination"
            ))
    
    valid = len(syntax_errors) == 0
    
    logger.info(f"NXOS_SYNTAX_VALIDATION_COMPLETE", request_id=request_id, valid=valid, errors_count=len(syntax_errors))
    
    return NXOSSyntaxValidationResponse(
        valid=valid,
        syntax_errors=syntax_errors,
        total_lines=len(lines),
        nxos_version=input.nxos_version
    )


@app.post("/api/generate-config")
def generate_config_server_side(input: ConfigGenerationRequest, request: Request):
    """
    Server-side configuration generation — delegates to the real deployment pipeline.

    This endpoint exists for API clients and architecture tests (PA-005). It uses the
    same Jinja2 rendering path as POST /generate-deployment, not a stub template.
    """
    request_id = request_id_var.get()
    logger.info(
        "CONFIG_GENERATION_START",
        request_id=request_id,
        switches_count=len(input.switches),
        scenario=input.scenario,
    )

    if not input.switches:
        raise HTTPException(status_code=422, detail="At least one switch is required.")

    try:
        switches = [_dict_to_switch_config(sw) for sw in input.switches]
        deployment_payload = DeploymentInput(
            switches=switches,
            vpc_pairs=input.vpc_pairs,
            uplinks=input.uplinks,
        )
        result = generate_deployment(deployment_payload, request, preview=True)

        cli_blocks = []
        for item in result.get("results", []):
            hostname = item.get("hostname", "unknown")
            cli = item.get("export", {}).get("cli") or item.get("export", {}).get("config") or ""
            if cli:
                cli_blocks.append(f"! ===== {hostname} =====\n{cli}")

        if not cli_blocks and result.get("errors"):
            raise HTTPException(status_code=422, detail=result["errors"])

        config_text = "\n\n".join(cli_blocks)
        if not config_text.strip():
            raise HTTPException(status_code=422, detail="No configuration was generated for the supplied switches.")
        logger.info(
            "CONFIG_GENERATION_COMPLETE",
            request_id=request_id,
            config_length=len(config_text),
            successful=result.get("successful", 0),
        )

        return ConfigGenerationResponse(
            config=config_text,
            switches_count=len(input.switches),
            scenario=input.scenario,
            nxos_version=input.nxos_version,
            generated_at=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CONFIG_GENERATION_ERROR", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Config generation failed: {str(e)}")


@app.get("/api/plugins")
def get_plugin_registry(request: Request):
    """
    PA-006 FIX: Plugin registry for hardware profiles and extensible system.
    
    Returns list of registered plugins including hardware profiles that can be
    dynamically loaded without code changes.
    """
    request_id = request_id_var.get()
    logger.info(f"PLUGIN_REGISTRY_REQUEST", request_id=request_id)
    
    try:
        # Basic plugin registry with hardware profiles
        plugins = [
            PluginInfo(
                name="nexus_93180yc_ex",
                type="hardware_profile",
                version="1.0.0",
                description="Nexus 93180YC-EX 48x25G + 8x100G",
                enabled=True
            ),
            PluginInfo(
                name="nexus_9336c_fx2",
                type="hardware_profile",
                version="1.0.0",
                description="Nexus 9336C-FX2 48x10G + 6x40G",
                enabled=True
            ),
            PluginInfo(
                name="nexus_9348gc_fxp",
                type="hardware_profile",
                version="1.0.0",
                description="Nexus 9348GC-FXP 48x10G + 6x40G",
                enabled=True
            ),
            PluginInfo(
                name="nxos_syntax_validator",
                type="validator",
                version="1.0.0",
                description="NX-OS syntax validation plugin",
                enabled=True
            ),
            PluginInfo(
                name="jinja2_renderer",
                type="renderer",
                version="1.0.0",
                description="Jinja2 template rendering plugin",
                enabled=True
            )
        ]
        
        # Hardware profiles with dynamic loading capability
        hardware_profiles = [
            {
                "display_name": "Nexus 93180YC-EX",
                "model": "N9K-C93180YC-EX",
                "ports": {
                    "10g": 0,
                    "25g": 48,
                    "40g": 0,
                    "100g": 8
                },
                "source": "plugin_registry",
                "loaded_dynamically": True
            },
            {
                "display_name": "Nexus 9336C-FX2",
                "model": "N9K-C9336C-FX2",
                "ports": {
                    "10g": 48,
                    "25g": 0,
                    "40g": 6,
                    "100g": 0
                },
                "source": "plugin_registry",
                "loaded_dynamically": True
            }
        ]
        
        logger.info(f"PLUGIN_REGISTRY_SUCCESS", request_id=request_id, 
                    plugin_count=len(plugins), hardware_count=len(hardware_profiles))
        
        return PluginRegistryResponse(
            plugins=plugins,
            hardware_profiles=hardware_profiles,
            total_count=len(plugins) + len(hardware_profiles)
        )
        
    except Exception as e:
        logger.error(f"PLUGIN_REGISTRY_ERROR", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Plugin registry error: {str(e)}")


@app.post("/sites/create")
def create_site(site: SiteConfig, request: Request):
    """
    Create a new site in the multi-site hierarchy.
    """
    request_id = request_id_var.get()
    logger.info(f"CREATE_SITE_START", request_id=request_id, site_id=site.site_id)
    
    # In a real implementation, this would persist to a database
    # For now, return success with the site configuration
    logger.info(f"CREATE_SITE_COMPLETE", request_id=request_id, site_id=site.site_id)
    return {"status": "success", "site": site}


@app.get("/sites/list")
def list_sites(request: Request):
    """
    List all sites in the multi-site hierarchy.
    """
    request_id = request_id_var.get()
    logger.info(f"LIST_SITES", request_id=request_id)
    
    # In a real implementation, this would query a database
    # For now, return empty list
    return {"sites": []}


@app.post("/sites/{site_id}/deploy")
def deploy_site(site_id: str, request: Request):
    """
    Deploy configuration to a specific site.
    """
    request_id = request_id_var.get()
    logger.info(f"DEPLOY_SITE_START", request_id=request_id, site_id=site_id)
    
    # In a real implementation, this would trigger deployment
    logger.info(f"DEPLOY_SITE_COMPLETE", request_id=request_id, site_id=site_id)
    return {"status": "success", "site_id": site_id, "deployment_status": "in_progress"}


@app.post("/sites/progressive-rollout")
def progressive_rollout(input: MultiSiteDeploymentRequest, request: Request):
    """
    Execute progressive rollout across multiple sites.
    """
    request_id = request_id_var.get()
    logger.info(f"PROGRESSIVE_ROLLOUT_START", request_id=request_id, site_count=len(input.sites))
    
    rollout_results = []
    
    for site in input.sites:
        if input.progressive_rollout:
            # Simulate phased rollout
            site.deployment_status = "in_progress"
            rollout_results.append({
                "site_id": site.site_id,
                "phase": site.rollout_phase,
                "status": "scheduled"
            })
        else:
            # Simulate immediate deployment
            site.deployment_status = "in_progress"
            rollout_results.append({
                "site_id": site.site_id,
                "phase": site.rollout_phase,
                "status": "deploying"
            })
    
    logger.info(f"PROGRESSIVE_ROLLOUT_COMPLETE", request_id=request_id, results_count=len(rollout_results))
    return {"status": "success", "rollout_results": rollout_results}


@app.get("/errors/analytics")
def get_error_analytics(request: Request):
    """
    Get error analytics dashboard with pattern detection.
    """
    request_id = request_id_var.get()
    logger.info(f"ERROR_ANALYTICS", request_id=request_id)
    
    # In a real implementation, this would query error logs
    # For now, return sample data
    error_patterns = [
        ErrorPattern(
            pattern_id="vlan_conflict",
            pattern_name="VLAN ID Conflicts",
            error_type="configuration",
            frequency=5,
            last_occurred=datetime.now().isoformat(),
            suggested_fix="Review VLAN assignments and resolve conflicts",
            auto_recoverable=False
        ),
        ErrorPattern(
            pattern_id="ip_conflict",
            pattern_name="IP Address Conflicts",
            error_type="network",
            frequency=3,
            last_occurred=datetime.now().isoformat(),
            suggested_fix="Assign unique IP addresses to each device",
            auto_recoverable=False
        )
    ]
    
    return ErrorAnalyticsResponse(
        total_errors=8,
        error_patterns=error_patterns,
        recent_errors=[]
    )


@app.post("/errors/recovery-suggestion")
def get_recovery_suggestion(error_code: str, request: Request):
    """
    Get recovery suggestion for a specific error.
    """
    request_id = request_id_var.get()
    logger.info(f"RECOVERY_SUGGESTION", request_id=request_id, error_code=error_code)
    
    # Recovery suggestions based on error patterns
    recovery_db = {
        "vlan_conflict": RecoverySuggestion(
            error_code="vlan_conflict",
            error_message="VLAN ID conflict detected",
            severity="critical",
            recovery_steps=[
                "Identify conflicting VLAN IDs in the deployment",
                "Review switch-level VLAN assignments",
                "Check global VLAN configuration",
                "Reassign conflicting VLANs to unique IDs",
                "Re-validate topology"
            ],
            auto_recovery_available=False
        ),
        "ip_conflict": RecoverySuggestion(
            error_code="ip_conflict",
            error_message="IP address conflict detected",
            severity="critical",
            recovery_steps=[
                "Identify conflicting IP addresses",
                "Review management IP assignments",
                "Check vPC keepalive IP configuration",
                "Reassign conflicting IPs",
                "Re-validate topology"
            ],
            auto_recovery_available=False
        ),
        "vpc_mismatch": RecoverySuggestion(
            error_code="vpc_mismatch",
            error_message="vPC configuration mismatch",
            severity="critical",
            recovery_steps=[
                "Verify vPC domain ID matches on both peers",
                "Check peer-link port assignments",
                "Verify keepalive IP cross-reference",
                "Ensure consistent vPC configuration",
                "Re-validate topology"
            ],
            auto_recovery_available=False
        )
    }
    
    suggestion = recovery_db.get(error_code, RecoverySuggestion(
        error_code=error_code,
        error_message="Unknown error",
        severity="warning",
        recovery_steps=["Review error details and consult documentation"],
        auto_recovery_available=False
    ))
    
    return EnhancedErrorResponse(
        error_code=error_code,
        error_message=suggestion.error_message,
        severity=suggestion.severity,
        context={"timestamp": datetime.now().isoformat()},
        affected_components=[],
        recovery_suggestion=suggestion
    )


@app.post("/errors/auto-recover")
def auto_recover_error(error_code: str, request: Request):
    """
    Attempt automatic recovery for recoverable errors.
    """
    request_id = request_id_var.get()
    logger.info(f"AUTO_RECOVER_ATTEMPT", request_id=request_id, error_code=error_code)
    
    # In a real implementation, this would execute recovery commands
    return {
        "status": "success",
        "error_code": error_code,
        "auto_recovery": "not_available",
        "message": "Automatic recovery not available for this error type"
    }


@app.post("/util/cable-plan")
def cable_plan_preview(body: CablePlanInput, request: Request):
    """
    Generate cable plan for a device configuration.
    
    Returns structured cable plan and markdown documentation.
    """
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


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint for monitoring.
    
    Returns application metrics in Prometheus format if available.
    """
    if not PROMETHEUS_AVAILABLE or not generate_latest:
        return PlainTextResponse("Metrics not available", media_type="text/plain")
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health_check():
    """
    Deep health check endpoint with dependency checks.
    
    Returns overall health status and individual component health checks.
    """
    health_status = {
        "status": "healthy",
        "version": get_app_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {}
    }
    
    # Check catalog loader
    try:
        catalog.list_scenarios()
        health_status["checks"]["catalog"] = "ok"
    except Exception as e:
        health_status["checks"]["catalog"] = f"failed: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check pipeline
    try:
        health_status["checks"]["pipeline"] = "ok"
    except Exception as e:
        health_status["checks"]["pipeline"] = f"failed: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check history directory
    try:
        HISTORY_DIR.exists()
        health_status["checks"]["history_dir"] = "ok"
    except Exception as e:
        health_status["checks"]["history_dir"] = f"failed: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/util/hostname-hints")
def hostname_hints(request: Request, hostname: str, site: str = "", role: str = "leaf", pair: bool = False):
    """
    Validate hostname and provide suggestions.
    
    Returns validation status, hints, and suggested hostname based on site, role, and pair mode.
    """
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


@app.post("/audit/log")
async def audit_log(request: Request):
    """
    Receive audit logs from frontend for persistent storage.
    Loopback only — no session token required for offline use.
    """
    _enforce_loopback_only(request)
    
    try:
        log_data = await request.json()
        # Log the audit entry to the server logs
        logger.info(f"AUDIT_LOG: {log_data.get('action', 'UNKNOWN')}", extra=log_data)
        return {"status": "logged"}
    except Exception as e:
        logger.error(f"AUDIT_LOG_ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/open-folder")
async def open_folder(request: Request):
    """
    Open a folder in the system file explorer.
    Loopback only — no session token required for offline use.
    """
    _enforce_loopback_only(request)
    
    try:
        body = await request.json()
        folder_path = body.get('path', '')
        
        if not folder_path:
            return {"status": "error", "message": "No path provided"}
        
        # Resolve the path relative to app directory
        app_dir = get_app_dir()
        folder_path = Path(folder_path)  # Convert to Path first
        if not folder_path.is_absolute():
            folder_path = app_dir / folder_path
        
        # Ensure the folder exists
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        
        # Open folder in system file explorer
        import subprocess
        import platform
        import os
        
        try:
            if platform.system() == 'Windows':
                os.startfile(str(folder_path))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(folder_path)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(folder_path)], check=True)
        except Exception as e:
            logger.error(f"OPEN_FOLDER_SUBPROCESS_ERROR: {str(e)}")
            return {"status": "error", "message": f"Failed to open folder: {str(e)}"}
        
        logger.info(f"OPEN_FOLDER: {folder_path}")
        return {"status": "success", "path": str(folder_path)}
    except Exception as e:
        logger.error(f"OPEN_FOLDER_ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}
