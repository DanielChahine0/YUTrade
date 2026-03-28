import pytest
from app.models import User, Listing


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


# ── Basic rating tests ───────────────────────────────────────────────────


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


# ── My rating tests ─────────────────────────────────────────────────────


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


def test_get_my_rating_unauthenticated(client, auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    resp = client.get(f"/listings/{listing_id}/rating/me")
    assert resp.status_code == 401


# ── Update rating tests ─────────────────────────────────────────────────


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


def test_update_rating_comment_only(client, auth_headers, second_auth_headers, db_session):
    """Can update just the comment without changing score."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"comment": "Updated comment"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["comment"] == "Updated comment"
    assert resp.json()["score"] == 4  # Score unchanged


def test_update_rating_unauthenticated(client, auth_headers, db_session):
    """Updating rating without auth returns 401."""
    listing_id = _create_listing(client, auth_headers)
    resp = client.patch(f"/listings/{listing_id}/rating", json={"score": 3})
    assert resp.status_code == 401


# ── Delete rating tests ─────────────────────────────────────────────────


def test_delete_rating(client, auth_headers, second_auth_headers, db_session):
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    resp = client.delete(f"/listings/{listing_id}/rating", headers=second_auth_headers)
    assert resp.status_code == 204

    check = client.get(f"/users/{seller_id}/ratings")
    assert check.json()["total_count"] == 0


def test_delete_rating_unauthenticated(client, auth_headers, db_session):
    """Deleting rating without auth returns 401."""
    listing_id = _create_listing(client, auth_headers)
    resp = client.delete(f"/listings/{listing_id}/rating")
    assert resp.status_code == 401


# ── Listing not found tests ─────────────────────────────────────────────


def test_create_rating_listing_not_found(client, second_auth_headers):
    resp = client.post(
        "/listings/99999/rating",
        json={"score": 5},
        headers=second_auth_headers,
    )
    assert resp.status_code == 404


def test_get_my_rating_listing_not_found(client, auth_headers):
    """Getting my rating for non-existent listing returns 404."""
    resp = client.get("/listings/99999/rating/me", headers=auth_headers)
    assert resp.status_code == 404


# ── Score boundary tests ────────────────────────────────────────────────


def test_rating_score_minimum_1(client, auth_headers, second_auth_headers, db_session):
    """Score of 1 (minimum) is accepted."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 1},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["score"] == 1


def test_rating_score_maximum_5(client, auth_headers, second_auth_headers, db_session):
    """Score of 5 (maximum) is accepted."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["score"] == 5


def test_rating_score_below_minimum(client, auth_headers, second_auth_headers, db_session):
    """Score of 0 is rejected (minimum is 1)."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 0},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_rating_score_above_maximum(client, auth_headers, second_auth_headers, db_session):
    """Score of 6 is rejected (maximum is 5)."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 6},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_rating_score_negative(client, auth_headers, second_auth_headers, db_session):
    """Negative score is rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": -1},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_rating_missing_score(client, auth_headers, second_auth_headers, db_session):
    """Rating without score field is rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"comment": "No score"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


# ── Comment boundary tests ──────────────────────────────────────────────


def test_rating_without_comment(client, auth_headers, second_auth_headers, db_session):
    """Rating without comment is accepted (comment is optional)."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 4},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["comment"] is None


def test_rating_comment_at_max_length(client, auth_headers, second_auth_headers, db_session):
    """Comment of exactly 1000 characters is accepted."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    comment_1000 = "x" * 1000
    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 4, "comment": comment_1000},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert len(resp.json()["comment"]) == 1000


def test_rating_comment_exceeds_max_length(client, auth_headers, second_auth_headers, db_session):
    """Comment exceeding 1000 characters is rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    comment_1001 = "x" * 1001
    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 4, "comment": comment_1001},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


# ── Average score tests ─────────────────────────────────────────────────


def test_average_score_calculation(client, auth_headers, second_auth_headers, db_session):
    """Average score is correctly calculated across multiple ratings."""
    listing1_id = _create_listing(client, auth_headers)
    listing2_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")

    # Second user rates two listings
    _send_message(client, listing1_id, second_auth_headers)
    _send_message(client, listing2_id, second_auth_headers)
    client.post(f"/listings/{listing1_id}/rating", json={"score": 4}, headers=second_auth_headers)
    client.post(f"/listings/{listing2_id}/rating", json={"score": 2}, headers=second_auth_headers)

    resp = client.get(f"/users/{seller_id}/ratings")
    data = resp.json()
    assert data["total_count"] == 2
    assert data["average_score"] == 3.0  # (4 + 2) / 2


def test_get_seller_ratings_nonexistent_user(client):
    """Getting ratings for non-existent seller returns 200 with empty data."""
    resp = client.get("/users/99999/ratings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 0
    assert data["ratings"] == []


# ── Rating response structure tests ──────────────────────────────────────


def test_rating_response_has_timestamps(client, auth_headers, second_auth_headers, db_session):
    """Rating response includes created_at."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert "created_at" in resp.json()


def test_rating_response_includes_ids(client, auth_headers, second_auth_headers, db_session):
    """Rating response includes listing_id, seller_id, rater_id."""
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    rater_id = _get_user_id(db_session, "testuser2@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 3},
        headers=second_auth_headers,
    )
    data = resp.json()
    assert data["listing_id"] == listing_id
    assert data["seller_id"] == seller_id
    assert data["rater_id"] == rater_id


def test_seller_ratings_include_seller_info(client, auth_headers, second_auth_headers, db_session):
    """GET /users/{id}/ratings includes seller info when ratings exist."""
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    resp = client.get(f"/users/{seller_id}/ratings")
    data = resp.json()
    assert data["seller"] is not None
    assert data["seller"]["id"] == seller_id
    assert data["seller"]["name"] == "Test User"
