"""
ExportView — Review & Export section for the NX-OS Configuration Authority CTK app.

Implements tasks 9.1-9.8: preview pane with tabs, debounced refresh, generate/export
button, validation, checkpoint save/load, audit results, and configuration history.
"""

import os
from typing import Optional

import customtkinter as ctk

from gui.app_state import AppState
from gui.widgets.preview_pane import PreviewPane
from utils.logger import get_logger
from utils.app_dirs import get_history_dir, get_checkpoints_dir

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Task 9.1 — ExportView class
# ---------------------------------------------------------------------------

class ExportView(ctk.CTkFrame):
    """Review & Export view with live preview, export controls, history, and audit results.

    Parameters
    ----------
    master : widget
        Parent widget.
    app_state : AppState
        Shared application state instance.
    **kwargs
        Forwarded to CTkFrame.
    """

    def __init__(self, master, app_state: AppState, **kwargs) -> None:
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._app_state = app_state

        # Preview pane references
        self._standalone_pane: Optional[PreviewPane] = None
        self._vpc_tabview: Optional[ctk.CTkTabview] = None
        self._pane_a: Optional[PreviewPane] = None
        self._pane_b: Optional[PreviewPane] = None

        # Export controls
        self._export_button: Optional[ctk.CTkButton] = None
        self._status_banner: Optional[ctk.CTkLabel] = None

        # Audit result labels
        self._risk_label: Optional[ctk.CTkLabel] = None
        self._compliance_label: Optional[ctk.CTkLabel] = None

        # History panel
        self._history_frame: Optional[ctk.CTkScrollableFrame] = None

        # Debounce state
        self._dirty: bool = False
        self._after_id: Optional[str] = None

        self._build_ui()

        # Register reactive callback
        self._app_state.register_callback(self._on_state_change)

    def _build_ui(self) -> None:
        """Build the two-column layout."""
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Left column — preview pane
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="Configuration Preview",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Task 9.2 — Preview pane container
        self._preview_container = ctk.CTkFrame(left, fg_color="transparent")
        self._preview_container.grid(row=1, column=0, sticky="nsew")
        self._preview_container.rowconfigure(0, weight=1)
        self._preview_container.columnconfigure(0, weight=1)

        self._build_preview_panes()

        # Right column — controls + history + audit
        right = ctk.CTkScrollableFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.columnconfigure(0, weight=1)

        self._build_export_controls(right)
        self._build_audit_panel(right)
        self._build_history_panel(right)

    # ------------------------------------------------------------------
    # Task 9.2 — Preview pane integration
    # ------------------------------------------------------------------

    def _build_preview_panes(self) -> None:
        """Create standalone or tabbed preview panes based on vpc_mode."""
        # Clear existing panes
        for widget in self._preview_container.winfo_children():
            widget.destroy()

        if self._app_state.vpc_mode:
            # vPC mode: two tabs
            self._vpc_tabview = ctk.CTkTabview(self._preview_container)
            self._vpc_tabview.grid(row=0, column=0, sticky="nsew")

            self._vpc_tabview.add("Switch-A Config")
            self._vpc_tabview.add("Switch-B Config")

            self._pane_a = PreviewPane(self._vpc_tabview.tab("Switch-A Config"))
            self._pane_a.pack(fill="both", expand=True)

            self._pane_b = PreviewPane(self._vpc_tabview.tab("Switch-B Config"))
            self._pane_b.pack(fill="both", expand=True)

            self._standalone_pane = None
        else:
            # Standalone mode: single pane
            self._standalone_pane = PreviewPane(self._preview_container)
            self._standalone_pane.grid(row=0, column=0, sticky="nsew")
            self._vpc_tabview = None
            self._pane_a = None
            self._pane_b = None

    # ------------------------------------------------------------------
    # Task 9.3 — Debounced preview refresh
    # ------------------------------------------------------------------

    def _on_state_change(self) -> None:
        """Called by AppState.notify() — schedule a debounced preview refresh."""
        # Rebuild panes if vpc_mode changed
        if self._app_state.vpc_mode and self._standalone_pane is not None:
            self._build_preview_panes()
        elif not self._app_state.vpc_mode and self._standalone_pane is None:
            self._build_preview_panes()

        self._dirty = True
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.after(500, self._refresh_preview)

        # Update export button state
        self._update_export_button_state()

    def _refresh_preview(self) -> None:
        """Render the current configuration and update the preview pane(s)."""
        self._dirty = False
        self._after_id = None

        try:
            from core.renderer import ConfigRenderer
            renderer = ConfigRenderer()

            if self._app_state.vpc_mode:
                # Render Switch-A
                try:
                    device_a = self._app_state.build_device_a()
                    config_a = renderer.render_device_config(device_a)
                    if self._pane_a:
                        self._pane_a.update_text(config_a)
                except ValueError:
                    if self._pane_a:
                        self._pane_a.update_text("Complete required fields to preview configuration")

                # Render Switch-B
                try:
                    device_b = self._app_state.build_device_b()
                    config_b = renderer.render_device_config(device_b)
                    if self._pane_b:
                        self._pane_b.update_text(config_b)
                except ValueError:
                    if self._pane_b:
                        self._pane_b.update_text("Complete required fields to preview configuration")
            else:
                # Render standalone
                try:
                    device = self._app_state.build_device_a()
                    config = renderer.render_device_config(device)
                    if self._standalone_pane:
                        self._standalone_pane.update_text(config)
                except ValueError:
                    if self._standalone_pane:
                        self._standalone_pane.update_text("Complete required fields to preview configuration")

        except Exception as e:
            error_text = f"Template rendering error:\n{e}"
            logger.exception("Preview refresh failed: %s", e)
            if self._standalone_pane:
                self._standalone_pane.update_text(error_text)
            if self._pane_a:
                self._pane_a.update_text(error_text)
            if self._pane_b:
                self._pane_b.update_text(error_text)

    # ------------------------------------------------------------------
    # Task 9.4 — Generate & Export button
    # ------------------------------------------------------------------

    def _build_export_controls(self, parent: ctk.CTkFrame) -> None:
        """Create the export controls section."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Generate & Export",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self._export_button = ctk.CTkButton(
            frame,
            text="Generate & Export",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_generate_export,
        )
        self._export_button.pack(fill="x", padx=15, pady=(0, 5))

        # Task 9.8 — Load Checkpoint button
        ctk.CTkButton(
            frame,
            text="Load Checkpoint",
            height=32,
            fg_color="#2c3e50",
            hover_color="#34495e",
            command=self._on_load_checkpoint,
        ).pack(fill="x", padx=15, pady=(0, 5))

        # Status banner
        self._status_banner = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="w",
            wraplength=300,
        )
        self._status_banner.pack(anchor="w", padx=15, pady=(0, 15))

        self._update_export_button_state()

    def _update_export_button_state(self) -> None:
        """Enable/disable the export button based on validation errors."""
        if not self._export_button:
            return
        if self._app_state.validation_errors:
            self._export_button.configure(state="disabled")
        else:
            self._export_button.configure(state="normal")

    def _on_generate_export(self) -> None:
        """Handle Generate & Export button click."""
        from tkinter import filedialog
        output_dir = filedialog.askdirectory(title="Select Export Directory")
        if not output_dir:
            return
        self._run_export(output_dir)

    # ------------------------------------------------------------------
    # Task 9.5 — _run_export implementation
    # ------------------------------------------------------------------

    def _run_export(self, output_dir: str) -> None:
        """Execute the full export pipeline."""
        from core.validator import DeviceValidator, ValidationError
        from core.checkpoint_manager import CheckpointManager
        from pipelines.build_pipeline import ConfigurationPipeline

        validator = DeviceValidator()
        checkpoint_mgr = CheckpointManager()
        pipeline = ConfigurationPipeline(output_dir=output_dir)

        try:
            device_a = self._app_state.build_device_a()
        except ValueError as e:
            self._show_status(f"Missing required field: {e}", error=True)
            return

        # Validate device A
        result_a = validator.validate(device_a)
        if result_a["status"] == "fail":
            self._show_validation_errors(result_a["errors"])
            return

        devices = [device_a]

        if self._app_state.vpc_mode:
            try:
                device_b = self._app_state.build_device_b()
            except ValueError as e:
                self._show_status(f"Missing required field for Switch-B: {e}", error=True)
                return

            result_b = validator.validate(device_b)
            if result_b["status"] == "fail":
                self._show_validation_errors(result_b["errors"])
                return

            # vPC pair consistency check
            vpc_result = validator.validate_vpc_pair(device_a, device_b)
            if vpc_result["status"] == "fail":
                self._show_validation_errors(vpc_result["errors"])
                return

            devices.append(device_b)

        # Save checkpoints and run pipeline
        exported_files = []
        try:
            for device in devices:
                checkpoint_mgr.save_checkpoint(device, label="pre-export")
                result = pipeline.execute(device)
                exported_files.append(result)

            # Show success
            success_msg = f"✓ Export successful!\n{chr(10).join(exported_files)}"
            self._show_status(success_msg, error=False)

            # Task 9.6 — Show audit results
            self._show_audit_results(device_a)

            # Refresh history panel
            self._refresh_history()

        except Exception as e:
            logger.exception("Export pipeline failed: %s", e)
            self._show_status(f"Export failed: {e}", error=True)

    def _show_validation_errors(self, errors: list) -> None:
        """Display validation errors in a dialog."""
        try:
            from tkinter import messagebox
            error_text = "Validation failed:\n\n" + "\n".join(f"• {e}" for e in errors)
            messagebox.showerror("Validation Errors", error_text)
        except Exception:
            self._show_status("Validation failed: " + "; ".join(errors), error=True)

    def _show_status(self, message: str, error: bool = False) -> None:
        """Update the status banner."""
        if self._status_banner:
            color = "#e74c3c" if error else "#27ae60"
            self._status_banner.configure(text=message, text_color=color)

    # ------------------------------------------------------------------
    # Task 9.6 — Post-export audit results panel
    # ------------------------------------------------------------------

    def _build_audit_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the audit results display panel."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Audit Results",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self._risk_label = ctk.CTkLabel(
            frame,
            text="Risk: —",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._risk_label.pack(anchor="w", padx=15, pady=2)

        self._compliance_label = ctk.CTkLabel(
            frame,
            text="Compliance: —",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._compliance_label.pack(anchor="w", padx=15, pady=(2, 15))

    def _show_audit_results(self, device) -> None:
        """Run and display risk and compliance audit results."""
        try:
            from core.risk_analyzer import RiskAnalyzer
            from core.compliance import ComplianceEngine
            from core.renderer import ConfigRenderer

            renderer = ConfigRenderer()
            config_text = renderer.render_device_config(device)

            # Risk analysis
            risk_analyzer = RiskAnalyzer()
            analysis = risk_analyzer.analyze(config_text.splitlines())
            overall = analysis.get("overall_risk", "UNKNOWN")
            findings = analysis.get("findings", [])

            counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for f in findings:
                level = f.get("level", "LOW")
                counts[level] = counts.get(level, 0) + 1

            risk_color = {
                "CRITICAL": "#e74c3c",
                "HIGH": "#e67e22",
                "MEDIUM": "#f1c40f",
                "LOW": "#27ae60",
            }.get(overall, "#7f8c8d")

            risk_text = (
                f"Risk: {overall}  |  "
                f"CRITICAL: {counts['CRITICAL']}  "
                f"HIGH: {counts['HIGH']}  "
                f"MEDIUM: {counts['MEDIUM']}  "
                f"LOW: {counts['LOW']}"
            )
            if self._risk_label:
                self._risk_label.configure(text=risk_text, text_color=risk_color)

            # Compliance audit
            compliance = ComplianceEngine()
            compliance_findings = compliance.audit(device)
            errors = sum(1 for f in compliance_findings if f.get("level") == "error")
            warnings = sum(1 for f in compliance_findings if f.get("level") == "warning")

            compliance_text = f"Compliance: {errors} error(s), {warnings} warning(s)"
            compliance_color = "#e74c3c" if errors > 0 else ("#e67e22" if warnings > 0 else "#27ae60")
            if self._compliance_label:
                self._compliance_label.configure(text=compliance_text, text_color=compliance_color)

        except Exception as e:
            logger.exception("Audit failed: %s", e)

    # ------------------------------------------------------------------
    # Task 9.7 — Configuration history panel
    # ------------------------------------------------------------------

    def _build_history_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the configuration history panel."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Configuration History",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self._history_frame = ctk.CTkScrollableFrame(frame, height=200)
        self._history_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._refresh_history()

    def _refresh_history(self) -> None:
        """Reload the history list from the exe-relative configs/history/."""
        if not self._history_frame:
            return

        for widget in self._history_frame.winfo_children():
            widget.destroy()

        history_dir = get_history_dir()
        if not os.path.exists(history_dir):
            ctk.CTkLabel(self._history_frame, text="No history yet",
                         text_color="#7f8c8d", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=5, pady=2)
            return

        try:
            files = [f for f in os.listdir(history_dir) if f.endswith("_config.txt")]
            files.sort(key=lambda f: os.path.getmtime(os.path.join(history_dir, f)), reverse=True)
        except Exception:
            files = []

        if not files:
            ctk.CTkLabel(self._history_frame, text="No history yet",
                         text_color="#7f8c8d", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=5, pady=2)
            return

        for filename in files:
            filepath = os.path.join(history_dir, filename)
            btn = ctk.CTkButton(
                self._history_frame, text=filename, anchor="w",
                font=ctk.CTkFont(family="Consolas", size=10),
                fg_color="transparent", text_color=("#2980b9", "#5dade2"),
                hover_color=("#e8f4fd", "#1a3a5c"),
                command=lambda fp=filepath: self._show_history_file(fp),
            )
            btn.pack(fill="x", pady=1)

    def _show_history_file(self, filepath: str) -> None:
        """Display a history file in a popup window."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            popup = ctk.CTkToplevel(self)
            popup.title(os.path.basename(filepath))
            popup.geometry("900x600")
            popup.grab_set()

            textbox = ctk.CTkTextbox(
                popup,
                font=ctk.CTkFont(family="Consolas", size=11),
                state="normal",
            )
            textbox.pack(fill="both", expand=True, padx=10, pady=10)
            textbox.insert("0.0", content)
            textbox.configure(state="disabled")

        except Exception as e:
            logger.exception("Failed to open history file: %s", e)

    # ------------------------------------------------------------------
    # Task 9.8 — Load Checkpoint
    # ------------------------------------------------------------------

    def _on_load_checkpoint(self) -> None:
        """Handle Load Checkpoint button click."""
        from tkinter import filedialog, messagebox

        checkpoint_dir = get_checkpoints_dir()
        filepath = filedialog.askopenfilename(
            title="Load Checkpoint",
            initialdir=checkpoint_dir if os.path.exists(checkpoint_dir) else ".",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not filepath:
            return

        try:
            from core.checkpoint_manager import CheckpointManager
            mgr = CheckpointManager()
            data = mgr.load_checkpoint(filepath)

            # Map checkpoint data back to AppState
            self._restore_from_checkpoint(data)
            self._show_status("✓ Checkpoint loaded successfully", error=False)

        except Exception as e:
            logger.exception("Failed to load checkpoint: %s", e)
            try:
                messagebox.showerror(
                    "Checkpoint Error",
                    "Checkpoint file is invalid or incompatible",
                )
            except Exception:
                self._show_status("Checkpoint file is invalid or incompatible", error=True)

    def _restore_from_checkpoint(self, data: dict) -> None:
        """Restore AppState fields from a checkpoint dict."""
        state = self._app_state

        # Basic device fields
        state.hostname = data.get("hostname", "")
        state.mgmt_ip = data.get("mgmt_ip", "")
        state.mgmt_gw = data.get("mgmt_gw", "")
        state.motd = data.get("motd", "Authorized Access Only")
        state.admin_user = data.get("admin_user", "admin")
        state.admin_password = data.get("admin_password", "")
        state.model = data.get("model", "Nexus 93180YC-EX")

        # VLANs
        from models.vlan_model import VLAN
        state.vlans = []
        for v in data.get("vlans", []):
            try:
                state.vlans.append(VLAN(id=v["id"], name=v["name"]))
            except Exception:
                pass

        # Interfaces
        from models.interface_model import Interface
        state.interfaces = []
        for i in data.get("interfaces", []):
            try:
                iface = Interface(
                    name=i["name"],
                    mode=i.get("mode", "access"),
                    vlan=i.get("vlan"),
                    description=i.get("description"),
                    shutdown=i.get("shutdown", True),
                    vpc_id=i.get("vpc_id"),
                )
                state.interfaces.append(iface)
            except Exception:
                pass

        # vPC config
        vpc_data = data.get("vpc")
        if vpc_data:
            state.vpc_mode = True
            state.vpc_domain_id = str(vpc_data.get("domain_id", ""))
            state.vpc_kpa_vrf = vpc_data.get("keepalive_vrf", "management")
            state.vpc_peer_link_id = str(vpc_data.get("peer_link_id", "1"))
            state.vpc_peer_link_ports = vpc_data.get("peer_link_interfaces", [])
            state.a_kpa_ip = vpc_data.get("local_keepalive_ip", "")
            state.b_kpa_ip = vpc_data.get("remote_keepalive_ip", "")
        else:
            state.vpc_mode = False

        state.notify()
