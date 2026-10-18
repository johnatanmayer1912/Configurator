"""
Shared Pydantic contracts for wizard, single-switch, and deployment APIs.

Single source of truth for hostname, management IP, and deployment topology shapes.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

HOSTNAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$")


def validate_hostname_value(value: str) -> str:
    v = (value or "").strip()
    if len(v) < 1:
        raise ValueError("Hostname is required.")
    if not HOSTNAME_PATTERN.fullmatch(v):
        raise ValueError("Hostname must use letters, numbers, and hyphens only.")
    return v


def validate_mgmt_ip_cidr(value: str) -> str:
    v = (value or "").strip()
    if "/" not in v:
        raise ValueError("Management IP must include CIDR notation (e.g. 10.10.10.10/24).")
    ip_part = v.split("/")[0]
    parts = ip_part.split(".")
    if len(parts) != 4:
        raise ValueError(f"Invalid IPv4 address: {v}")
    for part in parts:
        num = int(part)
        if num < 0 or num > 255:
            raise ValueError(f"Invalid IPv4 address: {v}")
    return v


def validate_ipv4_loose(value: str) -> str:
    """Gateway or keepalive — CIDR optional."""
    if not value or not str(value).strip():
        raise ValueError("IP address cannot be empty.")
    v = str(value).strip()
    ip_part = v.split("/")[0]
    parts = ip_part.split(".")
    if len(parts) != 4:
        raise ValueError(f"Invalid IPv4 address: {v}")
    for part in parts:
        num = int(part)
        if num < 0 or num > 255:
            raise ValueError(f"Invalid IPv4 address: {v}")
    return v


class VPCPairInput(BaseModel):
    domain: int = Field(..., ge=1, le=4095)
    primary: str
    secondary: str
    peer_link_ports: str = Field(default="", alias="vpc_pl_ints")
    description: Optional[str] = None

    model_config = {"populate_by_name": True}

    @field_validator("primary", "secondary")
    @classmethod
    def _hostname(cls, v: str) -> str:
        return validate_hostname_value(v)

    @model_validator(mode="after")
    def _peers_differ(self) -> "VPCPairInput":
        if self.primary == self.secondary:
            raise ValueError("vPC primary and secondary must be different switches.")
        if not str(self.peer_link_ports or "").strip():
            raise ValueError("vPC peer_link_ports (or vpc_pl_ints) is required.")
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "primary": self.primary,
            "secondary": self.secondary,
            "peer_link_ports": self.peer_link_ports,
            "description": self.description,
        }


class UplinkInput(BaseModel):
    """Fabric uplink — supports distinct port lists on each end."""

    uplink_id: Optional[str] = None
    from_switch: str = Field(..., alias="from")
    to_switch: str = Field(..., alias="to")
    ports: str = ""
    from_ports: str = ""
    to_ports: str = ""
    po_id: Optional[int] = Field(default=None, ge=1, le=4096)
    description: Optional[str] = None

    model_config = {"populate_by_name": True}

    @field_validator("from_switch", "to_switch")
    @classmethod
    def _hostname(cls, v: str) -> str:
        return validate_hostname_value(v)

    @model_validator(mode="after")
    def _ports_present(self) -> "UplinkInput":
        if not (self.ports or self.from_ports or self.to_ports):
            raise ValueError("Uplink requires ports, from_ports, or to_ports.")
        return self

    def ports_for(self, hostname: str) -> str:
        if hostname == self.from_switch and self.from_ports:
            return self.from_ports
        if hostname == self.to_switch and self.to_ports:
            return self.to_ports
        return self.ports

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uplink_id": self.uplink_id,
            "from": self.from_switch,
            "to": self.to_switch,
            "ports": self.ports,
            "from_ports": self.from_ports,
            "to_ports": self.to_ports,
            "po_id": self.po_id,
            "description": self.description,
        }


class UnifiedGenerateRequest(BaseModel):
    """Single entry point for config generation (wizard / single / deployment)."""

    mode: str = Field(default="single", description="single | deployment | preview")
    device: Optional[Dict[str, Any]] = None
    deployment: Optional[Dict[str, Any]] = None
    preview: bool = False

    @field_validator("mode")
    @classmethod
    def _mode(cls, v: str) -> str:
        m = (v or "single").lower().strip()
        if m not in {"single", "deployment", "preview", "wizard"}:
            raise ValueError("mode must be single, deployment, preview, or wizard")
        return m
