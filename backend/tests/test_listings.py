# Assigned to: Lakshan Kandeepan
# Phase: 2 (B2.6)
#
# Comprehensive listing tests covering:
# - Create listing (success, unauthorized, validation boundaries)
# - Get listings (pagination, search, category, price range, sort, date filters)
# - Get listing by ID (success, not found)
# - Update listing (owner, non-owner, not found, status transitions)
# - Delete listing (owner, non-owner, not found)
# - Image upload

from pathlib import Path


def _create_listing(
    client,
    headers,
    *,
    title="Test Listing",
    price="25.00",
    category="Textbooks",
    description="A test listing",
    files=None,
):
    """Helper to create a listing through the real API."""
    return client.post(
        "/listings/",
        data={
            "title": title,
            "description": description,
            "price": price,
            "category": category,
        },
        files=files,
        headers=headers,
    )


# ── Create listing tests ────────────────────────────────────────────────


def test_create_listing_success(client, auth_headers):
    """POST /listings/ with valid data returns 201 with listing details."""
    resp = _create_listing(
        client, auth_headers,
        title="My First Listing",
        price="10.50",
        category="Textbooks",
        description="Selling a book",
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "id" in data
    assert data["title"] == "My First Listing"
    assert "seller_id" in data
    assert "seller" in data
    assert data["seller"]["email"] == "testuser@my.yorku.ca"


def test_create_listing_unauthorized(client):
    """POST /listings/ without auth returns 401."""
    resp = client.post(
        "/listings/",
        data={
            "title": "No Auth Listing",
            "description": "Should fail",
            "price": "9.99",
            "category": "Other",
        },
    )
    assert resp.status_code == 401


def test_create_listing_zero_price(client, auth_headers):
    """Listing with price=0 is rejected (price must be > 0)."""
    resp = _create_listing(client, auth_headers, price="0")
    assert resp.status_code == 422


def test_create_listing_negative_price(client, auth_headers):
    """Listing with negative price is rejected."""
    resp = _create_listing(client, auth_headers, price="-5.00")
    assert resp.status_code == 422


def test_create_listing_very_small_price(client, auth_headers):
    """Listing with a very small positive price (e.g. $0.01) is accepted."""
    resp = _create_listing(client, auth_headers, price="0.01")
    assert resp.status_code == 201
    assert resp.json()["price"] == 0.01


def test_create_listing_large_price(client, auth_headers):
    """Listing with a large price is accepted."""
    resp = _create_listing(client, auth_headers, price="99999.99")
    assert resp.status_code == 201


def test_create_listing_no_description(client, auth_headers):
    """Listing without a description is accepted (description is optional)."""
    resp = client.post(
        "/listings/",
        data={"title": "No Desc", "price": "10.00", "category": "Other"},
        headers=auth_headers,
    )
    assert resp.status_code == 201


def test_create_listing_no_category(client, auth_headers):
    """Listing without a category is accepted (category is optional)."""
    resp = client.post(
        "/listings/",
        data={"title": "No Category", "price": "10.00", "description": "desc"},
        headers=auth_headers,
    )
    assert resp.status_code == 201


def test_create_listing_default_status_active(client, auth_headers):
    """Newly created listing has status 'active'."""
    resp = _create_listing(client, auth_headers)
    assert resp.status_code == 201
    assert resp.json()["status"] == "active"


def test_create_listing_has_timestamps(client, auth_headers):
    """Created listing includes created_at and updated_at."""
    resp = _create_listing(client, auth_headers)
    data = resp.json()
    assert "created_at" in data
    assert "updated_at" in data


# ── Get listings tests ──────────────────────────────────────────────────


def test_get_listings(client, auth_headers):
    """GET /listings/ returns paginated results."""
    _create_listing(client, auth_headers, title="Listing 1", price="5.00", category="Other")
    _create_listing(client, auth_headers, title="Listing 2", price="15.00", category="Textbooks")

    resp = client.get("/listings/")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "listings" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["limit"] == 20
    titles = [l["title"] for l in data["listings"]]
    assert "Listing 1" in titles
    assert "Listing 2" in titles
    assert data["total"] >= 2


def test_get_listings_search(client, auth_headers):
    """GET /listings/?search=keyword filters by title/description."""
    _create_listing(client, auth_headers, title="MacBook Charger", price="20.00", category="Electronics")
    _create_listing(client, auth_headers, title="Textbook Calculus", price="30.00", category="Textbooks")
    _create_listing(client, auth_headers, title="Chair", price="10.00", category="Furniture")

    resp = client.get("/listings/", params={"search": "Textbook"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["listings"]) >= 1
    assert all(
        ("Textbook" in (l.get("title") or "")) or ("Textbook" in (l.get("description") or ""))
        for l in data["listings"]
    )


def test_get_listings_search_in_description(client, auth_headers):
    """Search also matches against description field."""
    _create_listing(
        client, auth_headers,
        title="Random Item",
        description="This is a rare calculus textbook",
        price="15.00",
    )
    resp = client.get("/listings/", params={"search": "calculus"})
    assert resp.status_code == 200
    assert len(resp.json()["listings"]) >= 1


def test_get_listings_search_no_results(client, auth_headers):
    """Search with non-matching keyword returns empty results."""
    _create_listing(client, auth_headers, title="Normal Item", price="10.00")
    resp = client.get("/listings/", params={"search": "zzzznonexistent"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["listings"] == []


def test_get_listings_category_filter(client, auth_headers):
    """GET /listings/?category=... filters by category."""
    _create_listing(client, auth_headers, title="Book A", price="12.00", category="Textbooks")
    _create_listing(client, auth_headers, title="Laptop", price="200.00", category="Electronics")

    resp = client.get("/listings/", params={"category": "Textbooks"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] >= 1
    assert all(l["category"] == "Textbooks" for l in data["listings"])


def test_get_listings_price_range_filter(client, auth_headers):
    """min_price and max_price filter listings by price range."""
    _create_listing(client, auth_headers, title="Cheap", price="5.00", category="Other")
    _create_listing(client, auth_headers, title="Mid", price="50.00", category="Other")
    _create_listing(client, auth_headers, title="Expensive", price="500.00", category="Other")

    resp = client.get("/listings/", params={"min_price": 10, "max_price": 100})
    assert resp.status_code == 200
    listings = resp.json()["listings"]
    assert all(10 <= l["price"] <= 100 for l in listings)
    titles = [l["title"] for l in listings]
    assert "Mid" in titles
    assert "Cheap" not in titles
    assert "Expensive" not in titles


def test_get_listings_min_price_only(client, auth_headers):
    """min_price without max_price filters lower bound only."""
    _create_listing(client, auth_headers, title="Low Price", price="2.00", category="Other")
    _create_listing(client, auth_headers, title="High Price", price="200.00", category="Other")

    resp = client.get("/listings/", params={"min_price": 100})
    assert resp.status_code == 200
    assert all(l["price"] >= 100 for l in resp.json()["listings"])


def test_get_listings_max_price_only(client, auth_headers):
    """max_price without min_price filters upper bound only."""
    _create_listing(client, auth_headers, title="Budget", price="5.00", category="Other")
    _create_listing(client, auth_headers, title="Premium", price="999.00", category="Other")

    resp = client.get("/listings/", params={"max_price": 10})
    assert resp.status_code == 200
    assert all(l["price"] <= 10 for l in resp.json()["listings"])


def test_get_listings_min_greater_than_max(client, auth_headers):
    """min_price > max_price returns 400."""
    resp = client.get("/listings/", params={"min_price": 100, "max_price": 10})
    assert resp.status_code == 400


def test_get_listings_sort_price_low_to_high(client, auth_headers):
    """Sort by price ascending returns listings in correct order."""
    _create_listing(client, auth_headers, title="Expensive Item", price="100.00")
    _create_listing(client, auth_headers, title="Cheap Item", price="1.00")

    resp = client.get("/listings/", params={"sort": "price_low_to_high"})
    assert resp.status_code == 200
    prices = [l["price"] for l in resp.json()["listings"]]
    assert prices == sorted(prices)


def test_get_listings_sort_price_high_to_low(client, auth_headers):
    """Sort by price descending returns listings in correct order."""
    _create_listing(client, auth_headers, title="Cheap Item", price="1.00")
    _create_listing(client, auth_headers, title="Expensive Item", price="100.00")

    resp = client.get("/listings/", params={"sort": "price_high_to_low"})
    assert resp.status_code == 200
    prices = [l["price"] for l in resp.json()["listings"]]
    assert prices == sorted(prices, reverse=True)


def test_get_listings_sort_newest(client, auth_headers):
    """Sort by newest returns most recent listings first."""
    _create_listing(client, auth_headers, title="First Created", price="10.00")
    _create_listing(client, auth_headers, title="Second Created", price="20.00")

    resp = client.get("/listings/", params={"sort": "newest"})
    assert resp.status_code == 200
    listings = resp.json()["listings"]
    assert len(listings) >= 2
    # Most recent should be first
    assert listings[0]["title"] == "Second Created"


def test_get_listings_invalid_sort(client):
    """Invalid sort value returns 400."""
    resp = client.get("/listings/", params={"sort": "random"})
    assert resp.status_code == 400


def test_get_listings_invalid_date_listed(client):
    """Invalid date_listed value returns 400."""
    resp = client.get("/listings/", params={"date_listed": "last_year"})
    assert resp.status_code == 400


def test_get_listings_pagination(client, auth_headers):
    """Pagination with custom page and limit works."""
    for i in range(5):
        _create_listing(client, auth_headers, title=f"Paginated {i}", price="10.00")

    resp = client.get("/listings/", params={"page": 1, "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["listings"]) == 2
    assert data["limit"] == 2
    assert data["page"] == 1
    assert data["total"] >= 5


def test_get_listings_page_2(client, auth_headers):
    """Requesting page 2 returns different results than page 1."""
    for i in range(5):
        _create_listing(client, auth_headers, title=f"Page Test {i}", price="10.00")

    resp1 = client.get("/listings/", params={"page": 1, "limit": 2})
    resp2 = client.get("/listings/", params={"page": 2, "limit": 2})

    ids_page1 = {l["id"] for l in resp1.json()["listings"]}
    ids_page2 = {l["id"] for l in resp2.json()["listings"]}
    assert ids_page1.isdisjoint(ids_page2)


def test_get_listings_limit_max_100(client):
    """Limit > 100 is rejected (max limit is 100)."""
    resp = client.get("/listings/", params={"limit": 101})
    assert resp.status_code == 422


def test_get_listings_limit_zero(client):
    """Limit of 0 is rejected (min limit is 1)."""
    resp = client.get("/listings/", params={"limit": 0})
    assert resp.status_code == 422


def test_get_listings_page_zero(client):
    """Page 0 is rejected (min page is 1)."""
    resp = client.get("/listings/", params={"page": 0})
    assert resp.status_code == 422


def test_get_listings_default_active_only(client, auth_headers):
    """By default, only active listings are returned."""
    resp1 = _create_listing(client, auth_headers, title="Active Listing", price="10.00")
    listing_id = resp1.json()["id"]

    # Mark as sold
    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)

    resp = client.get("/listings/")
    titles = [l["title"] for l in resp.json()["listings"]]
    assert "Active Listing" not in titles


def test_get_listings_filter_sold(client, auth_headers):
    """Can filter for sold listings."""
    resp1 = _create_listing(client, auth_headers, title="Will Be Sold", price="10.00")
    listing_id = resp1.json()["id"]
    client.patch(f"/listings/{listing_id}", data={"status": "sold"}, headers=auth_headers)

    resp = client.get("/listings/", params={"status": "sold"})
    assert resp.status_code == 200
    titles = [l["title"] for l in resp.json()["listings"]]
    assert "Will Be Sold" in titles


# ── Get listing by ID tests ─────────────────────────────────────────────


def test_get_listing_by_id(client, auth_headers):
    """GET /listings/{id} returns full listing with seller and images."""
    create_resp = _create_listing(client, auth_headers, title="Single Listing", price="9.00", category="Other")
    listing_id = create_resp.json()["id"]

    resp = client.get(f"/listings/{listing_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == listing_id
    assert "seller" in data
    assert data["seller"]["email"] == "testuser@my.yorku.ca"
    assert "images" in data
    assert isinstance(data["images"], list)


def test_get_listing_not_found(client):
    """GET /listings/99999 returns 404."""
    resp = client.get("/listings/99999")
    assert resp.status_code == 404


# ── Update listing tests ────────────────────────────────────────────────


def test_update_listing_owner(client, auth_headers):
    """Owner can update their listing's title and status."""
    create_resp = _create_listing(client, auth_headers, title="Old Title", price="10.00", category="Other")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"title": "New Title", "status": "sold"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    data = patch_resp.json()
    assert data["title"] == "New Title"
    assert data["status"] == "sold"


def test_update_listing_not_owner(client, auth_headers, second_auth_headers):
    """Non-owner cannot update someone else's listing (403)."""
    create_resp = _create_listing(client, auth_headers, title="Owner Listing", price="10.00", category="Other")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"status": "removed"},
        headers=second_auth_headers,
    )
    assert patch_resp.status_code == 403


def test_update_listing_pending_status(client, auth_headers):
    """Owner can set listing status to 'pending'."""
    create_resp = _create_listing(client, auth_headers, title="Pending Test", price="15.00", category="Other")
    assert create_resp.status_code == 201
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"status": "pending"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "pending"


def test_update_listing_removed_status(client, auth_headers):
    """Owner can set listing status to 'removed'."""
    create_resp = _create_listing(client, auth_headers, title="Remove Test", price="15.00")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"status": "removed"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "removed"


def test_update_listing_price(client, auth_headers):
    """Owner can update listing price."""
    create_resp = _create_listing(client, auth_headers, title="Price Update", price="10.00")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"price": "99.99"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["price"] == 99.99


def test_update_listing_description(client, auth_headers):
    """Owner can update listing description."""
    create_resp = _create_listing(client, auth_headers, title="Desc Update", description="Old desc")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/listings/{listing_id}",
        data={"description": "New description"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["description"] == "New description"


def test_update_listing_unauthenticated(client, auth_headers):
    """Updating listing without auth returns 401."""
    create_resp = _create_listing(client, auth_headers, title="No Auth Update")
    listing_id = create_resp.json()["id"]

    patch_resp = client.patch(f"/listings/{listing_id}", data={"title": "Hacked"})
    assert patch_resp.status_code == 401


def test_update_listing_not_found(client, auth_headers):
    """Updating non-existent listing returns 404."""
    patch_resp = client.patch(
        "/listings/99999",
        data={"title": "Ghost"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 404


# ── Delete listing tests ────────────────────────────────────────────────


def test_delete_listing_owner(client, auth_headers):
    """Owner can delete their listing."""
    create_resp = _create_listing(client, auth_headers, title="Delete Me")
    listing_id = create_resp.json()["id"]

    del_resp = client.delete(f"/listings/{listing_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify listing is gone
    get_resp = client.get(f"/listings/{listing_id}")
    assert get_resp.status_code == 404


def test_delete_listing_not_owner(client, auth_headers, second_auth_headers):
    """Non-owner cannot delete someone else's listing (403)."""
    create_resp = _create_listing(client, auth_headers, title="Not Yours")
    listing_id = create_resp.json()["id"]

    del_resp = client.delete(f"/listings/{listing_id}", headers=second_auth_headers)
    assert del_resp.status_code == 403


def test_delete_listing_not_found(client, auth_headers):
    """Deleting a non-existent listing returns 404."""
    del_resp = client.delete("/listings/99999", headers=auth_headers)
    assert del_resp.status_code == 404


def test_delete_listing_unauthenticated(client, auth_headers):
    """Deleting a listing without auth returns 401."""
    create_resp = _create_listing(client, auth_headers, title="No Auth Delete")
    listing_id = create_resp.json()["id"]

    del_resp = client.delete(f"/listings/{listing_id}")
    assert del_resp.status_code == 401


# ── Image upload tests ──────────────────────────────────────────────────


def test_create_listing_with_images(client, auth_headers):
    """POST /listings/ with images returns listing with image data."""
    files = [
        ("images", ("test-image.jpg", b"fake-image-bytes", "image/jpeg")),
    ]
    resp = _create_listing(
        client, auth_headers,
        title="Listing With Image",
        price="19.99",
        category="Other",
        description="Has an image",
        files=files,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "images" in data
    assert len(data["images"]) == 1
    file_path = data["images"][0]["file_path"]
    assert file_path.startswith("uploads/")

    disk_path_repo_root = Path(file_path)
    disk_path_backend = Path("backend") / file_path
    assert (
        disk_path_repo_root.exists() or disk_path_backend.exists()
    ), f"Expected uploaded file at {disk_path_repo_root} or {disk_path_backend}"


def test_create_listing_with_multiple_images(client, auth_headers):
    """Multiple images are uploaded with correct positions."""
    files = [
        ("images", ("img1.jpg", b"fake1", "image/jpeg")),
        ("images", ("img2.png", b"fake2", "image/png")),
    ]
    resp = _create_listing(client, auth_headers, title="Multi Image", files=files)
    assert resp.status_code == 201
    images = resp.json()["images"]
    assert len(images) == 2
    positions = [img["position"] for img in images]
    assert 0 in positions
    assert 1 in positions


def test_create_listing_without_images(client, auth_headers):
    """Listing without images returns empty images array."""
    resp = _create_listing(client, auth_headers, title="No Images")
    assert resp.status_code == 201
    assert resp.json()["images"] == []
