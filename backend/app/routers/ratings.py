from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingUpdate, RatingOut, SellerRatingsOut, MyRatingOut
from app.services import rating_service

router = APIRouter()


@router.get("/users/{user_id}/ratings", response_model=SellerRatingsOut)
def get_seller_ratings(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Public: Get all ratings for a seller."""
    return rating_service.get_seller_ratings(db, seller_id=user_id)


@router.get("/listings/{listing_id}/rating/me", response_model=MyRatingOut)
def get_my_rating(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auth required: Check eligibility and retrieve current user's rating for this listing."""
    return rating_service.get_my_rating_for_listing(
        db, listing_id=listing_id, rater_id=current_user.id
    )


@router.post(
    "/listings/{listing_id}/rating",
    response_model=RatingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rating(
    listing_id: int,
    body: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auth required: Submit a rating for a seller (must have messaged on this listing)."""
    return rating_service.create_rating(
        db,
        listing_id=listing_id,
        rater_id=current_user.id,
        score=body.score,
        comment=body.comment,
    )


@router.patch("/listings/{listing_id}/rating", response_model=RatingOut)
def update_rating(
    listing_id: int,
    body: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auth required: Edit an existing rating."""
    return rating_service.update_rating(
        db,
        listing_id=listing_id,
        rater_id=current_user.id,
        score=body.score,
        comment=body.comment,
    )


@router.delete("/listings/{listing_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auth required: Delete your own rating."""
    rating_service.delete_rating(db, listing_id=listing_id, rater_id=current_user.id)
