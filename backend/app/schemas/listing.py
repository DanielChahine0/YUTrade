# Assigned to: Lakshan Kandeepan
# Phase: 2 (B2.2)
#
# TODO: Define Pydantic schemas for listing endpoints.
#
# ListingCreate (used for POST /listings — note: actual endpoint uses Form fields, not JSON,
#   because images are uploaded as multipart. This schema documents the expected fields):
#   - title: str (max 200 chars)
#   - description: Optional[str]
#   - price: float (must be > 0)
#   - category: Optional[str]
#
# ImageOut:
#   - id: int
#   - file_path: str
#   - position: int
#   class Config: from_attributes = True
#
# SellerOut (minimal user info shown on listing):
#   - id: int
#   - name: str
#   - email: str
#   class Config: from_attributes = True
#
# ListingOut (full listing response):
#   - id: int
#   - seller_id: int
#   - seller: SellerOut
#   - title: str
#   - description: Optional[str]
#   - price: float
#   - category: Optional[str]
#   - status: str
#   - images: List[ImageOut]
#   - created_at: datetime
#   - updated_at: datetime
#   class Config: from_attributes = True
#
# ListingUpdate (for PATCH /listings/{id}):
#   - title: Optional[str]
#   - description: Optional[str]
#   - price: Optional[float]
#   - status: Optional[str] (must be one of "active", "sold", "removed")
#
# PaginatedListings (for GET /listings):
#   - listings: List[ListingOut]
#   - total: int
#   - page: int
#   - limit: int

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ListingCreate(BaseModel):
    title: str = Field(..., max_length=200, description="Listing title", example="EECS 2011 Textbook")
    description: Optional[str] = Field(None, description="Detailed item description", example="Good condition, light highlighting on chapters 1–3")
    price: float = Field(..., gt=0, description="Asking price in CAD dollars", example=25.00)
    category: Optional[str] = Field(None, description="Item category (Textbooks, Electronics, Furniture, Clothing, Other)", example="Textbooks")


class ImageOut(BaseModel):
    id: int = Field(..., description="Image record ID", example=1)
    file_path: str = Field(..., description="Server-relative path to the image file", example="uploads/a1b2c3d4-....jpg")
    position: int = Field(..., description="Display order position (0-indexed)", example=0)

    class Config:
        from_attributes = True


class SellerOut(BaseModel):
    id: int = Field(..., description="Seller's user ID", example=7)
    name: str = Field(..., description="Seller's display name", example="Jane Smith")
    email: str = Field(..., description="Seller's York University email", example="jsmith@my.yorku.ca")

    class Config:
        from_attributes = True


class ListingOut(BaseModel):
    id: int = Field(..., description="Unique listing ID", example=42)
    seller_id: int = Field(..., description="ID of the seller user", example=7)
    seller: SellerOut = Field(..., description="Basic seller information")
    title: str = Field(..., description="Listing title", example="EECS 2011 Textbook")
    description: Optional[str] = Field(None, description="Item description", example="Good condition")
    price: float = Field(..., description="Price in CAD dollars", example=25.00)
    category: Optional[str] = Field(None, description="Item category", example="Textbooks")
    status: str = Field(..., description="Listing status: active, sold, or removed", example="active")
    images: List[ImageOut] = Field(..., description="List of uploaded images")
    created_at: datetime = Field(..., description="Timestamp when the listing was created")
    updated_at: datetime = Field(..., description="Timestamp of the last update")

    class Config:
        from_attributes = True


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, description="New title (max 200 chars)", example="Updated: EECS 2011 Textbook — Final Edition")
    description: Optional[str] = Field(None, description="Updated item description", example="Minor cover wear, otherwise excellent")
    price: Optional[float] = Field(None, gt=0, description="New asking price in CAD dollars", example=20.00)
    status: Optional[Literal["active", "sold", "removed"]] = Field(None, description="New status — use 'sold' when sold, 'removed' to take down", example="sold")


class PaginatedListings(BaseModel):
    listings: List[ListingOut] = Field(..., description="Array of listing objects for the current page")
    total: int = Field(..., description="Total number of listings matching the query", example=134)
    page: int = Field(..., description="Current page number", example=1)
    limit: int = Field(..., description="Results per page", example=20)
