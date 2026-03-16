from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.device_services import DeviceService
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


def make_session(rowcount=1, side_effect=None):
    session = MagicMock()
    result = MagicMock()
    result.rowcount = rowcount
    if side_effect:
        session.execute = AsyncMock(side_effect=side_effect)
    else:
        session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_soft_delete_success():
    session = make_session(rowcount=1)
    service = DeviceService(session)

    await service.soft_delete(device_id=123)

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_soft_delete_not_found():
    session = make_session(rowcount=0)
    service = DeviceService(session)

    with pytest.raises(HTTPException) as exc:
        await service.soft_delete(device_id=999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Device not found"
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_soft_delete_db_error():
    session = make_session(side_effect=SQLAlchemyError("boom"))
    service = DeviceService(session)

    with pytest.raises(SQLAlchemyError):
        await service.soft_delete(device_id=123)
