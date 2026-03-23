import asyncio
import os
from datetime import datetime, timedelta, timezone

import jose
import pytest
from app.core.config import Config
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import text

# 1. Define the CI Skip Flag
# This checks if the 'CI' environment variable is set to 'true'.
skip_in_ci = pytest.mark.skipif(
    os.environ.get("CI", "false").lower() == "true",
    reason="Local test only, skipping in CI environments",
)

# Apply the skip flag to the entire file (optional, but cleaner than decorating every function)
pytestmark = skip_in_ci

EXPIRED_TOKEN = jose.jwt.encode(
    {
        "sub": "1",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    },
    Config.SECRET_KEY,
    algorithm=Config.ALGORITHM,
)


@pytest.fixture(autouse=True)
async def clean_db():
    """Kept async because your SQLAlchemy engine (create_postgres) appears to be async."""
    from app.utils.databases import create_postgres

    engine = create_postgres()
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await engine.dispose()


@pytest.fixture
def client():
    """Provides a synchronous test client."""
    return TestClient(app)


def create_and_elevate_user(client: TestClient, email: str, role: str) -> str:
    """Helper to register a user, manually elevate their role in the DB, and return a token."""
    # 1. Register
    client.post(
        "/api/v1/auth/register",
        json={"name": f"User {role}", "email": email, "password": "StrongPassword123!"},
    )

    # 2. Elevate role (Requires a quick async runner since DB connection is async)
    async def update_role():
        from app.utils.databases import create_postgres

        engine = create_postgres()
        async with engine.begin() as conn:
            await conn.execute(
                text("UPDATE users SET role = :role WHERE email = :email"),
                {"role": role, "email": email},
            )
        await engine.dispose()

    asyncio.run(update_role())

    # 3. Login
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "StrongPassword123!"}
    )
    return response.json()["access_token"]


# --- Registration Tests ---


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 201


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User 2",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 409


def test_register_invalid_data(client):
    response = client.post(
        "/api/v1/auth/register", json={"name": "Test User", "email": "not-an-email"}
    )
    assert response.status_code == 422


# --- Login Tests ---


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "StrongPassword123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_wrong@example.com", "password": "password"},
    )
    assert response.status_code in [401, 404]


# --- Token Refresh Tests ---


def test_refresh_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "StrongPassword123!"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_refresh_invalid_token(client):
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401


# --- Endpoint Protection Tests ---


def test_protected_endpoint_with_valid_token(client):
    access_token = create_and_elevate_user(client, "test@example.com", "READONLY")
    response = client.get(
        "/api/v1/devices", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


def test_protected_endpoint_without_token(client):
    response = client.get("/api/v1/devices")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client):
    response = client.get(
        "/api/v1/devices", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code in [401, 403]


def test_protected_endpoint_with_expired_token(client):
    response = client.get(
        "/api/v1/devices", headers={"Authorization": f"Bearer {EXPIRED_TOKEN}"}
    )
    assert response.status_code == 401


# --- RBAC Tests ---


def test_rbac_delete_device_admin(client):
    admin_token = create_and_elevate_user(client, "admin@example.com", "ADMIN")
    response = client.delete(
        "/api/v1/devices/1", headers={"Authorization": f"Bearer {admin_token}"}
    )
    # The crucial check here is that it's NOT a 403 Forbidden.
    assert response.status_code != 403


def test_rbac_delete_device_readonly(client):
    readonly_token = create_and_elevate_user(client, "readonly@example.com", "READONLY")
    response = client.delete(
        "/api/v1/devices/1", headers={"Authorization": f"Bearer {readonly_token}"}
    )
    assert response.status_code == 403
