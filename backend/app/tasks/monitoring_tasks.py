# app/tasks/monitoring_tasks.py
from sqlalchemy.exc import SQLAlchemyError
from celery.exceptions import MaxRetriesExceededError, TimeoutError
from celery import shared_task
from icmplib import _async_ping as ping
from app.services.ping_services import insert_ping_result
from app.services.device_services import get_all_devices

PING_COUNT = 5
PING_TIMEOUT = 2.0 

@shared_task(bind=True, name="device_icmp")
async def device_icmp(self, device_id: int, device_address: str):
    
    result = {"status": "ERROR", "reason": "Unknown error."}
   

    try:
        
        address = device_address
        
        # 2. Wykonanie Pingu (ICMP)
        host = await ping(address, count=PING_COUNT, timeout=PING_TIMEOUT, privileged=False) 
        
        # 3. Zapis Wyników (do TimescaleDB) 
        insert_ping_result(
            device_id=device_id,
            ip_address=host.address,               
            is_alive=host.is_alive,
            rtt_avg_ms=host.avg_rtt,
            packet_loss_percent=host.packet_loss,
            diagnostic_message="host available" if host.is_alive else "host unreachable",
        )
        return {"status": "UP" , "rtt_avg_ms": host.avg_rtt,"ip_address": host.address,"packet_loss_percent": host.packet_loss} if host.is_alive else {"status": "DOWN", "error": "Host unreachable"}
        
    except SQLAlchemyError as db_err:
        result = {"status": "ERROR", "reason": f"Database error: {str(db_err)}"}
        return result
    except Exception as e:
        result = {"status": "ERROR", "reason": f"General error: {str(e)}"}
        return result

@shared_task(name="schedule_all_pings")
def schedule_all_pings(only_active: bool = True):
    
    
    
    count = 0
    try:
        devices = get_all_devices() # Pobranie wszystkich urządzeń z bazy danych kiryl mówi że jakoś ma byc ale jakoś nie ma sensu
        if only_active:
            devices = [d for d in devices if d.is_active]

        for device in devices:
            try:
                device_icmp.delay(device_address=device.ip_address, device_id=device.id)
                count += 1
            except (MaxRetriesExceededError, TimeoutError) as e:
                print(f"Failed to schedule ping for {device.ip_address}: {str(e)}")
                continue

        return f"Scheduled {count} ICMP polls."
    except SQLAlchemyError as db_err:
        return f"Error scheduling ICMP polls (Database connection issue): {str(db_err)}"
    except AttributeError as attr_err:
        return f"Error scheduling ICMP polls (Device attribute missing): {str(attr_err)}. Check 'is_active' or 'ip_address' on devices."
    except Exception as e:
        return f"Error scheduling ICMP polls (General failure): {str(e)}"