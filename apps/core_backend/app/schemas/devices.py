from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total_count: int
    limit: int
    offset: int


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
