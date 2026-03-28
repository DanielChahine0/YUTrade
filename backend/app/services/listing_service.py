# Assigned to: Lakshan Kandeepan
# Phase: 2 (B2.3)
#
# TODO: Implement listing business logic.
#
# create_listing(db, seller_id, title, description, price, category, images) -> Listing:
#   - Create Listing record in DB
#   - For each uploaded image file:
#       - Generate a UUID-based filename to avoid collisions (e.g. f"{uuid4()}.{ext}")
#       - Save file to uploads/ directory
#       - Create Image record with file_path and position (index)
#   - Commit and return the listing with relationships loaded

# get_listings(db, search, category, status, min_price, max_price, sort, date_listed, page, limit) -> (List[Listing], total):#   - Start with query on Listing
#   - Start with query on Listing
#   - Filter by status (default "active")
#   - If search: filter where title ILIKE %search% OR description ILIKE %search%
#   - If category: filter where category == category
#   - If min_price: filter where price >= min_price
#   - If max_price: filter where price <= max_price
#   - If date_listed: filter by created_at cutoff (last_24_hours, last_7_days, last_30_days)
#   - Apply sort order: newest, price_low_to_high, or price_high_to_low
#   - Count total matching records
#   - Apply offset = (page - 1) * limit and limit
#   - Return (listings, total_count)

# get_listing_by_id(db, listing_id) -> Listing | None:
#   - Query listing by ID with joinedload on images and seller
#   - Return listing or None
#
# update_listing(db, listing_id, seller_id, update_data) -> Listing:
#   - Fetch listing, verify seller_id matches
#   - Update only provided fields (title, description, price, status)
#   - Set updated_at to now
#   - Commit and return updated listing

import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models.image import Image
from app.models.listing import Listing


# TODO complete:
# - Create Listing record in DB
# - Save uploaded images under uploads/ using UUID filenames
# - Create Image DB rows with file_path + position
# - Commit and return listing with relationships loaded
def create_listing(
    db: Session,
    seller_id: int,
    title: str,
    description: Optional[str],
    price: float,
    category: Optional[str],
    images,
) -> Listing:
    listing = Listing(
        seller_id=seller_id,
        title=title,
        description=description,
        price=price,
        category=category,
    )

    db.add(listing)
    db.flush()  # Get listing.id before creating Image rows

    for index, image in enumerate(images):
        ext = ""
        if image.filename and "." in image.filename:
            ext = image.filename.rsplit(".", 1)[1]

        filename = f"{uuid4()}.{ext}" if ext else str(uuid4())
        disk_path = os.path.join(settings.UPLOAD_DIR, filename)

        with open(disk_path, "wb") as file_object:
            file_object.write(image.file.read())

        image_record = Image(
            listing_id=listing.id,
            file_path=f"uploads/{filename}",
            position=index,
        )
        db.add(image_record)

    db.commit()

    # Return the listing with seller + images loaded
    return get_listing_by_id(db, listing.id)


# TODO complete:
# - Start with query on Listing
# - Filter by status
# - Apply search on title OR description
# - Apply category filter
# - Count total
# - Apply offset + limit
# - Return (listings, total)
def get_listings(
    db: Session,
    search: Optional[str],
    category: Optional[str],
    status: str,
    min_price: Optional[float],
    max_price: Optional[float],
    sort: str,
    date_listed: Optional[str],
    page: int,
    limit: int,
):
    query = db.query(Listing).options(
        joinedload(Listing.images),
        joinedload(Listing.seller),
    )

    if status != "all":
        query = query.filter(Listing.status == status)

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%"),
            )
        )

    if category:
        query = query.filter(Listing.category == category)

    if min_price is not None:
        query = query.filter(Listing.price >= min_price)

    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    if date_listed == "last_24_hours":
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(Listing.created_at >= cutoff)
    elif date_listed == "last_7_days":
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Listing.created_at >= cutoff)
    elif date_listed == "last_30_days":
        cutoff = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Listing.created_at >= cutoff)

    if sort == "price_low_to_high":
        query = query.order_by(Listing.price.asc())
    elif sort == "price_high_to_low":
        query = query.order_by(Listing.price.desc())
    else:
        query = query.order_by(Listing.created_at.desc())

    total = query.count()

    offset = (page - 1) * limit
    listings = query.offset(offset).limit(limit).all()

    return listings, total


# TODO complete:
# - Query listing by ID
# - Eager-load images and seller
# - Return listing or None
def get_listing_by_id(db: Session, listing_id: int) -> Optional[Listing]:
    return (
        db.query(Listing)
        .options(
            joinedload(Listing.images),
            joinedload(Listing.seller),
        )
        .filter(Listing.id == listing_id)
        .first()
    )


# TODO complete:
# - Fetch listing
# - Verify seller_id matches
# - Update only provided fields
# - Set updated_at to now
# - Commit and return updated listing
def update_listing(
    db: Session,
    listing_id: int,
    seller_id: int,
    update_data,
    new_images=None,
    delete_image_ids=None,
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        return None

    if listing.seller_id != seller_id:
        raise PermissionError("Only the listing owner can update this listing")

    if update_data.title is not None:
        listing.title = update_data.title

    if update_data.description is not None:
        listing.description = update_data.description

    if update_data.price is not None:
        listing.price = update_data.price

    if update_data.category is not None:
        listing.category = update_data.category

    if update_data.status is not None:
        listing.status = update_data.status

    # Delete requested images
    if delete_image_ids:
        for image_id in delete_image_ids:
            image = db.query(Image).filter(
                Image.id == image_id,
                Image.listing_id == listing_id,
            ).first()
            if image:
                try:
                    filename = image.file_path.replace("uploads/", "", 1)
                    disk_path = os.path.join(settings.UPLOAD_DIR, filename)
                    os.remove(disk_path)
                except OSError:
                    pass
                db.delete(image)

    # Add new images
    if new_images:
        existing_count = db.query(Image).filter(Image.listing_id == listing_id).count()
        for index, image in enumerate(new_images):
            ext = ""
            if image.filename and "." in image.filename:
                ext = image.filename.rsplit(".", 1)[1]

            filename = f"{uuid4()}.{ext}" if ext else str(uuid4())
            disk_path = os.path.join(settings.UPLOAD_DIR, filename)

            with open(disk_path, "wb") as file_object:
                file_object.write(image.file.read())

            image_record = Image(
                listing_id=listing_id,
                file_path=f"uploads/{filename}",
                position=existing_count + index,
            )
            db.add(image_record)

    listing.updated_at = datetime.utcnow()

    db.commit()

    return get_listing_by_id(db, listing.id)


def delete_listing(db: Session, listing_id: int, seller_id: int) -> bool:
    """Hard-delete a listing, its images from disk, and all related DB rows."""
    listing = db.query(Listing).options(joinedload(Listing.images)).filter(Listing.id == listing_id).first()

    if not listing:
        return None

    if listing.seller_id != seller_id:
        raise PermissionError("Only the listing owner can delete this listing")

    # Delete image files from disk
    for image in listing.images:
        try:
            filename = image.file_path.replace("uploads/", "", 1)
            disk_path = os.path.join(settings.UPLOAD_DIR, filename)
            os.remove(disk_path)
        except OSError:
            pass

    # Cascade handles images and ratings; delete messages manually
    from app.models.message import Message
    db.query(Message).filter(Message.listing_id == listing_id).delete()

    db.delete(listing)
    db.commit()
    return True