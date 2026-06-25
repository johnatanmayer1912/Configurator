"""
resource_path.py — Asset path resolver for bundled and development environments.

Provides a single helper function that resolves paths to bundled assets correctly
whether the application is running as a PyInstaller frozen executable or directly
from source. All modules that load bundled assets (images, templates, YAML profiles,
etc.) should use this helper instead of constructing paths manually.
"""

import os
import sys


def resource_path(relative: str) -> str:
    """Return the absolute path to a bundled asset.

    When running as a PyInstaller frozen executable, assets are extracted to a
    temporary directory stored in ``sys._MEIPASS``.  When running from source,
    assets live under the project root (one level above the ``gui/`` package).

    Args:
        relative: Path to the asset relative to the project root, e.g.
                  ``"hardware_profiles.yaml"`` or ``"templates/nxos_base.j2"``.

    Returns:
        Absolute path string suitable for use with ``open()``, ``os.path``, etc.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running inside a PyInstaller bundle — assets are in the temp extraction dir
        return os.path.join(sys._MEIPASS, relative)

    # Running from source — resolve relative to the project root (parent of gui/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative)
