import os
import difflib
import json
import re
from datetime import datetime
from typing import Optional, Dict, List, Any

from models.device_model import Device
from core.engine import ConfigEngine
from core.risk_analyzer import RiskAnalyzer
from utils.app_dirs import get_history_dir
from utils.export_paths import (
    build_file_prefix,
    resolve_export_base,
    resolve_output_directory,
    safe_hostname,
    slugify,
)
from utils.change_package import write_device_json


class ConfigurationPipeline:
    def __init__(self, output_dir: str = None):
        self.engine = ConfigEngine()
        self.risk_analyzer = RiskAnalyzer()
        self.output_dir = output_dir if output_dir else get_history_dir()
        os.makedirs(self.output_dir, exist_ok=True)

        from utils.version import get_app_version
        self.version = get_app_version()

    def execute(
        self,
        device: Device,
        base_config: str = "",
        extra_artifacts: Optional[Dict[str, str]] = None,
        output_dir: Optional[str] = None,
        render_metadata: Optional[Dict] = None,
        *,
        site_name: str = "DEFAULT_SITE",
        scenario_slug: str = "scenario",
        pair_batch: bool = False,
        batch_timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run validate → render → diff → risk → save. Returns export manifest."""
        effective_base = output_dir if output_dir is not None else self.output_dir
        timestamp = batch_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir, batch_folder = resolve_output_directory(
            effective_base,
            pair_batch=pair_batch,
            site_name=site_name,
            scenario_slug=scenario_slug,
            timestamp=timestamp,
        )

        metadata = {
            "version": self.version,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "vPC Pair" if device.vpc else "Standalone",
            "system": "Configuration Authority System",
            "nxos_version": device.nxos_version,
            "site_name": site_name,
            "scenario": scenario_slug,
        }
        if render_metadata:
            metadata.update(render_metadata)

        config_text = self.engine.build_config(device, metadata=metadata)
        diff_text = self.generate_diff(base_config, config_text)
        analysis = self.risk_analyzer.analyze(config_text.splitlines())
        risk_report = self.risk_analyzer.generate_report(analysis)

        prefix = build_file_prefix(site_name, scenario_slug, device.hostname, timestamp)
        files_written: List[str] = []

        device_json_name = write_device_json(target_dir, prefix, device)
        files_written.append(device_json_name)

        for suffix, content in [
            ("config", config_text),
            ("diff", diff_text),
            ("risk", risk_report),
        ]:
            name = f"{prefix}_{suffix}.txt"
            self._write_file(name, content, target_dir)
            files_written.append(name)

        if extra_artifacts:
            for artifact_name, artifact_content in extra_artifacts.items():
                suffix = re.sub(r"[^a-zA-Z0-9_.-]", "_", artifact_name)
                if isinstance(artifact_content, (dict, list)):
                    content = json.dumps(artifact_content, indent=2)
                else:
                    content = str(artifact_content)
                name = f"{prefix}_{suffix}.txt"
                self._write_file(name, content, target_dir)
                files_written.append(name)

        return {
            "message": f"Artifacts saved to {target_dir}",
            "output_dir": target_dir,
            "files": files_written,
            "prefix": prefix,
            "batch_folder": batch_folder,
            "timestamp": timestamp,
            "hostname": device.hostname,
            "config_preview": config_text,
        }

    @staticmethod
    def resolve_export_directory(override: Optional[str]) -> str:
        return resolve_export_base(override, get_history_dir())

    def generate_diff(self, a: str, b: str) -> str:
        a_lines = a.splitlines(keepends=True)
        b_lines = b.splitlines(keepends=True)
        diff = difflib.unified_diff(a_lines, b_lines, fromfile="baseline", tofile="proposed")
        return "".join(diff)

    def _write_file(self, filename: str, content: str, output_dir: Optional[str] = None):
        dir_to_use = output_dir if output_dir is not None else self.output_dir
        path = os.path.join(dir_to_use, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
