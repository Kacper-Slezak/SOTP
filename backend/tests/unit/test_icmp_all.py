import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# 1. Removed the try/except/exit(1) block. Let pytest handle imports.
from app.tasks.monitoring_tasks import (
    PING_COUNT,
    PING_TIMEOUT,
    device_icmp,
    schedule_all_pings,
)
from sqlalchemy.exc import SQLAlchemyError


# -----------------------------------------------------------------
# Test 1: Testing the 'device_icmp' async task
# -----------------------------------------------------------------
class TestDeviceICMPTask(unittest.TestCase):

    # 2. Added mock for 'insert_ping_result' to fix DB_ERROR
    @patch("app.tasks.monitoring_tasks.insert_ping_result", new_callable=AsyncMock)
    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_success_up(self, mock_ping, mock_insert):
        """Tests 'device_icmp' for a successful ping (status UP)."""
        # 3. Removed polish print statements
        mock_host = MagicMock()
        mock_host.is_alive = True
        mock_host.avg_rtt = 12.5
        mock_host.address = "8.8.8.8"
        mock_host.packet_loss = 0.0
        mock_ping.return_value = mock_host

        result = asyncio.run(device_icmp(device_id=1, device_address="8.8.8.8"))

        mock_ping.assert_called_once_with(
            "8.8.8.8", count=PING_COUNT, timeout=PING_TIMEOUT, privileged=False
        )
        # Verify it would have tried to save
        mock_insert.assert_called_once()
        self.assertEqual(result["status"], "UP")
        self.assertEqual(result["rtt_avg_ms"], 12.5)
        self.assertEqual(result["ip_address"], "8.8.8.8")

    # 2. Added mock for 'insert_ping_result' to fix DB_ERROR
    @patch("app.tasks.monitoring_tasks.insert_ping_result", new_callable=AsyncMock)
    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_success_down(self, mock_ping, mock_insert):
        """Tests 'device_icmp' for a failed ping (status DOWN)."""
        mock_host = MagicMock()
        mock_host.is_alive = False
        mock_ping.return_value = mock_host

        result = asyncio.run(device_icmp(device_id=2, device_address="192.0.2.1"))

        # Verify it would have tried to save
        mock_insert.assert_called_once()
        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(result["error"], "Host unreachable")

    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_bad_ip_format(self, mock_ping):
        """Tests 'device_icmp' for a bad IP format (e.g., domain)."""
        result = asyncio.run(device_icmp(device_id=3, device_address="google.com"))

        self.assertEqual(result["status"], "ERROR")
        # 4. Fixed assertion to match the actual error message
        self.assertIn("Bad IP format", result["reason"])
        mock_ping.assert_not_called()


# -----------------------------------------------------------------
# Mock Device object for 'schedule_all_pings' test
# -----------------------------------------------------------------
class MockDevice:
    def __init__(self, id, ip_address, is_active):
        self.id = id
        self.ip_address = ip_address
        self.is_active = is_active


MOCK_DEVICES_LIST = [
    MockDevice(id=1, ip_address="1.1.1.1", is_active=True),
    MockDevice(id=2, ip_address="8.8.8.8", is_active=True),
    MockDevice(id=3, ip_address="192.168.1.50", is_active=False),
]


# -----------------------------------------------------------------
# Test 2: Testing the 'schedule_all_pings' sync task
# -----------------------------------------------------------------
class TestScheduleAllPingsTask(unittest.TestCase):

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_active_only(self, mock_get_all_devices, mock_delay):
        """Tests that only ACTIVE devices are queued by default."""
        mock_get_all_devices.return_value = MOCK_DEVICES_LIST

        result = schedule_all_pings(only_active=True)

        self.assertEqual(mock_delay.call_count, 2)
        mock_delay.assert_any_call(device_address="1.1.1.1", device_id=1)
        mock_delay.assert_any_call(device_address="8.8.8.8", device_id=2)
        self.assertEqual(result, "Scheduled 2 ICMP polls.")

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_all_devices(self, mock_get_all_devices, mock_delay):
        """Tests if 'only_active=False' queues ALL devices."""
        mock_get_all_devices.return_value = MOCK_DEVICES_LIST

        result = schedule_all_pings(only_active=False)

        self.assertEqual(mock_delay.call_count, 3)
        self.assertEqual(result, "Scheduled 3 ICMP polls.")

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_no_devices_found(self, mock_get_all_devices, mock_delay):
        """Tests what happens when 'get_all_devices' returns an empty list."""
        mock_get_all_devices.return_value = []

        result = schedule_all_pings()

        self.assertEqual(result, "No devices found.")
        mock_delay.assert_not_called()

    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_database_error(self, mock_get_all_devices):
        """Tests if a database error is caught correctly."""
        mock_get_all_devices.side_effect = SQLAlchemyError("Simulated connection error")

        result = schedule_all_pings()

        self.assertIn("Database connection issue", result)


# --- RUNNER (MAIN) SECTION ---
if __name__ == "__main__":
    unittest.main()
