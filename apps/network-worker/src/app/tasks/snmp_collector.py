import datetime
import asyncio
from celery import shared_task
from pysnmp.hlapi import *
from sqlalchemy import select
from app.core.config import Config 

# Importy z Twojego Workera (ścieżki app.db i app.models)
from app.db.postgres_session import get_postgres_session
from app.db.timescaleDB_session import get_timescale_session
from app.models.device import Device
from app.models.metric import DeviceMetric

OIDS = {
    "uptime": "1.3.6.1.2.1.1.3.0",
    "cpu_load": "1.3.6.1.4.1.2021.11.11.0",
    "mem_total": "1.3.6.1.4.1.2021.4.5.0",
    "mem_avail": "1.3.6.1.4.1.2021.4.6.0",
    "if_count": "1.3.6.1.2.1.2.1.0"
}

def snmp_get_all(target):
    results = {}
    if not all([Config.SNMP_USER, Config.SNMP_AUTH, Config.SNMP_PRIV]):
        return results

    auth_data = UserData(
        Config.SNMP_USER, 
        authKey=Config.SNMP_AUTH, 
        privKey=Config.SNMP_PRIV,
        authProtocol=usmHMACSHAAuthProtocol,
        privProtocol=usmAesCfb128Protocol
    )

    var_objs = [ObjectType(ObjectIdentity(oid)) for oid in OIDS.values()]
    iterator = getCmd(SnmpEngine(), auth_data,
                      UdpTransportTarget((target, 161), timeout=1, retries=1),
                      ContextData(), *var_objs)
    
    error_indication, error_status, _, var_binds = next(iterator)

    if not error_indication and not error_status:
        for i, var_bind in enumerate(var_binds):
            key = list(OIDS.keys())[i]
            results[key] = str(var_bind[1])
    return results

async def get_active_devices():
    # Zobacz, jak czysto to teraz wygląda!
    async with get_postgres_session() as session:
        result = await session.execute(select(Device).where(Device.is_active == True))
        return result.scalars().all()

async def save_metrics(device_id: int, data: dict):
    # Używamy Twojego context managera
    async with get_timescale_session() as session:
        now = datetime.datetime.utcnow()
        for metric_name, value in data.items():
            try:
                metric = DeviceMetric(
                    device_id=device_id,
                    metric_name=metric_name,
                    value=float(value), 
                    timestamp=now
                )
                session.add(metric)
            except ValueError:
                pass

# --- ZADANIA CELERY ---

@shared_task(name="snmp.collect_single_device")
def collect_device_snmp(device_id, ip_address):
    # Zwróć uwagę - teraz podajemy TYLKO ip_address!
    data = snmp_get_all(ip_address)
    if data:
        asyncio.run(save_metrics(device_id, data))

@shared_task(name="snmp.schedule_all_scans")
def schedule_all_snmp():
    try:
        devices = asyncio.run(get_active_devices())
        for dev in devices:
            # Dyspozytor wysyła workerom tylko ID i IP
            collect_device_snmp.delay(dev.id, dev.ip_address)
    except Exception as e:
        print(f"Błąd Dyspozytora SNMP: {str(e)}")