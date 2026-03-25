# Assigned to: Daniel Chahine
# Phase: 1 (B1.4)
#
# TODO: Define Pydantic schemas for user data.
#
# UserOut (used in API responses — never expose password_hash):
#   - id: int
#   - email: str
#   - name: str
#   - is_verified: bool
#   - created_at: datetime
#
#   class Config:
#       from_attributes = True  (allows creating from ORM objects)

from datetime import datetime
from pydantic import BaseModel


class UserOut(BaseModel):
    """User response schema — never exposes password_hash."""

    id: int
    email: str
    name: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile (name only)."""
    name: str


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password while logged in."""
    current_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    """Request schema for deleting user account — requires password confirmation."""
    password: str
