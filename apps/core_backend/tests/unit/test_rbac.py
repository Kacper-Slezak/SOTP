import pytest
from app.api.dependencies import get_current_user
from app.main import app
from app.models.user import User, UserRole
from fastapi.testclient import TestClient

readonly_user = User(
    id=1,
    email="readonly@example.com",
    name="Readonly User",
    role=UserRole.READONLY,
    is_active=True,
)
operator_user = User(
    id=3,
    email="operator@example.com",
    name="Operator User",
    role=UserRole.OPERATOR,
    is_active=True,
)
admin_user = User(
    id=2,
    email="admin@example.com",
    name="Admin User",
    role=UserRole.ADMIN,
    is_active=True,
)


def test_readonly_cannot_post_device():
    app.dependency_overrides[get_current_user] = lambda: readonly_user

    client = TestClient(app)

    response = client.post("/api/v1/devices", json={"name": "Test Device"})
    assert response.status_code == 403


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_readonly_cannot_delete_device():
    app.dependency_overrides[get_current_user] = lambda: readonly_user
    client = TestClient(app)
    response = client.delete("/api/v1/devices/1")
    assert response.status_code == 403


def test_operator_cannot_delete_device():
    app.dependency_overrides[get_current_user] = lambda: operator_user
    client = TestClient(app)
    response = client.delete("/api/v1/devices/1")
    assert response.status_code == 403


def test_admin_cannot_be_tested_without_db_mock():
    # Ten zostawiamy na później
    pass
