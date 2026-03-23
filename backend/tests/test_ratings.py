import pytest
from app.models import User, Listing, VerificationCode


# ── helpers ──────────────────────────────────────────────────────────────────

def _create_listing(client, auth_headers):
    """Create a basic listing and return its id."""
    resp = client.post(
        "/listings/",
        data={"title": "Test Item", "description": "desc", "price": "10.00", "category": "Other"},
        files=[],
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _get_user_id(db_session, email):
    return db_session.query(User).filter(User.email == email).first().id


def _send_message(client, listing_id, headers, content="Hi, is this available?"):
    resp = client.post(
        f"/listings/{listing_id}/messages/",
        json={"content": content},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp


# ── tests ─────────────────────────────────────────────────────────────────────

def test_get_seller_ratings_empty(client, auth_headers, db_session):
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    resp = client.get(f"/users/{seller_id}/ratings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 0
    assert data["average_score"] is None
    assert data["ratings"] == []


def test_cannot_rate_without_messaging(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5},
        headers=second_auth_headers,
    )
    assert resp.status_code == 400
    assert "contacted" in resp.json()["detail"].lower()


def test_cannot_rate_own_listing(client, auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "own" in resp.json()["detail"].lower()


def test_create_rating_success(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5, "comment": "Great seller!"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 5
    assert data["comment"] == "Great seller!"
    assert data["listing_id"] == listing_id
    assert data["rater"]["name"] == "Test User 2"


def test_get_seller_ratings_after_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    resp = client.get(f"/users/{seller_id}/ratings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 1
    assert data["average_score"] == 5.0
    assert len(data["ratings"]) == 1


def test_duplicate_rating_rejected(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 3},
        headers=second_auth_headers,
    )
    assert resp.status_code == 409


def test_get_my_rating_before_messaging(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    resp = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] is None
    assert data["can_rate"] is False


def test_get_my_rating_after_messaging_before_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] is None
    assert data["can_rate"] is True


def test_get_my_rating_after_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4, "comment": "Good"}, headers=second_auth_headers)

    resp = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] is not None
    assert data["rating"]["score"] == 4
    assert data["can_rate"] is True


def test_update_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 3},
        headers=second_auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["score"] == 3


def test_delete_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    resp = client.delete(f"/listings/{listing_id}/rating", headers=second_auth_headers)
    assert resp.status_code == 204

    check = client.get(f"/users/{seller_id}/ratings")
    assert check.json()["total_count"] == 0


def test_get_my_rating_unauthenticated(client, auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    resp = client.get(f"/listings/{listing_id}/rating/me")
    assert resp.status_code == 401


def test_create_rating_listing_not_found(client, second_auth_headers):
    resp = client.post(
        "/listings/99999/rating",
        json={"score": 5},
        headers=second_auth_headers,
    )
    assert resp.status_code == 404
