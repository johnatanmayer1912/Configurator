"""
Configuration Vault for Multi-Switch Configurations

Stores and manages configurations for multiple switches in a deployment.
Provides persistence and retrieval of switch configurations with port maps.
"""

import os
import json
import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from utils.app_dirs import get_vault_dir


@dataclass
class SwitchConfig:
    """Configuration for a single switch"""
    hostname: str
    mgmt_ip: str
    cli_config: str
    port_map: Dict[str, Any] = field(default_factory=dict)
    role: str = "primary"  # primary, secondary, or leaf
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DeploymentConfig:
    """Configuration for a multi-switch deployment"""
    deployment_id: str
    scenario_id: str
    site_name: str
    switches: List[SwitchConfig] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_switch(self, switch_config: SwitchConfig):
        """Add a switch configuration to the deployment"""
        self.switches.append(switch_config)
    
    def get_switch_by_hostname(self, hostname: str) -> Optional[SwitchConfig]:
        """Retrieve a switch configuration by hostname"""
        for switch in self.switches:
            if switch.hostname == hostname:
                return switch
        return None
    
    def get_switches_by_role(self, role: str) -> List[SwitchConfig]:
        """Retrieve all switches with a specific role"""
        return [s for s in self.switches if s.role == role]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ConfigurationVault:
    """Manages storage and retrieval of deployment configurations"""
    
    def __init__(self, vault_dir: str = None):
        self.vault_dir = vault_dir if vault_dir else get_vault_dir()
        os.makedirs(self.vault_dir, exist_ok=True)
    
    def save_deployment(self, deployment: DeploymentConfig) -> str:
        """Save a deployment configuration to the vault"""
        filename = f"{deployment.deployment_id}_{deployment.scenario_id}.json"
        path = os.path.join(self.vault_dir, filename)
        
        with open(path, "w") as f:
            json.dump(deployment.to_dict(), f, indent=4)
        
        return path
    
    def load_deployment(self, deployment_id: str, scenario_id: str) -> Optional[DeploymentConfig]:
        """Load a deployment configuration from the vault"""
        filename = f"{deployment_id}_{scenario_id}.json"
        path = os.path.join(self.vault_dir, filename)
        
        if not os.path.exists(path):
            return None
        
        with open(path, "r") as f:
            data = json.load(f)
        
        # Reconstruct DeploymentConfig from dict
        switches = [SwitchConfig(**s) for s in data.get("switches", [])]
        return DeploymentConfig(
            deployment_id=data["deployment_id"],
            scenario_id=data["scenario_id"],
            site_name=data["site_name"],
            switches=switches,
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {})
        )
    
    def list_deployments(self) -> List[Dict]:
        """List all deployments in the vault"""
        deployments = []
        
        for file in os.listdir(self.vault_dir):
            if file.endswith(".json"):
                path = os.path.join(self.vault_dir, file)
                mtime = os.path.getmtime(path)
                
                with open(path, "r") as f:
                    data = json.load(f)
                
                deployments.append({
                    "deployment_id": data.get("deployment_id"),
                    "scenario_id": data.get("scenario_id"),
                    "site_name": data.get("site_name"),
                    "switch_count": len(data.get("switches", [])),
                    "created_at": data.get("created_at"),
                    "modified_at": datetime.datetime.fromtimestamp(mtime).isoformat(),
                    "filename": file
                })
        
        return sorted(deployments, key=lambda x: x["created_at"], reverse=True)
    
    def delete_deployment(self, deployment_id: str, scenario_id: str) -> bool:
        """Delete a deployment from the vault"""
        filename = f"{deployment_id}_{scenario_id}.json"
        path = os.path.join(self.vault_dir, filename)
        
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
