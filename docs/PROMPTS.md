# NX-OS Configuration Authority — Prompts Reference

This document captures the master feature request and decomposed sub-prompts used to generate each major module. Intended for AI-assisted reconstruction or onboarding new engineers.

---

## Master Feature Request

> Redesign and rebuild the Cisco NX-OS Configuration Authority System as a world-class, production-ready offline desktop application. Replace the existing Tkinter/web-based hybrid with a pure CustomTkinter GUI (dark mode, Modern Windows aesthetic), retaining and elevating all existing backend logic (Jinja2 rendering, model-driven validation, risk analysis, compliance engine, vPC intelligence, and the full build pipeline) while delivering a dramatically superior operator experience.
>
> The application targets Principal Network Automation Engineers and Senior Network Operators who provision Cisco Nexus 9000-series switches (9300/9500 families) in enterprise and data-center environments. It must operate 100% offline — no internet connectivity, no external API calls, no browser dependency.

---

## Sub-Prompts by Module

### hardware_profiles.yaml

> Create a YAML file at the project root defining hardware profiles for Nexus 93180YC-EX, Nexus 9336C-FX2, Nexus 9348GC-FXP, and Generic. Each profile must include: name, total_ports, port_groups (speed/start/end/type), vpc_peer_link list, and vpc_keepalive list. Use the exact port specifications from Requirement 2 of the spec.

### gui/resource_path.py

> Create a resource_path(relative: str) -> str helper that checks sys._MEIPASS first (PyInstaller frozen), then falls back to the project root (one level above gui/). This is used by all modules that load bundled assets.

### gui/hardware_loader.py

> Create a HardwareLoader class that loads hardware_profiles.yaml via resource_path(). Falls back to hardcoded NexusModel constants if the YAML is missing. Exposes: load(), get_profile(name), get_all_names(), get_port_speed(name, port_index), get_vpc_ports(name) returning {"peer_link": [...], "keepalive": [...]}.

### gui/app_state.py

> Create an AppState class holding all in-memory configuration for the CTK application. Fields: model, vpc_mode, generic port counts, standalone device fields (hostname/mgmt_ip/mgmt_gw/motd/admin_user/admin_password), vPC Switch-A fields (a_hostname/a_mgmt_ip/a_mgmt_gw/a_kpa_ip), vPC Switch-B fields, vpc_domain_id, vpc_kpa_vrf, vpc_peer_link_id, vpc_peer_link_ports, vpc_keepalive_ports, vpc_override_ports, vlans list, interfaces list, validation_errors dict, section_status dict.
>
> Implement register_callback(fn) and notify() for reactive updates. Implement build_device_a() and build_device_b() that assemble Device + VPCConfig dataclasses from current state, raising ValueError(field_name) for empty required fields. build_device_b() swaps local/remote keepalive IPs for the secondary role.

### gui/widgets/validated_entry.py

> Create ValidatedEntry(CTkFrame) wrapping a CTkEntry + error CTkLabel. Accepts validator: Callable[[str], tuple[bool, str]], field_key: str, on_change: Callable[[str, bool], None]. On FocusOut: run validator, set border_color="#e74c3c" on fail / default on pass, show/hide error label, call on_change(field_key, is_valid). Expose get() and set(value).

### gui/widgets/sidebar_button.py

> Create SidebarButton(CTkFrame) with a full-width CTkButton and a circular status badge CTkLabel overlaid on the right. set_status(status) accepts "ok" (green ✓), "error" (red ✗), "pending" (grey ○), "disabled" (badge hidden, button non-clickable).

### gui/widgets/port_badge.py

> Create PortBadge(CTkLabel) displaying a port speed string with color-coded background. Priority matching: 100G/40G → blue (#2980b9), 25G/10G → teal (#16a085), 1G → grey (#7f8c8d). Expose set_speed(speed) and get_speed().

### gui/widgets/preview_pane.py

> Create PreviewPane(CTkFrame) with a read-only CTkTextbox (Consolas 11pt). update_text(text) applies syntax highlighting via the underlying Tkinter ._textbox tag API: ! lines → grey, interface lines → white bold, section headers → cyan, IP addresses → yellow. Include a Copy to Clipboard button and a line/char count label. Degrade gracefully if the internal attribute is unavailable.

### gui/widgets/vlan_table.py

> Create VLANTable(CTkScrollableFrame) with add_vlan(vlan), remove_vlan(vlan_id), get_vlans() -> list[VLAN] sorted by ID, and clear(). Each row: VLAN ID label, VLAN Name label, red Delete button. All mutations fire the on_change callback.

### gui/main_app.py

> Create NXOSConfigApp(CTk) with dark mode, blue theme, title "NX-OS Configuration Authority v{version}", minsize 1280x800. Two-column layout: 220px sidebar (dark background) + content area. Sidebar: bold title label + five SidebarButton instances. Navigation: show_view(name) hides all views and packs the selected one. Header bar: section title (left, 16pt bold) + version badge (right). Wire AppState.notify() to update sidebar badges and disable/enable VPC button based on vpc_mode.

### gui/views/home_view.py

> Create HomeView(CTkScrollableFrame) with: app name (24pt bold), version, one-line description; Quick Start panel with five numbered steps and "Go →" navigation buttons; Configuration Status 2×2 grid of status cards; global readiness indicator ("✓ Ready to Generate" green / "⚠ Configuration Incomplete (N issues)" amber). All status elements update via AppState callback.

### gui/views/hardware_view.py

> Create HardwareView(CTkScrollableFrame) with: model selector CTkComboBox from hardware_loader.get_all_names(); vPC Pair Mode CTkSwitch; standalone identity panel (Hostname/CIDR IP/Gateway/MOTD with ValidatedEntry); dual-device panel (Switch-A and Switch-B side-by-side with Hostname/CIDR IP/Gateway/KPA IP); admin credentials (username + masked password); hardware summary read-only CTkTextbox; Generic mode port count fields (shown only for Generic model). _update_section_status() sets section_status["hardware"] to ok/error/pending.

### gui/views/vpc_view.py

> Create VPCView(CTkScrollableFrame) with: domain parameters (Domain ID 1-1000, KPA VRF, Peer-Link PO ID); peer-link port assignment (read-only textbox + Override toggle + editable entry); keepalive port assignment (same pattern); vPC Intelligence Summary grid (Switch-A priority 10, Switch-B priority 20, system priority 32667, PO ID); keepalive cross-reference labels (shown only when both KPA IPs populated); infrastructure note label. _update_section_status() sets section_status["vpc"].

### gui/views/interface_view.py

> Create InterfaceView(CTkFrame) split into left panel (port list + config) and right panel (VLAN management). Left: port range selector with expand_interface_range(); scrollable port list with checkboxes, PortBadge, interface name labels (excludes vPC reserved ports in vPC mode); per-interface config panel (Mode segmented button, Access VLAN combo, Trunk VLAN entry, Description, Shutdown switch, vPC Member checkbox + ID); Apply to Selected and Reset All Interfaces buttons; reserved port warning. Right: VLAN add form with inline validation (reject duplicates, reserved range 3968-4047, 4094, out-of-range); Import from File; VLANTable widget.

### gui/views/export_view.py

> Create ExportView(CTkFrame) with two-column layout. Left: PreviewPane (standalone) or CTkTabview with Switch-A/Switch-B tabs (vPC mode); debounced 500ms refresh via AppState callback calling build_device_a/b() → ConfigRenderer → PreviewPane.update_text(); placeholder on missing fields; catch Jinja2 exceptions. Right: Generate & Export button (disabled when validation_errors non-empty) opening directory picker; Load Checkpoint button; status banner; audit results panel (RiskAnalyzer + ComplianceEngine); configuration history scrollable list with popup viewer.

### templates/nxos_base.j2

> Update the Jinja2 template to: render feature vpc only when device.vpc is not None; render feature hsrp only when device.svis contains HSRP config; add spanning-tree port type edge and storm-control defaults to access-mode interfaces; add no ip redirects and no ip proxy-arp to all SVI interfaces; add explicit no shutdown to mgmt0; add no ip redirects to routed interfaces; render switchport trunk allowed vlan {intf.trunk_vlans} when intf.trunk_vlans is set.

### pipelines/build_pipeline.py

> Update ConfigurationPipeline.execute() to accept an optional output_dir parameter that overrides self.output_dir for that call. Ensure backward compatibility — existing callers with no output_dir argument continue to work unchanged.

### gui_main.py

> Create the application entry point that: sets CTK appearance_mode="dark" and color_theme="blue"; instantiates AppState and HardwareLoader (calling load()); creates NXOSConfigApp; instantiates all five views (HomeView, HardwareView, VPCView, InterfaceView, ExportView) and registers them via app.add_view(); calls show_view("home"); calls app.mainloop(). Guard with if __name__ == "__main__".

### utils/build_ctk_exe.py

> Create a PyInstaller build script that runs: pyinstaller --onefile --windowed --name NXOSConfigAuthority --collect-all customtkinter --collect-all jinja2 --add-data "templates;templates" --add-data "hardware_profiles.yaml;." --add-data "VERSION;." gui_main.py. Print the output executable path on success.
