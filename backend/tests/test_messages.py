# Assigned to: Raj (Rajendra Brahmbhatt)
# Phase: 3 (B3.6)
#
# Comprehensive messaging tests covering:
# - Send message (buyer to seller, seller reply, unauthorized, listing not found)
# - Self-messaging prevention
# - Message read tracking (default, auto-mark, explicit mark)
# - Thread listing with unread counts
# - Empty message content
# - Multiple threads and isolation
# - Get messages (authorized, unauthorized, non-participant)

from app.models.listing import Listing
from app.models.user import User


def _create_listing(db_session, seller_id: int) -> Listing:
    """Helper to insert a listing directly via ORM."""
    listing = Listing(
        seller_id=seller_id,
        title="Test Textbook",
        description="A test listing",
        price=25.00,
        category="Textbooks",
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing


def _get_user_id(db_session, email: str) -> int:
    """Look up a user's ID by email."""
    return db_session.query(User).filter(User.email == email).first().id


# ── Send message tests ──────────────────────────────────────────────────


def test_send_message_to_seller(client, db_session, auth_headers, second_auth_headers):
    """User B sends a message to User A's listing. Receiver should be the seller."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Is this still available?"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["listing_id"] == listing.id
    assert data["receiver_id"] == seller_id
    assert data["content"] == "Is this still available?"


def test_seller_reply(client, db_session, auth_headers, second_auth_headers):
    """After a buyer messages, the seller can reply back to that buyer."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    buyer_id = _get_user_id(db_session, "testuser2@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Buyer sends first message
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Hi, is this available?"},
        headers=second_auth_headers,
    )

    # Seller replies
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Yes it is!"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["sender_id"] == seller_id
    assert data["receiver_id"] == buyer_id


def test_send_message_unauthorized(client, db_session, auth_headers):
    """Sending a message without auth returns 401."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "No auth"},
    )
    assert resp.status_code == 401


def test_send_message_listing_not_found(client, second_auth_headers):
    """Messaging a non-existent listing returns 404."""
    resp = client.post(
        "/listings/99999/messages/",
        json={"content": "Hello?"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 404


def test_cannot_message_self(client, db_session, auth_headers):
    """Seller cannot start a thread on their own listing with no prior buyer message."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Talking to myself"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_send_empty_message(client, db_session, auth_headers, second_auth_headers):
    """Sending an empty message content is rejected (min_length=1)."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": ""},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_send_message_missing_content(client, db_session, auth_headers, second_auth_headers):
    """Sending message without content field returns 422."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={},
        headers=second_auth_headers,
    )
    assert resp.status_code == 422


def test_send_long_message(client, db_session, auth_headers, second_auth_headers):
    """A long message content is accepted."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    long_content = "A" * 5000
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": long_content},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["content"] == long_content


# ── Get messages tests ──────────────────────────────────────────────────


def test_get_messages(client, db_session, auth_headers, second_auth_headers):
    """Participants can retrieve messages in chronological order."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "First message"},
        headers=second_auth_headers,
    )
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Second message"},
        headers=auth_headers,
    )

    resp = client.get(
        f"/listings/{listing.id}/messages/",
        headers=second_auth_headers,
    )
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["content"] == "First message"
    assert messages[1]["content"] == "Second message"


def test_get_messages_unauthorized(client, db_session, auth_headers):
    """Getting messages without auth returns 401."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.get(f"/listings/{listing.id}/messages/")
    assert resp.status_code == 401


def test_get_messages_includes_sender_info(client, db_session, auth_headers, second_auth_headers):
    """Messages include sender name and id."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Hello!"},
        headers=second_auth_headers,
    )

    resp = client.get(f"/listings/{listing.id}/messages/", headers=auth_headers)
    msg = resp.json()["messages"][0]
    assert "sender" in msg
    assert msg["sender"]["name"] == "Test User 2"
    assert "id" in msg["sender"]


# ── Read tracking tests ─────────────────────────────────────────────────


def test_message_is_read_default_false(client, db_session, auth_headers, second_auth_headers):
    """New messages should have is_read=False by default."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Is this available?"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_read"] is False


def test_get_messages_marks_unread_as_read(client, db_session, auth_headers, second_auth_headers):
    """Fetching messages marks unread messages addressed to the current user as read."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Buyer sends message to seller
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Hello!"},
        headers=second_auth_headers,
    )

    # Seller fetches messages — should mark buyer's message as read
    resp = client.get(
        f"/listings/{listing.id}/messages/",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["is_read"] is True


def test_mark_messages_read_endpoint(client, db_session, auth_headers, second_auth_headers):
    """PUT /listings/{id}/messages/read marks unread messages as read."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Buyer sends two messages
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Message 1"},
        headers=second_auth_headers,
    )
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Message 2"},
        headers=second_auth_headers,
    )

    # Seller marks all as read
    resp = client.put(
        f"/listings/{listing.id}/messages/read",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["marked_read"] == 2

    # Calling again should return 0
    resp = client.put(
        f"/listings/{listing.id}/messages/read",
        headers=auth_headers,
    )
    assert resp.json()["marked_read"] == 0


def test_threads_include_unread_count(client, db_session, auth_headers, second_auth_headers):
    """GET /messages/threads should include unread_count per thread."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Buyer sends a message
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Hey!"},
        headers=second_auth_headers,
    )

    # Seller checks threads — should see 1 unread
    resp = client.get("/messages/threads", headers=auth_headers)
    assert resp.status_code == 200
    threads = resp.json()["threads"]
    assert len(threads) == 1
    assert threads[0]["unread_count"] == 1


def test_threads_unauthenticated(client):
    """GET /messages/threads without auth returns 401."""
    resp = client.get("/messages/threads")
    assert resp.status_code == 401


def test_threads_empty_for_new_user(client, auth_headers):
    """A user with no messages has empty thread list."""
    resp = client.get("/messages/threads", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["threads"] == []


def test_threads_include_listing_info(client, db_session, auth_headers, second_auth_headers):
    """Threads include listing title and other user info."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Interested!"},
        headers=second_auth_headers,
    )

    resp = client.get("/messages/threads", headers=auth_headers)
    thread = resp.json()["threads"][0]
    assert "listing_id" in thread
    assert "listing_title" in thread
    assert "other_user_id" in thread
    assert "last_message" in thread
    assert "message_count" in thread


def test_threads_show_latest_message(client, db_session, auth_headers, second_auth_headers):
    """Thread last_message reflects the most recent message."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "First msg"},
        headers=second_auth_headers,
    )
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Latest msg"},
        headers=auth_headers,
    )

    resp = client.get("/messages/threads", headers=second_auth_headers)
    thread = resp.json()["threads"][0]
    assert thread["last_message"] == "Latest msg"
    assert thread["message_count"] == 2


# ── Multi-conversation tests ────────────────────────────────────────────


def test_multiple_threads_on_different_listings(client, db_session, auth_headers, second_auth_headers):
    """A user can have threads on multiple listings."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing1 = _create_listing(db_session, seller_id)
    listing2 = _create_listing(db_session, seller_id)

    client.post(
        f"/listings/{listing1.id}/messages/",
        json={"content": "About listing 1"},
        headers=second_auth_headers,
    )
    client.post(
        f"/listings/{listing2.id}/messages/",
        json={"content": "About listing 2"},
        headers=second_auth_headers,
    )

    resp = client.get("/messages/threads", headers=auth_headers)
    threads = resp.json()["threads"]
    assert len(threads) == 2
    listing_ids = {t["listing_id"] for t in threads}
    assert listing1.id in listing_ids
    assert listing2.id in listing_ids


def test_message_response_has_timestamps(client, db_session, auth_headers, second_auth_headers):
    """Messages include created_at timestamps."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Timed message"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert "created_at" in resp.json()
