from datetime import datetime, timezone
from typing import Sequence

from app.models.device import Device
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class DeviceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> Sequence[Device]:
        query = select(Device).where(Device.deleted_at.is_(None)).order_by(Device.id)
        result = await self.session.execute(query)
        return result.scalars().all()

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
            .values(deleted_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        await self.session.commit()
