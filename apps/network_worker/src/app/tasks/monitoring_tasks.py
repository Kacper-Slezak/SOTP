# app/tasks/monitoring_tasks.py
import asyncio
import datetime
import ipaddress

from app.db.postgres_session import get_postgres_session
from app.db.timescaleDB_session import get_timescale_session

# --- Importy modeli i sesji DB
from app.models import PingResult, device
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, TimeoutError
from icmplib import ping
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

PING_COUNT = 2
PING_TIMEOUT = 2.0


async def _async_insert_ping_result(
    ip_address: str, is_alive: bool, rtt_avg_ms: float, packet_loss_percent: float
):
    async with get_timescale_session() as session:
        try:
            new_ping = PingResult(
                timestamp=datetime.datetime.utcnow(),
                ip_address=ip_address,
                is_alive=is_alive,
                rtt_avg_ms=rtt_avg_ms,
                packet_loss_percent=packet_loss_percent,
            )
            session.add(new_ping)
        except Exception as e:
            print(f"Błąd zapisu wyników ICMP dla {ip_address}: {e}")


def insert_ping_result(
    ip_address: str, is_alive: bool, rtt_avg_ms: float, packet_loss_percent: float
):
    asyncio.run(
        _async_insert_ping_result(
            ip_address=ip_address,
            is_alive=is_alive,
            rtt_avg_ms=rtt_avg_ms,
            packet_loss_percent=packet_loss_percent,
        )
    )


async def get_all_devices():
    async with get_postgres_session() as session:
        result = await session.execute(select(device))
        return result.scalars().all()


@shared_task(bind=True, name="device_icmp")
def device_icmp(self, device_address: str):
    try:
        if not device_address or not device_address.strip():
            return {"status": "ERROR", "reason": "Empty IP address"}
        try:
            ipaddress.ip_address(device_address)
        except ValueError:
            return {
                "status": "ERROR",
                "reason": f"Invalid IP address: {device_address}",
            }
        # 1. Wykonanie Pingu (ICMP)
        host = ping(
            device_address, count=PING_COUNT, timeout=PING_TIMEOUT, privileged=False
        )

        # 2. Zapis Wyników (do TimescaleDB)
        insert_ping_result(
            ip_address=host.address,
            is_alive=host.is_alive,
            rtt_avg_ms=host.avg_rtt,
            packet_loss_percent=host.packet_loss,
        )

        # 3. Zwrócenie wyniku
        if host.is_alive:
            return {
                "status": "UP",
                "rtt_avg_ms": host.avg_rtt,
                "ip_address": host.address,
                "packet_loss_percent": host.packet_loss,
            }
        else:
            return {"status": "DOWN", "error": "Host unreachable"}

    except SQLAlchemyError as db_err:
        return {"status": "ERROR", "reason": f"Database error: {str(db_err)}"}
    except Exception as e:
        # Tuta wpadnie np. błąd "Name lookup failed" z icmplib przy złym formacie IP
        return {"status": "ERROR", "reason": f"General error: {str(e)}"}


@shared_task(name="schedule_all_pings")
def schedule_all_pings(only_active: bool = True):
    count = 0
    try:
        # POPRAWKA: Używamy asyncio.run() aby pobrać faktyczną listę zamiast obietnicy!
        devices = asyncio.run(get_all_devices())

        # POPRAWKA: Jeśli baza jest pusta, od razu zwracamy odpowiedni komunikat
        if not devices:
            return "No devices found."

        if only_active:
            devices = [d for d in devices if d.is_active]

        for device_obj in devices:
            try:
                device_icmp.delay(device_address=device_obj.ip_address)
                count += 1
            except (MaxRetriesExceededError, TimeoutError) as e:
                print(f"Failed to schedule ping for {device_obj.ip_address}: {str(e)}")
                continue

        return f"Scheduled {count} ICMP polls."

    except SQLAlchemyError as db_err:
        return f"Error scheduling ICMP polls (Database connection issue): {str(db_err)}"
    except AttributeError as attr_err:
        return f"Error scheduling ICMP polls (Device attribute missing): {str(attr_err)}. Check 'is_active' or 'ip_address' on devices."
    except Exception as e:
        return f"Error scheduling ICMP polls (General failure): {str(e)}"
