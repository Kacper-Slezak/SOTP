from app.db.timescaleDB_session import get_timescale_session
from app.models.PingResult import PingResult


async def insert_ping_result(
    device_id: int,
    ip_address: str,
    is_alive: bool,
    rtt_avg_ms: float | None,
    packet_loss_percent: float | None,
    diagnostic_message: str | None = None,
):
    async with get_timescale_session() as db:

        new_result = PingResult(
            device_id=device_id,
            ip_address=ip_address,
            is_alive=is_alive,
            rtt_avg_ms=rtt_avg_ms,
            packet_loss_percent=packet_loss_percent,
            diagnostic_message=diagnostic_message,
        )

        db.add(new_result)
