from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean as Bool,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class PingResult(Base):
    __tablename__ = "ping_results"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    is_alive = Column(Bool, nullable=False, index=True) 
    rtt_avg_ms = Column(Float, nullable=True) 
    packet_loss_percent = Column(Float, nullable=True) 
    timestamp = Column(DateTime, default=func.now(), index=True, nullable=False)
    diagnostic_message = Column(String, nullable=True) 
    device = relationship("Device", back_populates="ping_results") 

    def __repr__(self):
        status = "UP" if self.is_alive else "DOWN"
        rtt = f"{self.rtt_avg_ms:.2f}ms" if self.rtt_avg_ms is not None else "N/A"
        # Dodanie ip_address do reprezentacji
        return (
            f"<PingResult(device_id={self.device_id}, ip='{self.ip_address}', "
            f"status='{status}', rtt={rtt})>"
        )