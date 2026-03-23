from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.rating import Rating
from app.models.listing import Listing
from app.models.message import Message
from app.models.user import User
from app.schemas.rating import SellerRatingsOut, MyRatingOut


def _get_rating_with_rater(db: Session, rating_id: int) -> Rating:
    return (
        db.query(Rating)
        .options(joinedload(Rating.rater))
        .filter(Rating.id == rating_id)
        .first()
    )


def create_rating(
    db: Session,
    listing_id: int,
    rater_id: int,
    score: int,
    comment: Optional[str],
) -> Rating:
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if rater_id == listing.seller_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You cannot rate your own listing")

    contacted = db.query(Message).filter(
        Message.listing_id == listing_id,
        Message.sender_id  == rater_id,
    ).first()
    if not contacted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must have contacted the seller about this listing before rating",
        )

    existing = db.query(Rating).filter(
        Rating.listing_id == listing_id,
        Rating.rater_id   == rater_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="You have already rated this listing")

    rating = Rating(
        listing_id=listing_id,
        seller_id=listing.seller_id,
        rater_id=rater_id,
        score=score,
        comment=comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return _get_rating_with_rater(db, rating.id)


def update_rating(
    db: Session,
    listing_id: int,
    rater_id: int,
    score: Optional[int],
    comment: Optional[str],
) -> Rating:
    rating = db.query(Rating).filter(
        Rating.listing_id == listing_id,
        Rating.rater_id   == rater_id,
    ).first()
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    if score is not None:
        rating.score = score
    if comment is not None:
        rating.comment = comment or None  # empty string → NULL

    db.commit()
    return _get_rating_with_rater(db, rating.id)


def delete_rating(db: Session, listing_id: int, rater_id: int) -> None:
    rating = db.query(Rating).filter(
        Rating.listing_id == listing_id,
        Rating.rater_id   == rater_id,
    ).first()
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    db.delete(rating)
    db.commit()


def get_my_rating_for_listing(
    db: Session,
    listing_id: int,
    rater_id: int,
) -> MyRatingOut:
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    can_rate = False
    if rater_id != listing.seller_id:
        contacted = db.query(Message).filter(
            Message.listing_id == listing_id,
            Message.sender_id  == rater_id,
        ).first()
        can_rate = contacted is not None

    rating = (
        db.query(Rating)
        .options(joinedload(Rating.rater))
        .filter(Rating.listing_id == listing_id, Rating.rater_id == rater_id)
        .first()
    )
    return MyRatingOut(rating=rating, can_rate=can_rate)


def get_seller_ratings(db: Session, seller_id: int) -> SellerRatingsOut:
    ratings = (
        db.query(Rating)
        .options(joinedload(Rating.rater))
        .filter(Rating.seller_id == seller_id)
        .order_by(Rating.created_at.desc())
        .all()
    )

    total_count = len(ratings)
    if total_count > 0:
        avg_result = (
            db.query(func.avg(Rating.score))
            .filter(Rating.seller_id == seller_id)
            .scalar()
        )
        average_score = round(float(avg_result), 2) if avg_result is not None else None
    else:
        average_score = None

    seller = db.query(User).filter(User.id == seller_id).first()

    return SellerRatingsOut(
        ratings=ratings,
        average_score=average_score,
        total_count=total_count,
        seller=seller,
    )
