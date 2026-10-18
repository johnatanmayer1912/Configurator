"""
HomeView — landing page for the NX-OS Configuration Authority CTK application.

Displays the application title, version, and description (Task 5.1), a Quick Start
workflow steps panel with navigation buttons (Task 5.2), a section status summary
grid (Task 5.3), and a global readiness indicator (Task 5.4).
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from gui.app_state import AppState


# ---------------------------------------------------------------------------
# Status badge colour map — mirrors the SidebarButton convention
# ---------------------------------------------------------------------------
_STATUS_COLORS: dict[str, tuple[str, str]] = {
    "ok":      ("#27ae60", "#ffffff"),   # green
    "error":   ("#e74c3c", "#ffffff"),   # red
    "pending": ("#7f8c8d", "#ffffff"),   # grey
}

# ---------------------------------------------------------------------------
# Quick Start step definitions
# (step_number, display_name, view_name)
# ---------------------------------------------------------------------------
_QUICK_START_STEPS: list[tuple[int, str, str]] = [
    (1, "Hardware Setup",     "hardware"),
    (2, "VPC Config",         "vpc"),
    (3, "Interface Config",   "interfaces"),
    (4, "VLAN Management",    "interfaces"),
    (5, "Review & Export",    "export"),
]

# Status card definitions — (display_label, section_status_key)
_STATUS_CARDS: list[tuple[str, str]] = [
    ("Hardware",    "hardware"),
    ("VPC",         "vpc"),
    ("Interfaces",  "interfaces"),
    ("Export",      "export"),
]


class HomeView(ctk.CTkScrollableFrame):
    """Landing / home view for the NX-OS Configuration Authority application.

    Parameters
    ----------
    master:
        Parent widget.
    app_state:
        Shared application state instance.
    navigate_fn:
        Callable that accepts a view name string and navigates to that view.
    version:
        Version string displayed in the header.  Falls back to an empty string
        when not provided.
    **kwargs:
        Forwarded to ``CTkScrollableFrame``.
    """

    def __init__(
        self,
        master,
        app_state: AppState,
        navigate_fn: Callable[[str], None],
        version: str = "",
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._app_state = app_state
        self._navigate_fn = navigate_fn
        self._version = version

        # Internal references updated during refresh
        self._badge_labels: dict[str, ctk.CTkLabel] = {}
        self._readiness_label: ctk.CTkLabel | None = None

        self._build_header()
        self._build_quick_start()
        self._build_status_summary()
        self._build_readiness_indicator()

        # Register reactive callback so status cards and readiness indicator
        # update whenever any part of AppState changes.
        self._app_state.register_callback(self._refresh_status)

    # ------------------------------------------------------------------
    # Task 5.1 — Header: app name, version, description
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        """Render the application name, version badge, and one-line description."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(24, 8))

        # App name — 24pt bold
        ctk.CTkLabel(
            header_frame,
            text="NX-OS Configuration Authority",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        ).pack(anchor="w")

        # Version string (shown only when non-empty)
        if self._version:
            ctk.CTkLabel(
                header_frame,
                text=f"v{self._version}",
                font=ctk.CTkFont(size=13),
                text_color="#7f8c8d",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        # One-line description
        ctk.CTkLabel(
            header_frame,
            text=(
                "Model-driven NX-OS configuration generator for "
                "Cisco Nexus 9000-series switches"
            ),
            font=ctk.CTkFont(size=13),
            text_color="#bdc3c7",
            anchor="w",
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        # Multi-switch web UI parity note (P2 UX)
        ctk.CTkLabel(
            header_frame,
            text=(
                "For multi-switch fabric deployments (vPC pairs, spine-leaf, custom uplinks), "
                "use the web console: run web_launcher.py and open http://127.0.0.1:9000 "
                "— the desktop wizard covers single-switch and vPC pair workflows only."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#f39c12",
            anchor="w",
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(10, 0))

        # Horizontal divider
        ctk.CTkFrame(self, height=1, fg_color="#3a3a3a").pack(
            fill="x", padx=24, pady=(12, 0)
        )

    # ------------------------------------------------------------------
    # Task 5.2 — Quick Start workflow steps panel
    # ------------------------------------------------------------------

    def _build_quick_start(self) -> None:
        """Render the Quick Start section with five numbered workflow steps."""
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=24, pady=(20, 8))

        # Section heading — 16pt bold
        ctk.CTkLabel(
            section_frame,
            text="Quick Start",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        # Container card for the step rows
        steps_card = ctk.CTkFrame(section_frame, corner_radius=8)
        steps_card.pack(fill="x")

        for idx, (step_num, step_name, view_name) in enumerate(_QUICK_START_STEPS):
            self._build_step_row(steps_card, step_num, step_name, view_name, idx)

    def _build_step_row(
        self,
        parent: ctk.CTkFrame,
        step_num: int,
        step_name: str,
        view_name: str,
        row_index: int,
    ) -> None:
        """Render a single Quick Start step row inside *parent*."""
        # Alternate row background for readability
        row_bg = "#2b2b2b" if row_index % 2 == 0 else "#323232"

        row = ctk.CTkFrame(parent, fg_color=row_bg, corner_radius=0)
        row.pack(fill="x")
        row.columnconfigure(1, weight=1)

        # Step number badge
        ctk.CTkLabel(
            row,
            text=str(step_num),
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#2980b9",
            text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(14, 10), pady=10)

        # Step name label
        label_text = step_name
        if step_num == 2:
            label_text = f"{step_name} (optional)"
        ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)

        # "Go →" navigation button — captures view_name via default arg
        ctk.CTkButton(
            row,
            text="Go →",
            width=72,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            command=lambda vn=view_name: self._navigate_fn(vn),
        ).grid(row=0, column=2, padx=(0, 14), pady=10)

    # ------------------------------------------------------------------
    # Task 5.3 — Section status summary (2×2 grid of status cards)
    # ------------------------------------------------------------------

    def _build_status_summary(self) -> None:
        """Render the Configuration Status section with four status cards."""
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=24, pady=(20, 8))

        # Section heading — 16pt bold
        ctk.CTkLabel(
            section_frame,
            text="Configuration Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        # 2×2 grid container
        grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for i, (display_name, status_key) in enumerate(_STATUS_CARDS):
            row = i // 2
            col = i % 2
            card = self._build_status_card(grid_frame, display_name, status_key)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

    def _build_status_card(
        self,
        parent,
        display_name: str,
        status_key: str,
    ) -> ctk.CTkFrame:
        """Create and return a single status card frame.

        The badge label reference is stored in ``self._badge_labels`` so it can
        be updated by :meth:`_refresh_status`.
        """
        card = ctk.CTkFrame(parent, corner_radius=8)

        # Section name
        ctk.CTkLabel(
            card,
            text=display_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(12, 4))

        # Determine initial status
        initial_status = self._app_state.section_status.get(status_key, "pending")
        fg_color, text_color = _STATUS_COLORS.get(
            initial_status, _STATUS_COLORS["pending"]
        )
        badge_text = self._status_badge_text(initial_status)

        badge = ctk.CTkLabel(
            card,
            text=badge_text,
            font=ctk.CTkFont(size=12),
            fg_color=fg_color,
            text_color=text_color,
            corner_radius=6,
            padx=8,
            pady=3,
        )
        badge.pack(anchor="w", padx=14, pady=(0, 12))

        # Store reference for later updates
        self._badge_labels[status_key] = badge

        return card

    # ------------------------------------------------------------------
    # Task 5.4 — Global readiness indicator
    # ------------------------------------------------------------------

    def _build_readiness_indicator(self) -> None:
        """Render the global readiness indicator label."""
        indicator_frame = ctk.CTkFrame(self, fg_color="transparent")
        indicator_frame.pack(fill="x", padx=24, pady=(16, 24))

        text, color = self._readiness_text_and_color()

        self._readiness_label = ctk.CTkLabel(
            indicator_frame,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color,
            anchor="w",
        )
        self._readiness_label.pack(anchor="w")

    # ------------------------------------------------------------------
    # Reactive refresh — called on every AppState.notify()
    # ------------------------------------------------------------------

    def _refresh_status(self) -> None:
        """Update all status badge labels and the readiness indicator."""
        # Refresh each status card badge
        for status_key, badge_label in self._badge_labels.items():
            current_status = self._app_state.section_status.get(status_key, "pending")
            fg_color, text_color = _STATUS_COLORS.get(
                current_status, _STATUS_COLORS["pending"]
            )
            badge_text = self._status_badge_text(current_status)
            badge_label.configure(
                text=badge_text,
                fg_color=fg_color,
                text_color=text_color,
            )

        # Refresh readiness indicator
        if self._readiness_label is not None:
            text, color = self._readiness_text_and_color()
            self._readiness_label.configure(text=text, text_color=color)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _status_badge_text(status: str) -> str:
        """Return a human-readable badge string for the given status value."""
        return {
            "ok":      "✓  OK",
            "error":   "✗  Error",
            "pending": "○  Pending",
        }.get(status, "○  Pending")

    def _readiness_text_and_color(self) -> tuple[str, str]:
        """Compute the readiness label text and colour from current AppState.

        Returns
        -------
        tuple[str, str]
            ``(label_text, hex_colour)``
        """
        statuses = self._app_state.section_status
        issues = sum(1 for v in statuses.values() if v != "ok")

        if issues == 0:
            return "✓  Ready to Generate", "#27ae60"   # green

        return f"⚠  Configuration Incomplete ({issues} issue{'s' if issues != 1 else ''})", "#e67e22"  # amber
