from sqlalchemy import Column, DateTime, Float, Integer, String, func

from .base import Base

# ForeignKey import removed as it is no longer required
# from sqlalchemy import ForeignKey


class DeviceMetric(Base):
    __tablename__ = "device_metrics"

    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())

    # Standalone foreign reference in hypertable:
    device_id = Column(Integer, primary_key=True)  # ForeignKey("devices.id") removed

    metric_name = Column(
        String, primary_key=True
    )  # e.g., 'cpu_utilization', 'memory_usage'
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime)
