from unittest.mock import patch

import pytest
from app.tasks.monitoring_tasks import device_icmp, schedule_all_pings

# =================================================================
# Scenario Tests - Verifying SYSTEM BEHAVIOR
# Real ICMP ping, mock database only
# =================================================================

pytestmark = pytest.mark.integration


class MockDevice:
    def __init__(self, id, ip_address, is_active=True):
        self.id = id
        self.ip_address = ip_address
        self.is_active = is_active


# -----------------------------------------------------------------
# SCENARIO 1: Fault Isolation
# "If one device fails, do the others continue working?"
# -----------------------------------------------------------------


class TestFaultIsolation:
    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_one_dead_host_does_not_kill_others(self, mock_insert):
        """
        Three devices: localhost (alive), unreachable IP, localhost (alive).
        Verifies each result is evaluated independently.
        """
        devices = [
            MockDevice(id=1, ip_address="127.0.0.1"),  # always UP
            MockDevice(id=2, ip_address="10.0.2.34"),  # unreachable test address
            MockDevice(id=3, ip_address="127.0.0.1"),  # always UP
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert results[0]["status"] == "UP", "Device 1 should be UP"
        assert results[1]["status"] == "DOWN", "Device 2 should be DOWN"
        assert results[2]["status"] == "UP", (
            "Device 3 should be UP - not affected by device 2 failure"
        )

    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_all_dead_hosts(self, mock_insert):
        """All hosts unreachable - each should return DOWN, no crashes."""
        devices = [
            MockDevice(id=1, ip_address="192.0.2.1"),
            MockDevice(id=2, ip_address="192.0.2.2"),
            MockDevice(id=3, ip_address="192.0.2.3"),
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert all(r["status"] == "DOWN" for r in results), (
            f"Expected all DOWN, received: {[r['status'] for r in results]}"
        )

    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_mixed_valid_and_invalid_addresses(self, mock_insert):
        """
        Mixed: reachable IP, unreachable IP, completely invalid address.
        None should raise an unhandled exception.
        """
        devices = [
            MockDevice(id=1, ip_address="127.0.0.1"),
            MockDevice(id=2, ip_address="192.0.2.1"),
            MockDevice(id=3, ip_address="not_a_valid_ip_address!!!"),
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert results[0]["status"] == "UP"
        assert results[1]["status"] == "DOWN"
        assert results[2]["status"] == "ERROR", (
            "Invalid address should return ERROR status without crashing"
        )


# -----------------------------------------------------------------
# SCENARIO 2: Dispatcher behavior
# -----------------------------------------------------------------


class TestDispatcherBehavior:
    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_dispatcher_skips_inactive_by_default(self, mock_get_devices, mock_delay):
        """
        Dispatcher should not queue tasks for inactive devices by default.
        """
        mock_get_devices.return_value = [
            MockDevice(id=1, ip_address="1.1.1.1", is_active=True),
            MockDevice(
                id=2, ip_address="2.2.2.2", is_active=False
            ),  # should be skipped
            MockDevice(id=3, ip_address="3.3.3.3", is_active=True),
        ]

        schedule_all_pings(only_active=True)

        called_with = [
            call.kwargs["device_address"] for call in mock_delay.call_args_list
        ]
        assert "1.1.1.1" in called_with
        assert "2.2.2.2" not in called_with, (
            "Inactive device should not be added to dispatch queue"
        )
        assert "3.3.3.3" in called_with

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_dispatcher_sends_each_device_exactly_once(
        self, mock_get_devices, mock_delay
    ):
        """Each device should receive exactly one scheduled task - no duplicates."""
        mock_get_devices.return_value = [
            MockDevice(id=1, ip_address="1.1.1.1"),
            MockDevice(id=2, ip_address="2.2.2.2"),
        ]

        schedule_all_pings()

        called_ips = [
            call.kwargs["device_address"] for call in mock_delay.call_args_list
        ]
        assert len(called_ips) == len(set(called_ips)), (
            f"Found duplicate items in dispatch queue: {called_ips}"
        )


# -----------------------------------------------------------------
# SCENARIO 3: Robustness against database edge cases
# -----------------------------------------------------------------


class TestDataEdgeCases:
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_empty_ip_address(self, mock_insert):
        """Handle device record with empty IP string gracefully."""
        result = device_icmp(device_address="")

        assert result["status"] == "ERROR", "Empty IP should return ERROR, not crash"

    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_ipv6_localhost(self, mock_insert):
        """Handle IPv6 addresses properly."""
        try:
            result = device_icmp(device_address="::1")
            assert result["status"] in (
                "UP",
                "ERROR",
            ), "IPv6 should return UP or ERROR, not an unhandled crash"
        except Exception as e:
            pytest.fail(f"IPv6 raised unhandled exception: {e}")
