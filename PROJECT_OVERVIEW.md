# YUTrade — Comprehensive Project Overview

## 1. What is YUTrade?

YUTrade is a verified campus marketplace exclusively for York University students and faculty. Users can buy and sell items — textbooks, electronics, furniture, clothing — within a trusted community. Registration is restricted to `@my.yorku.ca` and `@yorku.ca` email addresses, ensuring every account belongs to a real York community member.

Built as an EECS 4314 course project by a team of 6.

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | **FastAPI** (Python 3.10+) |
| Frontend | **React 19** (TypeScript) |
| Database | **SQLite** via SQLAlchemy ORM |
| Auth | **JWT** (python-jose) + **bcrypt** (passlib) |
| Email | **aiosmtplib** (SMTP) / **Resend API** / console fallback |
| Image Storage | Local filesystem (`uploads/` directory, UUID filenames) |
| Deployment | **Render** (backend) + **Vercel** (frontend) |
| Testing | **pytest** with in-memory SQLite (`StaticPool`) |

### 2.1 Backend Packages (`requirements.txt`)

| Package | Purpose | Example Usage |
|---------|---------|---------------|
| **fastapi** | Web framework for building the REST API. Provides routing, request validation, dependency injection, and auto-generated OpenAPI docs at `/docs`. | `@router.post("/auth/register")` defines an endpoint; `Depends(get_db)` injects a DB session. |
| **uvicorn[standard]** | ASGI server that runs the FastAPI application. The `[standard]` extra includes `uvloop` and `httptools` for better performance. | `uvicorn app.main:app --reload` starts the dev server with hot-reload on file changes. |
| **sqlalchemy** | ORM (Object-Relational Mapper) that maps Python classes to database tables. Handles queries, relationships, transactions, and migrations without writing raw SQL. | `db.query(Listing).filter(Listing.status == "active").all()` fetches all active listings. |
| **pydantic[email]** | Data validation library used for request/response schemas. The `[email]` extra adds `EmailStr` for email validation. FastAPI uses Pydantic models to auto-validate incoming JSON. | `class RegisterRequest(BaseModel): email: EmailStr` rejects `"not-an-email"` with a 422 error automatically. |
| **python-jose[cryptography]** | JWT (JSON Web Token) library for creating and decoding auth tokens. The `[cryptography]` backend provides the HS256 signing algorithm. | `jwt.encode({"sub": user.email, "exp": expire}, SECRET_KEY, algorithm="HS256")` creates a signed token. |
| **passlib[bcrypt]** | Password hashing library. The `[bcrypt]` extra uses the bcrypt algorithm with automatic salting and configurable cost factor (default 12 rounds). | `pwd_context.hash("mypassword")` returns `"$2b$12$..."` — a salted bcrypt hash. `pwd_context.verify("mypassword", hash)` checks it. |
| **bcrypt==4.0.1** | Low-level bcrypt implementation pinned to 4.x because passlib 1.7.4 is incompatible with bcrypt 5.x (internal API changed). | Used internally by passlib — not called directly. |
| **python-multipart** | Parses `multipart/form-data` requests, required by FastAPI for file uploads and form fields. | `images: List[UploadFile] = File(default=[])` in the create listing endpoint reads uploaded image files. |
| **python-dotenv** | Loads environment variables from a `.env` file into `os.environ`. Keeps secrets (API keys, DB URLs) out of source code. | `load_dotenv(_env_path)` in `config.py` loads `SECRET_KEY`, `SMTP_PASSWORD`, etc. from `backend/.env`. |
| **aiosmtplib** | Async SMTP client for sending emails. Supports STARTTLS encryption. Used to send verification and password-reset codes via Gmail. | `aiosmtplib.send(msg, hostname="smtp.gmail.com", port=587, start_tls=True)` sends an email through Google's SMTP server. |
| **pytest** | Testing framework. Discovers and runs test functions, provides fixtures for setup/teardown, and reports pass/fail results. | `def test_register_success(client): response = client.post("/auth/register", json={...}); assert response.status_code == 201` |
| **httpx** | Async-capable HTTP client used by FastAPI's `TestClient` under the hood. Required for running tests against the FastAPI app without starting a real server. | `client = TestClient(app)` — internally uses httpx to make requests to the app in-process. |

### 2.2 Frontend Packages (`package.json`)

| Package | Purpose | Example Usage |
|---------|---------|---------------|
| **react** | Core UI library for building component-based user interfaces. Components are functions that return JSX and manage state via hooks. | `const [email, setEmail] = useState("")` creates reactive state; `<input value={email} onChange={e => setEmail(e.target.value)} />` binds it to an input. |
| **react-dom** | Renders React components into the browser DOM. Entry point for the entire app. | `ReactDOM.createRoot(document.getElementById("root")).render(<App />)` in `index.tsx` mounts the app. |
| **react-router-dom** | Client-side routing library. Maps URL paths to React page components without full page reloads. | `<Route path="/listings/:id" element={<ListingDetailPage />} />` renders the detail page when navigating to `/listings/42`. |
| **axios** | HTTP client for making API requests. Supports interceptors (middleware for requests/responses), automatic JSON parsing, and multipart uploads. | `client.post("/auth/login", { email, password }).then(res => res.data)` calls the backend login endpoint and returns the JWT. |
| **typescript** | Adds static type checking to JavaScript. Catches type errors at compile time (e.g., passing a string where a number is expected). | `interface Listing { id: number; title: string; price: number }` — TypeScript will error if you try to access `listing.nam` (typo). |
| **react-scripts** | Build toolchain from Create React App. Bundles the app with Webpack, runs the dev server with hot reload, and compiles TypeScript. | `npm start` runs the dev server at `localhost:3000`; `npm run build` creates an optimized production bundle in `build/`. |
| **@testing-library/react** | Testing utilities for React components. Renders components in a test environment and provides queries that mimic how users find elements. | `render(<LoginPage />); const input = screen.getByPlaceholderText("Email"); fireEvent.change(input, { target: { value: "test@my.yorku.ca" } })` |
| **@testing-library/jest-dom** | Custom Jest matchers for DOM assertions. Makes test assertions more readable. | `expect(button).toBeDisabled()` and `expect(element).toHaveTextContent("Login")` instead of checking raw DOM properties. |
| **@testing-library/user-event** | Simulates real user interactions (typing, clicking, tabbing) more accurately than `fireEvent`. | `await userEvent.type(emailInput, "raj@my.yorku.ca")` simulates keystroke-by-keystroke typing. |
| **@types/react, @types/react-dom, @types/jest, @types/node** | TypeScript type definitions for React, ReactDOM, Jest, and Node.js. Provides autocompletion and type checking for these libraries. | These are dev-only — they provide types like `React.FC`, `React.FormEvent`, `HTMLInputElement` so TypeScript understands React's API. |
| **web-vitals** | Measures Core Web Vitals performance metrics (LCP, FID, CLS). Used for monitoring frontend performance in production. | `reportWebVitals(console.log)` in `index.tsx` logs performance metrics to the console. |

---

## 3. Team & Responsibilities

| Member | Role | Assigned Tasks |
|--------|------|---------------|
| Mickey (Michael Byalsky) | Database Layer | Models, database setup, SQLAlchemy config, `main.py` entry point |
| Daniel Chahine | Authentication | Auth endpoints, JWT, password hashing, email service, password reset |
| Lakshan Kandeepan | Listings | Listing CRUD, image upload/storage, search, filtering, pagination |
| Raj (Rajendra Brahmbhatt) | Messaging + DevOps | Message endpoints, thread logic, test infrastructure fixes, SMTP config, deployment fixes |
| Mai Komar | Frontend Pages & API | Auth pages, listing pages, API client, Axios interceptors |
| Harnaindeep Kaur | Frontend UI & Components | Browse page, components, styling, layout, types, messages page |

---

## 4. Architecture & Design Patterns

### 4.1 Dominant Architecture: Layered (N-Tier) + RESTful Client-Server

YUTrade follows a **Layered (N-Tier) Architecture** on the backend and a **Client-Server Architecture** overall, with a React frontend communicating with a FastAPI backend through a RESTful API.

The backend is split into three strict layers where each layer only communicates with the one directly below it:

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                      │
│         Presentation Tier — User Interface              │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP / REST (JSON)
┌──────────────────────▼──────────────────────────────────┐
│              ROUTERS (app/routers/)                      │
│         Presentation Tier — API Layer                   │
│  Handles HTTP concerns: validation, status codes, auth  │
└──────────────────────┬──────────────────────────────────┘
                       │  Python function calls
┌──────────────────────▼──────────────────────────────────┐
│              SERVICES (app/services/)                    │
│         Business Logic Tier                             │
│  Pure business rules: no HTTP, no database dialect      │
└──────────────────────┬──────────────────────────────────┘
                       │  SQLAlchemy ORM queries
┌──────────────────────▼──────────────────────────────────┐
│              MODELS (app/models/)                        │
│         Data Access Tier                                │
│  ORM classes mapped to SQLite tables                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                  [ SQLite DB ]
```

**Why this matters:** Each layer has a single responsibility. A router never writes SQL. A service never returns HTTP status codes. A model never decides business rules. This makes the code testable, maintainable, and easy to divide across team members.

---

### 4.2 Design Patterns Used (with Examples)

#### 4.2.1 Dependency Injection

FastAPI's `Depends()` injects database sessions and the authenticated user into route handlers. This decouples the handler from how those objects are created, making routes easy to test by swapping real dependencies for test doubles.

```python
# backend/app/routers/listings.py
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_listing(
    title: str = Form(...),
    db: Session = Depends(get_db),                    # ← DB session injected
    current_user: User = Depends(get_current_user),   # ← Auth user injected
):
    listing = listing_service.create_listing(db, current_user.id, title, ...)
    return listing
```

In tests, `get_db` is overridden to return an in-memory SQLite session — the route handler doesn't know or care:

```python
# backend/tests/conftest.py
app.dependency_overrides[get_db] = lambda: test_db_session
```

#### 4.2.2 Repository Pattern (via ORM)

SQLAlchemy ORM acts as an implicit Repository — services interact with Python objects, never raw SQL. The ORM translates operations into SQL behind the scenes.

```python
# backend/app/services/listing_service.py — no SQL anywhere
listing = Listing(seller_id=seller_id, title=title, price=price, ...)
db.add(listing)        # ORM handles INSERT
db.commit()

# Querying uses Python expressions, not SQL strings
listings = db.query(Listing).filter(
    Listing.status == "active",
    Listing.title.ilike(f"%{search}%")
).all()
```

#### 4.2.3 DTO / Data Transfer Object (Pydantic Schemas)

Pydantic schemas define strict contracts between layers. Internal ORM models are never exposed directly to the API — they're serialized through response schemas that control exactly what the client sees.

```python
# Internal model has password_hash, but the DTO hides it:
# backend/app/schemas/user.py
class UserOut(BaseModel):       # ← Only these fields go to the client
    id: int
    email: str
    name: str
    is_verified: bool
    created_at: datetime

# backend/app/models/user.py
class User(Base):               # ← Internal model has sensitive fields
    password_hash = Column(String(255))   # Never exposed
    ...
```

#### 4.2.4 MVC (Model-View-Controller) Variant

The project follows a variant of MVC adapted for API + SPA architecture:

| MVC Role | YUTrade Component | Example |
|----------|------------------|---------|
| **Model** | SQLAlchemy models | `models/listing.py` — defines Listing table |
| **Controller** | FastAPI routers | `routers/listings.py` — handles HTTP, delegates to services |
| **View** | React pages | `pages/BrowsePage.tsx` — renders listing grid |

The **Service layer** sits between Controller and Model, which is an enhancement over basic MVC — it keeps business logic out of both the router and the model.

#### 4.2.5 Context/Provider Pattern (Frontend State)

React's Context API provides global auth state to any component without prop drilling.

```typescript
// backend/app/context/AuthContext.tsx — Provider wraps the entire app
<AuthProvider>         // ← Provides user, token, login(), logout()
  <App />
</AuthProvider>

// Any nested component can consume it:
// frontend/src/hooks/useAuth.ts
const { user, isAuthenticated, login, logout } = useAuth()
```

#### 4.2.6 Interceptor Pattern

Axios interceptors act as middleware on every HTTP request and response, implementing cross-cutting concerns (auth headers, error handling) in one place.

```typescript
// frontend/src/api/client.ts

// REQUEST interceptor — auto-attaches JWT to every outgoing request
client.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token")
    if (token) {
        config.headers.set("Authorization", `Bearer ${token}`)
    }
    return config
})

// RESPONSE interceptor — global 401 handling
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("access_token")
            window.location.href = "/login"      // ← Auto-logout on expired token
        }
        return Promise.reject(error)
    }
)
```

#### 4.2.7 Higher-Order Component / Guard Pattern

`ProtectedRoute` wraps pages that require authentication, redirecting unauthenticated users to login.

```typescript
// frontend/src/App.tsx
<Route path="/create" element={
    <ProtectedRoute>              {/* ← Guard checks auth */}
        <CreateListingPage />     {/* ← Only renders if authenticated */}
    </ProtectedRoute>
} />

// frontend/src/components/ProtectedRoute.tsx
function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth()
    if (loading) return null
    if (!isAuthenticated) return <Navigate to="/login" />
    return children
}
```

#### 4.2.8 Middleware Pattern

CORS middleware applies globally to every request, and the SQLite PRAGMA listener enforces foreign key constraints on every database connection.

```python
# backend/app/main.py — CORS applied to all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# backend/app/database.py — runs on every new DB connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

#### 4.2.9 Cascade Pattern (Database)

Parent deletion automatically propagates to all children through foreign key cascades, preventing orphan records.

```python
# backend/app/models/listing.py
seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
images = relationship("Image", cascade="all, delete-orphan")

# Deleting a user triggers this chain:
# User deleted → Listings deleted → Images deleted (cascade)
#                                 → Messages deleted (cascade)
#              → VerificationCodes deleted (cascade)
#              → PasswordResetCodes deleted (cascade)
```

#### 4.2.10 Graceful Degradation / Fallback Pattern

The email service tries SMTP first and falls back to console output if it fails, ensuring the app stays functional even when email infrastructure is down.

```python
# backend/app/services/email_service.py
if settings.EMAIL_BACKEND == "smtp":
    try:
        # Try sending real email via SMTP
        loop = asyncio.new_event_loop()
        loop.run_until_complete(aiosmtplib.send(msg, ...))
        print(f"[SMTP] Verification email sent to {email}")
    except Exception as e:
        # Fallback: print code to console so registration isn't blocked
        print(f"[SMTP ERROR] Failed to send email to {email}: {e}")
        print(f"[FALLBACK] Verification code for {email}: {code}")
```

#### 4.2.11 12-Factor App Configuration

All configuration is loaded from environment variables (via `.env` file), never hardcoded. The same codebase runs in dev (`EMAIL_BACKEND=console`) and production (`EMAIL_BACKEND=smtp`) with zero code changes.

```python
# backend/app/config.py
load_dotenv(_env_path)

class Settings:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
        self.EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "console")
        self.SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
        ...
```

#### 4.2.12 Fixture-Based Integration Testing

Tests use real database operations (no mocking) with pytest fixtures that provide a fresh in-memory database, pre-authenticated users, and a test HTTP client for each test.

```python
# backend/tests/conftest.py
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=TEST_ENGINE)    # Fresh tables
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=TEST_ENGINE)      # Clean teardown

@pytest.fixture
def auth_headers(client, db_session):
    # Registers, verifies, and logs in a real user — no mocking
    client.post("/auth/register", json={...})
    code = db_session.query(VerificationCode).first().code
    client.post("/auth/verify", json={...})
    response = client.post("/auth/login", json={...})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

### 4.3 Backend Layer Flow: Router → Service → DB

```
HTTP Request
    ↓
Router (app/routers/)        ← Handles HTTP concerns: validation, status codes, auth dependency
    ↓
Service (app/services/)      ← Business logic: no HTTP awareness, pure Python
    ↓
Model (app/models/)          ← SQLAlchemy ORM: database reads/writes
    ↓
SQLite Database (yutrade.db)
```

### 4.4 Frontend Layer Flow: Pages → API Client → Backend

```
User Interaction
    ↓
Page (src/pages/)            ← Full-page React components with forms, state, effects
    ↓
API Client (src/api/)        ← Axios functions that call backend endpoints
    ↓
Axios Instance (client.ts)   ← Auto-injects JWT from localStorage, handles 401 redirect
    ↓
Backend API (localhost:8000)
```

### 4.5 Auth Flow Diagram

```
Register → 6-digit code emailed → Verify code → Account active → Login → JWT issued
                                                                           ↓
                                                              Stored in localStorage
                                                                           ↓
                                                              Auto-injected on every request
                                                              via Axios request interceptor
```

---

## 5. Data Model

### 5.1 Entity Relationship

```
users (1) ──────── (many) listings (1) ──────── (many) images
  │                          │
  │                          └──────────── (many) messages
  │
  ├── (many) verification_codes
  ├── (many) password_reset_codes
  ├── (many) messages (as sender)
  └── (many) messages (as receiver)
```

### 5.2 Tables

**users**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key, Auto-increment |
| email | String(255) | Unique, Not Null |
| password_hash | String(255) | Not Null (bcrypt) |
| name | String(100) | Not Null |
| is_verified | Boolean | Default: False |
| created_at | DateTime | Default: now |

**listings**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key |
| seller_id | Integer | FK → users (CASCADE), Indexed |
| title | String(200) | Not Null |
| description | Text | Nullable |
| price | Numeric(10,2) | Not Null |
| category | String(50) | Nullable (Textbooks, Electronics, Furniture, Clothing, Other) |
| status | String(20) | Default: 'active' (active / sold / removed), Indexed |
| created_at | DateTime | Default: now |
| updated_at | DateTime | Default: now, auto-updates |

**images**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key |
| listing_id | Integer | FK → listings (CASCADE) |
| file_path | String(500) | e.g., `uploads/a1b2c3d4.jpg` |
| position | Integer | Display order (0-indexed) |

**messages**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key |
| listing_id | Integer | FK → listings (CASCADE), Indexed |
| sender_id | Integer | FK → users (CASCADE), Indexed |
| receiver_id | Integer | FK → users (CASCADE), Indexed |
| content | Text | Not Null |
| created_at | DateTime | Default: now |

**verification_codes**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key |
| user_id | Integer | FK → users (CASCADE) |
| code | String(6) | 6-digit random |
| expires_at | DateTime | created_at + 15 minutes |
| used | Boolean | Default: False |

**password_reset_codes**
| Column | Type | Constraints |
|--------|------|------------|
| id | Integer | Primary Key |
| user_id | Integer | FK → users (CASCADE) |
| code | String(6) | 6-digit random |
| expires_at | DateTime | created_at + 15 minutes |
| used | Boolean | Default: False |

### 5.3 Cascade Deletes

All foreign keys use `ondelete="CASCADE"`. SQLite requires `PRAGMA foreign_keys=ON` to enforce this — the app sets this on every database connection via a SQLAlchemy event listener. Additionally, the listings→images relationship uses `cascade="all, delete-orphan"` at the ORM level.

**Delete chain example:** Deleting a user removes all their listings → which removes all listing images and messages → plus all verification and password reset codes.

### 5.4 Automatic Code Cleanup

The `purge_expired_codes()` function runs at the start of every auth-related operation (register, verify, resend, forgot-password, reset-password). It deletes all verification codes and password reset codes that are expired (`expires_at <= now`) or already used (`used == True`), preventing table bloat without a background scheduler.

---

## 6. API Endpoints

### 6.1 Authentication (`/auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Create a new account. Requires `@my.yorku.ca` or `@yorku.ca` email, password (min 8 chars), and name. Sends 6-digit verification code to email. Returns 201 with user_id. Returns 409 if email already registered. |
| POST | `/auth/verify` | No | Verify email with 6-digit code. Code must be unused and not expired (15 min). Returns 200 on success, 400 if code is invalid or expired. |
| POST | `/auth/resend-verification` | No | Resend a fresh verification code to an unverified user. Deletes all old codes first. Takes email as query param. |
| POST | `/auth/login` | No | Authenticate with email and password. Returns JWT `access_token`, `token_type`, and `user` object. Returns 401 if wrong password, 403 if email not verified, 404 if no account found. |
| POST | `/auth/forgot-password` | No | Send a 6-digit password reset code to the user's email. Returns 404 if no account found. |
| POST | `/auth/reset-password` | No | Reset password using a valid reset code. Requires email, code, and new_password (min 8 chars). |
| GET | `/auth/me` | Required | Get the current authenticated user's profile (id, email, name, is_verified, created_at). |
| PATCH | `/auth/me` | Required | Update the current user's display name. Request body: `{ "name": "New Name" }`. Returns updated user. |
| POST | `/auth/change-password` | Required | Change password while logged in. Requires `current_password` and `new_password`. Returns 400 if current password is wrong. |
| POST | `/auth/delete-account` | Required | Permanently delete the current user's account. Requires password confirmation. Cascades deletion of all listings, images (from disk), messages, ratings, and verification codes. |

### 6.2 Listings (`/listings`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/listings` | No | Browse listings with optional filters: `search` (keyword in title/description), `category`, `status` (default: active), `min_price`, `max_price`, `sort` (newest, price_low_to_high, price_high_to_low), `date_listed` (last_24_hours, last_7_days, last_30_days), `page` (default: 1), `limit` (default: 20, max: 100). Returns `{listings, total, page, limit}`. |
| POST | `/listings` | Required | Create a new listing. Accepts `multipart/form-data` with title, description, price, category, and image files. Images are saved to disk with UUID filenames. Returns 201 with the created listing. |
| GET | `/listings/{id}` | No | Get a single listing by ID with images and seller details. Returns 404 if not found. |
| PATCH | `/listings/{id}` | Required | Update a listing (owner only). Accepts `multipart/form-data`. All fields optional: title, description, price, category, status. Supports `new_images` (additional image uploads) and `delete_image_ids` (IDs of images to remove). Returns 403 if not the owner. |
| DELETE | `/listings/{id}` | Required | Permanently delete a listing (owner only). Removes the listing, all images from disk, associated messages, and cascaded ratings. Returns 403 if not the owner, 404 if not found. |

### 6.3 Messages (`/listings/{id}/messages`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/listings/{id}/messages` | Required | Send a message on a listing. If sender is not the seller, message goes to the seller. If sender is the seller, message goes to the last person who messaged. Cannot message yourself. Returns 201. |
| GET | `/listings/{id}/messages` | Required | Get all messages for a listing where you are a participant (sender or receiver). Returns messages in chronological order. |

### 6.4 Threads (`/messages`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/messages/threads` | Required | Get all conversation threads for the current user grouped by listing. Each thread includes: listing_id, listing_title, other_user_id, last_message preview, last_message_at timestamp, and message_count. Sorted by most recent first. |

### 6.5 Ratings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/{user_id}/ratings` | No | Get all ratings for a seller, including average score and total count. |
| GET | `/listings/{listing_id}/rating/me` | Required | Check if the current user can rate this listing's seller and retrieve their existing rating if any. |
| POST | `/listings/{listing_id}/rating` | Required | Submit a rating (1-5 score + optional comment) for a seller. Must have messaged on this listing. Cannot rate yourself. |
| PATCH | `/listings/{listing_id}/rating` | Required | Edit your existing rating for a listing. |
| DELETE | `/listings/{listing_id}/rating` | Required | Delete your own rating. Returns 204. |

### 6.6 Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check — returns `{"message": "YU Trade API"}` |
| GET | `/uploads/*` | Static file serving for uploaded images |
| GET | `/docs` | Interactive Swagger UI API documentation |

---

## 7. Frontend Pages — Features & How to Use

### 7.1 Register Page (`/register`)

**What it does:** Creates a new YUTrade account.

**How to use:**
1. Enter your full name
2. Enter your York University email (`@my.yorku.ca` or `@yorku.ca`)
3. Enter a password (minimum 8 characters)
4. Confirm your password
5. Click **Register**
6. You'll be redirected to the verification page

**Validations:** Email must be a YorkU domain. Password must be at least 8 characters. Passwords must match. If the email is already registered, you'll see an error.

---

### 7.2 Verify Page (`/verify`)

**What it does:** Verifies your email address with a 6-digit code.

**How to use:**
1. Check your YorkU email inbox for a message from YU Trade
2. Enter the 6-digit verification code
3. Click **Verify**
4. If the code expired (15 minutes), click **Resend Code** (available after a 60-second cooldown)
5. On success, you'll be redirected to the login page

---

### 7.3 Login Page (`/login`)

**What it does:** Signs you into your account.

**How to use:**
1. Enter your YorkU email
2. Enter your password
3. Click **Login**
4. On success, you're redirected to the Browse page
5. Your session persists across page refreshes (stored in localStorage)

**Error messages:** "No account found with this email" (404), "Invalid password" (401), "Please verify your email first" (403).

**Links:** "Forgot password?" takes you to the password reset flow. "Don't have an account?" takes you to registration.

---

### 7.4 Forgot Password Page (`/forgot-password`)

**What it does:** Initiates a password reset by sending a code to your email.

**How to use:**
1. Enter your registered YorkU email
2. Click **Send Reset Code**
3. Check your email for the 6-digit reset code
4. You'll be redirected to the Reset Password page

---

### 7.5 Reset Password Page (`/reset-password`)

**What it does:** Lets you set a new password using the reset code.

**How to use:**
1. Enter the 6-digit code from your email
2. Enter your new password (minimum 8 characters)
3. Confirm your new password
4. Click **Reset Password**
5. On success, you'll be redirected to login with your new password

---

### 7.6 Browse Page (`/` — Home)

**What it does:** The main marketplace — displays all active listings in a grid with advanced filtering and sorting.

**How to use:**
1. **Search:** Type keywords in the search bar to find items by title or description
2. **Filter by category:** Click category buttons (All, Textbooks, Electronics, Furniture, Clothing, Other)
3. **Filter by price range:** Set minimum and/or maximum price to narrow results
4. **Filter by date listed:** Choose how recent listings should be (last 24 hours, last 7 days, last 30 days)
5. **Sort results:** Sort by newest first, price low-to-high, or price high-to-low
6. **Browse:** Scroll through the listing cards showing image, title, price, category, date, and seller name
7. **Pagination:** Use Previous/Next buttons at the bottom to navigate pages
8. **View details:** Click any listing card to go to its detail page

**No login required** — anyone can browse listings.

---

### 7.7 Listing Detail Page (`/listings/:id`)

**What it does:** Shows full details of a single listing.

**How to use:**
1. View the image carousel on the left (click dots to switch images)
2. Read the title, description, price (shown in red), and category on the right
3. See the seller info section:
   - Seller name
   - **View Seller Profile** button to see all their listings
   - **Message Seller** button to start a conversation
   - Posted timestamp
4. If you're the owner, you can navigate to edit the listing

---

### 7.8 Create Listing Page (`/create`) — Protected

**What it does:** Post a new item for sale.

**How to use:**
1. Click **Sell Item** in the navbar (must be logged in)
2. Fill in:
   - **Title** (required, max 200 characters)
   - **Description** (optional, details about the item)
   - **Price** (required, must be greater than $0)
   - **Category** (dropdown: Textbooks, Electronics, Furniture, Clothing, Other)
   - **Images** (optional, drag and drop or click to upload, max 5MB per file)
3. Click **Create Listing**
4. You'll be redirected to your new listing's detail page

---

### 7.9 Edit Listing Page (`/listings/:id/edit`) — Protected

**What it does:** Update an existing listing you own, including managing images.

**How to use:**
1. From your listing detail page or My Listings, navigate to edit
2. Modify any fields: title, description, price, category
3. **Add new images:** Upload additional photos for the listing
4. **Remove existing images:** Delete specific images by their ID
5. Change status:
   - **Active** — visible to buyers
   - **Sold** — mark as sold (no longer appears in browse)
   - **Removed** — take down the listing
6. Click **Save Changes**

---

### 7.10 My Listings Page (`/my-listings`) — Protected

**What it does:** Shows all your listings in a table view.

**How to use:**
1. Click **My Listings** in the navbar
2. View your listings with image thumbnail, title, price, category, and status (color-coded)
3. Click a listing title to view its detail page
4. Click **Edit** to modify a listing
5. Click **Delete** to remove a listing (confirms before removing)
6. If you have no listings, click **Post Your First Item** to create one

---

### 7.11 Seller Profile Page (`/seller/:id`)

**What it does:** View another seller's public profile and their active listings.

**How to use:**
1. Click "View Seller Profile" from any listing detail page
2. See the seller's name, member since date, and rating
3. Browse their inventory table showing all active listings
4. Click **View** on any listing to see its detail page

---

### 7.12 Maps Page (`/maps`)

**What it does:** Shows suggested safe meetup locations on the York University campus for item exchanges.

**How to use:**
1. Click **Maps** in the navbar
2. View four suggested locations, each with an embedded Google Map:
   - **York Security** — Main security office
   - **Steacie Library** — Central campus library
   - **Second Student Centre** — Student hub
   - **York Lanes Mall** — On-campus shopping area
3. Use the embedded maps to find directions to each location

---

### 7.13 Messages Page (`/messages`) — Protected

**What it does:** Shows all your message conversations grouped by listing, and lets you open any conversation to read and send messages.

**How to use:**
1. Click **Messages** in the navbar (must be logged in)
2. View your inbox — all conversation threads sorted by most recent message
3. Each thread shows:
   - Listing thumbnail image
   - Other person's name
   - Listing title
   - Last message preview (truncated)
   - Timestamp of last message
4. **Click a thread** to open the conversation
5. In the conversation view:
   - See all messages in chronological order
   - Your messages appear on the right (sent), theirs on the left (received)
   - Type a message and click **Send** to reply
   - Messages auto-scroll to the latest
6. Click **Back to Messages** to return to the inbox
7. If you're the seller and no one has messaged yet, the message input is hidden

**Empty state:** "No messages yet" with a description explaining when conversations appear.

---

### 7.14 Account Settings Page (`/account`) — Protected

**What it does:** Manage your profile, change your password, or permanently delete your account.

**How to use:**
1. Click **Account** in the navbar (next to "Hello, [name]")
2. **Edit Profile:** Update your display name and click **Update Name**. The navbar greeting updates immediately.
3. **Change Password:** Enter your current password, then your new password twice. Click **Change Password**. You can verify it worked by logging out and logging back in with the new password.
4. **Delete Account:** Enter your password in the red danger zone section, click **Delete My Account**, and confirm the dialog. This permanently deletes your account and all associated data (listings, images, messages, ratings, verification codes). You'll be logged out and redirected to login.

**Validations:** Name cannot be empty. New password must be at least 6 characters and match confirmation. Current password must be correct. Delete requires password + browser confirmation dialog.

---

## 8. Security Features

| Feature | Implementation |
|---------|---------------|
| **Password hashing** | bcrypt via passlib (cost factor 12) |
| **JWT tokens** | HS256 algorithm, 60-minute expiry, signed with SECRET_KEY |
| **Email verification** | 6-digit codes, 15-minute expiry, single-use |
| **Domain restriction** | Only `@my.yorku.ca` and `@yorku.ca` emails accepted |
| **CORS** | Configured whitelist (default: `http://localhost:3000`) |
| **Cascade deletes** | Foreign keys with `ondelete=CASCADE`, SQLite PRAGMA enforced |
| **Code cleanup** | Expired/used verification codes auto-purged on every auth operation |
| **Password length** | Minimum 8 characters, maximum 72 bytes (bcrypt limit) |
| **401 handling** | Frontend auto-clears session and redirects to login |
| **Password-confirmed deletion** | Account and listing deletion require password re-entry |
| **Hard delete cascade** | Deleting account removes all user data from DB and image files from disk |

---

## 9. Testing

### 9.1 Test Infrastructure

- **In-memory SQLite** with `StaticPool` — all connections share one database
- **Fixtures:** `db_session` (fresh DB per test), `client` (FastAPI TestClient), `auth_headers` and `second_auth_headers` (pre-authenticated users)
- **No mocking** — tests register/verify/login real users against the test database

### 9.2 Test Cases (37 total)

**Authentication (8 tests):**
- Register with valid YorkU email → 201
- Register with non-YorkU email → 422
- Register with duplicate email → 409
- Verify with correct code → 200
- Verify with wrong code → 400
- Login with correct credentials → 200 + JWT
- Login with wrong password → 401
- Login with unverified account → 403

**Listings (10 tests):**
- Create listing (authenticated) → 201
- Create listing (unauthenticated) → 401
- Get all listings → paginated response
- Search listings by keyword
- Filter listings by category
- Get listing by ID → 200
- Get non-existent listing → 404
- Update listing (owner) → 200
- Update listing (non-owner) → 403
- Create listing with image upload

**Messages (6 tests):**
- Buyer sends message to seller → 201
- Seller replies to buyer → 201
- Get messages in chronological order
- Send message without auth → 401
- Send message to non-existent listing → 404
- Cannot message yourself on own listing → 400

**Ratings (14 tests):**
- Get seller ratings (empty) → 200
- Create rating for a seller → 201
- Cannot rate yourself → 400
- Must have messaged to rate → 400
- Get my rating for listing → 200
- Update existing rating → 200
- Delete rating → 204
- Cannot rate twice → 409
- Score must be 1-5 → 422
- Get seller ratings with average score
- Rate after buying (messaged) → 201
- Update rating score and comment
- Delete non-existent rating → 404
- Cannot rate non-existent listing → 404

### 9.3 Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Or use the script: `bash backend/run-tests.sh`

---

## 10. Configuration & Environment

### 10.1 Backend `.env`

```env
SECRET_KEY=your-secret-key-here          # JWT signing key
DATABASE_URL=sqlite:///./yutrade.db      # Database connection string
EMAIL_BACKEND=console                     # "console" (dev) or "smtp" (production)
SMTP_HOST=smtp.gmail.com                 # SMTP server
SMTP_PORT=587                            # SMTP port (STARTTLS)
SMTP_USER=your-email@my.yorku.ca         # Sender email
SMTP_PASSWORD=your-app-password          # Google App Password
ACCESS_TOKEN_EXPIRE_MINUTES=60           # JWT lifetime
VERIFICATION_CODE_EXPIRE_MINUTES=15      # Code expiry
```

**Dev mode:** Set `EMAIL_BACKEND=console` — verification codes print to the terminal. No SMTP credentials needed.

**Production (SMTP):** Set `EMAIL_BACKEND=smtp` with Google App Password credentials. Emails are sent via `smtp.gmail.com:587` with STARTTLS.

**Production (Resend):** Set `EMAIL_BACKEND=resend` and `RESEND_API_KEY=re_...`. Uses the Resend API for reliable email delivery without SMTP configuration.

### 10.2 Frontend `.env`

```env
REACT_APP_API_URL=http://localhost:8000
# Production: REACT_APP_API_URL=https://yutrade-api.onrender.com
```

---

## 11. Running the Application

### Backend

```bash
cd backend
bash start-backend.sh
# Or manually:
# python -m venv venv
# source venv/bin/activate  (or venv\Scripts\activate on Windows)
# pip install -r requirements.txt
# uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
bash start-frontend.sh
# Or manually:
# npm install
# npm start
```

Dev server starts at `http://localhost:3000`.

---

## 12. Deployment

### Backend — Render

Configured via `render.yaml`:
- **Plan:** Free tier
- **Runtime:** Python
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment variables:** SECRET_KEY (auto-generated), SMTP credentials (set manually in Render dashboard via `sync: false`)

### Frontend — Vercel

Deployed separately. Set `REACT_APP_API_URL` to the Render backend URL.

### Limitations on Free Tier

- Render free instances spin down after 15 minutes of inactivity (~30s cold start)
- SQLite database resets on every deploy (ephemeral filesystem)
- Uploaded images are lost on redeploy

---

## 13. Project File Structure

```
YUTrade/
├── render.yaml                    # Render deployment config
├── CLAUDE.md                      # AI assistant instructions
├── IMPLEMENTATION_PLAN.md         # Phase-by-phase task breakdown
├── README.md                      # Project readme
│
├── backend/
│   ├── requirements.txt           # Python dependencies
│   ├── start-backend.sh           # Startup script
│   ├── run-tests.sh               # Test runner script
│   ├── .env                       # Environment variables (not committed)
│   ├── .env.example               # Template for .env
│   ├── uploads/                   # Uploaded images (UUID filenames)
│   │
│   ├── app/
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── config.py              # Settings from environment
│   │   ├── database.py            # SQLAlchemy engine, session, Base
│   │   ├── dependencies.py        # get_db(), get_current_user()
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py        # Imports all models
│   │   │   ├── user.py            # User ORM model
│   │   │   ├── verification.py    # VerificationCode model
│   │   │   ├── password_reset.py  # PasswordResetCode model
│   │   │   ├── listing.py         # Listing model
│   │   │   ├── image.py           # Image model
│   │   │   ├── message.py         # Message model
│   │   │   └── rating.py          # Rating model
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py            # Register, Login, Verify, Reset schemas
│   │   │   ├── user.py            # UserOut, UpdateProfileRequest, ChangePasswordRequest, DeleteAccountRequest
│   │   │   ├── listing.py         # Listing CRUD + pagination schemas
│   │   │   ├── message.py         # MessageCreate, MessageOut schemas
│   │   │   └── rating.py          # RatingCreate, RatingUpdate, RatingOut, SellerRatingsOut
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py    # Auth business logic + code purging + account management
│   │   │   ├── email_service.py   # Console/SMTP/Resend email sending
│   │   │   ├── listing_service.py # Listing CRUD + image handling + hard delete
│   │   │   ├── message_service.py # Messaging + thread logic
│   │   │   └── rating_service.py  # Rating CRUD + eligibility checks
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py            # /auth/* endpoints (register, login, me, change-password, delete-account)
│   │   │   ├── listings.py        # /listings/* endpoints (CRUD + DELETE)
│   │   │   ├── messages.py        # /listings/{id}/messages/* endpoints
│   │   │   ├── threads.py         # /messages/threads endpoint
│   │   │   └── ratings.py         # /users/{id}/ratings, /listings/{id}/rating endpoints
│   │   │
│   │   └── utils/
│   │       └── security.py        # JWT + bcrypt utilities
│   │
│   └── tests/
│       ├── conftest.py            # Fixtures: db_session, client, auth_headers
│       ├── test_auth.py           # 8 auth tests
│       ├── test_auth_extended.py  # Extended auth tests
│       ├── test_listings.py       # 10 listing tests
│       ├── test_messages.py       # 6 message tests
│       └── test_ratings.py        # 14 rating tests
│
└── frontend/
    ├── package.json
    ├── start-frontend.sh          # Startup script
    ├── .env.example               # Template for .env
    │
    └── src/
        ├── App.tsx                # Route definitions
        ├── index.tsx              # React entry point
        │
        ├── types/
        │   └── index.ts           # All TypeScript interfaces
        │
        ├── api/
        │   ├── client.ts          # Axios instance with JWT interceptor
        │   ├── auth.ts            # Auth API (register, verify, login, resend, forgot/reset, updateProfile, changePassword, deleteAccount)
        │   ├── listings.ts        # Listings API (getListings, getListing, createListing, updateListing, deleteListing)
        │   ├── messages.ts        # Messages API (sendMessage, getMessages, getAllThreads)
        │   └── ratings.ts         # Ratings API (getSellerRatings, getMyRating, createRating, updateRating, deleteRating)
        │
        ├── context/
        │   └── AuthContext.tsx     # Global auth state (user, token, login, logout)
        │
        ├── hooks/
        │   └── useAuth.ts         # useAuth() custom hook
        │
        ├── utils/
        │   └── validators.ts      # Email, password, price validators + formatters
        │
        ├── components/
        │   ├── Layout.tsx         # Page wrapper (Navbar + Footer)
        │   ├── Navbar.tsx         # Top nav bar (YU red branding)
        │   ├── ProtectedRoute.tsx # Auth guard for routes
        │   ├── ListingCard.tsx    # Listing grid card
        │   ├── ImageUpload.tsx    # Drag-and-drop image upload
        │   ├── MessageThread.tsx  # Chat component (sent/received messages, send form)
        │   └── SearchBar.tsx      # Search/filter bar
        │
        └── pages/
            ├── RegisterPage.tsx       # Account registration
            ├── VerifyPage.tsx         # Email verification
            ├── LoginPage.tsx          # Login
            ├── ForgotPasswordPage.tsx  # Request password reset
            ├── ResetPasswordPage.tsx   # Reset password with code
            ├── BrowsePage.tsx         # Main marketplace grid
            ├── ListingDetailPage.tsx   # Single listing view
            ├── CreateListingPage.tsx   # Create new listing
            ├── EditListingPage.tsx     # Edit existing listing
            ├── MyListingsPage.tsx      # User's own listings
            ├── SellerProfilePage.tsx   # Public seller profile
            ├── MapsPage.tsx           # Campus meetup locations
            └── MessagesPage.tsx       # Inbox — thread list + active conversation view
```

---

## 14. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite instead of PostgreSQL | Simple setup for a course project; single-file DB, no server needed |
| JWT in localStorage (not cookies) | Simpler implementation; acceptable for a university project scope |
| Email verification required | Ensures only real YorkU community members can trade |
| Multipart form-data for listings | Needed for image file uploads alongside text fields |
| Nested message routes (`/listings/{id}/messages`) | Messages are contextual to a listing; keeps API RESTful |
| Separate `/messages/threads` endpoint | Inbox view needs cross-listing data; doesn't fit the nested pattern |
| `purge_expired_codes` (opportunistic) | Avoids background scheduler dependency; cleans up on every auth call |
| `StaticPool` for test DB | SQLite in-memory gives each connection its own DB; StaticPool forces sharing |
| Forward slashes for DB paths | `os.path.join` produces backslashes on Windows; URLs need forward slashes |
| Console email fallback | Developers can test without SMTP credentials; codes print to terminal |
