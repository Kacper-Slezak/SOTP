from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False) # np. 'CREATE_DEVICE', 'LOGIN_FAILURE'
    resource_type = Column(String) # np. 'Device', 'User'
    resource_id = Column(Integer)
    details_json = Column(JSON)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=func.now())

    # Relacja
    user = relationship("User", back_populates="audit_logs")