from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    score:   int           = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class RatingUpdate(BaseModel):
    score:   Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class RaterOut(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}


class SellerOut(BaseModel):
    id:         int
    name:       str
    created_at: datetime
    model_config = {"from_attributes": True}


class RatingOut(BaseModel):
    id:         int
    listing_id: int
    seller_id:  int
    rater_id:   int
    rater:      RaterOut
    score:      int
    comment:    Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class SellerRatingsOut(BaseModel):
    ratings:       list[RatingOut]
    average_score: Optional[float]
    total_count:   int
    seller:        Optional[SellerOut] = None


class MyRatingOut(BaseModel):
    rating:   Optional[RatingOut]
    can_rate: bool
