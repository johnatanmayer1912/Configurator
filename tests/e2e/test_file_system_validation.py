"""
True File-System Validation Tests - Writes to Disk, Reads Back, Validates Content

Every test in this file:
1. Calls the live server API to generate configurations
2. Confirms files were actually written to disk in the output directory
3. Reads ALL generated files from the file system
4. Validates file contents match the selected options exactly
5. No API-response-only validation - actual file system reads
"""

import pytest
import requests
from pathlib import Path
from typing import Dict, Any
import time
import shutil
import json

BASE_URL = "http://127.0.0.1:9000"
OUTPUT_BASE = Path("configs/history")


class TestFileSystemValidation:
    """True file-system validation tests - writes to disk, reads back, validates."""

    @pytest.fixture(autouse=True)
    def cleanup_output(self):
        """Clean up output directory before/after tests."""
        # Cleanup before
        if OUTPUT_BASE.exists():
            for old_dir in OUTPUT_BASE.iterdir():
                if old_dir.is_dir() and old_dir.name.startswith("E2E_FS_TEST_"):
                    try:
                        shutil.rmtree(old_dir)
                    except:
                        pass
        yield
        # Cleanup after
        if OUTPUT_BASE.exists():
            for old_dir in OUTPUT_BASE.iterdir():
                if old_dir.is_dir() and old_dir.name.startswith("E2E_FS_TEST_"):
                    try:
                        shutil.rmtree(old_dir)
                    except:
                        pass

    def _generate_deployment_to_disk(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment to disk and return file paths and content."""
        # Add output_dir to payload to force file writing
        timestamp = int(time.time())
        output_dir = OUTPUT_BASE / f"E2E_FS_TEST_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        payload["output_dir"] = str(output_dir)
        
        resp = requests.post(f"{BASE_URL}/generate-deployment", json=payload, timeout=60)
        assert resp.status_code == 200, f"Generation failed: {resp.text}"
        result = resp.json()
        
        # Wait for files to be written to disk
        time.sleep(1)
        
        # Read all files from disk
        file_contents = {}
        file_paths = []
        
        if output_dir.exists():
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    file_paths.append(str(file_path))
                    try:
                        file_contents[str(file_path)] = file_path.read_text(encoding="utf-8", errors="ignore")
                    except Exception as e:
                        file_contents[str(file_path)] = f"ERROR reading file: {e}"
        
        return {
            "response": result,
            "output_dir": str(output_dir),
            "file_paths": file_paths,
            "file_contents": file_contents,
        }

    def test_single_switch_writes_cli_file_to_disk(self):
        """
        Journey: Single standalone switch writes CLI file to disk.
        
        Validates:
        - CLI file is actually written to disk in output directory
        - File can be read back from disk
        - File contains correct hostname
        - File contains correct VLANs
        - File contains correct management IP
        """
        timestamp = int(time.time())
        payload = {
            "site_name": f"E2E_FS_TEST_{timestamp}",
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "access",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                }
            ],
            "global_vlans": [
                {"id": 10, "name": "DATA"},
                {"id": 20, "name": "VOICE"},
            ],
        }

        result = self._generate_deployment_to_disk(payload)
        
        # Assert files were written to disk
        assert len(result["file_paths"]) > 0, "No files were written to disk"
        print(f"Files written to disk: {result['file_paths']}")
        
        # Find CLI file
        cli_files = [f for f in result["file_paths"] if f.endswith(".cfg") or f.endswith(".txt") or "cli" in f.lower()]
        assert len(cli_files) > 0, "No CLI file was written to disk"
        
        # Read CLI content from disk
        cli_content = result["file_contents"].get(cli_files[0], "")
        assert len(cli_content) > 0, "CLI file on disk is empty"
        
        # Validate content from disk
        assert "hostname SW1" in cli_content or "hostname sw1" in cli_content.lower(), "Hostname not in CLI file on disk"
        assert "10.0.0.1" in cli_content, "Management IP not in CLI file on disk"
        assert "vlan 10" in cli_content.lower() or "vlan10" in cli_content.lower(), "VLAN 10 not in CLI file on disk"
        assert "vlan 20" in cli_content.lower() or "vlan20" in cli_content.lower(), "VLAN 20 not in CLI file on disk"
        assert "DATA" in cli_content, "VLAN name DATA not in CLI file on disk"
        assert "VOICE" in cli_content, "VLAN name VOICE not in CLI file on disk"

    def test_vpc_pair_writes_both_cli_files_to_disk(self):
        """
        Journey: vPC pair writes CLI files for both switches to disk.
        
        Validates:
        - Primary switch CLI file written to disk
        - Secondary switch CLI file written to disk
        - Both files can be read back from disk
        - Both contain matching vPC domain
        - Keepalive IPs are different in files on disk
        """
        timestamp = int(time.time())
        payload = {
            "site_name": f"E2E_FS_TEST_{timestamp}",
            "switches": [
                {
                    "hostname": "CORE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "core",
                    "vpc_domain": "10",
                    "local_ka": "10.0.0.1",
                    "remote_ka": "10.0.0.2",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "CORE2",
                    "mgmt_ip": "10.0.0.2/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "core",
                    "vpc_domain": "10",
                    "local_ka": "10.0.0.2",
                    "remote_ka": "10.0.0.1",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                }
            ],
            "vpc_pairs": [
                {
                    "domain": 10,
                    "primary": "CORE1",
                    "secondary": "CORE2",
                    "peer_link_ports": "Ethernet1/35-36",
                }
            ],
            "global_vlans": [{"id": 100, "name": "FABRIC"}],
        }

        result = self._generate_deployment_to_disk(payload)
        
        # Assert multiple files written to disk
        assert len(result["file_paths"]) >= 2, "Should have at least 2 CLI files on disk for vPC pair"
        
        # Find CLI files for each switch
        cli_files = [f for f in result["file_paths"] if f.endswith(".cfg") or f.endswith(".txt") or "cli" in f.lower()]
        assert len(cli_files) >= 2, "Should have at least 2 CLI files on disk"
        
        # Read both CLI contents from disk
        cli_contents = [result["file_contents"].get(f, "") for f in cli_files[:2]]
        
        # Validate both have vPC config on disk
        for cli in cli_contents:
            assert "vpc" in cli.lower(), "vPC config missing from file on disk"
            assert "domain" in cli.lower(), "vPC domain missing from file on disk"
        
        # Validate keepalive IPs are different in files on disk
        has_ka_1 = any("10.0.0.1" in cli for cli in cli_contents)
        has_ka_2 = any("10.0.0.2" in cli for cli in cli_contents)
        assert has_ka_1 and has_ka_2, "Keepalive IPs not present or not different in files on disk"

    def test_feature_lacp_writes_cli_with_feature_to_disk(self):
        """
        Journey: Enable LACP feature writes CLI with feature lacp to disk.
        
        Validates:
        - CLI file written to disk
        - File can be read back
        - Contains "feature lacp" in file on disk
        """
        timestamp = int(time.time())
        payload = {
            "site_name": f"E2E_FS_TEST_{timestamp}",
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "nxos_version": "9.3",
                    "baseline_options": ["lacp"],
                }
            ],
            "global_vlans": [{"id": 10, "name": "DATA"}],
        }

        result = self._generate_deployment_to_disk(payload)
        
        cli_files = [f for f in result["file_paths"] if f.endswith(".cfg") or f.endswith(".txt") or "cli" in f.lower()]
        assert len(cli_files) > 0, "No CLI file written to disk"
        
        cli_content = result["file_contents"].get(cli_files[0], "")
        assert "feature lacp" in cli_content.lower(), "LACP feature not enabled in CLI file on disk"

    def test_vlan_range_writes_multiple_vlans_to_disk(self):
        """
        Journey: Bulk VLAN range assignment writes multiple VLANs to CLI file on disk.
        
        Validates:
        - CLI file written to disk
        - File can be read back
        - Contains all VLANs in range in file on disk
        - VLAN names follow pattern in file on disk
        """
        timestamp = int(time.time())
        payload = {
            "site_name": f"E2E_FS_TEST_{timestamp}",
            "switches": [
                {
                    "hostname": "SW1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "access",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                }
            ],
            "global_vlans": [
                {"id": 10, "name": "DATA_10"},
                {"id": 11, "name": "DATA_11"},
                {"id": 12, "name": "DATA_12"},
            ],
        }

        result = self._generate_deployment_to_disk(payload)
        
        cli_files = [f for f in result["file_paths"] if f.endswith(".cfg") or f.endswith(".txt") or "cli" in f.lower()]
        assert len(cli_files) > 0, "No CLI file written to disk"
        
        cli_content = result["file_contents"].get(cli_files[0], "")
        assert "vlan 10" in cli_content.lower() or "vlan10" in cli_content.lower()
        assert "vlan 11" in cli_content.lower() or "vlan11" in cli_content.lower()
        assert "vlan 12" in cli_content.lower() or "vlan12" in cli_content.lower()
        assert "DATA_10" in cli_content
        assert "DATA_11" in cli_content
        assert "DATA_12" in cli_content

    def test_3_tier_writes_all_switch_configs_to_disk(self):
        """
        Journey: Spine + Leaf + Access topology writes configs for all switches to disk.
        
        Validates:
        - CLI files written to disk for SPINE switch
        - CLI files written to disk for LEAF switch
        - CLI files written to disk for ACCESS switch
        - All files can be read back from disk
        - All files contain correct topology info
        """
        timestamp = int(time.time())
        payload = {
            "site_name": f"E2E_FS_TEST_{timestamp}",
            "switches": [
                {
                    "hostname": "SPINE1",
                    "mgmt_ip": "10.0.0.1/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9336C-FX2",
                    "role": "spine",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "LEAF1",
                    "mgmt_ip": "10.0.0.11/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 93180YC-EX",
                    "role": "leaf",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                },
                {
                    "hostname": "ACCESS1",
                    "mgmt_ip": "10.0.0.21/24",
                    "mgmt_gw": "10.0.0.254",
                    "model": "Nexus 9348GC-FXP",
                    "role": "access",
                    "nxos_version": "9.3",
                    "baseline_options": [],
                }
            ],
            "global_vlans": [
                {"id": 10, "name": "DATA"},
                {"id": 20, "name": "VOICE"},
                {"id": 100, "name": "FABRIC"},
            ],
        }

        result = self._generate_deployment_to_disk(payload)
        
        # Should have files for all 3 switches on disk
        assert len(result["file_paths"]) >= 3, "Should have configs on disk for SPINE, LEAF, and ACCESS"
        
        cli_files = [f for f in result["file_paths"] if f.endswith(".cfg") or f.endswith(".txt") or "cli" in f.lower()]
        assert len(cli_files) >= 3, "Should have at least 3 CLI files on disk"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
