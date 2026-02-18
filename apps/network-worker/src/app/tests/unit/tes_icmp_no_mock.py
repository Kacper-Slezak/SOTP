import pytest
from unittest.mock import patch
from app.tasks.monitoring_tasks import device_icmp, schedule_all_pings

# =================================================================
# Testy scenariuszowe - sprawdzamy ZACHOWANIE SYSTEMU
# Ping jest prawdziwy, mockujemy tylko bazę danych
# =================================================================

pytestmark = pytest.mark.integration


class MockDevice:
    def __init__(self, id, ip_address, is_active=True):
        self.id = id
        self.ip_address = ip_address
        self.is_active = is_active


# -----------------------------------------------------------------
# SCENARIUSZ 1: Izolacja błędów
# "Czy jeśli jedno urządzenie pada, reszta dalej działa?"
# -----------------------------------------------------------------

class TestFaultIsolation:
    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_one_dead_host_does_not_kill_others(self, mock_insert):
        """
        Mamy 3 urządzenia: localhost (działa), martwy IP, localhost (działa).
        Sprawdzamy czy wynik każdego jest niezależny.
        """
        devices = [
            MockDevice(id=1, ip_address="127.0.0.1"),   # zawsze działa
            MockDevice(id=2, ip_address="10.0.2.34"),   # zawsze martwy (RFC 5737)
            MockDevice(id=3, ip_address="127.0.0.1"),   # zawsze działa
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert results[0]["status"] == "UP",   "Device 1 powinien być UP"
        assert results[1]["status"] == "DOWN", "Device 2 powinien być DOWN"
        assert results[2]["status"] == "UP",   "Device 3 powinien być UP - nie zaraził się błędem device 2"
    
    
    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_all_dead_hosts(self, mock_insert):
        """Wszystkie urządzenia martwe - każde powinno dostać DOWN, nie crash."""
        devices = [
            MockDevice(id=1, ip_address="192.0.2.1"),
            MockDevice(id=2, ip_address="192.0.2.2"),
            MockDevice(id=3, ip_address="192.0.2.3"),
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert all(r["status"] == "DOWN" for r in results), \
            f"Oczekiwano wszystkich DOWN, dostano: {[r['status'] for r in results]}"
    @patch("app.tasks.monitoring_tasks.PING_TIMEOUT", 1)
    @patch("app.tasks.monitoring_tasks.PING_COUNT", 1)
    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_mixed_valid_and_invalid_addresses(self, mock_insert):
        """
        Mix: działające IP, martwe IP, całkowicie błędny adres.
        Żaden nie powinien rzucić nieobsłużonego wyjątku.
        """
        devices = [
            MockDevice(id=1, ip_address="127.0.0.1"),
            MockDevice(id=2, ip_address="192.0.2.1"),
            MockDevice(id=3, ip_address="to_nie_jest_adres!!!"),
        ]

        results = [device_icmp(device_address=d.ip_address) for d in devices]

        assert results[0]["status"] == "UP"
        assert results[1]["status"] == "DOWN"
        assert results[2]["status"] == "ERROR", \
            "Błędny adres powinien dać ERROR, nie crash całego systemu"


# -----------------------------------------------------------------
# SCENARIUSZ 2: Dispatcher - co wysyła do kolejki?
# -----------------------------------------------------------------

class TestDispatcherBehavior:
    
    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_dispatcher_skips_inactive_by_default(self, mock_get_devices, mock_delay):
        """
        Dispatcher NIE powinien wysyłać tasków dla nieaktywnych urządzeń.
        Sprawdzamy jakie IP trafiły do kolejki.
        """
        mock_get_devices.return_value = [
            MockDevice(id=1, ip_address="1.1.1.1",   is_active=True),
            MockDevice(id=2, ip_address="2.2.2.2",   is_active=False),  # ← ma być pominięte
            MockDevice(id=3, ip_address="3.3.3.3",   is_active=True),
        ]

        schedule_all_pings(only_active=True)

        called_with = [call.kwargs["device_address"] for call in mock_delay.call_args_list]
        assert "1.1.1.1" in called_with
        assert "2.2.2.2" not in called_with,  "Nieaktywne urządzenie nie powinno trafić do kolejki"
        assert "3.3.3.3" in called_with

    @patch("app.tasks.monitoring_tasks.device_icmp.delay")
    @patch("app.tasks.monitoring_tasks.get_all_devices")
    def test_dispatcher_sends_each_device_exactly_once(self, mock_get_devices, mock_delay):
        """Każde urządzenie powinno dostać dokładnie jeden task - bez duplikatów."""
        mock_get_devices.return_value = [
            MockDevice(id=1, ip_address="1.1.1.1"),
            MockDevice(id=2, ip_address="2.2.2.2"),
        ]

        schedule_all_pings()

        called_ips = [call.kwargs["device_address"] for call in mock_delay.call_args_list]
        assert len(called_ips) == len(set(called_ips)), \
            f"Znaleziono duplikaty w kolejce: {called_ips}"


# -----------------------------------------------------------------
# SCENARIUSZ 3: Odporność na dane z bazy
# -----------------------------------------------------------------

class TestDataEdgeCases:

    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_empty_ip_address(self, mock_insert):
        """Co się stanie gdy w bazie jest urządzenie z pustym IP?"""
        result = device_icmp(device_address="")

        assert result["status"] == "ERROR", "Puste IP powinno dać ERROR, nie crash"

    @patch("app.tasks.monitoring_tasks.insert_ping_result")
    def test_ipv6_localhost(self, mock_insert):
        """Czy system obsługuje IPv6?"""
        try:
            result = device_icmp(device_address="::1")
            assert result["status"] in ("UP", "ERROR"), \
                "IPv6 powinno dać UP lub ERROR, nie cichy crash"
        except Exception as e:
            pytest.fail(f"IPv6 rzucił nieobsłużony wyjątek: {e}")