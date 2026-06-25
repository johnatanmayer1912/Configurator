"""
AppState — shared in-memory application state for the NX-OS Configuration Authority CTK app.

All GUI views read from and write to a single AppState instance. Views register callbacks
via register_callback(); AppState.notify() broadcasts changes to all registered listeners.
"""

from __future__ import annotations

from typing import Callable, List

from models.device_model import Device, VPCConfig
from models.vlan_model import VLAN
from models.interface_model import Interface
from utils.logger import get_logger

logger = get_logger(__name__)


class AppState:
    """Central application state container.

    Holds all in-memory configuration for the current session. Views register
    callbacks to receive reactive updates whenever state changes.
    """

    # ------------------------------------------------------------------
    # Task 2.1 — core configuration fields
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        # Hardware
        self.model: str = "Nexus 93180YC-EX"
        self.vpc_mode: bool = False

        # Generic model port counts
        self.generic_1g_count: int = 0
        self.generic_10g_count: int = 0
        self.generic_40g_count: int = 0

        # Standalone device identity
        self.hostname: str = ""
        self.mgmt_ip: str = ""
        self.mgmt_gw: str = ""
        self.motd: str = "Authorized Access Only"
        self.admin_user: str = "admin"
        self.admin_password: str = ""

        # vPC Switch-A identity
        self.a_hostname: str = ""
        self.a_mgmt_ip: str = ""
        self.a_mgmt_gw: str = ""
        self.a_kpa_ip: str = ""

        # vPC Switch-B identity
        self.b_hostname: str = ""
        self.b_mgmt_ip: str = ""
        self.b_mgmt_gw: str = ""
        self.b_kpa_ip: str = ""

        # vPC parameters
        self.vpc_domain_id: str = ""
        self.vpc_kpa_vrf: str = "management"
        self.vpc_peer_link_id: str = "1"
        self.vpc_peer_link_ports: List[str] = []
        self.vpc_keepalive_ports: List[str] = []
        self.vpc_override_ports: bool = False

        # Layer-2 / interface configuration
        self.vlans: List[VLAN] = []
        self.interfaces: List[Interface] = []

        # ------------------------------------------------------------------
        # Task 2.2 — validation and section status
        # ------------------------------------------------------------------

        # Keys are field names; values are human-readable error messages.
        self.validation_errors: dict = {}

        # Lifecycle status for each major wizard section.
        self.section_status: dict = {
            "hardware": "pending",
            "vpc": "pending",
            "interfaces": "pending",
            "export": "pending",
        }

        # ------------------------------------------------------------------
        # Task 2.3 — internal callback registry (private)
        # ------------------------------------------------------------------
        self._callbacks: List[Callable] = []
        self._notifying: bool = False  # re-entrancy guard

    # ------------------------------------------------------------------
    # Task 2.3 — reactive callback system
    # ------------------------------------------------------------------

    def register_callback(self, fn: Callable) -> None:
        """Register *fn* to be called whenever :meth:`notify` is invoked.

        The same callable may be registered multiple times; each registration
        results in an additional call during :meth:`notify`.
        """
        self._callbacks.append(fn)

    def notify(self) -> None:
        """Broadcast a state-change event to all registered callbacks.

        Re-entrant calls (notify() called from within a callback) are silently
        dropped to prevent infinite loops. Exceptions raised by individual
        callbacks are caught and logged so that a misbehaving listener cannot
        prevent other listeners from receiving the event.
        """
        if self._notifying:
            return  # prevent infinite recursion
        self._notifying = True
        try:
            for fn in self._callbacks:
                try:
                    fn()
                except Exception as exc:  # noqa: BLE001
                    logger.exception("AppState.notify: callback %r raised an exception: %s", fn, exc)
        finally:
            self._notifying = False

    # ------------------------------------------------------------------
    # Task 2.4 — Device assembly helpers
    # ------------------------------------------------------------------

    def _require(self, field_name: str, value: str) -> None:
        """Raise ``ValueError(field_name)`` when *value* is an empty string."""
        if value == "":
            raise ValueError(field_name)

    def build_device_a(self) -> Device:
        """Assemble and return a :class:`~models.device_model.Device` for Switch-A (or the
        standalone device).

        In **standalone** mode the device is built from the single-device identity
        fields (``hostname``, ``mgmt_ip``, ``mgmt_gw``, ``motd``, ``admin_user``,
        ``admin_password``).

        In **vPC** mode the device is built from the Switch-A identity fields and a
        :class:`~models.device_model.VPCConfig` with ``role="primary"`` is attached.

        Raises
        ------
        ValueError
            With the name of the first empty required field as the exception
            argument.
        """
        if not self.vpc_mode:
            # --- Standalone ---
            self._require("hostname", self.hostname)
            self._require("mgmt_ip", self.mgmt_ip)
            self._require("mgmt_gw", self.mgmt_gw)
            self._require("admin_user", self.admin_user)

            return Device(
                hostname=self.hostname,
                mgmt_ip=self.mgmt_ip,
                mgmt_gw=self.mgmt_gw,
                motd=self.motd,
                admin_user=self.admin_user,
                admin_password=self.admin_password,
                model=self.model,
                vlans=list(self.vlans),
                interfaces=list(self.interfaces),
            )

        # --- vPC mode — Switch-A (primary) ---
        self._require("a_hostname", self.a_hostname)
        self._require("a_mgmt_ip", self.a_mgmt_ip)
        self._require("a_mgmt_gw", self.a_mgmt_gw)
        self._require("a_kpa_ip", self.a_kpa_ip)
        self._require("b_kpa_ip", self.b_kpa_ip)
        self._require("vpc_domain_id", self.vpc_domain_id)
        self._require("vpc_peer_link_id", self.vpc_peer_link_id)

        vpc_cfg = VPCConfig(
            role="primary",
            domain_id=int(self.vpc_domain_id),
            keepalive_vrf=self.vpc_kpa_vrf,
            local_keepalive_ip=self.a_kpa_ip,
            remote_keepalive_ip=self.b_kpa_ip,
            peer_link_id=int(self.vpc_peer_link_id),
            peer_link_interfaces=list(self.vpc_peer_link_ports),
        )

        return Device(
            hostname=self.a_hostname,
            mgmt_ip=self.a_mgmt_ip,
            mgmt_gw=self.a_mgmt_gw,
            motd=self.motd,
            admin_user=self.admin_user,
            admin_password=self.admin_password,
            model=self.model,
            vlans=list(self.vlans),
            interfaces=list(self.interfaces),
            vpc=vpc_cfg,
        )

    def build_device_b(self) -> Device:
        """Assemble and return a :class:`~models.device_model.Device` for Switch-B.

        Only valid when ``vpc_mode`` is ``True``.  The returned device has a
        :class:`~models.device_model.VPCConfig` with ``role="secondary"`` and
        **swapped** keepalive IPs (``local_keepalive_ip=b_kpa_ip``,
        ``remote_keepalive_ip=a_kpa_ip``).

        Raises
        ------
        ValueError("vpc_mode")
            When ``vpc_mode`` is ``False``.
        ValueError
            With the name of the first empty required field as the exception
            argument.
        """
        if not self.vpc_mode:
            raise ValueError("vpc_mode")

        self._require("b_hostname", self.b_hostname)
        self._require("b_mgmt_ip", self.b_mgmt_ip)
        self._require("b_mgmt_gw", self.b_mgmt_gw)
        self._require("b_kpa_ip", self.b_kpa_ip)
        self._require("a_kpa_ip", self.a_kpa_ip)
        self._require("vpc_domain_id", self.vpc_domain_id)
        self._require("vpc_peer_link_id", self.vpc_peer_link_id)

        vpc_cfg = VPCConfig(
            role="secondary",
            domain_id=int(self.vpc_domain_id),
            keepalive_vrf=self.vpc_kpa_vrf,
            local_keepalive_ip=self.b_kpa_ip,
            remote_keepalive_ip=self.a_kpa_ip,  # swapped!
            peer_link_id=int(self.vpc_peer_link_id),
            peer_link_interfaces=list(self.vpc_peer_link_ports),
        )

        return Device(
            hostname=self.b_hostname,
            mgmt_ip=self.b_mgmt_ip,
            mgmt_gw=self.b_mgmt_gw,
            motd=self.motd,
            admin_user=self.admin_user,
            admin_password=self.admin_password,
            model=self.model,
            vlans=list(self.vlans),
            interfaces=list(self.interfaces),
            vpc=vpc_cfg,
        )
