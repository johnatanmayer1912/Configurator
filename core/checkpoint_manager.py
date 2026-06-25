import os
import json
import datetime
from dataclasses import asdict
from typing import List, Dict, Optional
from models.device_model import Device
from utils.app_dirs import get_checkpoints_dir

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = None):
        # Default to exe-relative directory; caller can override
        self.checkpoint_dir = checkpoint_dir if checkpoint_dir else get_checkpoints_dir()
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, device: Device, label: str = "manual") -> str:
        """
        Saves the current device model as a JSON snapshot.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device.hostname}_{label}_{timestamp}.json"
        path = os.path.join(self.checkpoint_dir, filename)
        
        # Convert dataclass to dict for JSON serialization
        # Note: We might need a custom encoder for complex types if asdict fails
        with open(path, "w") as f:
            json.dump(asdict(device), f, indent=4)
            
        return path

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
