from datetime import datetime, timezone
from enum import Enum

from app.models.device import Device
from fastapi import HTTPException
from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class DeviceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: SortOrder = SortOrder.asc,
        is_active: bool | None = None,
        device_type: str | None = None,
        vendor: str | None = None,
    ) -> tuple[list[Device], int]:
        query = select(Device).where(Device.deleted_at.is_(None))

        if is_active is not None:
            query = query.where(Device.is_active == is_active)
        if device_type is not None:
            query = query.where(Device.device_type == device_type)
        if vendor is not None:
            query = query.where(Device.vendor == vendor)

        total = (
            await self.session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            or 0
        )
        SORTABLE_FIELDS = {"id", "name", "ip_address", "created_at"}
        if sort_by not in SORTABLE_FIELDS:
            sort_by = "id"
        column = getattr(Device, sort_by)
        order = asc(column) if sort_order == "asc" else desc(column)
        result = await self.session.execute(
            query.order_by(order).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, device_id: int) -> Device:
        device = await self.session.get(Device, device_id)
        if not device or device.deleted_at:
            raise HTTPException(status_code=404, detail="Device not found")
        return device

    async def create(self, data: dict) -> Device:
        # Check for IP conflict
        exists = await self.session.execute(
            select(Device).where(Device.ip_address == data["ip_address"])
        )
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="IP address already exists")

        device = Device(**data)
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def update(self, device_id: int, data: dict) -> Device:
        device = await self.get_by_id(device_id)

        # Check IP conflict with other devices
        conflict = await self.session.execute(
            select(Device).where(
                Device.ip_address == data["ip_address"], Device.id != device_id
            )
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="IP already in use")

        for key, value in data.items():
            setattr(device, key, value)

        await self.session.commit()
        return device

    async def soft_delete(self, device_id: int):
        stmt = (
            update(Device)
            .where(Device.id == device_id, Device.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc).replace(tzinfo=None))
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        await self.session.commit()
