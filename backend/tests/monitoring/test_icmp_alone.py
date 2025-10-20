# test_device_icmp.py
import pytest
from unittest import mock
from app.tasks import monitoring_tasks



# --- POMOCNICZE KLASY MOCKÓW ---

# Symulacja obiektu urządzenia zwróconego przez bazę danych
class MockDevice:
    def __init__(self, id, ip_address):
        self.id = id
        self.ip_address = ip_address

# Symulacja obiektu wyniku pinga (zwracanego przez ping(address, ...))
class MockHostResult:
    def __init__(self, address, is_alive, avg_rtt, packet_loss):
        self.address = address
        self.is_alive = is_alive
        self.avg_rtt = avg_rtt
        self.packet_loss = packet_loss

# --- TESTY ---

@pytest.fixture
def mock_db_session():
    """Tworzy mock obiektu sesji bazy danych (db) i generatora."""
    
    # 1. Mockujemy obiekt urządzenia, które ma zwrócić baza
    mock_device_instance = MockDevice(id=1, ip_address="127.0.0.1")
    
    # 2. Mockujemy obiekt sesji bazy danych
    mock_db = mock.Mock()
    # Konfigurujemy, co ma zwrócić db.query(device).filter(...).one_or_none()
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = mock_device_instance
    
    # 3. Mockujemy generator i jego metodę next()
    mock_generator = mock.Mock()
    mock_generator.__next__.return_value = mock_db
    
    # 4. Mockujemy funkcję main.get_db()
    with mock.patch('your_module.main.get_db', return_value=mock_generator) as mock_get_db:
        yield mock_db
    
    # Assert, że generator został zawsze zamknięty
    mock_generator.close.assert_called_once()


@pytest.mark.parametrize("is_alive, expected_status", [
    (True, "UP"),
    (False, "DOWN"),
])
@mock.patch('your_module.main.insert_ping_result')
@mock.patch('your_module.ping') # Mockowanie funkcji ping
def test_device_icmp_success(mock_ping, mock_insert, mock_db_session, is_alive, expected_status):
    
    # Konfiguracja wyniku pinga
    mock_result = MockHostResult(
        address="127.0.0.1",
        is_alive=is_alive,
        avg_rtt=1.23 if is_alive else 0.0,
        packet_loss=0.0 if is_alive else 100.0
    )
    mock_ping.return_value = mock_result
    
    # Uruchomienie funkcji
    result = monitoring_tasks.device_icmp(None, device_id=1) 
    
    # 1. Sprawdzenie wyniku (Return Value)
    assert result["status"] == expected_status
    assert result["rtt_avg_ms"] == mock_result.avg_rtt

    # 2. Sprawdzenie, czy ping został wywołany z poprawnym adresem i parametrami
    mock_ping.assert_called_once_with(
        "127.0.0.1", 
        count=monitoring_tasks.PING_COUNT, 
        timeout=monitoring_tasks.PING_TIMEOUT, 
        privileged=False
    )
    
    # 3. Sprawdzenie, czy funkcja zapisu została wywołana z poprawnymi danymi
    mock_insert.assert_called_once_with(
        session=mock_db_session, 
        device_id=1,
        ip_address="127.0.0.1",
        is_alive=is_alive,
        rtt_avg_ms=mock_result.avg_rtt,
        packet_loss_percent=mock_result.packet_loss
    )


def test_device_icmp_device_not_found(mock_db_session):
    
    # Konfiguracja, aby zapytanie SQL zwróciło None
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None
    
    # Uruchomienie funkcji
    result = monitoring_tasks.device_icmp(None, device_id=999)
    
    # Sprawdzenie wyniku
    assert result == {"status": "ABORTED", "reason": "Device ID 999 not found."}
    
   