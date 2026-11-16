# RoomFund — TODO

Master task list tracking implementation across all phases. Update status as work progresses.

## Progress update — 2026-11-16

- [x] Recover the actual implementation status: FastAPI backend exists; React frontend was missing.
- [x] Add `frontend/` as a Next.js + React + TypeScript application.
- [x] Add registration and login screens connected to the FastAPI authentication API.
- [x] Add a protected responsive dashboard with room creation, balances, expense entry, and settlement entry.
- [x] Verify the frontend TypeScript compilation and production build.
- [ ] Replace the initial equal-split dashboard form with the complete personal/common multi-step form, participant selector, and all split methods.
- [ ] Add frontend tests, TanStack Query integration, report charts, recurring-expense UI, settings, and accessible toast/loading states.

## Phase 1 — Analysis (docs)

- [x] Read full specification (RoomFund_Full_Project_Specification.txt)
- [x] Review RoomFund_Icon.png branding asset
- [ ] Create PROJECT_STATUS.md
- [ ] Create ARCHITECTURE.md
- [ ] Create DATABASE.md
- [ ] Create API.md
- [ ] Create TEST_PLAN.md
- [ ] Create TODO.md (this file)

## Phase 2 — Scaffold

- [ ] Create frontend/ directory (Next.js + TypeScript + Tailwind)
- [ ] Create backend/ directory (FastAPI + SQLAlchemy + Alembic)
- [ ] Create docs/ directory structure
- [ ] Create test structure (backend pytest, frontend vitest/playwright)
- [ ] Create environment templates (.env.example for frontend + backend)
- [ ] Create GitHub configuration (.github/workflows)
- [ ] Initialize git repository

## Phase 3 — Database

- [ ] Define SQLAlchemy models (users, rooms, room_members, categories, expenses, expense_participants, settlements, recurring_expenses, invitations, payment_methods, attachments, audit_logs)
- [ ] Configure foreign keys, cascades, unique constraints
- [ ] Add indexes (room_id, user_id, expense_date, payer_id, settlement dates, recurring next_occurrence)
- [ ] Generate Alembic migrations
- [ ] Create seed data (Prem, Rahul, Aman; Bilaspur Shared Flat; rent/electricity/internet/groceries/cleaning)
- [ ] Write database tests (FK, unique membership, cascading, migrations, persistence, rollback)

## Phase 4 — Backend

- [ ] Authentication (register, login, logout, refresh, password hash, JWT, forgot/reset password, /me)
- [ ] Rooms CRUD (create, list, get, update, delete/archive)
- [ ] Members (invite, join via code, list, update role, remove)
- [ ] Expenses (personal + common CRUD)
- [ ] ExpenseSplitService (equal, percentage, custom amount, shares/units; Decimal math; deterministic rounding)
- [ ] Balance engine (per room + per member; credit/debt/net)
- [ ] Settlements (create, partial/full, reverse, history)
- [ ] Settlement suggestions optimizer (minimize transactions)
- [ ] Recurring expenses (daily/weekly/monthly/yearly; deterministic occurrence IDs)
- [ ] Rent management (statuses: upcoming/due/paid/partial/overdue)
- [ ] Reports (day/week/month/year/custom range; category/member breakdown)
- [ ] API security (auth + membership + role checks on every protected endpoint)
- [ ] Validation, error handling, consistent JSON error format

## Phase 5 — Frontend

- [ ] Layout (sidebar desktop, bottom nav mobile; top nav with logo, room selector, search, notifications, theme toggle, profile)
- [ ] Theme system (light/dark/system; persist preference)
- [ ] Auth pages (login, register, forgot/reset password)
- [ ] Dashboard (spending cards: my spending, room spending, I owe, I receive, this month, settled)
- [ ] Expense flows (personal/common stepper; split method selection; review split)
- [ ] Balance UI (you receive / you owe / settled)
- [ ] Settlement UI (record settlement, partial/full, reverse, history)
- [ ] Recurring UI (create/manage recurring expenses)
- [ ] Reports UI (charts: spending over time, category distribution, member contribution, personal vs common, paid vs owed, monthly trend; CSV export)
- [ ] Settings (profile, security, currency, timezone, theme, notifications)
- [ ] Loading states, empty states, validation messages, toasts

## Phase 6 — Integration

- [ ] Connect frontend to backend via TanStack Query
- [ ] Verify auth flow end-to-end
- [ ] Verify CRUD for rooms, members, expenses
- [ ] Verify balances and settlement suggestions
- [ ] Verify filters (day/week/month/year/custom)
- [ ] Verify reports

## Phase 7 — Testing

- [ ] Run lint (frontend + backend)
- [ ] Run type check (TypeScript + Python mypy)
- [ ] Run backend unit tests (split, percentage, custom, shares, rounding, balances, settlements, reversal, recurring dates)
- [ ] Run backend API tests (registration, login, auth, unauthorized, rooms, joining, expenses, settlements, reports)
- [ ] Run database tests
- [ ] Run frontend tests (login form, add expense form, split calculator, dashboard, filters, theme switch, validation, responsive)
- [ ] Run E2E critical flow (Playwright: register → create room → invite → common expense → equal split → balances → settlement → personal expense → recurring → theme → logout/login → persistence)
- [ ] Production build (frontend + backend)

## Phase 8 — Security Review

- [ ] Passwords hashed
- [ ] JWT/session secure
- [ ] Secrets not committed
- [ ] CORS restricted
- [ ] SQL injection protected
- [ ] Input validation
- [ ] Authorization checks
- [ ] Rate limiting
- [ ] Secure file uploads (MIME validation, size limits)
- [ ] No sensitive data in logs
- [ ] Safe error messages (no stack traces)
- [ ] Dependency audit

## Phase 9 — Deployment

- [ ] GitHub repository organized (frontend + backend separation or monorepo)
- [ ] GitHub Actions CI (push + PR)
- [ ] Backend hosting prepared
- [ ] Persistent production database (PostgreSQL)
- [ ] Vercel frontend deployment (NEXT_PUBLIC_API_URL)
- [ ] Environment variables configured
- [ ] Production persistence strategy documented

## Phase 10 — Final Self-Check

- [ ] Verify every acceptance criterion is checked
- [ ] Generate Project Health Report (PASS/FAIL per category)
- [ ] Do not hide failed tests
- [ ] Document known issues and remaining work
