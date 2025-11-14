from fastapi.testclient import TestClient


def test_register_creates_user_and_returns_token(client: TestClient):
    response = client.post(
        "/api/register",
        json={
            "email": "alice@example.com",
            "password": "strong-password",
            "full_name": "Alice Doe",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_returns_token_for_valid_credentials(client: TestClient):
    client.post(
        "/api/register",
        json={
            "email": "bob@example.com",
            "password": "another-strong-password",
            "full_name": "Bob Smith",
        },
    )

    response = client.post(
        "/api/login",
        json={
            "email": "bob@example.com",
            "password": "another-strong-password",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_fails_for_bad_credentials(client: TestClient):
    client.post(
        "/api/register",
        json={
            "email": "charlie@example.com",
            "password": "charlies-password",
            "full_name": "Charlie Kon",
        },
    )

    response = client.post(
        "/api/login",
        json={
            "email": "charlie@example.com",
            "password": "invalid-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

