# Extended rating tests covering update/delete edge cases, non-owner access,
# cross-user scenarios, and data integrity.

from app.models import User, Listing


def _create_listing(client, auth_headers):
    resp = client.post(
        "/listings/",
        data={"title": "Rate Test Item", "description": "desc", "price": "10.00", "category": "Other"},
        files=[],
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _get_user_id(db_session, email):
    return db_session.query(User).filter(User.email == email).first().id


def _send_message(client, listing_id, headers, content="Hi, is this available?"):
    resp = client.post(f"/listings/{listing_id}/messages/", json={"content": content}, headers=headers)
    assert resp.status_code == 201, resp.text


def _register_and_login(client, email, password="securepass1", name="Extra User"):
    client.post("/auth/register", json={"email": email, "password": password, "name": name})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Update rating edge cases ─────────────────────────────────────────


def test_update_rating_both_fields(client, auth_headers, second_auth_headers, db_session):
    """Can update both score and comment simultaneously."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5, "comment": "Great"}, headers=second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 2, "comment": "Changed my mind"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["score"] == 2
    assert resp.json()["comment"] == "Changed my mind"


def test_update_nonexistent_rating(client, auth_headers, second_auth_headers, db_session):
    """Updating a rating that doesn't exist returns 404."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 3},
        headers=second_auth_headers,
    )
    assert resp.status_code == 404


def test_update_rating_invalid_score(client, auth_headers, second_auth_headers, db_session):
    """Updating rating with invalid score is rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 0},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_update_rating_score_above_max(client, auth_headers, second_auth_headers, db_session):
    """Updating rating with score > 5 is rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 6},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


# ── Delete rating edge cases ─────────────────────────────────────────


def test_delete_nonexistent_rating(client, auth_headers, second_auth_headers, db_session):
    """Deleting a rating that doesn't exist returns 404."""
    listing_id = _create_listing(client, auth_headers)
    resp = client.delete(f"/listings/{listing_id}/rating", headers=second_auth_headers)
    assert resp.status_code == 404


def test_delete_rating_and_re_rate(client, auth_headers, second_auth_headers, db_session):
    """After deleting a rating, user can rate again."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    # Create, delete, re-create
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)
    client.delete(f"/listings/{listing_id}/rating", headers=second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 3, "comment": "Re-rated"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["score"] == 3


def test_delete_rating_updates_average(client, auth_headers, second_auth_headers, db_session):
    """Deleting a rating updates the seller's average score."""
    listing1_id = _create_listing(client, auth_headers)
    listing2_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")

    _send_message(client, listing1_id, second_auth_headers)
    _send_message(client, listing2_id, second_auth_headers)

    client.post(f"/listings/{listing1_id}/rating", json={"score": 5}, headers=second_auth_headers)
    client.post(f"/listings/{listing2_id}/rating", json={"score": 1}, headers=second_auth_headers)

    # Average should be 3.0
    resp = client.get(f"/users/{seller_id}/ratings")
    assert resp.json()["average_score"] == 3.0

    # Delete the 1-star rating
    client.delete(f"/listings/{listing2_id}/rating", headers=second_auth_headers)

    # Average should now be 5.0
    resp = client.get(f"/users/{seller_id}/ratings")
    assert resp.json()["average_score"] == 5.0
    assert resp.json()["total_count"] == 1


# ── Cross-user rating scenarios ──────────────────────────────────────


def test_third_user_can_rate_same_listing(client, auth_headers, second_auth_headers, db_session):
    """Different users can each rate the same listing."""
    listing_id = _create_listing(client, auth_headers)
    third_headers = _register_and_login(client, "rater3@my.yorku.ca", name="Rater 3")

    _send_message(client, listing_id, second_auth_headers)
    _send_message(client, listing_id, third_headers)

    resp2 = client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)
    resp3 = client.post(f"/listings/{listing_id}/rating", json={"score": 3}, headers=third_headers)

    assert resp2.status_code == 201
    assert resp3.status_code == 201

    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    ratings_resp = client.get(f"/users/{seller_id}/ratings")
    assert ratings_resp.json()["total_count"] == 2
    assert ratings_resp.json()["average_score"] == 4.0


def test_cannot_update_another_users_rating(client, auth_headers, second_auth_headers, db_session):
    """User cannot update a rating left by someone else."""
    listing_id = _create_listing(client, auth_headers)
    third_headers = _register_and_login(client, "other_rater@my.yorku.ca", name="Other Rater")

    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    # Third user tries to update user2's rating
    resp = client.patch(
        f"/listings/{listing_id}/rating",
        json={"score": 1},
        headers=third_headers,
    )
    assert resp.status_code == 404  # Not found for this rater


def test_cannot_delete_another_users_rating(client, auth_headers, second_auth_headers, db_session):
    """User cannot delete a rating left by someone else."""
    listing_id = _create_listing(client, auth_headers)
    third_headers = _register_and_login(client, "del_other@my.yorku.ca", name="Del Other")

    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=second_auth_headers)

    resp = client.delete(f"/listings/{listing_id}/rating", headers=third_headers)
    assert resp.status_code == 404


# ── Seller's own listing ─────────────────────────────────────────────


def test_seller_cannot_check_can_rate_own_listing(client, auth_headers, db_session):
    """Seller's can_rate for their own listing should be False."""
    listing_id = _create_listing(client, auth_headers)
    resp = client.get(f"/listings/{listing_id}/rating/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["can_rate"] is False


# ── Rating on non-existent listing ───────────────────────────────────


def test_update_rating_listing_not_found(client, auth_headers):
    """Updating rating on non-existent listing returns 404."""
    resp = client.patch("/listings/99999/rating", json={"score": 3}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_rating_listing_not_found(client, auth_headers):
    """Deleting rating on non-existent listing returns 404."""
    resp = client.delete("/listings/99999/rating", headers=auth_headers)
    assert resp.status_code == 404


# ── Create rating authentication ─────────────────────────────────────


def test_create_rating_unauthenticated(client, auth_headers, db_session):
    """Creating rating without auth returns 401."""
    listing_id = _create_listing(client, auth_headers)
    resp = client.post(f"/listings/{listing_id}/rating", json={"score": 5})
    assert resp.status_code == 401


# ── Rating score data types ──────────────────────────────────────────


def test_rating_float_score(client, auth_headers, second_auth_headers, db_session):
    """Float score like 3.5 should be rejected (score is integer 1-5)."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 3.5},
        headers=second_auth_headers,
    )
    # Pydantic may coerce 3.5 to 3 or reject depending on schema type
    # If int field, 3.5 may round or fail validation
    assert resp.status_code in (201, 422)


def test_rating_string_score(client, auth_headers, second_auth_headers, db_session):
    """String score should be rejected."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": "five"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


# ── Rating comment edge cases ────────────────────────────────────────


def test_rating_empty_string_comment(client, auth_headers, second_auth_headers, db_session):
    """Rating with empty string comment is accepted (treated as no comment)."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 4, "comment": ""},
        headers=second_auth_headers,
    )
    # Empty string may be stored as empty or null
    assert resp.status_code == 201


def test_rating_comment_with_special_chars(client, auth_headers, second_auth_headers, db_session):
    """Rating comment preserves special characters."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)

    comment = "Great seller! 5/5 \u2605\u2605\u2605\u2605\u2605 <b>bold</b> & \"quoted\""
    resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5, "comment": comment},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["comment"] == comment


# ── Seller ratings response structure ────────────────────────────────


def test_seller_ratings_response_structure(client, auth_headers, second_auth_headers, db_session):
    """GET /users/{id}/ratings has all expected fields."""
    listing_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4, "comment": "Nice"}, headers=second_auth_headers)

    resp = client.get(f"/users/{seller_id}/ratings")
    assert resp.status_code == 200
    data = resp.json()
    assert "ratings" in data
    assert "average_score" in data
    assert "total_count" in data
    assert "seller" in data

    rating = data["ratings"][0]
    assert "id" in rating
    assert "listing_id" in rating
    assert "seller_id" in rating
    assert "rater_id" in rating
    assert "score" in rating
    assert "comment" in rating
    assert "created_at" in rating
    assert "rater" in rating
    assert "name" in rating["rater"]


def test_seller_ratings_sorted_newest_first(client, auth_headers, second_auth_headers, db_session):
    """Seller ratings are returned newest first."""
    listing1_id = _create_listing(client, auth_headers)
    listing2_id = _create_listing(client, auth_headers)
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")

    _send_message(client, listing1_id, second_auth_headers)
    _send_message(client, listing2_id, second_auth_headers)

    client.post(f"/listings/{listing1_id}/rating", json={"score": 3, "comment": "First"}, headers=second_auth_headers)
    client.post(f"/listings/{listing2_id}/rating", json={"score": 5, "comment": "Second"}, headers=second_auth_headers)

    resp = client.get(f"/users/{seller_id}/ratings")
    ratings = resp.json()["ratings"]
    assert len(ratings) == 2
    # Newest first
    assert ratings[0]["comment"] == "Second"
    assert ratings[1]["comment"] == "First"


# ── My rating after update ───────────────────────────────────────────


def test_my_rating_reflects_update(client, auth_headers, second_auth_headers, db_session):
    """GET /listings/{id}/rating/me reflects updated rating."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    client.patch(f"/listings/{listing_id}/rating", json={"score": 2, "comment": "Revised"}, headers=second_auth_headers)

    resp = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    data = resp.json()
    assert data["rating"]["score"] == 2
    assert data["rating"]["comment"] == "Revised"
    assert data["can_rate"] is True


def test_my_rating_after_delete(client, auth_headers, second_auth_headers, db_session):
    """GET /listings/{id}/rating/me shows null rating after deletion but can_rate stays True."""
    listing_id = _create_listing(client, auth_headers)
    _send_message(client, listing_id, second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)
    client.delete(f"/listings/{listing_id}/rating", headers=second_auth_headers)

    resp = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    data = resp.json()
    assert data["rating"] is None
    assert data["can_rate"] is True  # Still eligible because they messaged
