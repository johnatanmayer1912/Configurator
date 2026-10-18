import os
import json
import datetime
from dataclasses import asdict
from typing import List, Dict, Optional
from models.device_model import Device
from utils.app_dirs import get_checkpoints_dir
from core.config_vault import ConfigurationVault, DeploymentConfig, SwitchConfig

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = None, vault: ConfigurationVault = None):
        # Default to exe-relative directory; caller can override
        self.checkpoint_dir = checkpoint_dir if checkpoint_dir else get_checkpoints_dir()
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.vault = vault if vault else ConfigurationVault()

    def save_checkpoint(self, device: Device, label: str = "manual", save_to_vault: bool = False) -> str:
        """
        Saves the current device model as a JSON snapshot.
        Optionally saves to configuration vault for multi-switch deployments.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device.hostname}_{label}_{timestamp}.json"
        path = os.path.join(self.checkpoint_dir, filename)
        
        # Convert dataclass to dict for JSON serialization
        # Note: We might need a custom encoder for complex types if asdict fails
        with open(path, "w") as f:
            json.dump(asdict(device), f, indent=4)
        
        # Optionally save to vault for multi-switch scenarios
        if save_to_vault:
            try:
                # Create a deployment config for this single switch
                deployment_id = f"{device.hostname}_{timestamp}"
                deployment = DeploymentConfig(
                    deployment_id=deployment_id,
                    scenario_id=label,
                    site_name=device.site_name or "default",
                    metadata={"checkpoint_label": label, "checkpoint_path": path}
                )
                
                # Add switch configuration
                switch_config = SwitchConfig(
                    hostname=device.hostname,
                    mgmt_ip=device.mgmt_ip or "",
                    cli_config="",  # Would need to render config
                    role="primary"
                )
                deployment.add_switch(switch_config)
                
                # Save to vault
                vault_path = self.vault.save_deployment(deployment)
                print(f"Checkpoint also saved to vault: {vault_path}")
            except Exception as e:
                print(f"Warning: Failed to save checkpoint to vault: {e}")
            
        return path

    def save_vpc_pair_checkpoint(
        self, 
        primary_device: Device, 
        secondary_device: Device, 
        scenario_id: str,
        label: str = "vpc_pair"
    ) -> Dict[str, str]:
        """
        Saves a vPC pair checkpoint to both checkpoint files and vault.
        Returns paths to saved files.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save individual checkpoints
        primary_path = self.save_checkpoint(primary_device, f"{label}_primary", save_to_vault=False)
        secondary_path = self.save_checkpoint(secondary_device, f"{label}_secondary", save_to_vault=False)
        
        # Save to vault as a deployment
        deployment_id = f"{primary_device.hostname}_{secondary_device.hostname}_{timestamp}"
        deployment = DeploymentConfig(
            deployment_id=deployment_id,
            scenario_id=scenario_id,
            site_name=primary_device.site_name or "default",
            metadata={"checkpoint_label": label, "vpc_pair": True}
        )
        
        # Add primary switch
        primary_config = SwitchConfig(
            hostname=primary_device.hostname,
            mgmt_ip=primary_device.mgmt_ip or "",
            cli_config="",
            role="primary"
        )
        deployment.add_switch(primary_config)
        
        # Add secondary switch
        secondary_config = SwitchConfig(
            hostname=secondary_device.hostname,
            mgmt_ip=secondary_device.mgmt_ip or "",
            cli_config="",
            role="secondary"
        )
        deployment.add_switch(secondary_config)
        
        # Save to vault
        vault_path = self.vault.save_deployment(deployment)
        
        return {
            "primary_checkpoint": primary_path,
            "secondary_checkpoint": secondary_path,
            "vault_deployment": vault_path,
            "deployment_id": deployment_id
        }

    def list_checkpoints(self, hostname: Optional[str] = None) -> List[Dict]:
        """
        Lists all available snapshots, optionally filtered by hostname.
        """
        checkpoints = []
        for file in os.listdir(self.checkpoint_dir):
            if file.endswith(".json"):
                if hostname and not file.startswith(hostname):
                    continue
                
                path = os.path.join(self.checkpoint_dir, file)
                mtime = os.path.getmtime(path)
                checkpoints.append({
                    "filename": file,
                    "timestamp": datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "path": path
                })
        
        # Sort by latest first
        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)

    def load_checkpoint(self, path: str) -> Dict:
        """
        Loads a snapshot from a file.
        """
        with open(path, "r") as f:
            return json.load(f)
