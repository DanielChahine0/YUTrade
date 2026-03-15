# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YUTrade is a York University marketplace app (EECS 4314 course project) — a FastAPI + React TypeScript full-stack app where YU students can buy/sell items.

## Commands

### Backend
```bash
cd backend
source venv/bin/activate  # or: source ../.venv/bin/activate
uvicorn app.main:app --reload  # dev server at http://localhost:8000
pytest tests/                  # run tests
# API docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm start    # dev server at http://localhost:3000
npm test     # run tests
npm run build
```

### Environment
- Copy `backend/.env.example` to `backend/.env` and set `SECRET_KEY`
- Set `EMAIL_BACKEND=console` in dev — verification codes print to stdout
- Frontend uses `REACT_APP_API_URL` (defaults to `http://localhost:8000`)

## Architecture

**Stack:** FastAPI (Python) + React 19 (TypeScript) + SQLite via SQLAlchemy + JWT auth

### Backend (`backend/app/`)
Follows a **Router → Service → DB** pattern:
- `routers/` — HTTP layer (validation, status codes, dependency injection)
- `services/` — business logic (no direct HTTP concerns)
- `models/` — SQLAlchemy ORM models
- `schemas/` — Pydantic request/response models
- `dependencies.py` — `get_db()` and `get_current_user()` FastAPI dependencies
- `utils/security.py` — JWT creation/decoding, password hashing

Key behaviors:
- SQLite with `PRAGMA foreign_keys = ON` enforced per connection
- Cascade delete: deleting a listing removes its DB rows and image files from disk
- Images stored at `backend/uploads/` with UUID filenames, served at `/uploads` static route
- `EMAIL_BACKEND=console` prints verification codes; `smtp` sends real email via aiosmtplib

### Frontend (`frontend/src/`)
- `api/client.ts` — Axios instance: auto-injects JWT from localStorage, redirects to `/login` on 401
- `context/AuthContext.tsx` — global user/token state, `login()`/`logout()`
- `hooks/useAuth.ts` — consumes AuthContext
- `components/ProtectedRoute.tsx` — guards authenticated routes
- `utils/validators.ts` — email domain validation (must be `@my.yorku.ca`)

### Auth Flow
1. Register → 6-digit code emailed → verify → account active
2. Login → JWT returned → stored in localStorage → auto-injected on all requests
3. `resend-verification` endpoint available at `POST /auth/resend-verification`

### Data Model
- `users` → `listings` (one-to-many) → `images` (cascade delete)
- `messages` link sender, receiver, and listing_id
- Listing statuses: `active`, `sold`, `removed`

### API Conventions
- Multipart form-data for image uploads; JSON for everything else
- Optional auth on public GET endpoints (listing browse/detail)
- Errors use standard HTTP codes (400/401/403/404/409) with `{"detail": "..."}` body
