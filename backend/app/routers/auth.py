# Assigned to: Daniel Chahine
# Phase: 1 (B1.8)
#
# TODO: Implement authentication API endpoints.
#
# Create router = APIRouter()
#
# POST /register
#   - Request body: RegisterRequest (email, password, name)
#   - Validate email domain ends with @my.yorku.ca or @yorku.ca → 400 if not
#   - Check if email already exists in DB → 409 if duplicate
#   - Hash the password using security.hash_password()
#   - Create User in DB with is_verified=False
#   - Generate a 6-digit verification code, save as VerificationCode with expires_at
#   - Send verification email (or log to console in dev mode) via email_service
#   - Return 201: {"message": "Verification code sent to your email", "user_id": user.id}
#
# POST /verify
#   - Request body: VerifyRequest (email, code)
#   - Look up user by email → 400 if not found
#   - Look up most recent unused, non-expired VerificationCode for user
#   - If code matches: mark code as used, set user.is_verified = True → 200
#   - If code doesn't match or is expired → 400
#
# POST /login
#   - Request body: LoginRequest (email, password)
#   - Look up user by email → 401 if not found
#   - Verify password using security.verify_password() → 401 if wrong
#   - Check user.is_verified → 403 if not verified
#   - Create JWT access token with sub=str(user.id) using security.create_access_token()
#   - Return 200: TokenResponse {access_token, token_type: "bearer", user: UserOut}

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, VerifyRequest, LoginRequest, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.schemas.user import UserOut, UpdateProfileRequest, ChangePasswordRequest, DeleteAccountRequest
from app.services.auth_service import (
    register_user, verify_user, authenticate_user, resend_verification_code,
    request_password_reset, reset_password, update_profile, change_password,
    delete_account,
)
from app.utils.security import create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and send a verification code."""
    user = register_user(db, request.email, request.password, request.name)
    return {"message": "Verification code sent to your email", "user_id": user.id}


@router.post("/verify", status_code=status.HTTP_200_OK)
def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    """Verify a user's email with the provided 6-digit code."""
    verify_user(db, request.email, request.code)
    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
def resend_verification(email: str, db: Session = Depends(get_db)):
    """Resend a verification code to an unverified user."""
    resend_verification_code(db, email)
    return {"message": "Verification code resent"}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = authenticate_user(db, request.email, request.password)
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send a password reset code to the user's email."""
    request_password_reset(db, request.email)
    return {"message": "Password reset code sent to your email"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password_endpoint(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset a user's password using a valid reset code."""
    reset_password(db, request.email, request.code, request.new_password)
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's name."""
    return update_profile(db, current_user.id, request.name)


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password_endpoint(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for the currently logged-in user."""
    change_password(db, current_user.id, request.current_password, request.new_password)
    return {"message": "Password changed successfully"}


@router.post("/delete-account", status_code=status.HTTP_200_OK)
def delete_account_endpoint(
    request: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete the current user's account and all associated data."""
    delete_account(db, current_user.id, request.password)
    return {"message": "Account deleted successfully"}
