from unittest.mock import MagicMock, patch

import pytest
from app.tasks.monitoring_tasks import (
    PING_COUNT,
    PING_TIMEOUT,
    device_icmp,
    schedule_all_pings,
)
from sqlalchemy.exc import SQLAlchemyError

# =================================================================
# Test 1: Testowanie zadania 'device_icmp' (Synchroniczne)
# =================================================================


# Usunęliśmy 'new_callable=AsyncMock' - używamy domyślnego (synchronicznego) mocka
@patch("app.tasks.monitoring_tasks.insert_ping_result")
@patch("app.tasks.monitoring_tasks.ping")
def test_device_icmp_success_up(mock_ping, mock_insert):
    """Testuje udany ping (status UP)."""
    mock_host = MagicMock()
    mock_host.is_alive = True
    mock_host.avg_rtt = 12.5
    mock_host.address = "8.8.8.8"
    mock_host.packet_loss = 0.0
    mock_ping.return_value = mock_host

    # Usunęliśmy 'await' - wywołujemy jak zwykłą funkcję
    result = device_icmp(device_address="8.8.8.8")

    mock_ping.assert_called_once_with(
        "8.8.8.8", count=PING_COUNT, timeout=PING_TIMEOUT, privileged=False
    )
    mock_insert.assert_called_once()

    assert result["status"] == "UP"
    assert result["rtt_avg_ms"] == 12.5
    assert result["ip_address"] == "8.8.8.8"


@patch("app.tasks.monitoring_tasks.insert_ping_result")
@patch("app.tasks.monitoring_tasks.ping")
def test_device_icmp_success_down(mock_ping, mock_insert):
    """Testuje nieudany ping (urządzenie nie odpowiada - DOWN)."""
    mock_host = MagicMock()
    mock_host.is_alive = False
    mock_ping.return_value = mock_host

    result = device_icmp(device_address="192.0.2.1")

    mock_insert.assert_called_once()
    assert result["status"] == "DOWN"
    assert result["error"] == "Host unreachable"


@patch("app.tasks.monitoring_tasks.ping")
def test_device_icmp_bad_ip_format(mock_ping):

    mock_ping.side_effect = Exception("Bad IP format / Name lookup failed")
    result = device_icmp(device_address="google.com")

    assert result["status"] == "ERROR"
    assert "Bad IP format" in result["reason"]

    mock_ping.assert_called_once()


# =================================================================
# Test 2: Testowanie Dyspozytora 'schedule_all_pings'
# =================================================================


class MockDevice:
    """Prosta klasa udająca model urządzenia z bazy danych."""

    def __init__(self, id, ip_address, is_active):
        self.id = id
        self.ip_address = ip_address
        self.is_active = is_active


MOCK_DEVICES_LIST = [
    MockDevice(id=1, ip_address="1.1.1.1", is_active=True),
    MockDevice(id=2, ip_address="8.8.8.8", is_active=True),
    MockDevice(id=3, ip_address="192.168.1.50", is_active=False),
]


@patch("app.tasks.monitoring_tasks.device_icmp.delay")
@patch("app.tasks.monitoring_tasks.get_all_devices")
def test_schedule_pings_active_only(mock_get_all_devices, mock_delay):
    """Testuje, czy domyślnie dodawane do kolejki są TYLKO aktywne urządzenia."""
    mock_get_all_devices.return_value = MOCK_DEVICES_LIST

    result = schedule_all_pings(only_active=True)

    assert mock_delay.call_count == 2
    assert "Scheduled 2 ICMP polls" in str(result)


@patch("app.tasks.monitoring_tasks.device_icmp.delay")
@patch("app.tasks.monitoring_tasks.get_all_devices")
def test_schedule_pings_all_devices(mock_get_all_devices, mock_delay):
    """Testuje wymuszenie skanowania wszystkich (nawet nieaktywnych) urządzeń."""
    mock_get_all_devices.return_value = MOCK_DEVICES_LIST

    result = schedule_all_pings(only_active=False)

    assert mock_delay.call_count == 3
    assert "Scheduled 3 ICMP polls" in str(result)


@patch("app.tasks.monitoring_tasks.device_icmp.delay")
@patch("app.tasks.monitoring_tasks.get_all_devices")
def test_schedule_pings_no_devices_found(mock_get_all_devices, mock_delay):
    """Testuje, co się stanie, gdy baza jest pusta."""
    mock_get_all_devices.return_value = []

    result = schedule_all_pings()

    assert "No devices found" in str(result)
    mock_delay.assert_not_called()


@patch("app.tasks.monitoring_tasks.get_all_devices")
def test_schedule_pings_database_error(mock_get_all_devices):
    """Testuje bezpieczną obsługę błędów bazy danych (np. brak połączenia)."""
    mock_get_all_devices.side_effect = SQLAlchemyError("Simulated connection error")

    result = schedule_all_pings()

    assert "Database connection issue" in str(result)
