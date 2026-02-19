from sqlalchemy import Column, DateTime, Float, Integer, String, func

from .base import Base

# Usunięto import ForeignKey, ponieważ nie jest już potrzebny
# from sqlalchemy import ForeignKey


class DeviceMetric(Base):
    __tablename__ = "device_metrics"

    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())

    # TA LINIA ZOSTAŁA ZMIENIONA:
    device_id = Column(Integer, primary_key=True)  # Usunięto ForeignKey("devices.id")

    metric_name = Column(
        String, primary_key=True
    )  # e.g., 'cpu_utilization', 'memory_usage'
    value = Column(Float, nullable=False)
