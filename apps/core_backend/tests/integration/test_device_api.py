from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from app.api.dependencies import get_current_user
from app.api.v1.devices import router as devices_router
from app.api.v1.users import router as users_router
from app.models.device import Device
from app.models.user import User, UserRole
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient


@asynccontextmanager
async def mock_session_maker():
    yield AsyncMock()


@asynccontextmanager
async def _noop_lifespan(app: FastAPI) -> AsyncGenerator:
    """Not connect with any database."""
    yield


_test_app = FastAPI(lifespan=_noop_lifespan)
_test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
_test_app.include_router(devices_router)
_test_app.include_router(users_router)


def _device(**kw) -> Device:
    base = dict(
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
        created_by_id=None,
        snmp_config=None,
        ssh_config=None,
        api_config=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    base.update(kw)
    return Device(**base)


def _user(role: UserRole, uid: int = 1) -> User:
    return User(
        id=uid,
        email=f"{role.value}@test.local",
        name=role.value,
        role=role,
        is_active=True,
        password_hash="x",
        created_at=datetime.now(timezone.utc),
    )


ADMIN = _user(UserRole.ADMIN)
OPERATOR = _user(UserRole.OPERATOR, 2)
READONLY = _user(UserRole.READONLY, 3)
AUDITOR = _user(UserRole.AUDITOR, 4)

VALID = dict(
    name="Router-01",
    ip_address="192.168.1.1",
    device_type="router",
    vendor="Cisco",
    model="ISR 4331",
    os_version="IOS-XE 17.6",
    location="Server Room A",
    is_active=True,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def _clean():
    yield
    _test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=_test_app), base_url="http://test"
    ) as ac:
        yield ac


def _as(user: User):
    _test_app.dependency_overrides[get_current_user] = lambda: user


def _svc(mock: MagicMock):
    from app.api.v1 import devices as mod

    _test_app.dependency_overrides[mod.get_device_service] = lambda _=None: mock


# ===========================================================================
# GET /api/v1/devices/
# ===========================================================================


class TestListDevices:
    @pytest.mark.asyncio
    async def test_200_for_readonly(self, client):
        svc = MagicMock(spec=["get_all"])
        svc.get_all = AsyncMock(return_value=([_device()], 1))
        _as(READONLY)
        _svc(svc)
        r = await client.get("/api/v1/devices/")
        assert r.status_code == 200
        assert r.json()["items"][0]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_empty_list(self, client):
        svc = MagicMock(spec=["get_all"])
        svc.get_all = AsyncMock(return_value=([], 0))
        _as(READONLY)
        _svc(svc)
        r = await client.get("/api/v1/devices/")
        assert r.status_code == 200
        assert r.json()["items"] == []

    @pytest.mark.asyncio
    async def test_all_roles_allowed(self, client):
        for user in [ADMIN, OPERATOR, READONLY, AUDITOR]:
            svc = MagicMock(spec=["get_all"])
            svc.get_all = AsyncMock(return_value=([], 0))
            _as(user)
            _svc(svc)
            r = await client.get("/api/v1/devices/")
            assert r.status_code == 200, f"Role {user.role} should have access"

    @pytest.mark.asyncio
    async def test_no_auth_returns_401(self, client):
        r = await client.get("/api/v1/devices/")
        assert r.status_code == 401


# ===========================================================================
# GET /api/v1/devices/{id}
# ===========================================================================


class TestGetDevice:
    @pytest.mark.asyncio
    async def test_returns_device(self, client):
        svc = MagicMock(spec=["get_by_id"])
        svc.get_by_id = AsyncMock(return_value=_device())
        _as(READONLY)
        _svc(svc)
        r = await client.get("/api/v1/devices/1")
        assert r.status_code == 200
        assert r.json()["name"] == "Router-01"

    @pytest.mark.asyncio
    async def test_404_when_missing(self, client):
        svc = MagicMock(spec=["get_by_id"])
        svc.get_by_id = AsyncMock(side_effect=HTTPException(404, "Device not found"))
        _as(READONLY)
        _svc(svc)
        r = await client.get("/api/v1/devices/999")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_auditor_can_read(self, client):
        svc = MagicMock(spec=["get_by_id"])
        svc.get_by_id = AsyncMock(return_value=_device())
        _as(AUDITOR)
        _svc(svc)
        r = await client.get("/api/v1/devices/1")
        assert r.status_code == 200


# ===========================================================================
# POST /api/v1/devices/
# ===========================================================================


class TestCreateDevice:
    @pytest.mark.asyncio
    async def test_admin_creates_201(self, client):
        svc = MagicMock(spec=["create"])
        svc.create = AsyncMock(return_value=_device())
        _as(ADMIN)
        _svc(svc)
        r = await client.post("/api/v1/devices/", json=VALID)
        assert r.status_code == 201
        svc.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_readonly_forbidden(self, client):
        svc = MagicMock(spec=["create"])
        svc.create = AsyncMock()
        _as(READONLY)
        _svc(svc)
        r = await client.post("/api/v1/devices/", json=VALID)
        assert r.status_code == 403
        svc.create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_operator_forbidden(self, client):
        svc = MagicMock(spec=["create"])
        svc.create = AsyncMock()
        _as(OPERATOR)
        _svc(svc)
        r = await client.post("/api/v1/devices/", json=VALID)
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_duplicate_ip_409(self, client):
        svc = MagicMock(spec=["create"])
        svc.create = AsyncMock(
            side_effect=HTTPException(409, "IP address already exists")
        )
        _as(ADMIN)
        _svc(svc)
        r = await client.post("/api/v1/devices/", json=VALID)
        assert r.status_code == 409

    @pytest.mark.asyncio
    async def test_missing_fields_422(self, client):
        _as(ADMIN)
        r = await client.post("/api/v1/devices/", json={"name": "only"})
        assert r.status_code == 422


# ===========================================================================
# PUT /api/v1/devices/{id}
# ===========================================================================


class TestUpdateDevice:
    @pytest.mark.asyncio
    async def test_admin_updates(self, client):
        svc = MagicMock(spec=["update"])
        svc.update = AsyncMock(return_value=_device(os_version="IOS-XE 17.9"))
        _as(ADMIN)
        _svc(svc)
        r = await client.put(
            "/api/v1/devices/1", json={**VALID, "os_version": "IOS-XE 17.9"}
        )
        assert r.status_code == 200
        assert r.json()["os_version"] == "IOS-XE 17.9"

    @pytest.mark.asyncio
    async def test_operator_updates(self, client):
        svc = MagicMock(spec=["update"])
        svc.update = AsyncMock(return_value=_device())
        _as(OPERATOR)
        _svc(svc)
        r = await client.put("/api/v1/devices/1", json=VALID)
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_readonly_forbidden(self, client):
        svc = MagicMock(spec=["update"])
        svc.update = AsyncMock()
        _as(READONLY)
        _svc(svc)
        r = await client.put("/api/v1/devices/1", json=VALID)
        assert r.status_code == 403
        svc.update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_missing_device_404(self, client):
        svc = MagicMock(spec=["update"])
        svc.update = AsyncMock(side_effect=HTTPException(404, "Device not found"))
        _as(ADMIN)
        _svc(svc)
        r = await client.put("/api/v1/devices/999", json=VALID)
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_ip_conflict_409(self, client):
        svc = MagicMock(spec=["update"])
        svc.update = AsyncMock(side_effect=HTTPException(409, "IP already in use"))
        _as(ADMIN)
        _svc(svc)
        r = await client.put("/api/v1/devices/1", json=VALID)
        assert r.status_code == 409


# ===========================================================================
# DELETE /api/v1/devices/{id}
# ===========================================================================


class TestDeleteDevice:
    @pytest.mark.asyncio
    async def test_admin_deletes(self, client):
        svc = MagicMock(spec=["soft_delete"])
        svc.soft_delete = AsyncMock(return_value=None)
        _as(ADMIN)
        _svc(svc)
        r = await client.delete("/api/v1/devices/1")
        assert r.status_code == 200
        svc.soft_delete.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_operator_forbidden(self, client):
        svc = MagicMock(spec=["soft_delete"])
        svc.soft_delete = AsyncMock()
        _as(OPERATOR)
        _svc(svc)
        r = await client.delete("/api/v1/devices/1")
        assert r.status_code == 403
        svc.soft_delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_readonly_forbidden(self, client):
        svc = MagicMock(spec=["soft_delete"])
        svc.soft_delete = AsyncMock()
        _as(READONLY)
        _svc(svc)
        r = await client.delete("/api/v1/devices/1")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_device_404(self, client):
        svc = MagicMock(spec=["soft_delete"])
        svc.soft_delete = AsyncMock(side_effect=HTTPException(404, "Device not found"))
        _as(ADMIN)
        _svc(svc)
        r = await client.delete("/api/v1/devices/999")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_no_auth_401(self, client):
        r = await client.delete("/api/v1/devices/1")
        assert r.status_code == 401
