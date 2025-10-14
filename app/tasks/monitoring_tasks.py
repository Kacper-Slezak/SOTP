# app/tasks/monitoring_tasks.py

from celery import shared_task
from icmplib import ping
from datetime import datetime, timezone

# --- Importy modeli i sesji DB

from skądś import get_db 
# Pamiętaj, aby zaimportować swoje modele
from app.models import PingResult, Device  # tutaj mi pisze gemini że musi i byc coś takiego ze względu na sqlalchemy ORM.

PING_COUNT = 5
PING_TIMEOUT = 2.0 

@shared_task(bind=True, name="device_icmp")
def device_icmp(self, device_id: int):
    
    
   
    db_generator = get_db() #czy jakkolwiek pobieranie bazy danych będzie działało u nas
    db = next(db_generator) 

    

    try:
        # Pobranie urządzenia (SQLAlchemy ORM)
        device = db.query(Device).filter(Device.id == device_id).one_or_none()
        if not device:
            return {"status": "ABORTED", "reason": f"Device ID {device_id} not found."}

        address = device.ip_address
        
        # 2. Wykonanie Pingu (ICMP)
        host = ping(address, count=PING_COUNT, timeout=PING_TIMEOUT, privileged=False) 
        
        # 3. Zapis Wyników (do TimescaleDB)
        new_result = PingResult(
           
        )
        db.add(new_result)
        db.commit()

        return {"status": "UP" if host.is_alive else "DOWN", "rtt_avg_ms": host.avg_rtt}
        
        
    finally:
        db_generator.close()


@shared_task(name="schedule_all_pings")
def schedule_all_pings(only_active: bool = True):
    
    db_generator = get_db()
    db = next(db_generator)
    
    count = 0
    try:
        query = db.query(Device.id)
    
        if only_active:
            active_devices_ids = query.filter(Device.is_active == True).all()
        else:
            # Jeśli only_active jest False, bierzemy wszystkie ID
            active_devices_ids = query.all()
        
        for device_id_tuple in active_devices_ids:
            # Wysyła zadanie do kolejki
            device_icmp.delay(device_id=device_id_tuple[0])
            count += 1
            
        return f"Scheduled {count} ICMP polls."
        
    finally:
        db_generator.close()