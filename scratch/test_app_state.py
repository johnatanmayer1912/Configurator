"""
Unit tests for AppState — Task 2.5 of the NX-OS Configurator CTK Redesign spec.

Covers:
  - notify() fires all registered callbacks
  - notify() isolates exceptions from misbehaving callbacks
  - build_device_a() standalone mode
  - build_device_a() raises ValueError on missing required field
  - build_device_a() vPC mode (primary role, correct keepalive IPs)
  - build_device_b() vPC mode (secondary role, swapped keepalive IPs)
  - build_device_b() raises ValueError("vpc_mode") when vpc_mode is False
"""

import unittest

from gui.app_state import AppState


def _vpc_state() -> AppState:
    """Return an AppState pre-populated with valid vPC fields."""
    state = AppState()
    state.vpc_mode = True
    state.a_hostname = "SW-A"
    state.a_mgmt_ip = "10.0.0.1"
    state.a_mgmt_gw = "10.0.0.254"
    state.a_kpa_ip = "192.168.1.1"
    state.b_hostname = "SW-B"
    state.b_mgmt_ip = "10.0.0.2"
    state.b_mgmt_gw = "10.0.0.254"
    state.b_kpa_ip = "192.168.1.2"
    state.vpc_domain_id = "10"
    state.vpc_peer_link_id = "1"
    return state


class TestNotify(unittest.TestCase):

    def test_notify_fires_callbacks(self):
        """register two callbacks, call notify(), verify both were called."""
        state = AppState()
        calls = []
        state.register_callback(lambda: calls.append("first"))
        state.register_callback(lambda: calls.append("second"))
        state.notify()
        self.assertEqual(calls, ["first", "second"])

    def test_notify_isolates_exceptions(self):
        """A raising callback must not prevent subsequent callbacks from firing."""
        state = AppState()
        calls = []

        def bad_cb():
            raise RuntimeError("boom")

        state.register_callback(bad_cb)
        state.register_callback(lambda: calls.append("ok"))

        # Should not raise
        try:
            state.notify()
        except Exception as exc:
            self.fail(f"notify() propagated an exception: {exc}")

        self.assertEqual(calls, ["ok"])


class TestBuildDeviceA(unittest.TestCase):

    def test_build_device_a_standalone(self):
        """Standalone mode returns Device with correct fields and vpc=None."""
        state = AppState()
        state.hostname = "STANDALONE-SW"
        state.mgmt_ip = "10.1.1.1"
        state.mgmt_gw = "10.1.1.254"
        state.model = "Nexus 93180YC-EX"

        device = state.build_device_a()

        self.assertEqual(device.hostname, "STANDALONE-SW")
        self.assertEqual(device.mgmt_ip, "10.1.1.1")
        self.assertEqual(device.mgmt_gw, "10.1.1.254")
        self.assertEqual(device.model, "Nexus 93180YC-EX")
        self.assertIsNone(device.vpc)

    def test_build_device_a_missing_field_raises(self):
        """Empty hostname must raise ValueError with 'hostname' as the message."""
        state = AppState()
        state.hostname = ""  # intentionally empty
        state.mgmt_ip = "10.1.1.1"
        state.mgmt_gw = "10.1.1.254"

        with self.assertRaises(ValueError) as ctx:
            state.build_device_a()

        self.assertEqual(str(ctx.exception), "hostname")

    def test_build_device_a_vpc_mode(self):
        """vPC mode returns Device with role='primary' and correct keepalive IPs."""
        state = _vpc_state()

        device = state.build_device_a()

        self.assertIsNotNone(device.vpc)
        self.assertEqual(device.vpc.role, "primary")
        self.assertEqual(device.vpc.local_keepalive_ip, state.a_kpa_ip)
        self.assertEqual(device.vpc.remote_keepalive_ip, state.b_kpa_ip)


class TestBuildDeviceB(unittest.TestCase):

    def test_build_device_b_swapped_kpa(self):
        """Switch-B gets role='secondary' with keepalive IPs swapped vs Switch-A."""
        state = _vpc_state()

        device = state.build_device_b()

        self.assertIsNotNone(device.vpc)
        self.assertEqual(device.vpc.role, "secondary")
        # local for B == b_kpa_ip; remote for B == a_kpa_ip (swapped)
        self.assertEqual(device.vpc.local_keepalive_ip, state.b_kpa_ip)
        self.assertEqual(device.vpc.remote_keepalive_ip, state.a_kpa_ip)

    def test_build_device_b_requires_vpc_mode(self):
        """build_device_b() must raise ValueError('vpc_mode') when vpc_mode is False."""
        state = AppState()
        state.vpc_mode = False

        with self.assertRaises(ValueError) as ctx:
            state.build_device_b()

        self.assertEqual(str(ctx.exception), "vpc_mode")


if __name__ == "__main__":
    unittest.main()
