"""
PortBadge — a compact CTkLabel that displays a port-speed string with a
color-coded background.

Color mapping
-------------
Speed string contains "100G"  → blue  (#2980b9)
Speed string contains "25G"   → teal  (#16a085)
Speed string contains "40G"   → blue  (#2980b9)  (same tier as 100G)
Speed string contains "10G"   → teal  (#16a085)  (same tier as 25G)
Speed string contains "1G"    → grey  (#7f8c8d)
Anything else                 → grey  (#7f8c8d)

The matching is done in priority order so that "40/100G" resolves to blue
and "10/25G" resolves to teal.
"""

import customtkinter as ctk


# Priority-ordered list of (substring_to_match, fg_color)
_SPEED_COLORS: list[tuple[str, str]] = [
    ("100G", "#2980b9"),   # blue  — 100G tier
    ("40G",  "#2980b9"),   # blue  — 40G tier (same visual group)
    ("25G",  "#16a085"),   # teal  — 25G tier
    ("10G",  "#16a085"),   # teal  — 10G tier (same visual group)
    ("1G",   "#7f8c8d"),   # grey  — 1G tier
]

_DEFAULT_COLOR = "#7f8c8d"  # grey fallback


def _resolve_color(speed: str) -> str:
    """Return the badge background color for the given speed string."""
    upper = speed.upper()
    for token, color in _SPEED_COLORS:
        if token in upper:
            return color
    return _DEFAULT_COLOR


class PortBadge(ctk.CTkLabel):
    """
    A small, inline badge label showing a port speed with a color-coded background.

    Parameters
    ----------
    master : widget
        Parent widget.
    speed : str
        Port speed string, e.g. ``"10/25G"``, ``"40/100G"``, ``"1G"``.
    **kwargs
        Forwarded to CTkLabel.  ``fg_color``, ``text_color``, ``corner_radius``,
        ``font``, ``padx``, and ``pady`` are set to sensible defaults if not
        provided.
    """

    def __init__(self, master, speed: str, **kwargs):
        color = _resolve_color(speed)

        kwargs.setdefault("fg_color", color)
        kwargs.setdefault("text_color", "#ffffff")
        kwargs.setdefault("corner_radius", 4)
        kwargs.setdefault("font", ctk.CTkFont(size=10, weight="bold"))
        kwargs.setdefault("padx", 6)
        kwargs.setdefault("pady", 2)

        super().__init__(master, text=speed, **kwargs)

        self._speed = speed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_speed(self, speed: str) -> None:
        """Update the displayed speed and recalculate the badge color."""
        self._speed = speed
        color = _resolve_color(speed)
        self.configure(text=speed, fg_color=color)

    def get_speed(self) -> str:
        """Return the current speed string."""
        return self._speed
