"""
PreviewPane — a read-only configuration preview widget.

Contains:
  • A read-only CTkTextbox with Consolas 11pt monospace font.
  • A "Copy to Clipboard" button.
  • A line/character count label.

Syntax highlighting note
------------------------
CustomTkinter's CTkTextbox wraps the standard Tkinter Text widget but does
not expose the tag_configure / tag_add API through its public interface.
However, the underlying Tkinter Text widget is accessible via the
``._textbox`` attribute, which allows us to apply Tkinter text tags for
syntax coloring.  This is an internal implementation detail of CTK 5.x and
may change in future versions.  If the attribute is unavailable the pane
degrades gracefully to plain monospace display.
"""

import re
import customtkinter as ctk
from typing import Optional


# Regex patterns for syntax highlighting (applied in priority order)
_PATTERNS: list[tuple[str, str]] = [
    # NX-OS comment lines starting with !
    ("comment",   r"^!.*$"),
    # Interface declaration lines
    ("interface", r"^interface\s+\S+"),
    # Section headers (lines ending with a colon or all-caps words like "VLAN", "VPC")
    ("header",    r"^[A-Z][A-Z0-9 _-]{2,}$"),
    # IPv4 addresses (with or without prefix length)
    ("ip",        r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b"),
]

# Tag visual styles: (foreground_color, bold)
_TAG_STYLES: dict[str, tuple[str, bool]] = {
    "comment":   ("#95a5a6", False),   # grey
    "interface": ("#ecf0f1", True),    # white bold
    "header":    ("#1abc9c", False),   # cyan
    "ip":        ("#f1c40f", False),   # yellow
}


class PreviewPane(ctk.CTkFrame):
    """
    Read-only configuration preview pane with optional syntax highlighting.

    Parameters
    ----------
    master : widget
        Parent widget.
    **kwargs
        Forwarded to CTkFrame.
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._current_text: str = ""
        self._tags_configured: bool = False

        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=0, pady=(0, 4))

        self._stats_label = ctk.CTkLabel(
            toolbar,
            text="0 lines  |  0 chars",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w",
        )
        self._stats_label.pack(side="left", padx=4)

        self._copy_button = ctk.CTkButton(
            toolbar,
            text="Copy to Clipboard",
            width=140,
            height=28,
            font=ctk.CTkFont(size=12),
            command=self._copy_to_clipboard,
        )
        self._copy_button.pack(side="right", padx=4)

        # ── Text box ─────────────────────────────────────────────────
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none",
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True, padx=0, pady=0)

        # Configure syntax-highlight tags on the underlying Tk Text widget
        self._configure_tags()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_text(self, text: str) -> None:
        """
        Replace the displayed text and refresh syntax highlighting.

        Parameters
        ----------
        text : str
            The full configuration text to display.
        """
        self._current_text = text

        # Enable editing temporarily
        self._textbox.configure(state="normal")
        self._textbox.delete("0.0", "end")
        self._textbox.insert("0.0", text)
        self._textbox.configure(state="disabled")

        # Apply syntax highlighting via the underlying Tk widget
        self._apply_highlighting(text)

        # Update stats
        lines = text.count("\n") + (1 if text else 0)
        chars = len(text)
        self._stats_label.configure(text=f"{lines} lines  |  {chars} chars")

    def get_text(self) -> str:
        """Return the currently displayed text."""
        return self._current_text

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _configure_tags(self) -> None:
        """Configure Tkinter text tags for syntax highlighting."""
        try:
            tk_text = self._textbox._textbox  # internal CTK attribute
        except AttributeError:
            return  # graceful degradation

        import tkinter.font as tkfont

        mono_normal = tkfont.Font(family="Consolas", size=11)
        mono_bold   = tkfont.Font(family="Consolas", size=11, weight="bold")

        for tag, (color, bold) in _TAG_STYLES.items():
            font = mono_bold if bold else mono_normal
            tk_text.tag_configure(tag, foreground=color, font=font)

        self._tags_configured = True

    def _apply_highlighting(self, text: str) -> None:
        """Apply syntax-highlight tags to the Tk Text widget."""
        if not self._tags_configured:
            return

        try:
            tk_text = self._textbox._textbox
        except AttributeError:
            return

        # Remove all existing tags
        for tag in _TAG_STYLES:
            tk_text.tag_remove(tag, "1.0", "end")

        if not text:
            return

        lines = text.split("\n")

        for line_idx, line in enumerate(lines):
            tk_line = line_idx + 1  # Tk lines are 1-indexed

            # Line-level patterns (comment, interface, header) — whole line
            for tag, pattern in _PATTERNS:
                if tag in ("comment", "interface", "header"):
                    if re.match(pattern, line.strip(), re.IGNORECASE):
                        start = f"{tk_line}.0"
                        end   = f"{tk_line}.end"
                        tk_text.tag_add(tag, start, end)
                        break  # only one line-level tag per line

            # Inline pattern: IP addresses (can appear anywhere on a line)
            for match in re.finditer(_PATTERNS[3][1], line):
                start = f"{tk_line}.{match.start()}"
                end   = f"{tk_line}.{match.end()}"
                tk_text.tag_add("ip", start, end)

    def _copy_to_clipboard(self) -> None:
        """Copy the current text to the system clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self._current_text)
        # Brief visual feedback
        self._copy_button.configure(text="Copied ✓")
        self.after(1500, lambda: self._copy_button.configure(text="Copy to Clipboard"))
