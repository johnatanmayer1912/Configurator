"""
VPCView — VPC Configuration section for the NX-OS Configuration Authority CTK app.

Implements tasks 7.1-7.8: vPC domain parameters, port assignments, intelligence summary,
keepalive cross-reference, infrastructure note, and section status updates.
"""

from typing import Optional

import customtkinter as ctk

from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader
from gui.widgets.validated_entry import ValidatedEntry


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------

def validate_domain_id(value: str) -> tuple[bool, str]:
    """Validate vPC domain ID: integer 1-1000."""
    if not value:
        return False, "Domain ID is required"
    try:
        domain_id = int(value)
        if not (1 <= domain_id <= 1000):
            return False, "Domain ID must be between 1 and 1000"
        return True, ""
    except ValueError:
        return False, "Domain ID must be a valid integer"


def validate_port_channel_id(value: str) -> tuple[bool, str]:
    """Validate port-channel ID: integer 1-4096."""
    if not value:
        return False, "Port-Channel ID is required"
    try:
        pc_id = int(value)
        if not (1 <= pc_id <= 4096):
            return False, "Port-Channel ID must be between 1 and 4096"
        return True, ""
    except ValueError:
        return False, "Port-Channel ID must be a valid integer"


# ---------------------------------------------------------------------------
# Task 7.1 — VPCView class
# ---------------------------------------------------------------------------

class VPCView(ctk.CTkScrollableFrame):
    """VPC Configuration view for setting up vPC domain parameters and port assignments.
    
    Parameters
    ----------
    master : widget
        Parent widget.
    app_state : AppState
        Shared application state instance.
    hardware_loader : HardwareLoader
        Pre-loaded hardware profile loader.
    **kwargs
        Forwarded to CTkScrollableFrame.
    """

    def __init__(
        self,
        master,
        app_state: AppState,
        hardware_loader: HardwareLoader,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._app_state = app_state
        self._hardware_loader = hardware_loader

        # Stored widget references
        self._field_widgets: dict[str, ValidatedEntry] = {}

        # UI component references
        self._peer_link_textbox: Optional[ctk.CTkTextbox] = None
        self._peer_link_entry: Optional[ctk.CTkEntry] = None
        self._peer_link_override: Optional[ctk.CTkSwitch] = None
        self._keepalive_textbox: Optional[ctk.CTkTextbox] = None
        self._keepalive_entry: Optional[ctk.CTkEntry] = None
        self._keepalive_override: Optional[ctk.CTkSwitch] = None
        self._intelligence_labels: dict[str, ctk.CTkLabel] = {}
        self._kpa_cross_ref_frame: Optional[ctk.CTkFrame] = None

        self._build_ui()
        
        # Task 7.1 — Register callback to refresh all fields when state changes
        self._app_state.register_callback(self._on_state_change)

    def _build_ui(self) -> None:
        """Build the complete VPC Configuration UI."""
        # Task 7.2 — vPC domain parameters
        self._build_domain_parameters()
        
        # Task 7.3 & 7.4 — Port assignments
        self._build_port_assignments()
        
        # Task 7.5 — vPC Intelligence Summary
        self._build_intelligence_summary()
        
        # Task 7.6 — Keepalive cross-reference
        self._build_keepalive_cross_ref()
        
        # Task 7.7 — Infrastructure note
        self._build_infrastructure_note()
        
        # Initial state refresh
        self._refresh_port_assignments()
        self._refresh_intelligence_summary()
        self._refresh_keepalive_cross_ref()

    # ------------------------------------------------------------------
    # Task 7.2 — vPC domain parameters row
    # ------------------------------------------------------------------

    def _build_domain_parameters(self) -> None:
        """Create the vPC domain parameters configuration section."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame,
            text="vPC Domain Parameters:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        params_frame = ctk.CTkFrame(frame, fg_color="transparent")
        params_frame.pack(fill="x", padx=15, pady=(0, 15))
        params_frame.columnconfigure(0, weight=1)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(2, weight=1)

        # Domain ID
        domain_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        domain_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        domain_entry = ValidatedEntry(
            domain_frame,
            validator=validate_domain_id,
            field_key="vpc_domain_id",
            on_change=self._on_field_change,
            label_text="Domain ID (1-1000):",
            placeholder_text="10",
        )
        domain_entry.pack(fill="x")
        self._field_widgets["vpc_domain_id"] = domain_entry

        # Peer-Keepalive VRF
        vrf_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        vrf_frame.grid(row=0, column=1, sticky="ew", padx=2.5)

        ctk.CTkLabel(vrf_frame, text="Peer-Keepalive VRF:", anchor="w").pack(anchor="w", pady=(0, 2))
        vrf_entry = ctk.CTkEntry(vrf_frame, placeholder_text="management")
        vrf_entry.pack(fill="x")
        vrf_entry.insert(0, self._app_state.vpc_kpa_vrf)
        vrf_entry.bind("<KeyRelease>", lambda e: self._on_vrf_change(vrf_entry.get()))

        # Peer-Link Port-Channel ID
        pc_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        pc_frame.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        pc_entry = ValidatedEntry(
            pc_frame,
            validator=validate_port_channel_id,
            field_key="vpc_peer_link_id",
            on_change=self._on_field_change,
            label_text="Peer-Link Port-Channel ID:",
            placeholder_text="1",
        )
        pc_entry.pack(fill="x")
        self._field_widgets["vpc_peer_link_id"] = pc_entry

    def _on_field_change(self, field_key: str, is_valid: bool) -> None:
        """Handle validated field changes."""
        # Update validation errors
        if is_valid:
            self._app_state.validation_errors.pop(field_key, None)
        else:
            self._app_state.validation_errors[field_key] = "Invalid"

        # Update app state field using stored widget reference
        widget = self._field_widgets.get(field_key)
        if widget:
            setattr(self._app_state, field_key, widget.get())

        self._refresh_intelligence_summary()
        self._update_section_status()

    def _on_vrf_change(self, value: str) -> None:
        """Handle VRF field change."""
        self._app_state.vpc_kpa_vrf = value
        self._update_section_status()

    def _find_field_widget(self, field_key: str) -> Optional[ValidatedEntry]:
        """Find the ValidatedEntry widget for the given field key."""
        return self._field_widgets.get(field_key)

    # ------------------------------------------------------------------
    # Task 7.3 & 7.4 — Port assignment panels
    # ------------------------------------------------------------------

    def _build_port_assignments(self) -> None:
        """Create the peer-link and keepalive port assignment panels."""
        # Task 7.3 — Peer-link port assignment
        peer_frame = ctk.CTkFrame(self)
        peer_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            peer_frame,
            text="Peer-Link Port Assignment:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Read-only textbox for default ports
        self._peer_link_textbox = ctk.CTkTextbox(
            peer_frame,
            height=60,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
        )
        self._peer_link_textbox.pack(fill="x", padx=15, pady=(0, 5))

        # Override controls
        peer_override_frame = ctk.CTkFrame(peer_frame, fg_color="transparent")
        peer_override_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._peer_link_override = ctk.CTkSwitch(
            peer_override_frame,
            text="Override",
            command=self._on_peer_link_override_toggle,
        )
        self._peer_link_override.pack(side="left")

        self._peer_link_entry = ctk.CTkEntry(
            peer_override_frame,
            placeholder_text="Ethernet1/53,Ethernet1/54",
            state="disabled",
        )
        self._peer_link_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self._peer_link_entry.bind("<KeyRelease>", lambda e: self._on_peer_link_entry_change())

        # Task 7.4 — Keepalive port assignment (same pattern)
        kpa_frame = ctk.CTkFrame(self)
        kpa_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            kpa_frame,
            text="Keepalive Port Assignment:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Read-only textbox for default ports
        self._keepalive_textbox = ctk.CTkTextbox(
            kpa_frame,
            height=60,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
        )
        self._keepalive_textbox.pack(fill="x", padx=15, pady=(0, 5))

        # Override controls
        kpa_override_frame = ctk.CTkFrame(kpa_frame, fg_color="transparent")
        kpa_override_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._keepalive_override = ctk.CTkSwitch(
            kpa_override_frame,
            text="Override",
            command=self._on_keepalive_override_toggle,
        )
        self._keepalive_override.pack(side="left")

        self._keepalive_entry = ctk.CTkEntry(
            kpa_override_frame,
            placeholder_text="Ethernet1/47,Ethernet1/48",
            state="disabled",
        )
        self._keepalive_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self._keepalive_entry.bind("<KeyRelease>", lambda e: self._on_keepalive_entry_change())

    def _on_peer_link_override_toggle(self) -> None:
        """Handle peer-link override toggle."""
        if self._peer_link_override.get():
            self._peer_link_entry.configure(state="normal")
            # Copy current ports to entry
            ports_text = ", ".join(self._app_state.vpc_peer_link_ports)
            self._peer_link_entry.delete(0, "end")
            self._peer_link_entry.insert(0, ports_text)
        else:
            self._peer_link_entry.configure(state="disabled")
            # Restore default ports
            self._refresh_port_assignments()

        self._app_state.vpc_override_ports = self._peer_link_override.get()
        self._update_section_status()

    def _on_peer_link_entry_change(self) -> None:
        """Handle peer-link entry changes."""
        if self._peer_link_override.get():
            ports_text = self._peer_link_entry.get()
            # Parse comma-separated port names
            ports = [p.strip() for p in ports_text.split(",") if p.strip()]
            self._app_state.vpc_peer_link_ports = ports
            self._update_section_status()

    def _on_keepalive_override_toggle(self) -> None:
        """Handle keepalive override toggle."""
        if self._keepalive_override.get():
            self._keepalive_entry.configure(state="normal")
            # Copy current ports to entry
            ports_text = ", ".join(self._app_state.vpc_keepalive_ports)
            self._keepalive_entry.delete(0, "end")
            self._keepalive_entry.insert(0, ports_text)
        else:
            self._keepalive_entry.configure(state="disabled")
            # Restore default ports
            self._refresh_port_assignments()

        self._app_state.vpc_override_ports = self._keepalive_override.get()
        self._update_section_status()

    def _on_keepalive_entry_change(self) -> None:
        """Handle keepalive entry changes."""
        if self._keepalive_override.get():
            ports_text = self._keepalive_entry.get()
            # Parse comma-separated port names
            ports = [p.strip() for p in ports_text.split(",") if p.strip()]
            self._app_state.vpc_keepalive_ports = ports
            self._update_section_status()

    def _refresh_port_assignments(self) -> None:
        """Update port assignment displays — reads state, does NOT mutate app_state."""
        try:
            vpc_ports = self._hardware_loader.get_vpc_ports(self._app_state.model)

            # Only auto-populate if override is not active
            if not self._peer_link_override.get():
                peer_link_ports = vpc_ports.get("peer_link", [])
                # Update app state only if different (avoid triggering notify)
                if self._app_state.vpc_peer_link_ports != peer_link_ports:
                    self._app_state.vpc_peer_link_ports = peer_link_ports
            else:
                peer_link_ports = self._app_state.vpc_peer_link_ports

            peer_link_text = f"Default ports: {', '.join(peer_link_ports)}" if peer_link_ports else "No default peer-link ports defined for this model"
            self._peer_link_textbox.configure(state="normal")
            self._peer_link_textbox.delete("0.0", "end")
            self._peer_link_textbox.insert("0.0", peer_link_text)
            self._peer_link_textbox.configure(state="disabled")

            if not self._keepalive_override.get():
                keepalive_ports = vpc_ports.get("keepalive", [])
                if self._app_state.vpc_keepalive_ports != keepalive_ports:
                    self._app_state.vpc_keepalive_ports = keepalive_ports
            else:
                keepalive_ports = self._app_state.vpc_keepalive_ports

            keepalive_text = f"Default ports: {', '.join(keepalive_ports)}" if keepalive_ports else "No default keepalive ports defined for this model"
            self._keepalive_textbox.configure(state="normal")
            self._keepalive_textbox.delete("0.0", "end")
            self._keepalive_textbox.insert("0.0", keepalive_text)
            self._keepalive_textbox.configure(state="disabled")

        except Exception as e:
            error_text = f"Error loading vPC ports: {e}"
            for textbox in [self._peer_link_textbox, self._keepalive_textbox]:
                if textbox:
                    textbox.configure(state="normal")
                    textbox.delete("0.0", "end")
                    textbox.insert("0.0", error_text)
                    textbox.configure(state="disabled")

    # ------------------------------------------------------------------
    # Task 7.5 — vPC Intelligence Summary panel
    # ------------------------------------------------------------------

    def _build_intelligence_summary(self) -> None:
        """Create the vPC Intelligence Summary panel."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame,
            text="vPC Intelligence Summary:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Grid layout for summary items
        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # Switch-A Priority
        self._intelligence_labels["switch_a_priority"] = ctk.CTkLabel(
            grid_frame,
            text="Switch-A Priority: 10",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._intelligence_labels["switch_a_priority"].grid(row=0, column=0, sticky="w", pady=2)

        # Switch-B Priority
        self._intelligence_labels["switch_b_priority"] = ctk.CTkLabel(
            grid_frame,
            text="Switch-B Priority: 20",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._intelligence_labels["switch_b_priority"].grid(row=0, column=1, sticky="w", pady=2)

        # System Priority
        self._intelligence_labels["system_priority"] = ctk.CTkLabel(
            grid_frame,
            text="System Priority: 32667",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._intelligence_labels["system_priority"].grid(row=1, column=0, sticky="w", pady=2)

        # Peer-Link Port-Channel
        self._intelligence_labels["peer_link_po"] = ctk.CTkLabel(
            grid_frame,
            text="Peer-Link PO: 1",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._intelligence_labels["peer_link_po"].grid(row=1, column=1, sticky="w", pady=2)

    def _refresh_intelligence_summary(self) -> None:
        """Update the intelligence summary labels."""
        if "peer_link_po" in self._intelligence_labels:
            po_id = self._app_state.vpc_peer_link_id or "1"
            self._intelligence_labels["peer_link_po"].configure(
                text=f"Peer-Link PO: {po_id}"
            )

    # ------------------------------------------------------------------
    # Task 7.6 — Keepalive cross-reference display
    # ------------------------------------------------------------------

    def _build_keepalive_cross_ref(self) -> None:
        """Create the keepalive cross-reference display."""
        self._kpa_cross_ref_frame = ctk.CTkFrame(self)
        self._kpa_cross_ref_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            self._kpa_cross_ref_frame,
            text="Keepalive Cross-Reference:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Container for cross-reference labels (will be populated dynamically)
        self._kpa_labels_frame = ctk.CTkFrame(self._kpa_cross_ref_frame, fg_color="transparent")
        self._kpa_labels_frame.pack(fill="x", padx=15, pady=(0, 15))

    def _refresh_keepalive_cross_ref(self) -> None:
        """Update the keepalive cross-reference display."""
        # Clear existing labels
        for widget in self._kpa_labels_frame.winfo_children():
            widget.destroy()

        # Show cross-reference only when both KPA IPs are non-empty
        if self._app_state.a_kpa_ip.strip() and self._app_state.b_kpa_ip.strip():
            self._kpa_cross_ref_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                self._kpa_labels_frame,
                text=f"Switch-A {self._app_state.a_kpa_ip} → Switch-B (remote)",
                font=ctk.CTkFont(size=12),
                anchor="w",
            ).pack(anchor="w", pady=1)

            ctk.CTkLabel(
                self._kpa_labels_frame,
                text=f"Switch-B {self._app_state.b_kpa_ip} → Switch-A (remote)",
                font=ctk.CTkFont(size=12),
                anchor="w",
            ).pack(anchor="w", pady=1)
        else:
            self._kpa_cross_ref_frame.pack_forget()

    # ------------------------------------------------------------------
    # Task 7.7 — Infrastructure note label
    # ------------------------------------------------------------------

    def _build_infrastructure_note(self) -> None:
        """Create the infrastructure note label."""
        note_frame = ctk.CTkFrame(self, fg_color="transparent")
        note_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            note_frame,
            text="ℹ️  vPC peer-link and keepalive ports are excluded from the Interface Config wizard automatically",
            font=ctk.CTkFont(size=12),
            text_color="#7f8c8d",
            anchor="w",
            wraplength=800,
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # State change handling
    # ------------------------------------------------------------------

    def _on_state_change(self) -> None:
        """Handle AppState changes from other views."""
        self._refresh_port_assignments()
        self._refresh_intelligence_summary()
        self._refresh_keepalive_cross_ref()

    # ------------------------------------------------------------------
    # Task 7.8 — Section status updates
    # ------------------------------------------------------------------

    def _update_section_status(self) -> None:
        """Update the VPC section status based on current validation state."""
        if not self._app_state.vpc_mode:
            self._app_state.section_status["vpc"] = "pending"
        else:
            # Check for validation errors in VPC-related fields
            vpc_fields = {"vpc_domain_id", "vpc_peer_link_id"}
            has_errors = any(
                field in self._app_state.validation_errors 
                for field in vpc_fields
            )
            
            if has_errors:
                self._app_state.section_status["vpc"] = "error"
            else:
                # Check required fields
                required_fields = [
                    self._app_state.vpc_domain_id,
                    self._app_state.a_kpa_ip,
                    self._app_state.b_kpa_ip,
                ]
                
                has_peer_link_ports = bool(self._app_state.vpc_peer_link_ports)
                
                if all(field.strip() for field in required_fields) and has_peer_link_ports:
                    self._app_state.section_status["vpc"] = "ok"
                else:
                    self._app_state.section_status["vpc"] = "pending"
        
        self._app_state.notify()