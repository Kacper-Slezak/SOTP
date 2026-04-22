from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total_count: int
    limit: int
    offset: int


class DeviceCredentialsIn(BaseModel):
    """
    Optional credentials sent with a device create/update request.
    Each non-None field is stored as a separate Vault secret.

    Vault paths produced:
      snmp_community  →  secret/data/devices/{id}/snmp
      ssh_password    →  secret/data/devices/{id}/ssh
    """

    snmp_community: Optional[str] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None


class DeviceOut(BaseModel):
    id: int
    name: str
    ip_address: str
    device_type: str
    vendor: str
    model: str
    os_version: str
    location: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class DevicePut(BaseModel):
    name: str
    ip_address: str
    device_type: str
    vendor: str
    model: str
    os_version: str
    location: str
    is_active: bool
    snmp_config: Optional[dict[str, Any]] = None
    ssh_config: Optional[dict[str, Any]] = None
    api_config: Optional[dict[str, Any]] = None
    credentials: Optional[DeviceCredentialsIn] = None
