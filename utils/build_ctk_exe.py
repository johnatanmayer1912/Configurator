"""
build_ctk_exe.py — PyInstaller build script for the NX-OS Configuration Authority CTK app.

Usage:
    python utils/build_ctk_exe.py

Produces:
    dist/NXOSConfigAuthority.exe  (single-file Windows executable)

Requirements:
    pip install pyinstaller
"""

import os
import subprocess
import sys


def build() -> None:
    """Run the PyInstaller command to produce a single-file Windows executable."""

    # Resolve project root (one level up from utils/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    entry_point = os.path.join(project_root, "gui_main.py")

    if not os.path.exists(entry_point):
        print(f"ERROR: Entry point not found: {entry_point}")
        sys.exit(1)

    # Read version for the exe name
    try:
        version_file = os.path.join(project_root, "VERSION")
        with open(version_file, "r") as vf:
            version = vf.read().strip().replace(".", "_")
    except Exception:
        version = "unknown"

    exe_name = f"NXOSConfigAuthority_v{version}"

    # Build the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", exe_name,
        "--collect-all", "customtkinter",
        "--collect-all", "jinja2",
        "--add-data", "templates;templates",
        "--add-data", "hardware_profiles.yaml;.",
        "--add-data", "VERSION;.",
        entry_point,
    ]

    print("=" * 60)
    print("NX-OS Configuration Authority — PyInstaller Build")
    print("=" * 60)
    print(f"Project root : {project_root}")
    print(f"Entry point  : {entry_point}")
    print(f"Exe name     : {exe_name}.exe")
    print(f"Output dir   : {os.path.join(project_root, 'dist')}")
    print()
    print("Running PyInstaller...")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        exe_path = os.path.join(project_root, "dist", f"{exe_name}.exe")
        print()
        print("=" * 60)
        print("BUILD SUCCESSFUL")
        print(f"Executable: {exe_path}")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print(f"BUILD FAILED (exit code {result.returncode})")
        print("Check the output above for errors.")
        print("=" * 60)
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
