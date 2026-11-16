# RoomFund — Project Status

**Project:** RoomFund  
**Tagline:** Shared-room expense management made simple, fair, and transparent.  
**Status:** Phase 1 — Analysis (Planning)  
**Last Updated:** 2026-11-15

## Development Phases (per specification)

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 1 | Analysis | ✅ In Progress | Read spec; create PROJECT_STATUS.md, ARCHITECTURE.md, DATABASE.md, API.md, TEST_PLAN.md, TODO.md |
| 2 | Scaffold | ⏳ Pending | Create frontend/, backend/, database/, test structure, env templates, GitHub config |
| 3 | Database | ⏳ Pending | Models, relationships, indexes, migrations, seed data, database tests |
| 4 | Backend | ⏳ Pending | Auth, rooms, members, expenses, split engine, balances, settlements, recurring, reports |
| 5 | Frontend | ⏳ Pending | Layout, theme, auth, dashboard, expense flows, balance UI, settlement UI, recurring UI, reports, settings |
| 6 | Integration | ⏳ Pending | Connect frontend to backend; verify auth, CRUD, balances, settlements, filters, reports |
| 7 | Testing | ⏳ Pending | Lint, typecheck, unit/integration/database/E2E tests, production build |
| 8 | Security Review | ⏳ Pending | Auth, authorization, validation, secrets, CORS, file uploads, DB queries |
| 9 | Deployment | ⏳ Pending | GitHub, CI/CD, backend hosting, persistent production DB, Vercel frontend, env vars |
| 10 | Final Self-Check | ⏳ Pending | Verify every acceptance criterion; generate Project Health Report |

## Acceptance Criteria (summary)

- [ ] User can register/login
- [ ] User can create room
- [ ] User can invite/join roommates
- [ ] User can add personal expense
- [ ] User can add common expense
- [ ] User can choose participants
- [ ] Equal split works
- [ ] Percentage split works
- [ ] Custom split works
- [ ] Shares split works
- [ ] Rounding is exact
- [ ] Balances are correct
- [ ] Settlement works
- [ ] Settlement reversal works
- [ ] Recurring expenses work
- [ ] Day/week/month/year filters work
- [ ] Personal dashboard works
- [ ] Room dashboard works
- [ ] Reports work
- [ ] Light mode works
- [ ] Dark mode works
- [ ] Responsive UI works
- [ ] SQLite persistence works locally
- [ ] Migrations work
- [ ] API tests pass
- [ ] Database tests pass
- [ ] Frontend tests pass
- [ ] E2E critical flow passes
- [ ] GitHub repository is organized
- [ ] GitHub Actions CI passes
- [ ] Frontend builds successfully
- [ ] Vercel deployment configuration works
- [ ] Production persistence strategy is documented
- [ ] No secrets are committed
- [ ] README is complete

## Tech Stack

**Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, React Hook Form, Zod, TanStack Query, Recharts, Lucide icons  
**Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic, SQLite (dev) / PostgreSQL (prod)  
**Deployment:** Frontend → Vercel; Backend → persistent hosting + managed database

## Repository Layout (final deliverable)

```
ROOMFUND/
├── frontend/              # Next.js application
├── backend/               # FastAPI application
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

## Notes

- Icon: `RoomFund_Icon.png` (house + ₹ rupee + shared roommates concept)
- Brand colors: Navy + Gold
- Money stored as integer minor units (paise); no floating-point math
- Do not use the word "AI" in product branding
- Personal and common expenses must never be silently mixed

## Current implementation update (2026-11-16)

The repository was found to contain an in-progress FastAPI backend but no
frontend directory. A React-based Next.js application has now been added in
`frontend/`, including registration, login, protected dashboard access, room
creation, balance viewing, equal-split expense entry, and settlement entry.

The project is therefore in Phase 5 (frontend implementation), not Phase 1.
The existing backend still needs its automated test suite, API hardening, and
the remaining product modules before the acceptance criteria can be marked
complete.

## Shared-workspace update (2026-11-16)

- The existing `rooms` table is retained as the shared workspace to preserve
  compatible data; a migration adds the workspace location and user auth-provider metadata.
- Normal dashboard UI no longer offers room switching or a New Room action.
  First-time setup is a separate, one-time route and the API rejects duplicate workspace creation.
- Shared expenses are restricted to active workspace members and personal payments
  use a separate authenticated API scope (`/api/personal-payments`).
- Gmail addresses are normalized for invitations and registration. An invitation
  activates automatically when the invited address registers.
- Password sign-in remains the implemented local authentication provider. Google
  OAuth requires a registered Google OAuth client and redirect URI before it can
  be enabled safely; it has not been simulated with a fake Google button.
