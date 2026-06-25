"""
InterfaceView — Interface Config and VLAN Management section.

Implements tasks 8.1-8.10: port list panel, range selector, per-interface config,
apply/reset buttons, reserved port warnings, VLAN management, and section status.
"""

import re
from typing import Optional, Callable

import customtkinter as ctk

from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader
from gui.widgets.port_badge import PortBadge
from gui.widgets.vlan_table import VLANTable
from models.interface_model import Interface
from models.vlan_model import VLAN
from utils.range_parser import expand_interface_range


# ---------------------------------------------------------------------------
# Task 8.1 — InterfaceView class
# ---------------------------------------------------------------------------

class InterfaceView(ctk.CTkFrame):
    """Interface Config and VLAN Management view.

    Split into left panel (port list + config) and right panel (VLAN management).

    Parameters
    ----------
    master : widget
        Parent widget.
    app_state : AppState
        Shared application state instance.
    hardware_loader : HardwareLoader
        Pre-loaded hardware profile loader.
    **kwargs
        Forwarded to CTkFrame.
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

        # Port list state
        self._port_checkboxes: dict[str, ctk.CTkCheckBox] = {}
        self._port_vars: dict[str, ctk.BooleanVar] = {}
        self._port_rows: dict[str, ctk.CTkFrame] = {}

        # Config panel widgets
        self._config_panel: Optional[ctk.CTkFrame] = None
        self._mode_segmented: Optional[ctk.CTkSegmentedButton] = None
        self._access_vlan_combo: Optional[ctk.CTkComboBox] = None
        self._trunk_vlan_entry: Optional[ctk.CTkEntry] = None
        self._desc_entry: Optional[ctk.CTkEntry] = None
        self._shutdown_switch: Optional[ctk.CTkSwitch] = None
        self._vpc_member_check: Optional[ctk.CTkCheckBox] = None
        self._vpc_id_entry: Optional[ctk.CTkEntry] = None
        self._apply_button: Optional[ctk.CTkButton] = None
        self._reserved_warning: Optional[ctk.CTkLabel] = None

        # VLAN table
        self._vlan_table: Optional[VLANTable] = None
        self._vlan_error_label: Optional[ctk.CTkLabel] = None

        # Port list scroll frame reference
        self._port_list_frame: Optional[ctk.CTkScrollableFrame] = None

        self._build_ui()

        # Track last model/vpc_mode to avoid unnecessary port list rebuilds
        self._last_model: str = app_state.model
        self._last_vpc_mode: bool = app_state.vpc_mode

        # Register callback for reactive updates
        self._app_state.register_callback(self._on_state_change)

    def _build_ui(self) -> None:
        """Build the two-column layout."""
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Left panel — port list + config
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.rowconfigure(2, weight=1)
        left_panel.columnconfigure(0, weight=1)

        # Task 8.3 — Port range selector at top of left panel
        self._build_range_selector(left_panel)

        # Task 8.4 — Per-interface config panel
        self._build_config_panel(left_panel)

        # Task 8.2 — Port list (scrollable)
        self._build_port_list(left_panel)

        # Task 8.5 & 8.6 — Apply / Reset buttons
        self._build_action_buttons(left_panel)

        # Right panel — VLAN management
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Task 8.8 & 8.9 — VLAN management panel
        self._build_vlan_panel(right_panel)

        # Initial port list population
        self._rebuild_port_list()

    # ------------------------------------------------------------------
    # Task 8.3 — Port range selector
    # ------------------------------------------------------------------

    def _build_range_selector(self, parent: ctk.CTkFrame) -> None:
        """Create the port range input and Apply to Range button."""
        range_frame = ctk.CTkFrame(parent, fg_color="transparent")
        range_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        range_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            range_frame,
            text="Interface Config",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self._range_entry = ctk.CTkEntry(
            range_frame,
            placeholder_text="e.g. Eth1/1-24 or Ethernet1/1,Ethernet1/3",
        )
        self._range_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            range_frame,
            text="Apply to Range",
            width=120,
            command=self._on_apply_range,
        ).grid(row=1, column=1)

    def _on_apply_range(self) -> None:
        """Expand the range string and select matching checkboxes."""
        range_str = self._range_entry.get().strip()
        if not range_str:
            return

        try:
            expanded = expand_interface_range(range_str)
        except Exception:
            return

        # Deselect all first, then select matching
        for name, var in self._port_vars.items():
            var.set(name in expanded)

        self._on_selection_change()

    # ------------------------------------------------------------------
    # Task 8.4 — Per-interface config panel
    # ------------------------------------------------------------------

    def _build_config_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the per-interface configuration panel."""
        self._config_panel = ctk.CTkFrame(parent)
        self._config_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self._config_panel.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self._config_panel,
            text="Port Configuration",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Task 8.7 — Reserved port warning
        self._reserved_warning = ctk.CTkLabel(
            self._config_panel,
            text="⚠  This port is reserved for vPC infrastructure",
            text_color="#e67e22",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        # Not packed by default — shown when reserved port selected

        # Mode selector
        mode_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(mode_frame, text="Mode:", anchor="w", width=100).pack(side="left")
        self._mode_segmented = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Access", "Trunk", "Routed"],
            command=self._on_mode_change,
        )
        self._mode_segmented.pack(side="left", fill="x", expand=True)
        self._mode_segmented.set("Access")

        # Access VLAN row
        self._access_vlan_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")
        self._access_vlan_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(self._access_vlan_frame, text="Access VLAN:", anchor="w", width=100).pack(side="left")
        self._access_vlan_combo = ctk.CTkComboBox(
            self._access_vlan_frame,
            values=["(none)"],
            width=150,
        )
        self._access_vlan_combo.pack(side="left")

        # Trunk VLAN row (hidden by default)
        self._trunk_vlan_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")

        ctk.CTkLabel(self._trunk_vlan_frame, text="Trunk VLANs:", anchor="w", width=100).pack(side="left")
        self._trunk_vlan_entry = ctk.CTkEntry(
            self._trunk_vlan_frame,
            placeholder_text="10,20,30-50",
        )
        self._trunk_vlan_entry.pack(side="left", fill="x", expand=True)

        # Description row
        desc_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")
        desc_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(desc_frame, text="Description:", anchor="w", width=100).pack(side="left")
        self._desc_entry = ctk.CTkEntry(desc_frame, placeholder_text="Optional description")
        self._desc_entry.pack(side="left", fill="x", expand=True)

        # Shutdown toggle
        shutdown_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")
        shutdown_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(shutdown_frame, text="Shutdown:", anchor="w", width=100).pack(side="left")
        self._shutdown_switch = ctk.CTkSwitch(shutdown_frame, text="")
        self._shutdown_switch.pack(side="left")
        self._shutdown_switch.select()  # Default: shutdown = True

        # vPC Member row
        vpc_frame = ctk.CTkFrame(self._config_panel, fg_color="transparent")
        vpc_frame.pack(fill="x", padx=10, pady=3)

        self._vpc_member_check = ctk.CTkCheckBox(
            vpc_frame,
            text="vPC Member",
            command=self._on_vpc_member_toggle,
        )
        self._vpc_member_check.pack(side="left")

        self._vpc_id_frame = ctk.CTkFrame(vpc_frame, fg_color="transparent")
        ctk.CTkLabel(self._vpc_id_frame, text="vPC ID:", anchor="w").pack(side="left", padx=(10, 5))
        self._vpc_id_entry = ctk.CTkEntry(self._vpc_id_frame, width=80, placeholder_text="1")
        self._vpc_id_entry.pack(side="left")
        # Hidden by default

        # Bottom padding
        ctk.CTkFrame(self._config_panel, height=5, fg_color="transparent").pack()

    def _on_mode_change(self, mode: str) -> None:
        """Show/hide VLAN fields based on selected mode."""
        if mode == "Access":
            self._access_vlan_frame.pack(fill="x", padx=10, pady=3)
            self._trunk_vlan_frame.pack_forget()
        elif mode == "Trunk":
            self._access_vlan_frame.pack_forget()
            self._trunk_vlan_frame.pack(fill="x", padx=10, pady=3)
        else:  # Routed
            self._access_vlan_frame.pack_forget()
            self._trunk_vlan_frame.pack_forget()

    def _on_vpc_member_toggle(self) -> None:
        """Show/hide vPC ID field based on checkbox state."""
        if self._vpc_member_check.get():
            self._vpc_id_frame.pack(side="left")
        else:
            self._vpc_id_frame.pack_forget()

    # ------------------------------------------------------------------
    # Task 8.2 — Port list panel
    # ------------------------------------------------------------------

    def _build_port_list(self, parent: ctk.CTkFrame) -> None:
        """Create the scrollable port list."""
        self._port_list_frame = ctk.CTkScrollableFrame(
            parent,
            label_text="Available Interfaces",
        )
        self._port_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

    def _rebuild_port_list(self) -> None:
        """Regenerate the port list based on current model and vPC mode."""
        if not self._port_list_frame:
            return

        # Clear existing rows
        for widget in self._port_list_frame.winfo_children():
            widget.destroy()
        self._port_checkboxes.clear()
        self._port_vars.clear()
        self._port_rows.clear()

        # Get reserved ports when in vPC mode
        reserved_ports: set[str] = set()
        if self._app_state.vpc_mode:
            try:
                vpc_ports = self._hardware_loader.get_vpc_ports(self._app_state.model)
                reserved_ports = set(vpc_ports.get("peer_link", []) + vpc_ports.get("keepalive", []))
            except Exception:
                pass

        # Generate interface list from hardware profile
        interfaces = self._generate_interface_list()

        for iface_name in interfaces:
            if iface_name in reserved_ports:
                continue  # Skip reserved ports

            speed = self._get_port_speed(iface_name)

            row = ctk.CTkFrame(self._port_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            var = ctk.BooleanVar(value=False)
            self._port_vars[iface_name] = var

            cb = ctk.CTkCheckBox(
                row,
                text="",
                variable=var,
                width=20,
                command=self._on_selection_change,
            )
            cb.pack(side="left", padx=(5, 2))
            self._port_checkboxes[iface_name] = cb

            # Port speed badge
            badge = PortBadge(row, speed=speed)
            badge.pack(side="left", padx=(0, 5))

            # Interface name label
            ctk.CTkLabel(
                row,
                text=iface_name,
                font=ctk.CTkFont(family="Consolas", size=11),
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

            self._port_rows[iface_name] = row

        # Update status without triggering notify (we're inside a callback)
        if self._app_state.interfaces:
            self._app_state.section_status["interfaces"] = "ok"
        else:
            self._app_state.section_status["interfaces"] = "pending"

    def _generate_interface_list(self) -> list[str]:
        """Generate the list of interface names for the current model."""
        model = self._app_state.model

        if model == "Generic":
            interfaces = []
            for count, speed_prefix in [
                (self._app_state.generic_1g_count, "Ethernet1"),
                (self._app_state.generic_10g_count, "Ethernet2"),
                (self._app_state.generic_40g_count, "Ethernet3"),
            ]:
                for i in range(1, count + 1):
                    interfaces.append(f"{speed_prefix}/{i}")
            return interfaces

        try:
            profile = self._hardware_loader.get_profile(model)
            total = profile.get("total_ports", 0)
            return [f"Ethernet1/{i}" for i in range(1, total + 1)]
        except Exception:
            return []

    def _get_port_speed(self, iface_name: str) -> str:
        """Get the speed string for a given interface name."""
        try:
            # Extract port index from name like "Ethernet1/5"
            match = re.search(r"/(\d+)$", iface_name)
            if match:
                port_index = int(match.group(1))
                return self._hardware_loader.get_port_speed(self._app_state.model, port_index)
        except Exception:
            pass
        return "Unknown"

    def _on_selection_change(self) -> None:
        """Handle checkbox selection changes."""
        selected = [name for name, var in self._port_vars.items() if var.get()]

        # Task 8.7 — Check for reserved ports
        reserved_ports: set[str] = set()
        if self._app_state.vpc_mode:
            try:
                vpc_ports = self._hardware_loader.get_vpc_ports(self._app_state.model)
                reserved_ports = set(vpc_ports.get("peer_link", []) + vpc_ports.get("keepalive", []))
            except Exception:
                pass

        has_reserved = any(p in reserved_ports for p in selected)

        if has_reserved and self._reserved_warning:
            self._reserved_warning.pack(anchor="w", padx=10, pady=(0, 5))
            if self._apply_button:
                self._apply_button.configure(state="disabled")
        else:
            if self._reserved_warning:
                self._reserved_warning.pack_forget()
            if self._apply_button:
                self._apply_button.configure(state="normal")

        # Update access VLAN combo with current VLANs
        self._refresh_vlan_combo()

    def _refresh_vlan_combo(self) -> None:
        """Update the access VLAN combo box with current VLANs."""
        if self._access_vlan_combo:
            vlan_options = ["(none)"] + [
                str(v.id) for v in sorted(self._app_state.vlans, key=lambda v: v.id)
            ]
            self._access_vlan_combo.configure(values=vlan_options)

    # ------------------------------------------------------------------
    # Task 8.5 — Apply to Selected button
    # ------------------------------------------------------------------

    def _build_action_buttons(self, parent: ctk.CTkFrame) -> None:
        """Create Apply to Selected and Reset All Interfaces buttons."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))

        self._apply_button = ctk.CTkButton(
            btn_frame,
            text="Apply to Selected",
            command=self._on_apply_to_selected,
        )
        self._apply_button.pack(side="left", padx=(0, 5))

        # Task 8.6 — Reset All Interfaces button
        ctk.CTkButton(
            btn_frame,
            text="Reset All Interfaces",
            fg_color="#c0392b",
            hover_color="#e74c3c",
            command=self._on_reset_all,
        ).pack(side="left")

    def _on_apply_to_selected(self) -> None:
        """Apply current config panel values to all selected interfaces."""
        selected = [name for name, var in self._port_vars.items() if var.get()]
        if not selected:
            return

        mode = self._mode_segmented.get().lower() if self._mode_segmented else "access"

        # Get VLAN
        vlan_id = None
        if mode == "access" and self._access_vlan_combo:
            vlan_str = self._access_vlan_combo.get()
            if vlan_str and vlan_str != "(none)":
                try:
                    vlan_id = int(vlan_str)
                except ValueError:
                    pass

        # Get trunk VLANs
        trunk_vlans = None
        if mode == "trunk" and self._trunk_vlan_entry:
            trunk_vlans = self._trunk_vlan_entry.get().strip() or None

        # Get description
        description = None
        if self._desc_entry:
            description = self._desc_entry.get().strip() or None

        # Get shutdown state
        shutdown = bool(self._shutdown_switch.get()) if self._shutdown_switch else True

        # Get vPC ID
        vpc_id = None
        if self._vpc_member_check and self._vpc_member_check.get() and self._vpc_id_entry:
            try:
                vpc_id = int(self._vpc_id_entry.get())
            except ValueError:
                pass

        # Update or create Interface objects in app_state
        existing = {iface.name: iface for iface in self._app_state.interfaces}

        for name in selected:
            iface = existing.get(name, Interface(name=name))
            iface.mode = mode
            iface.vlan = vlan_id
            iface.description = description
            iface.shutdown = shutdown
            iface.vpc_id = vpc_id
            # trunk_vlans stored as attribute if present
            if hasattr(iface, 'trunk_vlans'):
                iface.trunk_vlans = trunk_vlans
            existing[name] = iface

        self._app_state.interfaces = list(existing.values())
        self._update_section_status()
        self._app_state.notify()

    def _on_reset_all(self) -> None:
        """Reset all interfaces to default state."""
        self._app_state.interfaces = []

        # Uncheck all checkboxes
        for var in self._port_vars.values():
            var.set(False)

        self._update_section_status()
        self._app_state.notify()

    # ------------------------------------------------------------------
    # Task 8.8 & 8.9 — VLAN management panel
    # ------------------------------------------------------------------

    def _build_vlan_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the VLAN management panel."""
        ctk.CTkLabel(
            parent,
            text="VLAN Management",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        # Add VLAN form
        add_frame = ctk.CTkFrame(parent)
        add_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        add_frame.columnconfigure(0, weight=1)

        # VLAN ID + Name inputs
        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(10, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=2)

        ctk.CTkLabel(input_frame, text="VLAN ID:", anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self._vlan_id_entry = ctk.CTkEntry(input_frame, placeholder_text="10")
        self._vlan_id_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(input_frame, text="VLAN Name:", anchor="w").grid(row=0, column=1, sticky="w", pady=(0, 2))
        self._vlan_name_entry = ctk.CTkEntry(input_frame, placeholder_text="DATA_VLAN")
        self._vlan_name_entry.grid(row=1, column=1, sticky="ew")

        # Error label
        self._vlan_error_label = ctk.CTkLabel(
            add_frame,
            text="",
            text_color="#e74c3c",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._vlan_error_label.pack(anchor="w", padx=10)

        # Buttons
        btn_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            btn_frame,
            text="Add VLAN",
            command=self._on_add_vlan,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Import from File",
            command=self._on_import_vlans,
        ).pack(side="left")

        # VLAN table
        self._vlan_table = VLANTable(
            add_frame,
            on_change=self._on_vlan_table_change,
        )
        self._vlan_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_add_vlan(self) -> None:
        """Handle Add VLAN button click."""
        vlan_id_str = self._vlan_id_entry.get().strip()
        vlan_name = self._vlan_name_entry.get().strip()

        # Validate VLAN ID
        error = self._validate_vlan_id(vlan_id_str)
        if error:
            self._vlan_error_label.configure(text=error)
            return

        vlan_id = int(vlan_id_str)

        # Check for duplicates
        existing_ids = {v.id for v in self._app_state.vlans}
        if vlan_id in existing_ids:
            self._vlan_error_label.configure(text=f"VLAN {vlan_id} already exists")
            return

        # Clear error and add VLAN
        self._vlan_error_label.configure(text="")
        vlan = VLAN(id=vlan_id, name=vlan_name or f"VLAN{vlan_id}")

        self._app_state.vlans.append(vlan)
        self._vlan_table.add_vlan(vlan)

        # Clear inputs
        self._vlan_id_entry.delete(0, "end")
        self._vlan_name_entry.delete(0, "end")

        self._refresh_vlan_combo()
        self._app_state.notify()

    def _validate_vlan_id(self, vlan_id_str: str) -> Optional[str]:
        """Validate a VLAN ID string. Returns error message or None if valid."""
        if not vlan_id_str:
            return "VLAN ID is required"

        try:
            vlan_id = int(vlan_id_str)
        except ValueError:
            return "VLAN ID must be a valid integer"

        if not (1 <= vlan_id <= 4093):
            return f"VLAN ID must be between 1 and 4093 (got {vlan_id})"

        if 3968 <= vlan_id <= 4047:
            return f"VLAN ID {vlan_id} is in the NX-OS reserved range (3968-4047)"

        if vlan_id == 4094:
            return "VLAN ID 4094 is reserved"

        return None

    def _on_import_vlans(self) -> None:
        """Handle Import from File button click."""
        try:
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(
                title="Import VLANs",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            if not filepath:
                return

            imported = 0
            errors = []
            existing_ids = {v.id for v in self._app_state.vlans}

            with open(filepath, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split(None, 1)
                    if not parts:
                        continue

                    vlan_id_str = parts[0]
                    vlan_name = parts[1] if len(parts) > 1 else f"VLAN{parts[0]}"

                    error = self._validate_vlan_id(vlan_id_str)
                    if error:
                        errors.append(f"Line {line_num}: {error}")
                        continue

                    vlan_id = int(vlan_id_str)
                    if vlan_id in existing_ids:
                        continue  # Skip duplicates silently

                    vlan = VLAN(id=vlan_id, name=vlan_name)
                    self._app_state.vlans.append(vlan)
                    self._vlan_table.add_vlan(vlan)
                    existing_ids.add(vlan_id)
                    imported += 1

            msg = f"Imported {imported} VLANs"
            if errors:
                msg += f" ({len(errors)} skipped)"
            self._vlan_error_label.configure(text=msg, text_color="#27ae60")

            self._refresh_vlan_combo()
            self._app_state.notify()

        except Exception as e:
            self._vlan_error_label.configure(
                text=f"Import error: {e}",
                text_color="#e74c3c",
            )

    def _on_vlan_table_change(self) -> None:
        """Handle VLAN table mutations (deletions)."""
        # Sync app_state.vlans with the table
        self._app_state.vlans = self._vlan_table.get_vlans()
        self._refresh_vlan_combo()
        self._app_state.notify()

    # ------------------------------------------------------------------
    # State change handling
    # ------------------------------------------------------------------

    def _on_state_change(self) -> None:
        """Handle AppState changes — only rebuild port list when model or vpc_mode changes."""
        model_changed = self._app_state.model != self._last_model
        vpc_changed = self._app_state.vpc_mode != self._last_vpc_mode

        if model_changed or vpc_changed:
            self._last_model = self._app_state.model
            self._last_vpc_mode = self._app_state.vpc_mode
            self._rebuild_port_list()

        self._refresh_vlan_combo()

    # ------------------------------------------------------------------
    # Task 8.10 — Section status updates
    # ------------------------------------------------------------------

    def _update_section_status(self) -> None:
        """Update the interfaces section status."""
        if self._app_state.interfaces:
            self._app_state.section_status["interfaces"] = "ok"
        else:
            self._app_state.section_status["interfaces"] = "pending"

        self._app_state.notify()
