# Assigned to: Daniel Chahine
# Phase: 1 (B1.9)
#
# Comprehensive authentication tests covering:
# - Registration (valid/invalid emails, password boundaries, empty fields)
# - Login (success, wrong password, non-existent user)
# - GET /auth/me, PATCH /auth/me
# - Change password, delete account
# - Forgot/reset password flow


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
    """POST /auth/register with a non-YorkU email returns 422 (validation error)."""
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


# ── Registration boundary tests ─────────────────────────────────────────


def test_register_yorku_ca_domain(client):
    """@yorku.ca domain is also accepted for registration."""
    resp = client.post("/auth/register", json={
        "email": "faculty@yorku.ca",
        "password": "securepass1",
        "name": "Faculty User",
    })
    assert resp.status_code == 201


def test_register_case_insensitive_email(client):
    """Email is stored lowercase; duplicate detection is case-insensitive."""
    client.post("/auth/register", json={
        "email": "CaSeUser@My.YorkU.Ca",
        "password": "securepass1",
        "name": "Case User",
    })
    # Same email, different case → should conflict
    resp = client.post("/auth/register", json={
        "email": "caseuser@my.yorku.ca",
        "password": "securepass1",
        "name": "Case User 2",
    })
    assert resp.status_code == 409


def test_register_password_too_short(client):
    """Password shorter than 8 characters is rejected (422)."""
    resp = client.post("/auth/register", json={
        "email": "shortpw@my.yorku.ca",
        "password": "1234567",
        "name": "Short PW",
    })
    assert resp.status_code == 422


def test_register_password_exactly_8_chars(client):
    """Password of exactly 8 characters is accepted."""
    resp = client.post("/auth/register", json={
        "email": "exact8@my.yorku.ca",
        "password": "12345678",
        "name": "Exact 8",
    })
    assert resp.status_code == 201


def test_register_password_too_long_bcrypt(client):
    """Password exceeding 72 bytes (bcrypt limit) is rejected."""
    long_password = "a" * 73  # 73 ASCII bytes
    resp = client.post("/auth/register", json={
        "email": "longpw@my.yorku.ca",
        "password": long_password,
        "name": "Long PW",
    })
    assert resp.status_code == 400


def test_register_password_exactly_72_bytes(client):
    """Password of exactly 72 bytes is accepted."""
    password_72 = "a" * 72
    resp = client.post("/auth/register", json={
        "email": "pw72@my.yorku.ca",
        "password": password_72,
        "name": "72 Byte PW",
    })
    assert resp.status_code == 201


def test_register_empty_name(client):
    """Empty name (whitespace only) is rejected (422)."""
    resp = client.post("/auth/register", json={
        "email": "noname@my.yorku.ca",
        "password": "securepass1",
        "name": "   ",
    })
    assert resp.status_code == 422


def test_register_missing_email(client):
    """Missing email field returns 422."""
    resp = client.post("/auth/register", json={
        "password": "securepass1",
        "name": "No Email",
    })
    assert resp.status_code == 422


def test_register_missing_password(client):
    """Missing password field returns 422."""
    resp = client.post("/auth/register", json={
        "email": "nopw@my.yorku.ca",
        "name": "No Password",
    })
    assert resp.status_code == 422


def test_register_missing_name(client):
    """Missing name field returns 422."""
    resp = client.post("/auth/register", json={
        "email": "noname2@my.yorku.ca",
        "password": "securepass1",
    })
    assert resp.status_code == 422


def test_register_invalid_email_format(client):
    """Malformed email (not a valid email address) returns 422."""
    resp = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "securepass1",
        "name": "Bad Email",
    })
    assert resp.status_code == 422


def test_register_hotmail_domain(client):
    """@hotmail.com domain is rejected."""
    resp = client.post("/auth/register", json={
        "email": "user@hotmail.com",
        "password": "securepass1",
        "name": "Hotmail User",
    })
    assert resp.status_code == 422


def test_register_outlook_domain(client):
    """@outlook.com domain is rejected."""
    resp = client.post("/auth/register", json={
        "email": "user@outlook.com",
        "password": "securepass1",
        "name": "Outlook User",
    })
    assert resp.status_code == 422


def test_register_empty_password(client):
    """Empty string password is rejected."""
    resp = client.post("/auth/register", json={
        "email": "emptypw@my.yorku.ca",
        "password": "",
        "name": "Empty PW",
    })
    assert resp.status_code == 422


# ── Login boundary tests ────────────────────────────────────────────────


def test_login_nonexistent_user(client):
    """Login with an email that was never registered returns 404."""
    resp = client.post("/auth/login", json={
        "email": "noone@my.yorku.ca",
        "password": "anypassword1",
    })
    assert resp.status_code == 404


def test_login_case_insensitive_email(client):
    """Login works regardless of email case."""
    client.post("/auth/register", json={
        "email": "caselogin@my.yorku.ca",
        "password": "securepass1",
        "name": "Case Login",
    })
    resp = client.post("/auth/login", json={
        "email": "CaseLogin@My.YorkU.Ca",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_missing_email(client):
    """Login without email returns 422."""
    resp = client.post("/auth/login", json={
        "password": "securepass1",
    })
    assert resp.status_code == 422


def test_login_missing_password(client):
    """Login without password returns 422."""
    resp = client.post("/auth/login", json={
        "email": "user@my.yorku.ca",
    })
    assert resp.status_code == 422


def test_login_empty_body(client):
    """Login with empty JSON body returns 422."""
    resp = client.post("/auth/login", json={})
    assert resp.status_code == 422


def test_login_response_contains_user_info(client):
    """Login response includes user details (id, email, name, is_verified)."""
    client.post("/auth/register", json={
        "email": "fullinfo@my.yorku.ca",
        "password": "securepass1",
        "name": "Full Info",
    })
    resp = client.post("/auth/login", json={
        "email": "fullinfo@my.yorku.ca",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    user = resp.json()["user"]
    assert user["email"] == "fullinfo@my.yorku.ca"
    assert user["name"] == "Full Info"
    assert user["is_verified"] is True
    assert "id" in user
    assert "created_at" in user


def test_login_response_does_not_expose_password(client):
    """Login response must never include password_hash."""
    client.post("/auth/register", json={
        "email": "nopwhash@my.yorku.ca",
        "password": "securepass1",
        "name": "No PW Hash",
    })
    resp = client.post("/auth/login", json={
        "email": "nopwhash@my.yorku.ca",
        "password": "securepass1",
    })
    data = resp.json()
    assert "password_hash" not in data
    assert "password_hash" not in data.get("user", {})
    assert "password" not in data.get("user", {})


# ── GET /auth/me tests ──────────────────────────────────────────────────


def test_get_me_authenticated(client, auth_headers):
    """GET /auth/me returns current user profile."""
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "testuser@my.yorku.ca"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "password_hash" not in data


def test_get_me_unauthenticated(client):
    """GET /auth/me without token returns 401."""
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_get_me_invalid_token(client):
    """GET /auth/me with an invalid token returns 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken123"})
    assert resp.status_code == 401


# ── PATCH /auth/me tests ────────────────────────────────────────────────


def test_update_profile_name(client, auth_headers):
    """PATCH /auth/me updates the user's display name."""
    resp = client.patch("/auth/me", json={"name": "Updated Name"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


def test_update_profile_unauthenticated(client):
    """PATCH /auth/me without token returns 401."""
    resp = client.patch("/auth/me", json={"name": "Hacker"})
    assert resp.status_code == 401


def test_update_profile_persists(client, auth_headers):
    """After updating name, GET /auth/me reflects the change."""
    client.patch("/auth/me", json={"name": "Persisted Name"}, headers=auth_headers)
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.json()["name"] == "Persisted Name"


# ── Change password tests ───────────────────────────────────────────────


def test_change_password_success(client, auth_headers):
    """Changing password with correct current password succeeds."""
    resp = client.post("/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "newpass1234",
    }, headers=auth_headers)
    assert resp.status_code == 200

    # Verify login works with new password
    login_resp = client.post("/auth/login", json={
        "email": "testuser@my.yorku.ca",
        "password": "newpass1234",
    })
    assert login_resp.status_code == 200


def test_change_password_wrong_current(client, auth_headers):
    """Changing password with wrong current password returns 400."""
    resp = client.post("/auth/change-password", json={
        "current_password": "wrongcurrent",
        "new_password": "newpass1234",
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_change_password_unauthenticated(client):
    """Changing password without token returns 401."""
    resp = client.post("/auth/change-password", json={
        "current_password": "anything",
        "new_password": "newpass1234",
    })
    assert resp.status_code == 401


def test_change_password_too_long(client, auth_headers):
    """New password exceeding 72 bytes is rejected."""
    resp = client.post("/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "a" * 73,
    }, headers=auth_headers)
    assert resp.status_code == 400


# ── Delete account tests ────────────────────────────────────────────────


def test_delete_account_success(client):
    """Deleting account with correct password succeeds."""
    # Register a throwaway user
    client.post("/auth/register", json={
        "email": "delete_me@my.yorku.ca",
        "password": "securepass1",
        "name": "Delete Me",
    })
    login_resp = client.post("/auth/login", json={
        "email": "delete_me@my.yorku.ca",
        "password": "securepass1",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/auth/delete-account", json={
        "password": "securepass1",
    }, headers=headers)
    assert resp.status_code == 200

    # Verify user can no longer log in
    login_resp2 = client.post("/auth/login", json={
        "email": "delete_me@my.yorku.ca",
        "password": "securepass1",
    })
    assert login_resp2.status_code == 404


def test_delete_account_wrong_password(client, auth_headers):
    """Deleting account with wrong password returns 400."""
    resp = client.post("/auth/delete-account", json={
        "password": "wrongpassword",
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_delete_account_unauthenticated(client):
    """Deleting account without token returns 401."""
    resp = client.post("/auth/delete-account", json={
        "password": "anything",
    })
    assert resp.status_code == 401


# ── Forgot / reset password tests ───────────────────────────────────────


def test_forgot_password_existing_user(client):
    """Forgot password for an existing user returns 200."""
    client.post("/auth/register", json={
        "email": "forgot@my.yorku.ca",
        "password": "securepass1",
        "name": "Forgot User",
    })
    resp = client.post("/auth/forgot-password", json={
        "email": "forgot@my.yorku.ca",
    })
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_forgot_password_nonexistent_user(client):
    """Forgot password for non-existent user returns 404."""
    resp = client.post("/auth/forgot-password", json={
        "email": "nonexistent@my.yorku.ca",
    })
    assert resp.status_code == 404


def test_reset_password_invalid_code(client):
    """Reset password with wrong code returns 400."""
    client.post("/auth/register", json={
        "email": "resetbad@my.yorku.ca",
        "password": "securepass1",
        "name": "Reset Bad",
    })
    client.post("/auth/forgot-password", json={"email": "resetbad@my.yorku.ca"})

    resp = client.post("/auth/reset-password", json={
        "email": "resetbad@my.yorku.ca",
        "code": "000000",
        "new_password": "newpassword1",
    })
    assert resp.status_code == 400


def test_reset_password_code_wrong_length(client):
    """Reset password code not exactly 6 chars returns 422."""
    resp = client.post("/auth/reset-password", json={
        "email": "anyone@my.yorku.ca",
        "code": "12345",
        "new_password": "newpassword1",
    })
    assert resp.status_code == 422


def test_reset_password_short_new_password(client):
    """Reset password with new password < 8 chars returns 422."""
    resp = client.post("/auth/reset-password", json={
        "email": "anyone@my.yorku.ca",
        "code": "123456",
        "new_password": "short",
    })
    assert resp.status_code == 422


def test_reset_password_nonexistent_email(client):
    """Reset password for email not in DB returns 400."""
    resp = client.post("/auth/reset-password", json={
        "email": "nobody@my.yorku.ca",
        "code": "123456",
        "new_password": "newpassword1",
    })
    assert resp.status_code == 400


def test_reset_password_success(client, db_session):
    """Full forgot→reset flow: request code, use it, login with new password."""
    from app.models.password_reset import PasswordResetCode

    client.post("/auth/register", json={
        "email": "resetok@my.yorku.ca",
        "password": "securepass1",
        "name": "Reset OK",
    })
    client.post("/auth/forgot-password", json={"email": "resetok@my.yorku.ca"})

    # Retrieve the code from DB
    reset = db_session.query(PasswordResetCode).order_by(
        PasswordResetCode.id.desc()
    ).first()
    assert reset is not None

    resp = client.post("/auth/reset-password", json={
        "email": "resetok@my.yorku.ca",
        "code": reset.code,
        "new_password": "brand_new_pw",
    })
    assert resp.status_code == 200

    # Verify login with new password
    login_resp = client.post("/auth/login", json={
        "email": "resetok@my.yorku.ca",
        "password": "brand_new_pw",
    })
    assert login_resp.status_code == 200


def test_reset_password_code_cannot_be_reused(client, db_session):
    """A reset code can only be used once."""
    from app.models.password_reset import PasswordResetCode

    client.post("/auth/register", json={
        "email": "reuse@my.yorku.ca",
        "password": "securepass1",
        "name": "Reuse Test",
    })
    client.post("/auth/forgot-password", json={"email": "reuse@my.yorku.ca"})

    reset = db_session.query(PasswordResetCode).order_by(
        PasswordResetCode.id.desc()
    ).first()

    # First use succeeds
    resp1 = client.post("/auth/reset-password", json={
        "email": "reuse@my.yorku.ca",
        "code": reset.code,
        "new_password": "first_reset1",
    })
    assert resp1.status_code == 200

    # Second use fails
    resp2 = client.post("/auth/reset-password", json={
        "email": "reuse@my.yorku.ca",
        "code": reset.code,
        "new_password": "second_reset",
    })
    assert resp2.status_code == 400
