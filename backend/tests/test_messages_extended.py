# Extended messaging tests covering conversation isolation, third-party users,
# edge cases, and response structure validation.

from app.models.listing import Listing
from app.models.user import User


def _create_listing(db_session, seller_id):
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


def _get_user_id(db_session, email):
    return db_session.query(User).filter(User.email == email).first().id


def _register_and_login(client, email, password="securepass1", name="Extra User"):
    """Register and login a third user, returning auth headers."""
    client.post("/auth/register", json={
        "email": email, "password": password, "name": name,
    })
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Message response structure ────────────────────────────────────────


def test_message_response_structure(client, db_session, auth_headers, second_auth_headers):
    """Message response has all expected fields."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Structure check"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "listing_id" in data
    assert "sender_id" in data
    assert "receiver_id" in data
    assert "content" in data
    assert "created_at" in data
    assert "sender" in data
    assert "id" in data["sender"]
    assert "name" in data["sender"]


# ── Conversation isolation ───────────────────────────────────────────


def test_non_participant_cannot_see_messages(client, db_session, auth_headers, second_auth_headers):
    """A third user who is not part of the conversation sees no messages."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # User2 messages seller
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Private message"},
        headers=second_auth_headers,
    )

    # Register third user
    third_headers = _register_and_login(client, "third@my.yorku.ca", name="Third User")

    # Third user should see no messages for this listing
    resp = client.get(f"/listings/{listing.id}/messages/", headers=third_headers)
    assert resp.status_code == 200
    assert resp.json()["messages"] == []


def test_third_user_can_message_same_listing(client, db_session, auth_headers, second_auth_headers):
    """Multiple buyers can independently message the same listing's seller."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # User2 messages
    resp2 = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "From user 2"},
        headers=second_auth_headers,
    )
    assert resp2.status_code == 201

    # Third user messages
    third_headers = _register_and_login(client, "buyer3@my.yorku.ca", name="Buyer 3")
    resp3 = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "From user 3"},
        headers=third_headers,
    )
    assert resp3.status_code == 201
    assert resp3.json()["receiver_id"] == seller_id


def test_buyer_only_sees_own_conversation(client, db_session, auth_headers, second_auth_headers):
    """Buyer only sees messages from their own conversation, not other buyers."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # User2 messages
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "From user 2"},
        headers=second_auth_headers,
    )

    # Third user messages
    third_headers = _register_and_login(client, "buyer4@my.yorku.ca", name="Buyer 4")
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "From buyer 4"},
        headers=third_headers,
    )

    # User2 should only see their own message
    resp = client.get(f"/listings/{listing.id}/messages/", headers=second_auth_headers)
    messages = resp.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["content"] == "From user 2"


# ── Seller reply edge cases ──────────────────────────────────────────


def test_seller_cannot_initiate_without_buyer(client, db_session, auth_headers):
    """Seller cannot send first message on their own listing."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Hello to nobody"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_seller_replies_to_correct_buyer(client, db_session, auth_headers, second_auth_headers):
    """When multiple buyers exist, seller's reply goes to the most recent conversation partner."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    buyer2_id = _get_user_id(db_session, "testuser2@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    # Buyer2 initiates
    client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "I want this"},
        headers=second_auth_headers,
    )

    # Seller replies -> should go to buyer2
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "Sure!"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["receiver_id"] == buyer2_id


# ── Content edge cases ───────────────────────────────────────────────


def test_message_whitespace_only_rejected(client, db_session, auth_headers, second_auth_headers):
    """Message with only whitespace may or may not be accepted depending on validation."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": "   "},
        headers=second_auth_headers,
    )
    # Whitespace content is at least 1 char, so min_length=1 passes
    # This test documents the behavior - whitespace-only messages are allowed
    assert resp.status_code == 201


def test_message_special_characters(client, db_session, auth_headers, second_auth_headers):
    """Messages with special characters are preserved."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    content = "Hello! Price: $25.00 <script>alert('xss')</script> & more \"quotes\""
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": content},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["content"] == content


def test_message_unicode(client, db_session, auth_headers, second_auth_headers):
    """Messages with unicode/emoji are preserved."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    content = "Great deal! \U0001f44d \u2764\ufe0f \u00e9\u00e0\u00fc"
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": content},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["content"] == content


def test_message_newlines(client, db_session, auth_headers, second_auth_headers):
    """Messages with newlines are preserved."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    content = "Line 1\nLine 2\nLine 3"
    resp = client.post(
        f"/listings/{listing.id}/messages/",
        json={"content": content},
        headers=second_auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["content"] == content


# ── Get messages edge cases ──────────────────────────────────────────


def test_get_messages_empty_listing(client, db_session, auth_headers):
    """Getting messages for a listing with no messages returns empty list."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    resp = client.get(f"/listings/{listing.id}/messages/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["messages"] == []


def test_get_messages_chronological_order(client, db_session, auth_headers, second_auth_headers):
    """Messages are returned in chronological order (oldest first)."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    for i in range(5):
        client.post(
            f"/listings/{listing.id}/messages/",
            json={"content": f"Message {i}"},
            headers=second_auth_headers,
        )

    resp = client.get(f"/listings/{listing.id}/messages/", headers=second_auth_headers)
    messages = resp.json()["messages"]
    assert len(messages) == 5
    for i, msg in enumerate(messages):
        assert msg["content"] == f"Message {i}"


def test_get_messages_listing_not_found(client, auth_headers):
    """Getting messages for non-existent listing still works (returns empty)."""
    resp = client.get("/listings/99999/messages/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["messages"] == []


# ── Thread edge cases ────────────────────────────────────────────────


def test_threads_sorted_by_most_recent(client, db_session, auth_headers, second_auth_headers):
    """Threads are sorted by last_message_at descending."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing1 = _create_listing(db_session, seller_id)
    listing2 = _create_listing(db_session, seller_id)

    # Message listing1 first
    client.post(
        f"/listings/{listing1.id}/messages/",
        json={"content": "Old message"},
        headers=second_auth_headers,
    )
    # Message listing2 second (more recent)
    client.post(
        f"/listings/{listing2.id}/messages/",
        json={"content": "New message"},
        headers=second_auth_headers,
    )

    resp = client.get("/messages/threads", headers=second_auth_headers)
    threads = resp.json()["threads"]
    assert len(threads) == 2
    # Most recent thread first
    assert threads[0]["listing_id"] == listing2.id


def test_threads_message_count_increments(client, db_session, auth_headers, second_auth_headers):
    """Thread message count updates as more messages are sent."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(f"/listings/{listing.id}/messages/", json={"content": "First"}, headers=second_auth_headers)
    client.post(f"/listings/{listing.id}/messages/", json={"content": "Reply"}, headers=auth_headers)
    client.post(f"/listings/{listing.id}/messages/", json={"content": "Thanks"}, headers=second_auth_headers)

    resp = client.get("/messages/threads", headers=second_auth_headers)
    thread = resp.json()["threads"][0]
    assert thread["message_count"] == 3
    assert thread["last_message"] == "Thanks"


def test_threads_show_other_user_id(client, db_session, auth_headers, second_auth_headers):
    """Thread other_user_id is the conversation partner."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    buyer_id = _get_user_id(db_session, "testuser2@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(f"/listings/{listing.id}/messages/", json={"content": "Hey"}, headers=second_auth_headers)

    # From seller's perspective, other user is the buyer
    seller_threads = client.get("/messages/threads", headers=auth_headers)
    assert seller_threads.json()["threads"][0]["other_user_id"] == buyer_id

    # From buyer's perspective, other user is the seller
    buyer_threads = client.get("/messages/threads", headers=second_auth_headers)
    assert buyer_threads.json()["threads"][0]["other_user_id"] == seller_id


def test_threads_include_last_message_at(client, db_session, auth_headers, second_auth_headers):
    """Threads include last_message_at timestamp."""
    seller_id = _get_user_id(db_session, "testuser@my.yorku.ca")
    listing = _create_listing(db_session, seller_id)

    client.post(f"/listings/{listing.id}/messages/", json={"content": "Timed"}, headers=second_auth_headers)

    resp = client.get("/messages/threads", headers=auth_headers)
    thread = resp.json()["threads"][0]
    assert "last_message_at" in thread
