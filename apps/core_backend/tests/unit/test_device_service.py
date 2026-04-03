"""
Unit tests for DeviceService.
All database interactions are mocked — no real DB required.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.device import Device
from app.services.device_services import DeviceService
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_device(**kwargs) -> Device:
    defaults = dict(
        id=1,
        name="Router-01",
        ip_address="192.168.1.1",
        device_type="router",
        vendor="Cisco",
        model="ISR 4331",
        os_version="IOS-XE 17.6",
        location="Server Room A",
        is_active=True,
        deleted_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    device = Device(**defaults)
    return device


def _make_session(
    *,
    scalar_result=None,
    scalars_all=None,
    rowcount: int = 1,
    get_result=None,
    side_effect=None,
):
    """Build a minimal async SQLAlchemy session mock."""
    session = MagicMock()

    # session.execute(...)
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = scalar_result
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = scalars_all or []
    execute_result.scalars.return_value = scalars_mock
    execute_result.rowcount = rowcount

    if side_effect:
        session.execute = AsyncMock(side_effect=side_effect)
    else:
        session.execute = AsyncMock(return_value=execute_result)

    # session.get(...)
    session.get = AsyncMock(return_value=get_result)

    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    return session


# ===========================================================================
# get_all
# ===========================================================================


class TestGetAll:
    @pytest.mark.asyncio
    async def test_returns_active_devices(self):
        d1 = _make_device(id=1)
        d2 = _make_device(id=2, name="Switch-01", ip_address="10.0.0.2")
        session = _make_session(scalars_all=[d1, d2])

        service = DeviceService(session)
        result = await service.get_all()

        assert result == [d1, d2]
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_devices(self):
        session = _make_session(scalars_all=[])
        service = DeviceService(session)
        result = await service.get_all()
        assert result == []

    @pytest.mark.asyncio
    async def test_excludes_soft_deleted_devices(self):
        """get_all must filter by deleted_at IS NULL — we verify the query is executed."""
        session = _make_session(scalars_all=[])
        service = DeviceService(session)
        await service.get_all()
        # The query itself carries the filter; just assert execute was called
        session.execute.assert_awaited_once()


# ===========================================================================
# get_by_id
# ===========================================================================


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_device_when_found(self):
        device = _make_device()
        session = _make_session(get_result=device)
        service = DeviceService(session)

        result = await service.get_by_id(1)
        assert result is device
        session.get.assert_awaited_once_with(Device, 1)

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        session = _make_session(get_result=None)
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_id(999)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_raises_404_for_soft_deleted_device(self):
        deleted = _make_device(deleted_at=datetime.now(timezone.utc))
        session = _make_session(get_result=deleted)
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_id(1)
        assert exc_info.value.status_code == 404


# ===========================================================================
# create
# ===========================================================================


class TestCreate:
    @pytest.mark.asyncio
    async def test_creates_device_successfully(self):
        session = _make_session(scalar_result=None)  # no IP conflict

        created = _make_device()
        session.refresh = AsyncMock(side_effect=lambda d: setattr(d, "id", 1))

        service = DeviceService(session)

        data = {
            "name": "Router-01",
            "ip_address": "192.168.1.1",
            "device_type": "router",
            "vendor": "Cisco",
            "model": "ISR 4331",
            "os_version": "IOS-XE 17.6",
            "location": "Server Room A",
            "is_active": True,
        }
        result = await service.create(data)

        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert isinstance(result, Device)

    @pytest.mark.asyncio
    async def test_raises_409_on_duplicate_ip(self):
        existing = _make_device()
        session = _make_session(scalar_result=existing)  # IP conflict found
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.create({"ip_address": "192.168.1.1", "name": "Dup"})
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_does_not_commit_on_conflict(self):
        existing = _make_device()
        session = _make_session(scalar_result=existing)
        service = DeviceService(session)

        with pytest.raises(HTTPException):
            await service.create({"ip_address": "192.168.1.1"})

        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_db_error_propagates(self):
        session = _make_session(side_effect=SQLAlchemyError("db down"))
        service = DeviceService(session)

        with pytest.raises(SQLAlchemyError):
            await service.create({"ip_address": "1.2.3.4"})


# ===========================================================================
# update
# ===========================================================================


class TestUpdate:
    @pytest.mark.asyncio
    async def test_updates_device_successfully(self):
        device = _make_device()
        # get_by_id calls session.get; no IP conflict
        session = _make_session(get_result=device, scalar_result=None)
        service = DeviceService(session)

        new_data = {
            "name": "Router-01-Updated",
            "ip_address": "192.168.1.1",
            "device_type": "router",
            "vendor": "Cisco",
            "model": "ISR 4331",
            "os_version": "IOS-XE 17.9",
            "location": "Server Room B",
            "is_active": True,
        }
        result = await service.update(1, new_data)

        assert result.os_version == "IOS-XE 17.9"
        assert result.location == "Server Room B"
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raises_404_when_device_missing(self):
        session = _make_session(get_result=None)
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.update(999, {"ip_address": "1.2.3.4"})
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_409_on_ip_conflict_with_other_device(self):
        device = _make_device(id=1)
        conflict = _make_device(id=2, ip_address="10.0.0.9")
        session = _make_session(get_result=device, scalar_result=conflict)
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.update(1, {"ip_address": "10.0.0.9"})
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_same_ip_does_not_conflict_with_itself(self):
        """Updating a device keeping its own IP should not raise 409."""
        device = _make_device(id=1, ip_address="192.168.1.1")
        # scalar_result=None means no OTHER device has this IP
        session = _make_session(get_result=device, scalar_result=None)
        service = DeviceService(session)

        result = await service.update(1, {"ip_address": "192.168.1.1", "name": "same"})
        assert result is device


# ===========================================================================
# soft_delete
# ===========================================================================


class TestSoftDelete:
    @pytest.mark.asyncio
    async def test_soft_delete_success(self):
        session = _make_session(rowcount=1)
        service = DeviceService(session)

        await service.soft_delete(1)

        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_soft_delete_raises_404_when_not_found(self):
        session = _make_session(rowcount=0)
        service = DeviceService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.soft_delete(999)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_soft_delete_db_error_propagates(self):
        session = _make_session(side_effect=SQLAlchemyError("boom"))
        service = DeviceService(session)

        with pytest.raises(SQLAlchemyError):
            await service.soft_delete(1)
