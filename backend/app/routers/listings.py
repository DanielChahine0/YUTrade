# Assigned to: Lakshan Kandeepan
# Phase: 2 (B2.5)
#
# TODO: Implement listings API endpoints.
#
# Create router = APIRouter()
#
# GET /
#   - Query params: search (str), category (str), status (str, default="active"),
#     page (int, default=1), limit (int, default=20)
#   - Auth: Optional (public endpoint)
#   - Call listing_service.get_listings() with filters
#   - Return 200: PaginatedListings {listings[], total, page, limit}
#   - Phase 3 (B3.5): Add min_price, max_price query params for filtering
#
# POST /
#   - Auth: Required (Depends(get_current_user))
#   - Accept multipart/form-data:
#       - title: str = Form(...)
#       - description: Optional[str] = Form(None)
#       - price: float = Form(...)
#       - category: Optional[str] = Form(None)
#       - images: List[UploadFile] = File(default=[])
#   - Call listing_service.create_listing() which:
#       - Creates Listing in DB
#       - Saves each image to uploads/ with a UUID filename
#       - Creates Image records in DB
#   - Return 201: ListingOut
#
# GET /{listing_id}
#   - Auth: Optional
#   - Fetch listing by ID with eager-loaded images and seller
#   - Return 404 if not found
#   - Return 200: ListingOut
#
# PATCH /{listing_id}
#   - Auth: Required (must be the listing owner)
#   - Request body: ListingUpdate (JSON)
#   - Only the listing's seller can update it → 403 if not owner
#   - Update only the provided fields
#   - Return 200: ListingOut

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.listing import ListingOut, ListingUpdate, PaginatedListings
from app.services import listing_service
from app.routers.messages import router as messages_router

router = APIRouter()

router.include_router(
    messages_router,
    prefix="/{listing_id}/messages",
    tags=["Messages"],
)


@router.get(
    "/",
    response_model=PaginatedListings,
    summary="Browse listings",
    responses={422: {"description": "Invalid query parameters"}},
)
def get_listings(
    search: Optional[str] = Query(None, description="Search keyword matched against title and description", examples=["calculus textbook"]),
    category: Optional[str] = Query(None, description="Filter by category (Textbooks, Electronics, Furniture, Clothing, Other)", examples=["Textbooks"]),
    status: str = Query("active", description="Filter by listing status. Use 'active' for available items", examples=["active"]),
    page: int = Query(1, description="Page number (1-indexed)", ge=1, examples=[1]),
    limit: int = Query(20, description="Number of results per page (max 100)", ge=1, le=100, examples=[20]),
    db: Session = Depends(get_db),
):
    """
    Browse all listings with optional search, filtering, and pagination.

    Returns a paginated list of listings. Defaults to active listings only.
    - Use `search` to match keywords in title or description.
    - Use `category` to narrow to a specific item type.
    - Use `status` to include sold (`sold`) or removed (`removed`) listings.
    - Use `page` and `limit` to paginate through results.

    No authentication required.
    """
    listings, total = listing_service.get_listings(
        db=db,
        search=search,
        category=category,
        status=status,
        page=page,
        limit=limit,
    )
    return {
        "listings": listings,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post(
    "/",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a listing",
    responses={
        401: {"description": "Not authenticated — Bearer token required"},
        422: {"description": "Validation error — check field constraints"},
    },
)
def create_listing(
    title: str = Form(..., description="Listing title", max_length=200, examples=["EECS 2011 Textbook"]),
    description: Optional[str] = Form(None, description="Detailed description of the item", examples=["Good condition, some highlighting in chapters 1-3"]),
    price: float = Form(..., description="Asking price in CAD dollars (must be > 0)", gt=0, examples=[25.00]),
    category: Optional[str] = Form(None, description="Item category: Textbooks, Electronics, Furniture, Clothing, or Other", examples=["Textbooks"]),
    images: List[UploadFile] = File(default=[], description="Optional image files (JPEG or PNG). Multiple files accepted."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new listing for sale.

    Accepts multipart/form-data. Uploaded images are stored server-side and
    accessible under the `/uploads/` path. Returns the created listing with
    assigned ID, seller info, and image URLs.

    Requires authentication: include `Authorization: Bearer <token>` header.
    """
    listing = listing_service.create_listing(
        db=db,
        seller_id=current_user.id,
        title=title,
        description=description,
        price=price,
        category=category,
        images=images,
    )
    return listing


@router.get(
    "/{listing_id}",
    response_model=ListingOut,
    summary="Get a listing",
    responses={404: {"description": "Listing not found"}},
)
def get_listing_by_id(
    listing_id: int = Path(..., description="The unique numeric ID of the listing", ge=1, examples=[42]),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single listing by its ID.

    Returns the full listing object including seller details and all uploaded
    images. No authentication required.

    Returns 404 if no listing exists with the given ID.
    """
    listing = listing_service.get_listing_by_id(db=db, listing_id=listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return listing


@router.patch(
    "/{listing_id}",
    response_model=ListingOut,
    summary="Update a listing",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "You are not the owner of this listing"},
        404: {"description": "Listing not found"},
    },
)
def update_listing(
    listing_id: int = Path(..., description="The unique numeric ID of the listing to update", ge=1, examples=[42]),
    update_data: ListingUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update one or more fields on an existing listing (owner only).

    All fields in the request body are optional — send only the fields you
    want to change. Valid status transitions:
    - `active` → `sold` (mark as sold)
    - `active` → `removed` (take down the listing)

    Only the listing's original seller can perform updates.

    Returns 403 if the authenticated user is not the listing owner.
    Returns 404 if no listing exists with the given ID.
    Requires authentication: include `Authorization: Bearer <token>` header.
    """
    try:
        listing = listing_service.update_listing(
            db=db,
            listing_id=listing_id,
            seller_id=current_user.id,
            update_data=update_data,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return listing
