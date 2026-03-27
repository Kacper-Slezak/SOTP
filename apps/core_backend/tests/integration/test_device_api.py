"""
API (integration) tests for the Device CRUD endpoints.

Uses FastAPI's dependency_overrides + httpx.AsyncClient so NO real database
is required.  The DeviceService is replaced with a MagicMock.

Run with:
    pytest apps/core_backend/tests/integration/test_device_api.py -v
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from app.api.dependencies import get_current_user
from app.main import app
from app.models.device import Device
from app.models.user import User, UserRole
from app.services.device_services import DeviceService
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_device(**overrides) -> Device:
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
        created_by_id=None,
        snmp_config=None,
        ssh_config=None,
        api_config=None,
    )
    defaults.update(overrides)
    return Device(**defaults)


_ADMIN_USER = User(
    id=1,
    email="admin@sotp.test",
    name="Admin",
    role=UserRole.ADMIN,
    is_active=True,
    password_hash="hashed",
    created_at=datetime.now(timezone.utc),
)

_READONLY_USER = User(
    id=2,
    email="readonly@sotp.test",
    name="Reader",
    role=UserRole.READONLY,
    is_active=True,
    password_hash="hashed",
    created_at=datetime.now(timezone.utc),
)

_OPERATOR_USER = User(
    id=3,
    email="operator@sotp.test",
    name="Operator",
    role=UserRole.OPERATOR,
    is_active=True,
    password_hash="hashed",
    created_at=datetime.now(timezone.utc),
)

_VALID_PAYLOAD = {
    "name": "Router-01",
    "ip_address": "192.168.1.1",
    "device_type": "router",
    "vendor": "Cisco",
    "model": "ISR 4331",
    "os_version": "IOS-XE 17.6",
    "location": "Server Room A",
    "is_active": True,
}


# ---------------------------------------------------------------------------
# Base client builder
# ---------------------------------------------------------------------------


def _override_user(user: User):
    app.dependency_overrides[get_current_user] = lambda: user


def _mock_service(mock: MagicMock):
    """Patch DeviceService so every endpoint uses our mock."""
    from app.api.v1 import devices as devices_module

    def _get_service(_session=None):
        return mock

    app.dependency_overrides[devices_module.get_device_service] = _get_service


@pytest_asyncio.fixture(autouse=True)
async def clean_overrides():
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ===========================================================================
# GET /api/v1/devices/
# ===========================================================================


class TestListDevices:
    @pytest.mark.asyncio
    async def test_list_returns_200_for_readonly(self, client):
        d = _make_device()
        svc = MagicMock()
        svc.get_all = AsyncMock(return_value=[d])
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.get("/api/v1/devices/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_list_returns_empty_list(self, client):
        svc = MagicMock()
        svc.get_all = AsyncMock(return_value=[])
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.get("/api/v1/devices/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_requires_auth(self, client):
        """No auth override → 401."""
        resp = await client.get("/api/v1/devices/")
        assert resp.status_code == 401


# ===========================================================================
# GET /api/v1/devices/{id}
# ===========================================================================


class TestGetDevice:
    @pytest.mark.asyncio
    async def test_get_existing_device(self, client):
        d = _make_device()
        svc = MagicMock()
        svc.get_by_id = AsyncMock(return_value=d)
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.get("/api/v1/devices/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Router-01"

    @pytest.mark.asyncio
    async def test_get_nonexistent_device_returns_404(self, client):
        svc = MagicMock()
        svc.get_by_id = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Device not found")
        )
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.get("/api/v1/devices/999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_auditor_can_read_device(self, client):
        auditor = User(
            id=4,
            email="a@sotp.test",
            name="Auditor",
            role=UserRole.AUDITOR,
            is_active=True,
            password_hash="x",
            created_at=datetime.now(timezone.utc),
        )
        d = _make_device()
        svc = MagicMock()
        svc.get_by_id = AsyncMock(return_value=d)
        _override_user(auditor)
        _mock_service(svc)

        resp = await client.get("/api/v1/devices/1")
        assert resp.status_code == 200


# ===========================================================================
# POST /api/v1/devices/
# ===========================================================================


class TestCreateDevice:
    @pytest.mark.asyncio
    async def test_admin_can_create_device(self, client):
        created = _make_device()
        svc = MagicMock()
        svc.create = AsyncMock(return_value=created)
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.post("/api/v1/devices/", json=_VALID_PAYLOAD)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Router-01"

    @pytest.mark.asyncio
    async def test_readonly_cannot_create_device(self, client):
        svc = MagicMock()
        svc.create = AsyncMock()
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.post("/api/v1/devices/", json=_VALID_PAYLOAD)
        assert resp.status_code == 403
        svc.create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_operator_cannot_create_device(self, client):
        svc = MagicMock()
        svc.create = AsyncMock()
        _override_user(_OPERATOR_USER)
        _mock_service(svc)

        resp = await client.post("/api/v1/devices/", json=_VALID_PAYLOAD)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_duplicate_ip_returns_409(self, client):
        svc = MagicMock()
        svc.create = AsyncMock(
            side_effect=HTTPException(
                status_code=409, detail="IP address already exists"
            )
        )
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.post("/api/v1/devices/", json=_VALID_PAYLOAD)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_missing_required_field_returns_422(self, client):
        _override_user(_ADMIN_USER)
        incomplete = {"name": "Router-01"}  # many required fields missing
        resp = await client.post("/api/v1/devices/", json=incomplete)
        assert resp.status_code == 422


# ===========================================================================
# PUT /api/v1/devices/{id}
# ===========================================================================


class TestUpdateDevice:
    @pytest.mark.asyncio
    async def test_admin_can_update_device(self, client):
        updated = _make_device(os_version="IOS-XE 17.9")
        svc = MagicMock()
        svc.update = AsyncMock(return_value=updated)
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        payload = {**_VALID_PAYLOAD, "os_version": "IOS-XE 17.9"}
        resp = await client.put("/api/v1/devices/1", json=payload)
        assert resp.status_code == 200
        assert resp.json()["os_version"] == "IOS-XE 17.9"

    @pytest.mark.asyncio
    async def test_operator_can_update_device(self, client):
        updated = _make_device()
        svc = MagicMock()
        svc.update = AsyncMock(return_value=updated)
        _override_user(_OPERATOR_USER)
        _mock_service(svc)

        resp = await client.put("/api/v1/devices/1", json=_VALID_PAYLOAD)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_readonly_cannot_update_device(self, client):
        svc = MagicMock()
        svc.update = AsyncMock()
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.put("/api/v1/devices/1", json=_VALID_PAYLOAD)
        assert resp.status_code == 403
        svc.update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_nonexistent_device_returns_404(self, client):
        svc = MagicMock()
        svc.update = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Device not found")
        )
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.put("/api/v1/devices/999", json=_VALID_PAYLOAD)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_ip_conflict_returns_409(self, client):
        svc = MagicMock()
        svc.update = AsyncMock(
            side_effect=HTTPException(status_code=409, detail="IP already in use")
        )
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.put("/api/v1/devices/1", json=_VALID_PAYLOAD)
        assert resp.status_code == 409


# ===========================================================================
# DELETE /api/v1/devices/{id}
# ===========================================================================


class TestDeleteDevice:
    @pytest.mark.asyncio
    async def test_admin_can_delete_device(self, client):
        svc = MagicMock()
        svc.soft_delete = AsyncMock(return_value=None)
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.delete("/api/v1/devices/1")
        assert resp.status_code == 200
        svc.soft_delete.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_operator_cannot_delete_device(self, client):
        svc = MagicMock()
        svc.soft_delete = AsyncMock()
        _override_user(_OPERATOR_USER)
        _mock_service(svc)

        resp = await client.delete("/api/v1/devices/1")
        assert resp.status_code == 403
        svc.soft_delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_readonly_cannot_delete_device(self, client):
        svc = MagicMock()
        svc.soft_delete = AsyncMock()
        _override_user(_READONLY_USER)
        _mock_service(svc)

        resp = await client.delete("/api/v1/devices/1")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_device_returns_404(self, client):
        svc = MagicMock()
        svc.soft_delete = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Device not found")
        )
        _override_user(_ADMIN_USER)
        _mock_service(svc)

        resp = await client.delete("/api/v1/devices/999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_delete(self, client):
        """No auth at all → 401 from oauth2 scheme."""
        resp = await client.delete("/api/v1/devices/1")
        assert resp.status_code == 401
