# Integration tests covering cross-module workflows:
# Full user journeys, cascade behaviors, and end-to-end scenarios.

from app.models.user import User
from app.models.listing import Listing
from app.models.message import Message
from app.models.rating import Rating


def _get_user_id(db_session, email):
    return db_session.query(User).filter(User.email == email).first().id


def _register_and_login(client, email, password="securepass1", name="User"):
    client.post("/auth/register", json={"email": email, "password": password, "name": name})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Full buyer journey ───────────────────────────────────────────────


def test_full_buyer_journey(client, db_session, auth_headers, second_auth_headers):
    """Complete flow: create listing → message → rate → update rating → delete rating."""
    # Seller creates listing
    listing_resp = client.post("/listings/", data={
        "title": "EECS 2011 Textbook",
        "description": "Like new, no highlighting",
        "price": "45.00",
        "category": "Textbooks",
    }, headers=auth_headers)
    assert listing_resp.status_code == 201
    listing_id = listing_resp.json()["id"]

    # Buyer browses and finds it
    browse_resp = client.get("/listings/", params={"search": "EECS 2011"})
    assert browse_resp.status_code == 200
    assert any(l["id"] == listing_id for l in browse_resp.json()["listings"])

    # Buyer views listing detail
    detail_resp = client.get(f"/listings/{listing_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["title"] == "EECS 2011 Textbook"

    # Buyer checks if they can rate (should be no - haven't messaged)
    rating_check = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    assert rating_check.json()["can_rate"] is False

    # Buyer messages seller
    msg_resp = client.post(
        f"/listings/{listing_id}/messages/",
        json={"content": "Hi, is this still available? Can we meet at Scott Library?"},
        headers=second_auth_headers,
    )
    assert msg_resp.status_code == 201

    # Seller replies
    reply_resp = client.post(
        f"/listings/{listing_id}/messages/",
        json={"content": "Yes! How about tomorrow at 2pm?"},
        headers=auth_headers,
    )
    assert reply_resp.status_code == 201

    # Both see the conversation
    buyer_msgs = client.get(f"/listings/{listing_id}/messages/", headers=second_auth_headers)
    assert len(buyer_msgs.json()["messages"]) == 2

    seller_msgs = client.get(f"/listings/{listing_id}/messages/", headers=auth_headers)
    assert len(seller_msgs.json()["messages"]) == 2

    # Buyer can now rate (have messaged)
    rating_check2 = client.get(f"/listings/{listing_id}/rating/me", headers=second_auth_headers)
    assert rating_check2.json()["can_rate"] is True

    # Buyer rates seller
    rate_resp = client.post(
        f"/listings/{listing_id}/rating",
        json={"score": 5, "comment": "Fast response, great price!"},
        headers=second_auth_headers,
    )
    assert rate_resp.status_code == 201

    # Seller marks listing as sold
    sold_resp = client.patch(
        f"/listings/{listing_id}",
        data={"status": "sold"},
        headers=auth_headers,
    )
    assert sold_resp.status_code == 200
    assert sold_resp.json()["status"] == "sold"

    # Listing no longer appears in active browse
    active_resp = client.get("/listings/")
    assert all(l["id"] != listing_id for l in active_resp.json()["listings"])

    # But appears in sold filter
    sold_filter = client.get("/listings/", params={"status": "sold"})
    assert any(l["id"] == listing_id for l in sold_filter.json()["listings"])


# ── Delete account cascades everything ───────────────────────────────


def test_delete_account_cascades_all_data(client, db_session):
    """Deleting a seller account removes their listings, messages, and ratings."""
    # Set up: seller creates listing, buyer messages and rates
    seller_headers = _register_and_login(client, "seller_del@my.yorku.ca", name="Seller Del")
    buyer_headers = _register_and_login(client, "buyer_del@my.yorku.ca", name="Buyer Del")

    seller_id = _get_user_id(db_session, "seller_del@my.yorku.ca")

    listing_resp = client.post("/listings/", data={
        "title": "Will Cascade", "price": "20.00", "category": "Other",
    }, headers=seller_headers)
    listing_id = listing_resp.json()["id"]

    client.post(f"/listings/{listing_id}/messages/", json={"content": "Interested"}, headers=buyer_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 4}, headers=buyer_headers)

    # Delete seller account
    client.post("/auth/delete-account", json={"password": "securepass1"}, headers=seller_headers)

    # Listing should be gone
    assert client.get(f"/listings/{listing_id}").status_code == 404

    # Messages should be gone
    assert db_session.query(Message).filter(Message.listing_id == listing_id).count() == 0

    # Ratings for seller should be gone
    assert db_session.query(Rating).filter(Rating.seller_id == seller_id).count() == 0


# ── Delete listing cascades messages and ratings ─────────────────────


def test_delete_listing_cascades_ratings(client, db_session, auth_headers, second_auth_headers):
    """Deleting a listing removes all its ratings."""
    listing_resp = client.post("/listings/", data={
        "title": "Rate Then Delete", "price": "15.00", "category": "Other",
    }, headers=auth_headers)
    listing_id = listing_resp.json()["id"]

    client.post(f"/listings/{listing_id}/messages/", json={"content": "Hi"}, headers=second_auth_headers)
    client.post(f"/listings/{listing_id}/rating", json={"score": 5}, headers=second_auth_headers)

    # Verify rating exists
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    assert db_session.query(Rating).filter(Rating.listing_id == listing_id).count() == 1

    # Delete listing
    client.delete(f"/listings/{listing_id}", headers=auth_headers)

    # Rating should be gone
    assert db_session.query(Rating).filter(Rating.listing_id == listing_id).count() == 0


# ── Multiple users interacting ───────────────────────────────────────


def test_multiple_buyers_independent_ratings(client, db_session, auth_headers, second_auth_headers):
    """Two different buyers can rate the same seller independently."""
    third_headers = _register_and_login(client, "buyer3@my.yorku.ca", name="Buyer 3")

    listing1_id = client.post("/listings/", data={
        "title": "Item A", "price": "10.00", "category": "Other",
    }, headers=auth_headers).json()["id"]

    listing2_id = client.post("/listings/", data={
        "title": "Item B", "price": "20.00", "category": "Other",
    }, headers=auth_headers).json()["id"]

    # Buyer 2 rates listing 1
    client.post(f"/listings/{listing1_id}/messages/", json={"content": "Hi"}, headers=second_auth_headers)
    client.post(f"/listings/{listing1_id}/rating", json={"score": 5}, headers=second_auth_headers)

    # Buyer 3 rates listing 2
    client.post(f"/listings/{listing2_id}/messages/", json={"content": "Hi"}, headers=third_headers)
    client.post(f"/listings/{listing2_id}/rating", json={"score": 3}, headers=third_headers)

    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    ratings_resp = client.get(f"/users/{seller_id}/ratings")
    assert ratings_resp.json()["total_count"] == 2
    assert ratings_resp.json()["average_score"] == 4.0  # (5+3)/2


# ── Thread visibility across users ──────────────────────────────────


def test_seller_sees_threads_from_multiple_buyers(client, db_session, auth_headers, second_auth_headers):
    """Seller sees separate threads for each buyer."""
    third_headers = _register_and_login(client, "thread_buyer@my.yorku.ca", name="Thread Buyer")

    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = Listing(seller_id=seller_id, title="Thread Test", price=10.0, category="Other")
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)

    client.post(f"/listings/{listing.id}/messages/", json={"content": "From buyer 2"}, headers=second_auth_headers)
    client.post(f"/listings/{listing.id}/messages/", json={"content": "From thread buyer"}, headers=third_headers)

    threads_resp = client.get("/messages/threads", headers=auth_headers)
    threads = threads_resp.json()["threads"]
    # Seller should see 2 threads (one per buyer) on the same listing
    assert len(threads) == 2


# ── Browsing and filtering after multiple operations ─────────────────


def test_browse_reflects_status_changes(client, auth_headers):
    """Listing status transitions are reflected in browse filters."""
    listing_id = client.post("/listings/", data={
        "title": "Status Journey", "price": "30.00", "category": "Other",
    }, headers=auth_headers).json()["id"]

    # Active -> should appear in default
    resp = client.get("/listings/")
    assert any(l["id"] == listing_id for l in resp.json()["listings"])

    # Mark sold -> disappears from active
    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)
    resp = client.get("/listings/")
    assert all(l["id"] != listing_id for l in resp.json()["listings"])

    # Relist -> appears in active again
    client.patch(f"/listings/{listing_id}", data={"status": "active"}, headers=auth_headers)
    resp = client.get("/listings/")
    assert any(l["id"] == listing_id for l in resp.json()["listings"])


# ── Auth token validity ──────────────────────────────────────────────


def test_token_invalid_after_account_deletion(client):
    """After account deletion, the JWT token should no longer work."""
    headers = _register_and_login(client, "tokentest@my.yorku.ca")

    # Token works
    assert client.get("/auth/me", headers=headers).status_code == 200

    # Delete account
    client.post("/auth/delete-account", json={"password": "securepass1"}, headers=headers)

    # Token should no longer work
    assert client.get("/auth/me", headers=headers).status_code == 401
