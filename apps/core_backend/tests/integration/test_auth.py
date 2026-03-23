from datetime import datetime, timedelta, timezone

import jose
import pytest
from app.core.config import Config
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import text

expired_token = jose.jwt.encode(
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
    from app.utils.databases import create_postgres

    engine = create_postgres()
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await engine.dispose()


def test_register_success():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 201


def test_register_duplicate_email():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User 2",
            "email": "test@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 400


def test_register_invalid_data():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/register", json={"name": "Test User", "email": "not-an-email"}
    )
    assert response.status_code == 422


def test_login_success():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "access_token" not in data
    assert "refresh_token" not in data


def test_login_nonexistent_user():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_wrong@example.com", "password": "password"},
    )
    assert response.status_code == 401


def test_refresh_success():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "password"}
    )
    refresh_token = login_response.json()["refresh_token"]
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_refresh_invalid_token():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password"},
    )
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "password"}
    )
    access_token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "READONLY"


def test_protected_endpoint_without_token():
    client = TestClient(app)
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token():
    client = TestClient(app)
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def expired_token():
    client = TestClient(app)
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
