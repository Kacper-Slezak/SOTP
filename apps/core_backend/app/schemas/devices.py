from typing import Optional

from pydantic import BaseModel


class DevicePut(BaseModel):
    name: str
    ip_address: str
    device_type: str
    vendor: str
    model: str
    os_version: str
    location: str
    is_active: bool
    snmp_config: Optional[str] = None
    ssh_config: Optional[str] = None
    api_config: Optional[str] = None
