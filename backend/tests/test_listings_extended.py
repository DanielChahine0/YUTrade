# Extended listing tests covering edge cases, combined filters, image management,
# cascade deletes, and pagination boundaries.

from app.models.user import User
from app.models.listing import Listing
from app.models.message import Message


def _create_listing(client, headers, **kwargs):
    """Helper to create a listing through the API."""
    data = {
        "title": kwargs.get("title", "Test Listing"),
        "price": kwargs.get("price", "25.00"),
        "category": kwargs.get("category", "Other"),
        "description": kwargs.get("description", "A test listing"),
    }
    return client.post("/listings/", data=data, files=kwargs.get("files", []), headers=headers)


# ── Create listing edge cases ─────────────────────────────────────────


def test_create_listing_missing_title(client, auth_headers):
    """POST /listings/ without title returns 422."""
    resp = client.post(
        "/listings/",
        data={"price": "10.00", "category": "Other"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_listing_missing_price(client, auth_headers):
    """POST /listings/ without price returns 422."""
    resp = client.post(
        "/listings/",
        data={"title": "No Price"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_listing_string_price(client, auth_headers):
    """POST /listings/ with non-numeric price returns 422."""
    resp = client.post(
        "/listings/",
        data={"title": "Bad Price", "price": "abc"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_listing_seller_info_matches(client, auth_headers):
    """Created listing's seller info matches the authenticated user."""
    resp = _create_listing(client, auth_headers, title="Seller Check")
    assert resp.status_code == 201
    data = resp.json()
    assert data["seller"]["name"] == "Test User"
    assert data["seller"]["email"] == "testuser@my.yorku.ca"


def test_create_listing_all_categories(client, auth_headers):
    """All documented categories are accepted."""
    categories = ["Textbooks", "Electronics", "Furniture", "Clothing", "Other"]
    for cat in categories:
        resp = _create_listing(client, auth_headers, title=f"Cat {cat}", category=cat)
        assert resp.status_code == 201, f"Category {cat} was rejected"
        assert resp.json()["category"] == cat


def test_create_listing_price_precision(client, auth_headers):
    """Price with decimal precision is preserved."""
    resp = _create_listing(client, auth_headers, price="29.99")
    assert resp.status_code == 201
    assert resp.json()["price"] == 29.99


# ── Get listings combined filters ─────────────────────────────────────


def test_get_listings_search_and_category(client, auth_headers):
    """Combining search and category filter."""
    _create_listing(client, auth_headers, title="Physics Book", category="Textbooks")
    _create_listing(client, auth_headers, title="Physics Lab Kit", category="Electronics")
    _create_listing(client, auth_headers, title="Math Book", category="Textbooks")

    resp = client.get("/listings/", params={"search": "Physics", "category": "Textbooks"})
    assert resp.status_code == 200
    listings = resp.json()["listings"]
    assert all(l["category"] == "Textbooks" for l in listings)
    assert all("Physics" in l["title"] for l in listings)


def test_get_listings_search_and_price_range(client, auth_headers):
    """Combining search and price range."""
    _create_listing(client, auth_headers, title="Cheap Textbook", price="5.00")
    _create_listing(client, auth_headers, title="Expensive Textbook", price="200.00")

    resp = client.get("/listings/", params={
        "search": "Textbook",
        "min_price": 10,
        "max_price": 300,
    })
    assert resp.status_code == 200
    listings = resp.json()["listings"]
    assert all(10 <= l["price"] <= 300 for l in listings)


def test_get_listings_all_filters_combined(client, auth_headers):
    """All filters combined: search + category + price range + sort."""
    _create_listing(client, auth_headers, title="EECS 2011 Book", price="40.00", category="Textbooks")
    _create_listing(client, auth_headers, title="EECS 3101 Book", price="60.00", category="Textbooks")
    _create_listing(client, auth_headers, title="EECS USB Cable", price="15.00", category="Electronics")

    resp = client.get("/listings/", params={
        "search": "EECS",
        "category": "Textbooks",
        "min_price": 30,
        "max_price": 70,
        "sort": "price_low_to_high",
    })
    assert resp.status_code == 200
    listings = resp.json()["listings"]
    assert len(listings) == 2
    prices = [l["price"] for l in listings]
    assert prices == sorted(prices)


def test_get_listings_empty_search_string(client, auth_headers):
    """Empty search string returns all listings."""
    _create_listing(client, auth_headers, title="Something")
    resp = client.get("/listings/", params={"search": ""})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_get_listings_case_insensitive_search(client, auth_headers):
    """Search is case-insensitive."""
    _create_listing(client, auth_headers, title="UPPERCASE BOOK")
    resp = client.get("/listings/", params={"search": "uppercase"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


# ── Pagination edge cases ────────────────────────────────────────────


def test_get_listings_page_beyond_total(client, auth_headers):
    """Requesting a page beyond total returns empty listings."""
    _create_listing(client, auth_headers, title="Only One")
    resp = client.get("/listings/", params={"page": 999, "limit": 10})
    assert resp.status_code == 200
    assert resp.json()["listings"] == []
    assert resp.json()["total"] >= 1  # total still counts all


def test_get_listings_limit_1(client, auth_headers):
    """Limit of 1 returns exactly 1 listing."""
    _create_listing(client, auth_headers, title="Lim A")
    _create_listing(client, auth_headers, title="Lim B")
    resp = client.get("/listings/", params={"limit": 1})
    assert resp.status_code == 200
    assert len(resp.json()["listings"]) == 1


def test_get_listings_negative_page(client):
    """Negative page number returns 422."""
    resp = client.get("/listings/", params={"page": -1})
    assert resp.status_code == 422


def test_get_listings_negative_limit(client):
    """Negative limit returns 422."""
    resp = client.get("/listings/", params={"limit": -1})
    assert resp.status_code == 422


# ── Get listing by ID edge cases ─────────────────────────────────────


def test_get_listing_includes_all_fields(client, auth_headers):
    """GET /listings/{id} response has all expected fields."""
    create_resp = _create_listing(client, auth_headers, title="Full Fields", description="desc", category="Electronics")
    listing_id = create_resp.json()["id"]

    resp = client.get(f"/listings/{listing_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "price" in data
    assert "category" in data
    assert "status" in data
    assert "seller" in data
    assert "images" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_listing_zero_id(client):
    """GET /listings/0 returns 422 (id must be >= 1)."""
    resp = client.get("/listings/0")
    assert resp.status_code == 422


def test_get_listing_negative_id(client):
    """GET /listings/-1 returns 422."""
    resp = client.get("/listings/-1")
    assert resp.status_code == 422


# ── Update listing edge cases ────────────────────────────────────────


def test_update_listing_multiple_fields(client, auth_headers):
    """Updating multiple fields at once works."""
    create_resp = _create_listing(client, auth_headers, title="Multi Update", price="10.00")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"title": "Updated Multi", "price": "99.99", "description": "New desc"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["title"] == "Updated Multi"
    assert data["price"] == 99.99
    assert data["description"] == "New desc"


def test_update_listing_category(client, auth_headers):
    """Owner can update listing category."""
    create_resp = _create_listing(client, auth_headers, title="Cat Update", category="Other")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"category": "Electronics"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["category"] == "Electronics"


def test_update_listing_sold_then_back_to_active(client, auth_headers):
    """Can transition from sold back to active."""
    create_resp = _create_listing(client, auth_headers, title="Relist")
    listing_id = create_resp.json()["id"]

    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)
    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"status": "active"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "active"


def test_update_listing_updates_timestamp(client, auth_headers):
    """Updating listing changes updated_at."""
    create_resp = _create_listing(client, auth_headers, title="Timestamp Test")
    listing_id = create_resp.json()["id"]
    original_updated = create_resp.json()["updated_at"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"title": "Updated Timestamp"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    # updated_at should be different (or at least not earlier)
    assert patch_resp.json()["updated_at"] >= original_updated


def test_update_listing_add_images(client, auth_headers):
    """Adding new images to an existing listing."""
    create_resp = _create_listing(client, auth_headers, title="Add Images")
    listing_id = create_resp.json()["id"]
    assert len(create_resp.json()["images"]) == 0

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={},
        files=[("new_images", ("new.jpg", b"image-bytes", "image/jpeg"))],
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert len(patch_resp.json()["images"]) == 1


def test_update_listing_delete_images(client, auth_headers):
    """Deleting images from a listing."""
    files = [("images", ("img.jpg", b"fake-data", "image/jpeg"))]
    create_resp = _create_listing(client, auth_headers, title="Del Images", files=files)
    listing_id = create_resp.json()["id"]
    image_id = create_resp.json()["images"][0]["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"delete_image_ids": [image_id]},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert len(patch_resp.json()["images"]) == 0


# ── Delete listing cascade ───────────────────────────────────────────


def test_delete_listing_cascades_messages(client, db_session, auth_headers, second_auth_headers):
    """Deleting a listing also deletes its messages."""
    seller_id = db_session.query(User).filter(User.email == "testuser@my.yorku.ca").first().id
    listing = Listing(seller_id=seller_id, title="Cascade Msg", price=10.0, category="Other")
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)

    # Send a message
    client.post(f"/listings/{listing.id}/messages/", json={"content": "Hi"}, headers=second_auth_headers)

    # Delete listing
    client.delete(f"/listings/{listing.id}", headers=auth_headers)

    # Messages should be gone
    count = db_session.query(Message).filter(Message.listing_id == listing.id).count()
    assert count == 0


def test_delete_listing_images_removed(client, auth_headers):
    """Deleting a listing removes its image records."""
    files = [("images", ("del.jpg", b"image-data", "image/jpeg"))]
    create_resp = _create_listing(client, auth_headers, title="Del With Img", files=files)
    listing_id = create_resp.json()["id"]
    assert len(create_resp.json()["images"]) == 1

    client.delete(f"/listings/{listing_id}", headers=auth_headers)
    get_resp = client.get(f"/listings/{listing_id}")
    assert get_resp.status_code == 404


# ── Public access tests ──────────────────────────────────────────────


def test_get_listings_no_auth_required(client, auth_headers):
    """GET /listings/ works without authentication."""
    _create_listing(client, auth_headers, title="Public View")
    resp = client.get("/listings/")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_get_listing_by_id_no_auth(client, auth_headers):
    """GET /listings/{id} works without authentication."""
    create_resp = _create_listing(client, auth_headers, title="Public Single")
    listing_id = create_resp.json()["id"]

    resp = client.get(f"/listings/{listing_id}")
    assert resp.status_code == 200


# ── Date filter tests ────────────────────────────────────────────────


def test_get_listings_date_filter_last_24_hours(client, auth_headers):
    """Listings created just now appear in last_24_hours filter."""
    _create_listing(client, auth_headers, title="Fresh Listing")
    resp = client.get("/listings/", params={"date_listed": "last_24_hours"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_get_listings_date_filter_last_7_days(client, auth_headers):
    """Listings created just now appear in last_7_days filter."""
    _create_listing(client, auth_headers, title="Weekly Listing")
    resp = client.get("/listings/", params={"date_listed": "last_7_days"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_get_listings_date_filter_last_30_days(client, auth_headers):
    """Listings created just now appear in last_30_days filter."""
    _create_listing(client, auth_headers, title="Monthly Listing")
    resp = client.get("/listings/", params={"date_listed": "last_30_days"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


# ── Status filter tests ─────────────────────────────────────────────


def test_get_listings_removed_status(client, auth_headers):
    """Can filter for removed listings."""
    create_resp = _create_listing(client, auth_headers, title="To Remove")
    listing_id = create_resp.json()["id"]
    client.patch(f"/listings/{listing_id}", data={"status": "removed"}, headers=auth_headers)

    resp = client.get("/listings/", params={"status": "removed"})
    assert resp.status_code == 200
    titles = [l["title"] for l in resp.json()["listings"]]
    assert "To Remove" in titles


def test_sold_listing_not_in_active(client, auth_headers):
    """Sold listings don't appear in default (active) results."""
    create_resp = _create_listing(client, auth_headers, title="Now Sold")
    listing_id = create_resp.json()["id"]
    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)

    resp = client.get("/listings/")
    titles = [l["title"] for l in resp.json()["listings"]]
    assert "Now Sold" not in titles


def test_get_listing_by_id_works_for_sold(client, auth_headers):
    """GET /listings/{id} returns sold listings (direct access by ID)."""
    create_resp = _create_listing(client, auth_headers, title="Sold Direct")
    listing_id = create_resp.json()["id"]
    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)

    resp = client.get(f"/listings/{listing_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "sold"
