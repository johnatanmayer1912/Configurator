"""
ValidatedEntry — a CTkFrame wrapping a CTkEntry with inline validation feedback.

Accepts a validator callable that returns (is_valid: bool, error_message: str).
On FocusOut, runs the validator, updates border color, shows/hides the error
label, and fires the on_change callback.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ValidatedEntry(ctk.CTkFrame):
    """
    A labeled entry widget with inline validation feedback.

    Parameters
    ----------
    master : widget
        Parent widget.
    validator : Callable[[str], tuple[bool, str]]
        Called with the current entry value; returns (is_valid, error_message).
    field_key : str
        Identifier passed to the on_change callback so callers know which field changed.
    on_change : Callable[[str, bool], None]
        Called after each validation with (field_key, is_valid).
    placeholder_text : str, optional
        Placeholder shown inside the CTkEntry when empty.
    label_text : str, optional
        Optional label rendered above the entry.
    **kwargs
        Forwarded to the CTkFrame constructor.
    """

    # Default border color used by CTkEntry (matches the blue theme default)
    _DEFAULT_BORDER_COLOR = ("gray65", "gray30")
    _ERROR_BORDER_COLOR = "#e74c3c"

    def __init__(
        self,
        master,
        validator: Callable[[str], tuple[bool, str]],
        field_key: str,
        on_change: Callable[[str, bool], None],
        placeholder_text: str = "",
        label_text: Optional[str] = None,
        **kwargs,
    ):
        # Remove fg_color default so the frame blends with its parent
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._validator = validator
        self._field_key = field_key
        self._on_change = on_change
        self._is_valid: bool = True

        # Optional label above the entry
        if label_text:
            self._label = ctk.CTkLabel(self, text=label_text, anchor="w")
            self._label.pack(fill="x", padx=2, pady=(0, 2))

        # The actual entry widget
        self._entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
        )
        self._entry.pack(fill="x", padx=0, pady=0)
        self._entry.bind("<FocusOut>", self._on_focus_out)

        # Error label — hidden by default
        self._error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#e74c3c",
            font=ctk.CTkFont(size=11),
            anchor="w",
            wraplength=300,
        )
        # Not packed yet; shown only on validation failure

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self) -> str:
        """Return the current entry value."""
        return self._entry.get()

    def set(self, value: str) -> None:
        """Set the entry value programmatically and re-validate."""
        self._entry.delete(0, "end")
        self._entry.insert(0, value)
        self._validate(value)

    def is_valid(self) -> bool:
        """Return the last validation result."""
        return self._is_valid

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_focus_out(self, event=None) -> None:
        """Triggered when the entry loses focus."""
        self._validate(self._entry.get())

    def _validate(self, value: str) -> None:
        """Run the validator and update visual state + callback."""
        valid, message = self._validator(value)
        self._is_valid = valid

        if valid:
            self._entry.configure(border_color=self._DEFAULT_BORDER_COLOR)
            self._hide_error()
        else:
            self._entry.configure(border_color=self._ERROR_BORDER_COLOR)
            self._show_error(message)

        self._on_change(self._field_key, valid)

    def _show_error(self, message: str) -> None:
        self._error_label.configure(text=message)
        self._error_label.pack(fill="x", padx=2, pady=(2, 0))

    def _hide_error(self) -> None:
        self._error_label.configure(text="")
        self._error_label.pack_forget()
