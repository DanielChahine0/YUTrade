# Assigned to: Daniel Chahine
# Phase: 1 (B1.9)
#
# TODO: Write tests for authentication endpoints.
#
# Test cases to implement:
#
# test_register_success:
#   - POST /auth/register with valid YorkU email
#   - Assert 201 status, response has "user_id" and "message"
#
# test_register_invalid_domain:
#   - POST /auth/register with non-YorkU email (e.g. "user@gmail.com")
#   - Assert 400 status
#
# test_register_duplicate_email:
#   - Register once, then register again with same email
#   - Assert 409 status on second attempt
#
# test_login_success:
#   - Register a user
#   - POST /auth/login with correct credentials
#   - Assert 200 status, response has "access_token" and "user"
#
# test_login_wrong_password:
#   - Register a user
#   - POST /auth/login with wrong password
#   - Assert 401 status


def test_register_success(client):
    """POST /auth/register with a valid YorkU email returns 201."""
    resp = client.post("/auth/register", json={
        "email": "newuser@my.yorku.ca",
        "password": "securepass1",
        "name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "user_id" in data
    assert "message" in data


def test_register_invalid_domain(client):
    """POST /auth/register with a non-YorkU email returns 400 (validation error)."""
    resp = client.post("/auth/register", json={
        "email": "user@gmail.com",
        "password": "securepass1",
        "name": "Bad Domain",
    })
    assert resp.status_code == 422  # Pydantic validation error


def test_register_duplicate_email(client):
    """Registering twice with the same email returns 409 on the second attempt."""
    payload = {
        "email": "duplicate@my.yorku.ca",
        "password": "securepass1",
        "name": "Dup User",
    }
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 409


def test_login_success(client):
    """Login with correct credentials after registration returns 200 with token."""
    client.post("/auth/register", json={
        "email": "loginok@my.yorku.ca",
        "password": "securepass1",
        "name": "Login User",
    })

    resp = client.post("/auth/login", json={
        "email": "loginok@my.yorku.ca",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "loginok@my.yorku.ca"


def test_login_wrong_password(client):
    """Login with wrong password returns 401."""
    client.post("/auth/register", json={
        "email": "wrongpw@my.yorku.ca",
        "password": "securepass1",
        "name": "WrongPW User",
    })

    resp = client.post("/auth/login", json={
        "email": "wrongpw@my.yorku.ca",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
