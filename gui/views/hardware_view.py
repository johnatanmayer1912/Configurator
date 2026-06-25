"""
HardwareView — Hardware Setup section for the NX-OS Configuration Authority CTK app.

Implements tasks 6.1-6.9: model selector, vPC mode toggle, device identity panels,
admin credentials, hardware summary, generic port counts, and section status updates.
"""

import re
from typing import Optional

import customtkinter as ctk

from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader
from gui.widgets.validated_entry import ValidatedEntry


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------

def validate_hostname(value: str) -> tuple[bool, str]:
    if not value:
        return False, "Hostname is required"
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*$', value):
        return False, "Invalid hostname — letters, digits, and hyphens only"
    return True, ""


def validate_cidr(value: str) -> tuple[bool, str]:
    if not value:
        return False, "IP address is required"
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$', value):
        return False, "Invalid IP — use CIDR format (e.g., 10.0.0.1/24)"
    return True, ""


def validate_ip(value: str) -> tuple[bool, str]:
    if not value:
        return False, "IP address is required"
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
        return False, "Invalid IP address"
    return True, ""


def validate_integer(value: str) -> tuple[bool, str]:
    if not value:
        return True, ""
    try:
        if int(value) < 0:
            return False, "Must be non-negative"
        return True, ""
    except ValueError:
        return False, "Must be a valid integer"


# ---------------------------------------------------------------------------
# HardwareView
# ---------------------------------------------------------------------------

class HardwareView(ctk.CTkScrollableFrame):
    """Hardware Setup view."""

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

        # Stored widget references — avoids tree-walking
        self._field_widgets: dict[str, ValidatedEntry] = {}

        # UI component references
        self._model_combo: Optional[ctk.CTkComboBox] = None
        self._vpc_switch: Optional[ctk.CTkSwitch] = None
        self._standalone_panel: Optional[ctk.CTkFrame] = None
        self._dual_panel: Optional[ctk.CTkFrame] = None
        self._hardware_summary: Optional[ctk.CTkTextbox] = None
        self._generic_panel: Optional[ctk.CTkFrame] = None

        self._build_ui()

        # Register callback AFTER build so _on_state_change doesn't fire during init
        self._app_state.register_callback(self._on_state_change)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_model_selector()
        self._build_vpc_toggle()
        self._build_identity_panels()
        self._build_admin_credentials()
        self._build_hardware_summary()
        self._build_generic_panel()
        self._refresh_visibility()
        self._refresh_hardware_summary()

    # ------------------------------------------------------------------
    # Model selector
    # ------------------------------------------------------------------

    def _build_model_selector(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame, text="Switch Model:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", pady=(0, 5))

        self._model_combo = ctk.CTkComboBox(
            frame,
            values=self._hardware_loader.get_all_names(),
            command=self._on_model_change,
            width=300,
        )
        self._model_combo.pack(anchor="w")
        self._model_combo.set(self._app_state.model)

    def _on_model_change(self, selected_model: str) -> None:
        self._app_state.model = selected_model
        self._refresh_hardware_summary()
        self._refresh_visibility()
        self._update_section_status()

    # ------------------------------------------------------------------
    # vPC toggle
    # ------------------------------------------------------------------

    def _build_vpc_toggle(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame, text="Deployment Mode:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", pady=(0, 5))

        self._vpc_switch = ctk.CTkSwitch(
            frame, text="vPC Pair Mode", command=self._on_vpc_toggle,
        )
        self._vpc_switch.pack(anchor="w")
        if self._app_state.vpc_mode:
            self._vpc_switch.select()

    def _on_vpc_toggle(self) -> None:
        self._app_state.vpc_mode = bool(self._vpc_switch.get())
        self._refresh_visibility()
        self._update_section_status()

    # ------------------------------------------------------------------
    # Identity panels
    # ------------------------------------------------------------------

    def _build_identity_panels(self) -> None:
        # --- Standalone panel ---
        self._standalone_panel = ctk.CTkFrame(self)
        self._standalone_panel.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            self._standalone_panel, text="Device Identity:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self._field_widgets["hostname"] = self._make_validated_entry(
            self._standalone_panel, "hostname", "Hostname:", "SW-01", validate_hostname,
        )
        self._field_widgets["mgmt_ip"] = self._make_validated_entry(
            self._standalone_panel, "mgmt_ip", "Management IP (CIDR):", "10.0.0.1/24", validate_cidr,
        )
        self._field_widgets["mgmt_gw"] = self._make_validated_entry(
            self._standalone_panel, "mgmt_gw", "Management Gateway:", "10.0.0.254", validate_ip,
        )

        # MOTD — plain entry, no validation
        motd_frame = ctk.CTkFrame(self._standalone_panel, fg_color="transparent")
        motd_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(motd_frame, text="MOTD Banner:", anchor="w").pack(anchor="w", pady=(0, 2))
        motd_entry = ctk.CTkEntry(motd_frame, placeholder_text="Authorized Access Only")
        motd_entry.pack(fill="x")
        motd_entry.insert(0, self._app_state.motd)
        motd_entry.bind("<KeyRelease>", lambda e: self._on_plain_field_change("motd", motd_entry.get()))

        # --- Dual-device panel ---
        self._dual_panel = ctk.CTkFrame(self)
        self._dual_panel.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            self._dual_panel, text="vPC Pair Identity:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        columns_frame = ctk.CTkFrame(self._dual_panel, fg_color="transparent")
        columns_frame.pack(fill="x", padx=15, pady=(0, 15))
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)

        # Switch-A
        sw_a = ctk.CTkFrame(columns_frame)
        sw_a.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(sw_a, text="Switch-A (Primary)", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
        self._field_widgets["a_hostname"] = self._make_validated_entry(sw_a, "a_hostname", "Hostname:", "SW-A", validate_hostname)
        self._field_widgets["a_mgmt_ip"]  = self._make_validated_entry(sw_a, "a_mgmt_ip",  "Management IP:", "10.0.0.1/24", validate_cidr)
        self._field_widgets["a_mgmt_gw"]  = self._make_validated_entry(sw_a, "a_mgmt_gw",  "Management Gateway:", "10.0.0.254", validate_ip)
        self._field_widgets["a_kpa_ip"]   = self._make_validated_entry(sw_a, "a_kpa_ip",   "Keepalive Source IP:", "192.168.1.1", validate_ip, bottom_pad=10)

        # Switch-B
        sw_b = ctk.CTkFrame(columns_frame)
        sw_b.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(sw_b, text="Switch-B (Secondary)", font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
        self._field_widgets["b_hostname"] = self._make_validated_entry(sw_b, "b_hostname", "Hostname:", "SW-B", validate_hostname)
        self._field_widgets["b_mgmt_ip"]  = self._make_validated_entry(sw_b, "b_mgmt_ip",  "Management IP:", "10.0.0.2/24", validate_cidr)
        self._field_widgets["b_mgmt_gw"]  = self._make_validated_entry(sw_b, "b_mgmt_gw",  "Management Gateway:", "10.0.0.254", validate_ip)
        self._field_widgets["b_kpa_ip"]   = self._make_validated_entry(sw_b, "b_kpa_ip",   "Keepalive Source IP:", "192.168.1.2", validate_ip, bottom_pad=10)

    def _make_validated_entry(
        self,
        parent,
        field_key: str,
        label: str,
        placeholder: str,
        validator,
        bottom_pad: int = 5,
    ) -> ValidatedEntry:
        """Create, pack, and return a ValidatedEntry with a label."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=(3, bottom_pad))

        ctk.CTkLabel(container, text=label, anchor="w").pack(anchor="w", pady=(0, 2))

        entry = ValidatedEntry(
            container,
            validator=validator,
            field_key=field_key,
            on_change=self._on_field_change,
            placeholder_text=placeholder,
        )
        entry.pack(fill="x")
        return entry

    def _on_field_change(self, field_key: str, is_valid: bool) -> None:
        """Called by ValidatedEntry on FocusOut after validation."""
        widget = self._field_widgets.get(field_key)
        value = widget.get() if widget else ""

        # Update app state
        setattr(self._app_state, field_key, value)

        # Update validation errors
        if is_valid:
            self._app_state.validation_errors.pop(field_key, None)
        else:
            self._app_state.validation_errors[field_key] = "Invalid"

        self._update_section_status()

    def _on_plain_field_change(self, field_key: str, value: str) -> None:
        """Called by plain CTkEntry fields (no validation)."""
        setattr(self._app_state, field_key, value)

    # ------------------------------------------------------------------
    # Admin credentials
    # ------------------------------------------------------------------

    def _build_admin_credentials(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame, text="Administrator Credentials:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        creds_frame = ctk.CTkFrame(frame, fg_color="transparent")
        creds_frame.pack(fill="x", padx=15, pady=(0, 15))
        creds_frame.columnconfigure(0, weight=1)
        creds_frame.columnconfigure(1, weight=1)

        # Username
        user_frame = ctk.CTkFrame(creds_frame, fg_color="transparent")
        user_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(user_frame, text="Username:", anchor="w").pack(anchor="w", pady=(0, 2))
        user_entry = ctk.CTkEntry(user_frame, placeholder_text="admin")
        user_entry.pack(fill="x")
        user_entry.insert(0, self._app_state.admin_user)
        user_entry.bind("<KeyRelease>", lambda e: self._on_admin_change("admin_user", user_entry.get()))

        # Password
        pass_frame = ctk.CTkFrame(creds_frame, fg_color="transparent")
        pass_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(pass_frame, text="Password:", anchor="w").pack(anchor="w", pady=(0, 2))
        pass_entry = ctk.CTkEntry(pass_frame, show="*", placeholder_text="Enter password")
        pass_entry.pack(fill="x")
        pass_entry.insert(0, self._app_state.admin_password)
        pass_entry.bind("<KeyRelease>", lambda e: self._on_admin_change("admin_password", pass_entry.get()))

    def _on_admin_change(self, field_key: str, value: str) -> None:
        setattr(self._app_state, field_key, value)
        self._update_section_status()

    # ------------------------------------------------------------------
    # Hardware summary
    # ------------------------------------------------------------------

    def _build_hardware_summary(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame, text="Hardware Summary:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self._hardware_summary = ctk.CTkTextbox(
            frame, height=120,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
        )
        self._hardware_summary.pack(fill="x", padx=15, pady=(0, 15))

    def _refresh_hardware_summary(self) -> None:
        if not self._hardware_summary:
            return
        try:
            profile = self._hardware_loader.get_profile(self._app_state.model)
            lines = [
                f"Model: {profile['name']}",
                f"Total Ports: {profile['total_ports']}",
                "",
                "Port Groups:",
            ]
            for g in profile.get("port_groups", []):
                s, e = g.get("start", 0), g.get("end", 0)
                lines.append(f"  Eth1/{s}-{e}  |  {g.get('speed','?')}  |  {g.get('type','?')}  |  {e-s+1} ports")
            if profile.get("vpc_peer_link"):
                lines += ["", f"vPC Peer-Link: {', '.join(profile['vpc_peer_link'])}"]
            if profile.get("vpc_keepalive"):
                lines.append(f"vPC Keepalive: {', '.join(profile['vpc_keepalive'])}")
            text = "\n".join(lines)
        except Exception as ex:
            text = f"Error loading profile: {ex}"

        self._hardware_summary.configure(state="normal")
        self._hardware_summary.delete("0.0", "end")
        self._hardware_summary.insert("0.0", text)
        self._hardware_summary.configure(state="disabled")

    # ------------------------------------------------------------------
    # Generic port counts
    # ------------------------------------------------------------------

    def _build_generic_panel(self) -> None:
        self._generic_panel = ctk.CTkFrame(self)
        self._generic_panel.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            self._generic_panel, text="Generic Port Configuration:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ports_frame = ctk.CTkFrame(self._generic_panel, fg_color="transparent")
        ports_frame.pack(fill="x", padx=15, pady=(0, 15))
        ports_frame.columnconfigure(0, weight=1)
        ports_frame.columnconfigure(1, weight=1)
        ports_frame.columnconfigure(2, weight=1)

        for col, (label, attr, speed) in enumerate([
            ("1G Ports:", "generic_1g_count", "1g"),
            ("10G Ports:", "generic_10g_count", "10g"),
            ("40G Ports:", "generic_40g_count", "40g"),
        ]):
            f = ctk.CTkFrame(ports_frame, fg_color="transparent")
            f.grid(row=0, column=col, sticky="ew", padx=3)
            ctk.CTkLabel(f, text=label, anchor="w").pack(anchor="w", pady=(0, 2))
            e = ctk.CTkEntry(f, placeholder_text="0")
            e.pack(fill="x")
            e.insert(0, str(getattr(self._app_state, attr)))
            e.bind("<KeyRelease>", lambda ev, a=attr, s=speed, entry=e: self._on_generic_change(a, entry.get()))

    def _on_generic_change(self, attr: str, value: str) -> None:
        ok, _ = validate_integer(value)
        if ok and value:
            setattr(self._app_state, attr, int(value))
        self._update_section_status()

    # ------------------------------------------------------------------
    # Visibility management
    # ------------------------------------------------------------------

    def _refresh_visibility(self) -> None:
        """Show/hide panels based on vpc_mode and model — no notify() call."""
        if self._app_state.vpc_mode:
            if self._standalone_panel:
                self._standalone_panel.pack_forget()
            if self._dual_panel:
                self._dual_panel.pack(fill="x", padx=20, pady=10)
        else:
            if self._dual_panel:
                self._dual_panel.pack_forget()
            if self._standalone_panel:
                self._standalone_panel.pack(fill="x", padx=20, pady=10)

        if self._app_state.model == "Generic":
            if self._generic_panel:
                self._generic_panel.pack(fill="x", padx=20, pady=10)
        else:
            if self._generic_panel:
                self._generic_panel.pack_forget()

    def _on_state_change(self) -> None:
        """Callback from AppState.notify() — sync UI to state (no notify() call here)."""
        self._refresh_visibility()
        if self._model_combo:
            self._model_combo.set(self._app_state.model)
        if self._vpc_switch:
            if self._app_state.vpc_mode:
                self._vpc_switch.select()
            else:
                self._vpc_switch.deselect()

    # ------------------------------------------------------------------
    # Section status — NEVER calls notify() directly
    # ------------------------------------------------------------------

    def _update_section_status(self) -> None:
        """Compute and set section_status["hardware"], then call notify() once."""
        hardware_fields = {
            "hostname", "mgmt_ip", "mgmt_gw",
            "a_hostname", "a_mgmt_ip", "a_mgmt_gw", "a_kpa_ip",
            "b_hostname", "b_mgmt_ip", "b_mgmt_gw", "b_kpa_ip",
        }

        has_errors = any(f in self._app_state.validation_errors for f in hardware_fields)

        if has_errors:
            self._app_state.section_status["hardware"] = "error"
        else:
            if self._app_state.vpc_mode:
                required = [
                    self._app_state.a_hostname, self._app_state.a_mgmt_ip,
                    self._app_state.a_mgmt_gw, self._app_state.b_hostname,
                    self._app_state.b_mgmt_ip, self._app_state.b_mgmt_gw,
                    self._app_state.admin_user,
                ]
            else:
                required = [
                    self._app_state.hostname, self._app_state.mgmt_ip,
                    self._app_state.mgmt_gw, self._app_state.admin_user,
                ]

            if all(f.strip() for f in required):
                self._app_state.section_status["hardware"] = "ok"
            else:
                self._app_state.section_status["hardware"] = "pending"

        # Single notify() call — re-entrancy guard in AppState prevents loops
        self._app_state.notify()
