from sqlalchemy import (
    JSON,
)
from sqlalchemy import Boolean as Bool
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, unique=True, index=True, nullable=False)
    device_type = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    model = Column(String, nullable=False)
    os_version = Column(String, nullable=False)
    location = Column(String, nullable=True)
    is_active = Column(Bool, default=True, nullable=False)

    snmp_config = Column(JSON, nullable=True)  # JSON field for SNMP configuration
    ssh_config = Column(JSON, nullable=True)  # JSON field for SSH configuration
    api_config = Column(JSON, nullable=True)  # JSON field for API configuration

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # For soft delete

    # Relationships
    credentials = relationship(
        "Credential", back_populates="device", cascade="all, delete-orphan"
    )
    created_by = relationship("User", back_populates="devices")
    alerts = relationship(
        "Alert", back_populates="device", cascade="all, delete-orphan"
    )


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    credential_type = Column(String, nullable=False)  # e.g., "snmp", "ssh", "api"
    vault_path = Column(
        String, nullable=False, unique=True
    )  # Path in the vault where credentials are stored

    # Relationship
    device = relationship("Device", back_populates="credentials")
