from sqlalchemy import Column, Integer, String, Boolean as Bool, DateTime, func, Enum as SqlEnum
from sqlalchemy.orm import relationship
from .base import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    READONLY = "readonly"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.READONLY, nullable=False)
    is_active = Column(Bool, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relacje
    devices = relationship("Device", backref="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    


