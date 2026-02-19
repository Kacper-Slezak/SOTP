from sqlalchemy import Boolean as Bool
from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.schema import PrimaryKeyConstraint

from .base import Base


class PingResult(Base):
    __tablename__ = "ping_results"

    timestamp = Column(DateTime, default=func.now(), nullable=False)

    device_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    ip_address = Column(String(45), nullable=False)
    is_alive = Column(Bool, nullable=False, index=True)
    rtt_avg_ms = Column(Float, nullable=True)
    packet_loss_percent = Column(Float, nullable=True)
    diagnostic_message = Column(String, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("timestamp", "device_id"),
        {},
    )

    def __repr__(self):
        status = "UP" if self.is_alive else "DOWN"
        rtt = f"{self.rtt_avg_ms:.2f}ms" if self.rtt_avg_ms is not None else "N/A"
        return (
            f"<PingResult(device_id={self.device_id}, ip='{self.ip_address}', "
            f"status='{status}', rtt={rtt})>"
        )
