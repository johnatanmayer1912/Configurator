"""
main_app.py — NX-OS Configuration Authority CTK application shell.

Implements the top-level CustomTkinter window, two-column layout (sidebar +
content area), navigation controller, AppState callback wiring, and the top
header bar.
"""

from __future__ import annotations

import customtkinter as ctk

from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader
from gui.resource_path import resource_path
from gui.widgets.sidebar_button import SidebarButton

# ---------------------------------------------------------------------------
# Section name mapping for the header bar
# ---------------------------------------------------------------------------

_SECTION_NAMES: dict[str, str] = {
    "home": "Home",
    "hardware": "Hardware Setup",
    "vpc": "VPC Configuration",
    "interfaces": "Interface Config",
    "export": "Review & Export",
}

# ---------------------------------------------------------------------------
# Sidebar button definitions: (label, view_name, status_key_or_None)
# ---------------------------------------------------------------------------

_SIDEBAR_BUTTONS: list[tuple[str, str, str | None]] = [
    ("Home",             "home",       None),
    ("Hardware Setup",   "hardware",   "hardware"),
    ("VPC Config",       "vpc",        "vpc"),
    ("Interface Config", "interfaces", "interfaces"),
    ("Review & Export",  "export",     "export"),
]


# ---------------------------------------------------------------------------
# Task 4.1 — NXOSConfigApp
# ---------------------------------------------------------------------------

# Set global CTK options BEFORE any CTk widget is instantiated.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NXOSConfigApp(ctk.CTk):
    """Main application window for the NX-OS Configuration Authority.

    Parameters
    ----------
    app_state:
        Shared application state instance.
    hardware_loader:
        Pre-loaded hardware profile loader.
    """

    def __init__(self, app_state: AppState, hardware_loader: HardwareLoader) -> None:
        super().__init__()

        self._app_state = app_state
        self._hardware_loader = hardware_loader

        # Read version from bundled VERSION file
        try:
            version_path = resource_path("VERSION")
            with open(version_path, "r", encoding="utf-8") as fh:
                version = fh.read().strip()
        except Exception:  # noqa: BLE001
            version = "?.?.?"

        self.title(f"NX-OS Configuration Authority v{version}")
        self._version = version

        # Task 4.1 — window sizing
        self.minsize(1280, 800)
        self.geometry("1400x900")

        # Internal state
        self._views: dict[str, ctk.CTkFrame] = {}
        self._sidebar_buttons: dict[str, SidebarButton] = {}  # keyed by view_name
        self._current_view: str | None = None

        # Build UI
        self._build_layout()

        # Task 4.4 — wire reactive updates
        app_state.register_callback(self._on_state_change)

        # Navigate to default view
        self.show_view("home")

    # ------------------------------------------------------------------
    # Task 4.2 — Two-column layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        """Create the sidebar and content area frames."""

        # Configure root grid: two columns
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Left sidebar ---
        self._sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=("#1a1a2e", "#1a1a2e"),
            corner_radius=0,
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)  # keep fixed width

        # App title label at the top of the sidebar
        title_label = ctk.CTkLabel(
            self._sidebar,
            text="NX-OS Config\nAuthority",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center",
        )
        title_label.pack(pady=(20, 16), padx=10)

        # Separator line
        sep = ctk.CTkFrame(self._sidebar, height=1, fg_color="#2e2e4e")
        sep.pack(fill="x", padx=10, pady=(0, 12))

        # Five navigation SidebarButton instances
        for label, view_name, _status_key in _SIDEBAR_BUTTONS:
            btn = SidebarButton(
                self._sidebar,
                text=label,
                command=lambda vn=view_name: self.show_view(vn),
            )
            btn.pack(fill="x", padx=10, pady=4)
            self._sidebar_buttons[view_name] = btn

        # --- Right content area ---
        self._content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._content_area.grid(row=0, column=1, sticky="nsew")
        self._content_area.grid_rowconfigure(1, weight=1)
        self._content_area.grid_columnconfigure(0, weight=1)

        # Task 4.5 — top header bar
        self._build_header_bar(version=self._version)

        # Container frame where views are packed/unpacked
        self._view_container = ctk.CTkFrame(
            self._content_area,
            corner_radius=0,
            fg_color="transparent",
        )
        self._view_container.grid(row=1, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Task 4.5 — Top header bar
    # ------------------------------------------------------------------

    def _build_header_bar(self, version: str) -> None:
        """Create the header bar with section title (left) and version badge (right)."""

        header = ctk.CTkFrame(
            self._content_area,
            height=48,
            corner_radius=0,
            fg_color=("#16213e", "#16213e"),
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        # Section title label (left)
        self._header_title = ctk.CTkLabel(
            header,
            text="Home",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        self._header_title.grid(row=0, column=0, sticky="w", padx=16, pady=8)

        # Version badge (right)
        version_badge = ctk.CTkLabel(
            header,
            text=f"v{version}",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="e",
        )
        version_badge.grid(row=0, column=1, sticky="e", padx=16, pady=8)

    # ------------------------------------------------------------------
    # Task 4.3 — Navigation controller
    # ------------------------------------------------------------------

    def add_view(self, name: str, frame: ctk.CTkFrame) -> None:
        """Register a view frame under *name*.

        The frame is hidden immediately after registration; call
        :meth:`show_view` to make it visible.

        Parameters
        ----------
        name:
            View identifier (e.g. ``"home"``, ``"hardware"``).
        frame:
            The CTkFrame instance to associate with this view.
        """
        self._views[name] = frame
        # Ensure the frame is placed inside the view container
        frame.place_forget()

    def show_view(self, name: str) -> None:
        """Hide all registered view frames and display the one named *name*.

        Also updates the header title label to reflect the active section.

        Parameters
        ----------
        name:
            View identifier to display.  If the view has not been added via
            :meth:`add_view`, the method is a no-op for the content area but
            still updates the header.
        """
        # Hide all currently visible views
        for view_name, frame in self._views.items():
            frame.pack_forget()

        # Show the requested view
        if name in self._views:
            self._views[name].pack(in_=self._view_container, fill="both", expand=True)

        self._current_view = name

        # Update header title
        section_label = _SECTION_NAMES.get(name, name.replace("_", " ").title())
        self._header_title.configure(text=section_label)

    # ------------------------------------------------------------------
    # Task 4.4 — AppState callback wiring
    # ------------------------------------------------------------------

    def _on_state_change(self) -> None:
        """Called by AppState.notify() — refresh sidebar badges and VPC button state."""

        section_status = self._app_state.section_status

        for view_name, btn in self._sidebar_buttons.items():
            # Find the status key for this button
            status_key = next(
                (sk for lbl, vn, sk in _SIDEBAR_BUTTONS if vn == view_name),
                None,
            )

            if status_key is None:
                # Home button — no status badge needed; keep pending
                continue

            if view_name == "vpc":
                # Special handling: disable VPC button when vpc_mode is False
                if not self._app_state.vpc_mode:
                    btn.set_status("disabled")
                else:
                    # Use section_status if available, else pending
                    status = section_status.get(status_key, "pending")
                    btn.set_status(status)
            else:
                status = section_status.get(status_key, "pending")
                btn.set_status(status)
