import asyncio
import ipaddress

from app.tasks import monitoring_tasks


# --- TESTY ---
async def test_device_icmp(test_ip: str):

    TEST_IP = test_ip
    result = await monitoring_tasks.device_icmp(device_id=0, device_address=test_ip)
    assert result["status"] in ["UP", "DOWN", "ERROR", "DB_ERROR"]
    if result["status"] == "UP":
        print(f"Host [{TEST_IP}] is UP ⬆️")
        assert "rtt_avg_ms" in result
        assert result["rtt_avg_ms"] >= 0
        assert "ip_address" in result
        assert result["ip_address"] == TEST_IP
        assert "packet_loss_percent" in result
        assert result["packet_loss_percent"] >= 0
        print(result)

    elif result["status"] == "DOWN":
        print(f"Host [{TEST_IP}] is DOWN ⬇️   ")
        assert "error" in result
        assert result["error"] == "Host unreachable"
        print(result)
    elif result["status"] == "DB_ERROR":
        print(f"Host [{TEST_IP}] DB_ERROR ⚠️   ")
        assert "reason" in result
        print(result)
    else:
        assert result["status"] == "ERROR"
        print(f"Host [{TEST_IP}] is ERROR ⚠️")
        assert "reason" in result
        print(result)


async def main():
    """Główna funkcja asynchroniczna, która zarządza całą pętlą testów."""

    ADRESY_IP_DO_TESTU = [
        "googlebla bla bla", # Zostanie poprawnie pominięty
        "8.8.8.8",
        "1.1.1.1",
        "192.168.1.1",
        "192.168.71.5",
        "google.com"         # Zostanie poprawnie pominięty
    ]

    print("Uruchamianie wszystkich testów ICMP...")

    # Pętla 'for' musi być WEWNĄTRZ funkcji async
    for test_ip in ADRESY_IP_DO_TESTU:
        await test_device_icmp(test_ip)
        print("="*40) # Separator dla czytelności
    print("Wszy")


# --- SEKCJA URUCHOMIENIOWA ---
if __name__ == "__main__":
    # Wywołaj asyncio.run() TYLKO RAZ na funkcji 'main'
    try:
        asyncio.run(main())
        print("\nWszystkie testy zakończone.")
    except Exception as e:
        print(f"\nKrytyczny błąd podczas uruchamiania pętli głównej: {e}")
