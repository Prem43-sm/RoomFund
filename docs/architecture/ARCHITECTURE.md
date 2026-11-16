# RoomFund — Architecture

## 1. Overview

RoomFund is a production-ready shared-room expense management web application. It lets students, roommates, flatmates, PG residents, couples, and families track personal and common expenses, split bills fairly, calculate who owes whom, record settlements, and manage recurring costs such as rent.

The application follows a **decoupled full-stack architecture**:

- **Frontend:** Next.js (React, TypeScript) deployed on Vercel
- **Backend:** FastAPI (Python) with SQLAlchemy ORM, hosted separately from the frontend
- **Database:** SQLite for local development; PostgreSQL for production
- **Authentication:** JWT-based (access + refresh tokens), password hashing with bcrypt

## 2. Repository Layout

```
ROOMFUND/
├── frontend/                  # Next.js application
├── backend/                   # FastAPI application
├── docs/
│   ├── architecture/
│   ├── database/
│   ├── API/
│   └── deployment/
├── .github/
│   └── workflows/
├── README.md
└── .env.example
```

## 3. Frontend Architecture

### Framework & Libraries
- **Next.js** (App Router) — React framework with server/client components
- **TypeScript** — type safety, API contracts shared via types/
- **Tailwind CSS** — utility-first styling
- **shadcn/ui** — accessible primitive component system
- **React Hook Form** + **Zod** — form management and validation
- **TanStack Query** — API/server-state management, caching, loading states
- **Recharts** — charts for reports
- **Lucide React** — icons
- **next-themes** — light/dark/system theme management

### Key Design Decisions
- **Theme:** Light / Dark / System, persisted in localStorage, applied via `next-themes`
- **Responsive:** Sidebar on desktop; collapsible nav on tablet; bottom navigation on mobile (min 360px wide)
- **Room context:** Room selector in top nav; all room-scoped APIs require verified membership
- **Money display:** Formatted from integer minor units (paise) using currency-aware formatters; never floats
- **Branding:** Navy + Gold palette; logo = house + ₹ rupee + shared roommates; no "AI" branding

### Directory Responsibilities
| Directory | Purpose |
|-----------|---------|
| `app/` | Route handlers and page components (auth, dashboard, rooms, expenses, balances, settlements, recurring, reports, settings) |
| `components/ui/` | shadcn base UI primitives |
| `components/layout/` | Shell, sidebar, top nav, mobile bottom nav |
| `components/dashboard/` | Dashboard cards, quick actions |
| `components/expenses/` | Expense forms, split stepper, expense list/detail |
| `components/balances/` | Balance and settlement UI |
| `components/charts/` | Recharts-based report charts |
| `lib/api/` | TanStack Query API hooks and fetch client |
| `lib/auth/` | Session/token handling, auth guards |
| `lib/validation/` | Zod schemas mirroring backend validation |
| `lib/formatters/` | Currency, date, number formatting |
| `lib/calculations/` | Client-side split preview (UI only; backend is authoritative) |
| `hooks/` | Reusable hooks (useAuth, useRoom, useExpenses, useTheme) |
| `types/` | TypeScript interfaces for all API request/response shapes |

## 4. Backend Architecture

### Framework & Libraries
- **FastAPI** — high-performance Python web framework with OpenAPI docs (`/docs`, `/redoc`)
- **SQLAlchemy** — ORM with async/sync session support
- **Alembic** — database migration management
- **Pydantic** — request/response validation and serialization
- **python-jose / PyJWT** — JWT access and refresh tokens
- **passlib / bcrypt** — password hashing
- **SQLite** — local development database
- **PostgreSQL** — production database (architecture-compatible via SQLAlchemy dialect)

### Layered Design
```
HTTP Layer (FastAPI routes in app/api/)
    ↓
Service Layer (business logic in app/services/)
    ↓
Repository / Data Access (app/repositories/ or direct SQLAlchemy)
    ↓
Database (SQLite / PostgreSQL)
```

### Core Services
| Service | Responsibility |
|---------|----------------|
| `expense_split_service.py` | Split computation: equal, percentage, custom amount, shares/units; Decimal arithmetic; deterministic rounding |
| `balance_service.py` | Per-room and per-member balance calculation (paid, share, credit, debt, net) |
| `settlement_service.py` | Settlement creation, partial/full payment, reversal, history |
| `recurring_service.py` | Recurring expense occurrence generation with deterministic IDs |

### Security
- Every protected endpoint verifies: authenticated user, room membership, correct ownership/role, resource permissions
- Prevents IDOR, unauthorized room access, unauthorized expense editing, mass assignment, SQL injection, XSS, CSRF where applicable, insecure file uploads
- CORS restricted to configured frontend origins (never `*` in production for authenticated APIs)
- Room IDs supplied by frontend are never trusted without authorization checks

## 5. Database Architecture

### Development vs Production
| Environment | Database | Notes |
|-------------|----------|-------|
| Local / Dev / Test | SQLite | File-based, Alembic migrations, foreign keys ON |
| Production | PostgreSQL | Persistent, hosted; SQLAlchemy dialect-swappable |

Monetary values are stored as **integer minor units (paise)** to avoid floating-point errors. UTC timestamps are used throughout.

### Key Tables
- `users` — id, name, email, password_hash, avatar_url, currency, timezone, theme, created_at, updated_at, deleted_at
- `rooms` — id, name, description, currency, owner_id, invite_code, start_date, monthly_rent, rent_due_day, created_at, updated_at, archived_at
- `room_members` — id, room_id, user_id, role, joined_at, status; unique (room_id, user_id)
- `categories` — id, room_id (nullable), name, type (PERSONAL/COMMON/BOTH), icon, created_at
- `expenses` — id, room_id (nullable), user_id, title, amount_minor, currency, expense_type, category_id, payer_id, expense_date, split_method, note, attachment_url, recurring_id (nullable), created_at, updated_at, deleted_at
- `expense_participants` — id, expense_id, user_id, share_amount_minor, percentage, shares, created_at
- `settlements` — id, room_id, payer_id, receiver_id, amount_minor, currency, settlement_date, payment_method, note, status, created_at, updated_at, reversed_at
- `recurring_expenses` — id, room_id, created_by, title, amount_minor, expense_type, category_id, payer_id, split_method, frequency, interval, start_date, end_date, next_occurrence, active, created_at, updated_at
- `invitations` — id, room_id, inviter_id, invite_code, email (nullable), expires_at, used_at, created_at
- `payment_methods` — id, user_id, name, created_at
- `attachments` — id, expense_id, file_url, file_name, mime_type, size, created_at
- `audit_logs` — id, user_id, room_id, action, entity_type, entity_id, metadata_json, created_at

### Indexes
- `room_id` on rooms-scoped tables
- `user_id` on user-scoped tables
- `expense_date` on expenses
- `payer_id` on expenses
- settlement dates
- `recurring.next_occurrence`

### Rules
- Foreign keys ON
- Proper cascading behavior; no orphaned participants
- Soft delete financial records where appropriate (deleted_at / reversed_at / archived_at)
- Never store money as floating point

## 6. Authentication & Session

- **Register:** email, name, password → hashed password stored
- **Login:** email + password → access token + refresh token
- **Logout:** invalidate/clear tokens
- **Refresh:** exchange refresh token for new access token
- **Password reset:** forgot-password → reset-password architecture
- **Protected routes:** JWT validation on backend; session handling on frontend
- **Room membership:** enforced on every room-scoped endpoint

## 7. Money Handling (Critical)

- All monetary values stored and transmitted as **integer minor units** (e.g., ₹1,000 = 100000 paise)
- Split engine uses `Decimal` arithmetic
- Rounding: remainder assigned deterministically (e.g., ₹1,000 / 3 = 333.33, 333.33, 333.34)
- Frontend displays formatted currency; backend is the authoritative source of truth
- Never use floating-point for financial calculations

## 8. Deployment Architecture

```
User
  |
  V
Vercel
  |
  Next.js frontend (NEXT_PUBLIC_API_URL)
  |
  HTTPS API
  |
  FastAPI backend
  |
  Persistent PostgreSQL database
```

- **Frontend:** Deployed to Vercel; `NEXT_PUBLIC_API_URL` points to backend
- **Backend:** Not run as serverless SQLite on Vercel; hosted separately with persistent PostgreSQL
- **MVP/local:** FastAPI + SQLite
- **Production:** FastAPI + PostgreSQL with automated backup and documented restore process
- Never rely on GitHub commits as the only database backup

## 9. API Documentation

FastAPI auto-generates OpenAPI documentation:
- `/docs` — Swagger UI
- `/redoc` — ReDoc

Every endpoint includes: description, request schema, response schema, error responses, authentication requirement.

## 10. CI/CD

GitHub Actions:
- **On push:** install dependencies, lint, type check, unit tests, integration tests, build frontend, build backend, migration verification
- **On pull request:** run complete test suite
- Known failing tests must not be treated as success

## 11. Design Principles (from specification)

1. Do not invent undocumented business behavior
2. Keep financial calculations deterministic
3. Do not use floating-point money calculations
4. Do not bypass backend validation
5. Do not trust frontend balances
6. Backend must calculate authoritative balances
7. Keep API and database logic separated
8. Use migrations
9. Write tests before declaring modules complete
10. Document every important architectural decision

