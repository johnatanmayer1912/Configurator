"""
Configuration Artifact Logger
==============================

Structured logging for all configuration artifacts produced by the configurator.
This ensures every output is captured and available for audit testing.

Logs:
- Full configuration content (or hash + retrievable content)
- Port maps (logical and physical)
- Visual representations
- HTML structure
- CLI preview content
- JSON/structured data
- Duplicate detection results
- Cross-view consistency check results
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ArtifactLogEntry:
    """A log entry for a configuration artifact."""
    timestamp: str
    artifact_type: str  # "nxos_config", "port_map", "html", "json", "cli_preview", etc.
    artifact_id: str  # Unique identifier for this artifact
    source: str  # API endpoint, UI page, etc.
    content_hash: str  # SHA256 hash of content
    content: Optional[str] = None  # Full content (may be truncated for large artifacts)
    content_path: Optional[str] = None  # Path to stored content file
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_status: str = "pending"  # pending, passed, failed
    audit_findings: List[Dict[str, Any]] = field(default_factory=list)


class ConfigArtifactLogger:
    """
    Logger for configuration artifacts.
    
    Captures all configuration outputs in a structured format suitable
    for automated auditing and manual inspection.
    """
    
    def __init__(self, log_dir: str = "logs/artifacts"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup structured logger
        self.logger = logging.getLogger("config_artifact_logger")
        self.logger.setLevel(logging.INFO)
        
        # File handler for JSON log
        log_file = self.log_dir / "artifacts.jsonl"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        
        # Also keep in-memory entries for testing
        self.entries: List[ArtifactLogEntry] = []
        
        # Content storage directory
        self.content_dir = self.log_dir / "content"
        self.content_dir.mkdir(exist_ok=True)
    
    def log_artifact(
        self,
        artifact_type: str,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        store_full_content: bool = True
    ) -> ArtifactLogEntry:
        """
        Log a configuration artifact.
        
        Args:
            artifact_type: Type of artifact (nxos_config, port_map, etc.)
            content: The artifact content
            source: Where this artifact came from
            metadata: Additional metadata about the artifact
            store_full_content: Whether to store full content to disk
        
        Returns:
            The created log entry
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        artifact_id = f"{artifact_type}_{content_hash[:16]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Store content to disk if requested
        content_path = None
        if store_full_content:
            content_path = str(self.content_dir / f"{artifact_id}.txt")
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create log entry
        entry = ArtifactLogEntry(
            timestamp=timestamp,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            source=source,
            content_hash=content_hash,
            content=content if len(content) < 10000 else content[:10000] + "...",
            content_path=content_path,
            metadata=metadata or {},
            audit_status="pending"
        )
        
        self.entries.append(entry)
        
        # Log to JSONL file
        self.logger.info(json.dumps(asdict(entry)))
        
        return entry
    
    def log_nxos_config(
        self,
        config: str,
        hostname: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log an NX-OS configuration."""
        if metadata is None:
            metadata = {}
        metadata['hostname'] = hostname
        metadata['config_type'] = 'nxos'
        
        return self.log_artifact(
            artifact_type="nxos_config",
            content=config,
            source=f"generate_deployment:{hostname}",
            metadata=metadata
        )
    
    def log_port_map(
        self,
        port_map: Dict[str, Any],
        hostname: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log a port map."""
        if metadata is None:
            metadata = {}
        metadata['hostname'] = hostname
        metadata['map_type'] = 'port_map'
        
        content = json.dumps(port_map, indent=2)
        
        return self.log_artifact(
            artifact_type="port_map",
            content=content,
            source=f"generate_deployment:{hostname}",
            metadata=metadata
        )
    
    def log_html_page(
        self,
        html: str,
        page_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log an HTML page structure."""
        if metadata is None:
            metadata = {}
        metadata['page_name'] = page_name
        
        return self.log_artifact(
            artifact_type="html",
            content=html,
            source=f"render_page:{page_name}",
            metadata=metadata
        )
    
    def log_cli_preview(
        self,
        preview: str,
        hostname: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log a CLI preview."""
        if metadata is None:
            metadata = {}
        metadata['hostname'] = hostname
        metadata['preview_type'] = 'cli'
        
        return self.log_artifact(
            artifact_type="cli_preview",
            content=preview,
            source=f"cli_preview:{hostname}",
            metadata=metadata
        )
    
    def log_duplicate_detection(
        self,
        duplicate_type: str,
        duplicates: List[str],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log duplicate detection results."""
        if metadata is None:
            metadata = {}
        metadata['duplicate_type'] = duplicate_type
        metadata['duplicate_count'] = len(duplicates)
        
        content = json.dumps({
            'duplicate_type': duplicate_type,
            'duplicates': duplicates,
            'count': len(duplicates)
        }, indent=2)
        
        return self.log_artifact(
            artifact_type="duplicate_detection",
            content=content,
            source=source,
            metadata=metadata
        )
    
    def log_consistency_check(
        self,
        check_type: str,
        artifact1_id: str,
        artifact2_id: str,
        is_consistent: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> ArtifactLogEntry:
        """Log cross-artifact consistency check results."""
        metadata = {
            'check_type': check_type,
            'artifact1_id': artifact1_id,
            'artifact2_id': artifact2_id,
            'is_consistent': is_consistent,
            'details': details or {}
        }
        
        content = json.dumps(metadata, indent=2)
        
        return self.log_artifact(
            artifact_type="consistency_check",
            content=content,
            source=f"consistency_check:{check_type}",
            metadata=metadata
        )
    
    def update_audit_status(
        self,
        artifact_id: str,
        status: str,
        findings: Optional[List[Dict[str, Any]]] = None
    ):
        """Update audit status for an artifact."""
        for entry in self.entries:
            if entry.artifact_id == artifact_id:
                entry.audit_status = status
                if findings:
                    entry.audit_findings = findings
                
                # Re-log the updated entry
                self.logger.info(json.dumps(asdict(entry)))
                break
    
    def get_artifacts_by_type(self, artifact_type: str) -> List[ArtifactLogEntry]:
        """Get all artifacts of a specific type."""
        return [e for e in self.entries if e.artifact_type == artifact_type]
    
    def get_artifacts_by_source(self, source: str) -> List[ArtifactLogEntry]:
        """Get all artifacts from a specific source."""
        return [e for e in self.entries if e.source == source]
    
    def get_failed_audits(self) -> List[ArtifactLogEntry]:
        """Get all artifacts that failed audit."""
        return [e for e in self.entries if e.audit_status == "failed"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of logged artifacts."""
        type_counts = {}
        status_counts = {}
        
        for entry in self.entries:
            type_counts[entry.artifact_type] = type_counts.get(entry.artifact_type, 0) + 1
            status_counts[entry.audit_status] = status_counts.get(entry.audit_status, 0) + 1
        
        return {
            "total_artifacts": len(self.entries),
            "type_breakdown": type_counts,
            "status_breakdown": status_counts,
            "failed_audits": status_counts.get("failed", 0),
            "pending_audits": status_counts.get("pending", 0)
        }


# Global instance for use across the application
_global_logger: Optional[ConfigArtifactLogger] = None


def get_artifact_logger() -> ConfigArtifactLogger:
    """Get the global artifact logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = ConfigArtifactLogger()
    return _global_logger
