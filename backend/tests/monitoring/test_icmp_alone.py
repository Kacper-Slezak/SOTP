from app.tasks import monitoring_tasks 

# --- TESTY ---
def test_device_icmp():
    
    TEST_IP = "8.8.8.8" # Stały adres IP do testowania
    result = monitoring_tasks.device_icmp(None, device_address=TEST_IP) 
    print(result.status)
    print(result)
    assert result["status"] in ["UP", "DOWN", "ERROR"]
    if result["status"] == "UP":
        assert "rtt_avg_ms" in result
        assert result["rtt_avg_ms"] >= 0
        assert "ip_address" in result
        assert result["ip_address"] == TEST_IP
        assert "packet_loss_percent" in result
        assert result["packet_loss_percent"] >= 0

    elif result["status"] == "DOWN":
        assert "error" in result
        assert result["error"] == "Host unreachable"
    else:
        assert result["status"] == "ERROR"
        assert "reason" in result

