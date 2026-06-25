"""
SidebarButton — a CTkFrame containing a full-width CTkButton and a small
status badge CTkLabel positioned to the right of the button text.

Status values
-------------
"ok"       → green  ✓
"error"    → red    ✗
"pending"  → grey   ○
"disabled" → dimmed text, button non-clickable
"""

import customtkinter as ctk
from typing import Callable, Optional


# Badge configuration: (symbol, fg_color, text_color)
_STATUS_CONFIG: dict[str, tuple[str, str, str]] = {
    "ok":       ("✓", "#27ae60", "#ffffff"),
    "error":    ("✗", "#e74c3c", "#ffffff"),
    "pending":  ("○", "#7f8c8d", "#ffffff"),
    "disabled": ("",  "#4a4a4a", "#888888"),
}

_VALID_STATUSES = frozenset(_STATUS_CONFIG.keys())


class SidebarButton(ctk.CTkFrame):
    """
    Navigation button for the application sidebar.

    The button spans the full width of the frame.  A compact badge label
    is overlaid on the right side of the button to show section status.

    Parameters
    ----------
    master : widget
        Parent widget.
    text : str
        Button label text.
    command : Callable
        Called when the button is clicked (ignored when status is "disabled").
    **kwargs
        Forwarded to the CTkFrame constructor.
    """

    def __init__(
        self,
        master,
        text: str,
        command: Callable,
        **kwargs,
    ):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._command = command
        self._current_status: str = "pending"

        # Main navigation button — fills the frame
        self._button = ctk.CTkButton(
            self,
            text=text,
            anchor="w",
            command=self._on_click,
            font=ctk.CTkFont(size=13),
            corner_radius=6,
        )
        self._button.pack(fill="x", expand=True, padx=0, pady=0)

        # Status badge — placed on top of the button, right-aligned
        self._badge = ctk.CTkLabel(
            self._button,
            text="○",
            width=22,
            height=22,
            corner_radius=11,
            fg_color="#7f8c8d",
            text_color="#ffffff",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self._badge.place(relx=1.0, rely=0.5, anchor="e", x=-8)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_status(self, status: str) -> None:
        """
        Update the badge and button state.

        Parameters
        ----------
        status : str
            One of "ok", "error", "pending", "disabled".

        Raises
        ------
        ValueError
            If an unrecognised status string is provided.
        """
        if status not in _VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {sorted(_VALID_STATUSES)}"
            )

        self._current_status = status
        symbol, fg_color, text_color = _STATUS_CONFIG[status]

        if status == "disabled":
            # Hide badge, dim button, disable interaction
            self._badge.place_forget()
            self._button.configure(state="disabled", text_color_disabled="#888888")
        else:
            # Re-show badge in case it was hidden
            self._badge.place(relx=1.0, rely=0.5, anchor="e", x=-8)
            self._badge.configure(
                text=symbol,
                fg_color=fg_color,
                text_color=text_color,
            )
            self._button.configure(state="normal")

    def get_status(self) -> str:
        """Return the current status string."""
        return self._current_status

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_click(self) -> None:
        """Invoke the command only when not disabled."""
        if self._current_status != "disabled":
            self._command()
