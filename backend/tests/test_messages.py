# Assigned to: Raj (Rajendra Brahmbhatt)
# Phase: 3 (B3.6)

from app.models.listing import Listing
from app.models.user import User


def _create_listing(db_session, seller_id: int) -> Listing:
    """Helper to insert a listing directly via ORM (listing router not yet implemented)."""
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


def test_get_messages(client, db_session, auth_headers, second_auth_headers):
    """Participants can retrieve messages in chronological order."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Exchange messages
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

    # Buyer fetches messages
    resp = client.get(
        f"/listings/{listing.id}/messages/",
        headers=second_auth_headers,
    )
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["content"] == "First message"
    assert messages[1]["content"] == "Second message"


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
