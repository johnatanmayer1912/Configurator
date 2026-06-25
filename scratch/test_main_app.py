"""
test_main_app.py — manual verification script for gui/main_app.py

Launches the NXOSConfigApp window with a minimal AppState and HardwareLoader.
Verifies:
- Window opens with correct title and size
- Sidebar displays all five navigation buttons
- Header bar shows section title and version
- Navigation works (clicking buttons changes view)
- AppState callbacks update sidebar badges
- VPC button is disabled when vpc_mode=False
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_app import NXOSConfigApp
from gui.app_state import AppState
from gui.hardware_loader import HardwareLoader


def main():
    """Launch the main app window for manual testing."""
    
    # Initialize dependencies
    app_state = AppState()
    hardware_loader = HardwareLoader()
    hardware_loader.load()
    
    # Create and launch the app
    app = NXOSConfigApp(app_state=app_state, hardware_loader=hardware_loader)
    
    # Add some test views (empty frames) to verify navigation
    import customtkinter as ctk
    
    for view_name in ["home", "hardware", "vpc", "interfaces", "export"]:
        test_frame = ctk.CTkFrame(app._view_container)
        test_label = ctk.CTkLabel(
            test_frame,
            text=f"This is the {view_name.upper()} view\n\n(View implementation pending)",
            font=ctk.CTkFont(size=18),
        )
        test_label.pack(expand=True)
        app.add_view(view_name, test_frame)
    
    # Test AppState callback wiring by updating section status
    def test_status_updates():
        """Cycle through different status values to verify badge updates."""
        import time
        
        # Wait 2 seconds, then update hardware status to "ok"
        app.after(2000, lambda: (
            app_state.section_status.update({"hardware": "ok"}),
            app_state.notify(),
            print("✓ Set hardware status to 'ok'")
        ))
        
        # Wait 4 seconds, then update interfaces status to "error"
        app.after(4000, lambda: (
            app_state.section_status.update({"interfaces": "error"}),
            app_state.notify(),
            print("✓ Set interfaces status to 'error'")
        ))
        
        # Wait 6 seconds, then enable vpc_mode
        app.after(6000, lambda: (
            setattr(app_state, "vpc_mode", True),
            app_state.section_status.update({"vpc": "pending"}),
            app_state.notify(),
            print("✓ Enabled vpc_mode — VPC button should now be enabled")
        ))
        
        # Wait 8 seconds, then set vpc status to "ok"
        app.after(8000, lambda: (
            app_state.section_status.update({"vpc": "ok"}),
            app_state.notify(),
            print("✓ Set vpc status to 'ok'")
        ))
    
    test_status_updates()
    
    print("\n" + "="*70)
    print("NXOSConfigApp Test Launcher")
    print("="*70)
    print("\nManual verification checklist:")
    print("  [1] Window title shows 'NX-OS Configuration Authority v2.0.1'")
    print("  [2] Window minimum size is 1280x800, initial size is 1400x900")
    print("  [3] Sidebar shows 'NX-OS Config Authority' title at top")
    print("  [4] Sidebar shows 5 navigation buttons with badges")
    print("  [5] Header bar shows section title (left) and version (right)")
    print("  [6] Clicking sidebar buttons changes the view and header title")
    print("  [7] VPC Config button starts disabled (dimmed)")
    print("  [8] After 2s: Hardware badge turns green ✓")
    print("  [9] After 4s: Interface Config badge turns red ✗")
    print(" [10] After 6s: VPC Config button becomes enabled")
    print(" [11] After 8s: VPC Config badge turns green ✓")
    print("\nClose the window when done testing.\n")
    
    app.mainloop()


if __name__ == "__main__":
    main()
