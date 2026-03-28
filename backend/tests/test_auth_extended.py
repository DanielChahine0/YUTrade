# Extended authentication tests covering edge cases and untested paths.

from app.models.password_reset import PasswordResetCode


# ── Registration edge cases ────────────────────────────────────────────


def test_register_subdomain_not_accepted(client):
    """@subdomain.my.yorku.ca should be rejected."""
    resp = client.post("/auth/register", json={
        "email": "user@subdomain.my.yorku.ca",
        "password": "securepass1",
        "name": "Subdomain User",
    })
    assert resp.status_code in (400, 422)


def test_register_yahoo_domain(client):
    """@yahoo.com domain is rejected."""
    resp = client.post("/auth/register", json={
        "email": "user@yahoo.com",
        "password": "securepass1",
        "name": "Yahoo User",
    })
    assert resp.status_code == 422


def test_register_email_with_plus_sign(client):
    """Email with + alias should be accepted if domain is valid."""
    resp = client.post("/auth/register", json={
        "email": "user+alias@my.yorku.ca",
        "password": "securepass1",
        "name": "Plus User",
    })
    assert resp.status_code == 201


def test_register_trims_or_stores_lowercase(client):
    """Registered email should be stored as lowercase."""
    resp = client.post("/auth/register", json={
        "email": "UPPER@MY.YORKU.CA",
        "password": "securepass1",
        "name": "Upper User",
    })
    assert resp.status_code == 201

    login_resp = client.post("/auth/login", json={
        "email": "upper@my.yorku.ca",
        "password": "securepass1",
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["user"]["email"] == "upper@my.yorku.ca"


def test_register_special_chars_in_name(client):
    """Name with special characters should be accepted."""
    resp = client.post("/auth/register", json={
        "email": "specialname@my.yorku.ca",
        "password": "securepass1",
        "name": "O'Brien-Smith Jr.",
    })
    assert resp.status_code == 201
    assert resp.json()["message"] is not None


def test_register_response_structure(client):
    """Registration response includes user_id and message."""
    resp = client.post("/auth/register", json={
        "email": "struct@my.yorku.ca",
        "password": "securepass1",
        "name": "Struct User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data["user_id"], int)
    assert isinstance(data["message"], str)


def test_register_multibyte_password_72_byte_boundary(client):
    """Multibyte chars that fit within 72 bytes are accepted."""
    # Each emoji is 4 bytes; 18 emojis = 72 bytes
    password = "\U0001f600" * 18
    assert len(password.encode("utf-8")) == 72
    resp = client.post("/auth/register", json={
        "email": "multibyte@my.yorku.ca",
        "password": password,
        "name": "Multibyte PW",
    })
    assert resp.status_code == 201


def test_register_multibyte_password_exceeds_72_bytes(client):
    """Multibyte chars exceeding 72 bytes are rejected."""
    password = "\U0001f600" * 19  # 76 bytes
    resp = client.post("/auth/register", json={
        "email": "multibyte2@my.yorku.ca",
        "password": password,
        "name": "Multibyte PW 2",
    })
    assert resp.status_code == 400


# ── Login edge cases ──────────────────────────────────────────────────


def test_login_returns_bearer_token_type(client):
    """Login response token_type is 'bearer'."""
    client.post("/auth/register", json={
        "email": "tokentype@my.yorku.ca",
        "password": "securepass1",
        "name": "Token Type",
    })
    resp = client.post("/auth/login", json={
        "email": "tokentype@my.yorku.ca",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"


def test_login_after_password_change(client, auth_headers):
    """Old password should fail after changing password."""
    client.post("/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "changedpass1",
    }, headers=auth_headers)

    # Old password should fail
    resp = client.post("/auth/login", json={
        "email": "testuser@my.yorku.ca",
        "password": "testpass123",
    })
    assert resp.status_code == 401


# ── GET /auth/me edge cases ──────────────────────────────────────────


def test_get_me_has_created_at(client, auth_headers):
    """GET /auth/me includes created_at."""
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "created_at" in resp.json()


def test_get_me_has_is_verified(client, auth_headers):
    """GET /auth/me includes is_verified field."""
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_verified"] is True


def test_get_me_expired_or_malformed_token(client):
    """GET /auth/me with a garbage token returns 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert resp.status_code == 401


def test_get_me_missing_bearer_prefix(client):
    """GET /auth/me with token but no 'Bearer' prefix returns 401."""
    resp = client.get("/auth/me", headers={"Authorization": "sometoken"})
    assert resp.status_code in (401, 403)


# ── PATCH /auth/me edge cases ────────────────────────────────────────


def test_update_profile_empty_name(client, auth_headers):
    """PATCH /auth/me with empty name — accepted (no min_length on UpdateProfileRequest.name)."""
    resp = client.patch("/auth/me", json={"name": ""}, headers=auth_headers)
    # Schema has no min_length constraint on name, so this is accepted
    assert resp.status_code == 200


def test_update_profile_long_name(client, auth_headers):
    """PATCH /auth/me with a very long name should succeed or be bounded."""
    long_name = "A" * 200
    resp = client.patch("/auth/me", json={"name": long_name}, headers=auth_headers)
    # Should succeed (no max_length constraint on name in schema)
    assert resp.status_code == 200
    assert resp.json()["name"] == long_name


# ── Change password edge cases ───────────────────────────────────────


def test_change_password_new_short_accepted(client, auth_headers):
    """Short new password — accepted (change_password only checks > 72 bytes, not minimum)."""
    resp = client.post("/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "short",
    }, headers=auth_headers)
    # Service only validates max 72 bytes, no min_length on change
    assert resp.status_code == 200


def test_change_password_same_as_current(client, auth_headers):
    """Changing to the same password should succeed (no restriction)."""
    resp = client.post("/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "testpass123",
    }, headers=auth_headers)
    # Most apps allow this; verify behavior
    assert resp.status_code == 200


def test_change_password_missing_fields(client, auth_headers):
    """Missing current_password or new_password returns 422."""
    resp1 = client.post("/auth/change-password", json={
        "current_password": "testpass123",
    }, headers=auth_headers)
    assert resp1.status_code == 422

    resp2 = client.post("/auth/change-password", json={
        "new_password": "newpass1234",
    }, headers=auth_headers)
    assert resp2.status_code == 422


# ── Delete account edge cases ────────────────────────────────────────


def test_delete_account_cascade_listings(client, db_session):
    """Deleting account also deletes user's listings."""
    from app.models.listing import Listing

    # Register, login, create listing
    client.post("/auth/register", json={
        "email": "cascade@my.yorku.ca",
        "password": "securepass1",
        "name": "Cascade User",
    })
    login_resp = client.post("/auth/login", json={
        "email": "cascade@my.yorku.ca",
        "password": "securepass1",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post("/listings/", data={
        "title": "Will Be Deleted",
        "price": "10.00",
        "category": "Other",
    }, headers=headers)
    listing_id = create_resp.json()["id"]

    # Delete account
    client.post("/auth/delete-account", json={
        "password": "securepass1",
    }, headers=headers)

    # Listing should be gone
    get_resp = client.get(f"/listings/{listing_id}")
    assert get_resp.status_code == 404


def test_delete_account_cascade_messages(client, db_session):
    """Deleting account removes messages sent/received by user."""
    from app.models.message import Message

    # Register two users
    client.post("/auth/register", json={
        "email": "delmsg1@my.yorku.ca", "password": "securepass1", "name": "Del Msg 1",
    })
    client.post("/auth/register", json={
        "email": "delmsg2@my.yorku.ca", "password": "securepass1", "name": "Del Msg 2",
    })
    login1 = client.post("/auth/login", json={"email": "delmsg1@my.yorku.ca", "password": "securepass1"})
    login2 = client.post("/auth/login", json={"email": "delmsg2@my.yorku.ca", "password": "securepass1"})
    h1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    h2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    # User1 creates listing, user2 messages
    listing_resp = client.post("/listings/", data={
        "title": "Msg Test", "price": "10.00", "category": "Other",
    }, headers=h1)
    listing_id = listing_resp.json()["id"]

    client.post(f"/listings/{listing_id}/messages/", json={"content": "Hello!"}, headers=h2)

    # Delete user2's account
    client.post("/auth/delete-account", json={"password": "securepass1"}, headers=h2)

    # Messages should be gone
    msg_count = db_session.query(Message).filter(Message.listing_id == listing_id).count()
    assert msg_count == 0


def test_delete_account_missing_password(client, auth_headers):
    """Delete account without password field returns 422."""
    resp = client.post("/auth/delete-account", json={}, headers=auth_headers)
    assert resp.status_code == 422


# ── Forgot/reset password edge cases ────────────────────────────────


def test_forgot_password_case_insensitive(client):
    """Forgot password should work regardless of email case."""
    client.post("/auth/register", json={
        "email": "forgotcase@my.yorku.ca",
        "password": "securepass1",
        "name": "Forgot Case",
    })
    resp = client.post("/auth/forgot-password", json={
        "email": "ForgotCase@My.YorkU.Ca",
    })
    assert resp.status_code == 200


def test_reset_password_too_long(client, db_session):
    """Reset password with new password exceeding 72 bytes is rejected."""
    client.post("/auth/register", json={
        "email": "resetlong@my.yorku.ca",
        "password": "securepass1",
        "name": "Reset Long",
    })
    client.post("/auth/forgot-password", json={"email": "resetlong@my.yorku.ca"})

    reset = db_session.query(PasswordResetCode).order_by(
        PasswordResetCode.id.desc()
    ).first()

    resp = client.post("/auth/reset-password", json={
        "email": "resetlong@my.yorku.ca",
        "code": reset.code,
        "new_password": "a" * 73,
    })
    assert resp.status_code == 400


def test_reset_password_missing_fields(client):
    """Reset password missing required fields returns 422."""
    resp = client.post("/auth/reset-password", json={
        "email": "someone@my.yorku.ca",
        "code": "123456",
    })
    assert resp.status_code == 422


def test_forgot_password_missing_email(client):
    """Forgot password without email returns 422."""
    resp = client.post("/auth/forgot-password", json={})
    assert resp.status_code == 422


def test_multiple_reset_codes_only_latest_valid(client, db_session):
    """Requesting multiple reset codes deletes previous ones; only the latest works."""
    client.post("/auth/register", json={
        "email": "multicode@my.yorku.ca",
        "password": "securepass1",
        "name": "Multi Code",
    })

    # Request first code, capture it
    client.post("/auth/forgot-password", json={"email": "multicode@my.yorku.ca"})
    first_code = db_session.query(PasswordResetCode).order_by(
        PasswordResetCode.id.desc()
    ).first()
    first_code_value = first_code.code

    # Request second code (deletes the first)
    client.post("/auth/forgot-password", json={"email": "multicode@my.yorku.ca"})
    db_session.expire_all()

    latest = db_session.query(PasswordResetCode).order_by(
        PasswordResetCode.id.desc()
    ).first()

    # First code should no longer work
    resp_old = client.post("/auth/reset-password", json={
        "email": "multicode@my.yorku.ca",
        "code": first_code_value,
        "new_password": "should_fail1",
    })
    assert resp_old.status_code == 400

    # Latest code works
    resp = client.post("/auth/reset-password", json={
        "email": "multicode@my.yorku.ca",
        "code": latest.code,
        "new_password": "brand_new_pw1",
    })
    assert resp.status_code == 200
