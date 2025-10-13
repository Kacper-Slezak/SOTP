import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class AlertSeverity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # np. 'CPU_HIGH', 'DEVICE_DOWN'
    severity = Column(
        SQLEnum(AlertSeverity), default=AlertSeverity.INFO, nullable=False
    )
    message = Column(String)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    device = relationship("Device", back_populates="alerts")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    condition = Column(String, nullable=False)  # np. 'cpu > 90 for 5m'
    threshold = Column(String)  # np. '90'
    notification_channel = Column(String)  # np. 'slack', 'email'
