"""
gui_main.py — Entry point for the NX-OS Configuration Authority CTK desktop application.

Run this file directly to launch the application:
    python gui_main.py

Or build a standalone executable with:
    python utils/build_ctk_exe.py
"""

import customtkinter as ctk

from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader
from gui.main_app import NXOSConfigApp
from gui.views.home_view import HomeView
from gui.views.hardware_view import HardwareView
from gui.views.vpc_view import VPCView
from gui.views.interface_view import InterfaceView
from gui.views.export_view import ExportView


def main() -> None:
    """Initialise and launch the CTK application."""
    # Set global CTK options before any widget is created
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Shared application state
    app_state = AppState()

    # Hardware profile loader
    hardware_loader = HardwareLoader()
    hardware_loader.load()

    # Create the main application window
    app = NXOSConfigApp(app_state=app_state, hardware_loader=hardware_loader)

    # Read version for views that need it
    try:
        from gui.resource_path import resource_path
        with open(resource_path("VERSION"), "r", encoding="utf-8") as fh:
            version = fh.read().strip()
    except Exception:
        version = "?.?.?"

    # Instantiate all views and register them with the navigation controller
    home_view = HomeView(
        app._view_container,
        app_state=app_state,
        navigate_fn=app.show_view,
        version=version,
    )
    app.add_view("home", home_view)

    hardware_view = HardwareView(
        app._view_container,
        app_state=app_state,
        hardware_loader=hardware_loader,
    )
    app.add_view("hardware", hardware_view)

    vpc_view = VPCView(
        app._view_container,
        app_state=app_state,
        hardware_loader=hardware_loader,
    )
    app.add_view("vpc", vpc_view)

    interface_view = InterfaceView(
        app._view_container,
        app_state=app_state,
        hardware_loader=hardware_loader,
    )
    app.add_view("interfaces", interface_view)

    export_view = ExportView(
        app._view_container,
        app_state=app_state,
    )
    app.add_view("export", export_view)

    # Navigate to the default home view
    app.show_view("home")

    # Start the event loop
    app.mainloop()


if __name__ == "__main__":
    main()
