from unittest.mock import AsyncMock, MagicMock

import pytest
from app.main import delete_device
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.asyncio
async def test_delete_device_success():
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    result = MagicMock()
    result.rowcount = 1
    session.execute.return_value = result

    resp = await delete_device(id=123, session=session)

    assert resp.status_code == 200
    assert b"Device deleted successfully" in resp.body

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_device_not_found():
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    result = MagicMock()
    result.rowcount = 0
    session.execute.return_value = result

    with pytest.raises(HTTPException) as exc:
        await delete_device(id=999, session=session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Device not found"

    session.execute.assert_awaited_once()
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_device_db_error():
    session = MagicMock()
    session.execute = AsyncMock(side_effect=SQLAlchemyError("boom"))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await delete_device(id=123, session=session)

    assert exc.value.status_code == 500
    assert exc.value.detail == "DB error"

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
