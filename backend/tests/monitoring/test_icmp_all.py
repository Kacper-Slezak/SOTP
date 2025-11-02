import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# -----------------------------------------------------------------
# WAŻNE: Importujemy prawdziwe funkcje, które będziemy testować
# -----------------------------------------------------------------
try:
    from celery.exceptions import MaxRetriesExceededError, TimeoutError

    # Importujemy też wyjątki, których kod szuka
    from sqlalchemy.exc import SQLAlchemyError

    from app.tasks.monitoring_tasks import (
        PING_COUNT,
        PING_TIMEOUT,
        device_icmp,
        schedule_all_pings,
    )
except ImportError as e:
    print(
        f"Błąd importu! Upewnij się, że test jest uruchamiany z głównego katalogu 'backend'."
    )
    print(e)
    exit(1)


# -----------------------------------------------------------------
# Test 1: Testowanie asynchronicznego zadania 'device_icmp'
# -----------------------------------------------------------------
class TestDeviceICMPTask(unittest.TestCase):

    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_success_up(self, mock_ping):
        """Testuje 'device_icmp' dla pomyślnego pingu (status UP)."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_device_icmp_success_up -Testuje 'device_icmp' dla pomyślnego pingu (status UP). ---"
        )

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
        self.assertEqual(result["status"], "UP")
        self.assertEqual(result["rtt_avg_ms"], 12.5)
        self.assertEqual(result["ip_address"], "8.8.8.8")
        print(
            "--- ✅ ZAKOŃCZONO: test_device_icmp_success_up -Testuje 'device_icmp' dla pomyślnego pingu (status UP). ---"
        )

    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_success_down(self, mock_ping):
        """Testuje 'device_icmp' dla nieudanego pingu (status DOWN)."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_device_icmp_success_down -Testuje 'device_icmp' dla nieudanego pingu (status DOWN). ---"
        )

        mock_host = MagicMock()
        mock_host.is_alive = False
        mock_ping.return_value = mock_host

        result = asyncio.run(device_icmp(device_id=2, device_address="192.0.2.1"))

        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(result["error"], "Host unreachable")
        print(
            "--- ✅ ZAKOŃCZONO: test_device_icmp_success_down -Testuje 'device_icmp' dla nieudanego pingu (status DOWN). ---"
        )

    @patch("app.tasks.monitoring_tasks.ping", new_callable=AsyncMock)
    def test_device_icmp_bad_ip_format(self, mock_ping):
        """Testuje 'device_icmp' dla złego formatu IP (np. domeny)."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_device_icmp_bad_ip_format -Testuje 'device_icmp' dla złego formatu IP (np. domeny). ---"
        )

        result = asyncio.run(device_icmp(device_id=3, device_address="google.com"))

        self.assertEqual(result["status"], "ERROR")
        self.assertIn("Zły format IP", result["reason"])
        mock_ping.assert_not_called()
        print(
            "--- ✅ ZAKOŃCZONO: test_device_icmp_bad_ip_format -Testuje 'device_icmp' dla złego formatu IP (np. domeny). ---"
        )


# -----------------------------------------------------------------
# Symulacja obiektu Device na potrzeby testu 'schedule_all_pings'
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
# Test 2: Testowanie synchronicznego zadania 'schedule_all_pings'
# -----------------------------------------------------------------
class TestScheduleAllPingsTask(unittest.TestCase):

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_active_only(self, mock_get_all_devices, mock_delay):
        """Testuje, czy domyślnie kolejkowane są tylko AKTYWNE urządzenia."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_schedule_pings_active_only -Testuje, czy domyślnie kolejkowane są tylko AKTYWNE urządzenia. ---"
        )

        mock_get_all_devices.return_value = MOCK_DEVICES_LIST

        result = schedule_all_pings(only_active=True)

        self.assertEqual(mock_delay.call_count, 2)
        mock_delay.assert_any_call(device_address="1.1.1.1", device_id=1)
        mock_delay.assert_any_call(device_address="8.8.8.8", device_id=2)
        self.assertEqual(result, "Scheduled 2 ICMP polls.")
        print(
            "--- ✅ ZAKOŃCZONO: test_schedule_pings_active_only -Testuje, czy domyślnie kolejkowane są tylko AKTYWNE urządzenia. ---"
        )

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_all_devices(self, mock_get_all_devices, mock_delay):
        """Testuje, czy 'only_active=False' kolejkuje WSZYSTKIE urządzenia."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_schedule_pings_all_devices -Testuje, czy 'only_active=False' kolejkuje WSZYSTKIE urządzenia. ---"
        )

        mock_get_all_devices.return_value = MOCK_DEVICES_LIST

        result = schedule_all_pings(only_active=False)

        self.assertEqual(mock_delay.call_count, 3)
        self.assertEqual(result, "Scheduled 3 ICMP polls.")
        print(
            "--- ✅ ZAKOŃCZONO: test_schedule_pings_all_devices -Testuje, czy 'only_active=False' kolejkuje WSZYSTKIE urządzenia. ---"
        )

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_no_devices_found(self, mock_get_all_devices, mock_delay):
        """Testuje, co się dzieje, gdy 'get_all_devices' zwraca pustą listę."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_schedule_pings_no_devices_found -Testuje, co się dzieje, gdy 'get_all_devices' zwraca pustą listę. ---"
        )

        mock_get_all_devices.return_value = []

        result = schedule_all_pings()

        self.assertEqual(result, "No devices found.")
        mock_delay.assert_not_called()
        print(
            "--- ✅ ZAKOŃCZONO: test_schedule_pings_no_devices_found -Testuje, co się dzieje, gdy 'get_all_devices' zwraca pustą listę. ---"
        )

    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_schedule_pings_database_error(self, mock_get_all_devices):
        """Testuje, czy błąd bazy danych jest poprawnie łapany."""
        print(
            "\n--- 🧪 URUCHAMIANIE: test_schedule_pings_database_error -Testuje, czy błąd bazy danych jest poprawnie łapany. ---"
        )

        mock_get_all_devices.side_effect = SQLAlchemyError("Symulacja błędu połączenia")

        result = schedule_all_pings()

        self.assertIn("Database connection issue", result)
        print(
            "--- ✅ ZAKOŃCZONO: test_schedule_pings_database_error -Testuje, czy błąd bazy danych jest poprawnie łapany. ---"
        )


# --- SEKCJA URUCHOMIENIOWA (MAIN) ---
if __name__ == "__main__":
    unittest.main()
