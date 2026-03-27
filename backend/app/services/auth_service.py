# Assigned to: Daniel Chahine
# Phase: 1 (B1.7)
#
# TODO: Implement authentication business logic.
#
# This service layer is called by routers/auth.py. It contains the core logic
# separated from HTTP concerns.
#
# register_user(db, email, password, name) -> User:
#   - Validate email domain (@my.yorku.ca or @yorku.ca)
#   - Check for existing user with same email
#   - Hash the password
#   - Create and save User(is_verified=False)
#   - Generate 6-digit random code (e.g. random.randint(100000, 999999))
#   - Create VerificationCode with expires_at = now + 15 minutes
#   - Call email_service.send_verification_email(email, code)
#   - Return the created user
#
# verify_user(db, email, code) -> bool:
#   - Look up user by email
#   - Find most recent VerificationCode where used=False and expires_at > now
#   - Compare code
#   - If match: mark code as used, set user.is_verified = True, commit, return True
#   - Otherwise: return False (or raise appropriate error)
#
# authenticate_user(db, email, password) -> User | None:
#   - Look up user by email
#   - Verify password hash
#   - Check is_verified
#   - Return user if all checks pass, None otherwise

import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.config import settings
from app.models.user import User
from app.models.password_reset import PasswordResetCode
from app.utils.security import hash_password, verify_password
from app.services.email_service import send_password_reset_email

ALLOWED_DOMAINS = ("@my.yorku.ca", "@yorku.ca")


def purge_expired_codes(db: Session) -> None:
    """Delete all expired or used password-reset codes."""
    now = datetime.utcnow()
    db.query(PasswordResetCode).filter(
        (PasswordResetCode.expires_at <= now) | (PasswordResetCode.used == True)
    ).delete(synchronize_session=False)
    db.commit()


def register_user(db: Session, email: str, password: str, name: str) -> User:
    """Register a new user, generate verification code, and send it."""
    purge_expired_codes(db)

    # Validate email domain
    email_lower = email.lower()
    if not any(email_lower.endswith(domain) for domain in ALLOWED_DOMAINS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a @my.yorku.ca or @yorku.ca address",
        )

    # Check for existing user
    existing = db.query(User).filter(User.email == email_lower).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Check password length (bcrypt supports up to 72 bytes)
    if len(password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes.",
        )

    # Create user (auto-verified — no email verification required)
    user = User(
        email=email_lower,
        password_hash=hash_password(password),
        name=name,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password. Raises on failure."""
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    return user


def request_password_reset(db: Session, email: str) -> None:
    """Generate a password reset code and email it to the user."""
    purge_expired_codes(db)

    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email",
        )

    # Delete any existing reset codes for this user
    db.query(PasswordResetCode).filter(PasswordResetCode.user_id == user.id).delete()

    code = str(random.randint(100000, 999999))
    reset = PasswordResetCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES),
    )
    db.add(reset)
    db.commit()

    send_password_reset_email(email.lower(), code)


def reset_password(db: Session, email: str, code: str, new_password: str) -> None:
    """Verify reset code and update the user's password."""
    purge_expired_codes(db)

    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    reset = (
        db.query(PasswordResetCode)
        .filter(
            PasswordResetCode.user_id == user.id,
            PasswordResetCode.used == False,
            PasswordResetCode.expires_at > datetime.utcnow(),
        )
        .order_by(PasswordResetCode.id.desc())
        .first()
    )

    if not reset or reset.code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code",
        )

    if len(new_password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes.",
        )

    reset.used = True
    user.password_hash = hash_password(new_password)
    db.commit()


def update_profile(db: Session, user_id: int, name: str) -> User:
    """Update the user's display name."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.name = name
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> None:
    """Change password for a logged-in user after verifying their current password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if len(new_password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()


def delete_account(db: Session, user_id: int, password: str) -> None:
    """Permanently delete a user account and all associated data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is incorrect")

    # Delete image files from disk for all user's listings
    from app.models.listing import Listing
    from app.models.image import Image
    from app.models.message import Message
    from app.models.rating import Rating

    listings = db.query(Listing).options(joinedload(Listing.images)).filter(Listing.seller_id == user_id).all()
    for listing in listings:
        for image in listing.images:
            try:
                filename = image.file_path.replace("uploads/", "", 1)
                disk_path = os.path.join(settings.UPLOAD_DIR, filename)
                os.remove(disk_path)
            except OSError:
                pass

    # Delete messages where user is sender or receiver
    db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).delete(synchronize_session=False)

    # Delete password reset codes
    db.query(PasswordResetCode).filter(PasswordResetCode.user_id == user_id).delete()

    # Delete ratings given by this user (rater_id is NOT NULL, so must delete explicitly)
    db.query(Rating).filter(Rating.rater_id == user_id).delete(synchronize_session=False)

    # Delete listings (cascades to images and ratings via ORM)
    for listing in listings:
        db.delete(listing)

    db.delete(user)
    db.commit()
