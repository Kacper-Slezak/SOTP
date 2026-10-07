from typing import Any, Generic, TypeVar

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

    snmp_community: str | None = None
    ssh_username: str | None = None
    ssh_password: str | None = None


class DeviceOut(BaseModel):
    id: int
    name: str
    ip_address: str
    device_type: str
    vendor: str
    model: str
    os_version: str
    location: str | None
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
    snmp_config: dict[str, Any] | None = None
    ssh_config: dict[str, Any] | None = None
    api_config: dict[str, Any] | None = None
    credentials: DeviceCredentialsIn | None = None
