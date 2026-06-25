"""
VLANTable — a scrollable table widget for displaying and managing VLAN entries.

Each row shows:
  • VLAN ID label
  • VLAN Name label
  • Delete button

Mutations (add / remove) emit the ``on_change`` callback so parent views can
react (e.g., update AppState and call notify()).
"""

import customtkinter as ctk
from typing import Callable, Optional
from models.vlan_model import VLAN


class VLANTable(ctk.CTkScrollableFrame):
    """
    Scrollable VLAN management table.

    Parameters
    ----------
    master : widget
        Parent widget.
    on_change : Callable, optional
        Called with no arguments after any add or remove operation.
    **kwargs
        Forwarded to CTkScrollableFrame.
    """

    # Column widths (pixels)
    _COL_ID   = 70
    _COL_NAME = 200
    _COL_DEL  = 70

    def __init__(
        self,
        master,
        on_change: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        kwargs.setdefault("label_text", "")
        super().__init__(master, **kwargs)

        self._on_change = on_change or (lambda: None)
        self._vlans: dict[int, VLAN] = {}          # vlan_id → VLAN
        self._rows:  dict[int, list] = {}           # vlan_id → [id_lbl, name_lbl, del_btn]

        # ── Header row ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=(0, 2))

        ctk.CTkLabel(
            header,
            text="VLAN ID",
            width=self._COL_ID,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            header,
            text="Name",
            width=self._COL_NAME,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            header,
            text="",
            width=self._COL_DEL,
        ).pack(side="left")

        # Separator
        ctk.CTkFrame(self, height=1, fg_color=("gray70", "gray30")).pack(
            fill="x", padx=4, pady=(0, 4)
        )

        # Container for data rows
        self._rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._rows_frame.pack(fill="both", expand=True, padx=4)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_vlan(self, vlan: VLAN) -> None:
        """
        Add a VLAN entry to the table.

        If a VLAN with the same ID already exists it is silently replaced.

        Parameters
        ----------
        vlan : VLAN
            The VLAN dataclass instance to add.
        """
        # Remove existing row for this ID if present
        if vlan.id in self._vlans:
            self._destroy_row(vlan.id)

        self._vlans[vlan.id] = vlan
        self._build_row(vlan)
        self._on_change()

    def remove_vlan(self, vlan_id: int) -> None:
        """
        Remove the VLAN with the given ID from the table.

        No-op if the ID is not present.

        Parameters
        ----------
        vlan_id : int
            The VLAN ID to remove.
        """
        if vlan_id not in self._vlans:
            return
        self._destroy_row(vlan_id)
        del self._vlans[vlan_id]
        self._on_change()

    def get_vlans(self) -> list[VLAN]:
        """
        Return the current VLAN list sorted by VLAN ID.

        Returns
        -------
        list[VLAN]
        """
        return sorted(self._vlans.values(), key=lambda v: v.id)

    def clear(self) -> None:
        """Remove all VLAN rows from the table."""
        for vlan_id in list(self._vlans.keys()):
            self._destroy_row(vlan_id)
        self._vlans.clear()
        self._on_change()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_row(self, vlan: VLAN) -> None:
        """Create and pack a row frame for the given VLAN."""
        row_frame = ctk.CTkFrame(self._rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)

        id_label = ctk.CTkLabel(
            row_frame,
            text=str(vlan.id),
            width=self._COL_ID,
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        id_label.pack(side="left", padx=(0, 8))

        name_label = ctk.CTkLabel(
            row_frame,
            text=vlan.name,
            width=self._COL_NAME,
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        name_label.pack(side="left", padx=(0, 8))

        # Capture vlan.id in the closure
        vlan_id = vlan.id
        del_button = ctk.CTkButton(
            row_frame,
            text="Delete",
            width=self._COL_DEL,
            height=24,
            fg_color="#c0392b",
            hover_color="#e74c3c",
            font=ctk.CTkFont(size=11),
            command=lambda vid=vlan_id: self.remove_vlan(vid),
        )
        del_button.pack(side="left")

        self._rows[vlan.id] = [row_frame, id_label, name_label, del_button]

    def _destroy_row(self, vlan_id: int) -> None:
        """Destroy the widgets for the given VLAN ID row."""
        if vlan_id not in self._rows:
            return
        row_frame = self._rows[vlan_id][0]
        row_frame.destroy()
        del self._rows[vlan_id]
