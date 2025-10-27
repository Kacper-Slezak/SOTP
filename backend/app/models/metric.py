# backend/app/models/metric.py

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func

from .base import Base


class DeviceMetric(Base):
    __tablename__ = "device_metrics"

    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())
    device_id = Column(Integer, ForeignKey("devices.id"), primary_key=True)
    metric_name = Column(
        String, primary_key=True
    )  # e.g., 'cpu_utilization', 'memory_usage'
    value = Column(Float, nullable=False)
