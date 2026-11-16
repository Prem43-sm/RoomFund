# RoomFund — Test Plan

## 1. Overview

This test plan covers all testing required by the RoomFund specification, across backend unit tests, backend API tests, database tests, frontend tests, and end-to-end (E2E) tests. Tests are written before modules are declared complete, and known failing tests are never treated as success.

## 2. Backend Unit Tests

Test the core business logic in isolation (no HTTP):

| Area | Test Cases |
|------|------------|
| Expense split engine | Equal split divides total evenly; percentage split totals exactly 100%; custom amounts sum to total; shares/units split divides by total shares; rounding is deterministic (remainder assigned to payer/last participant); zero or invalid amount rejected; participant validation (payer must be a participant) |
| Balance engine | Per-room totals computed correctly; per-member paid/share/credit/debt/net correct; personal expenses excluded from room balance; positive balance = receive, negative = owe, zero = settled |
| Settlement engine | Settlement reduces outstanding debt; partial payment supported; full payment clears debt; reversal restores original balance; settlement history preserved (no destructive delete) |
| Recurring dates | Next occurrence computed correctly for DAILY/WEEKLY/MONTHLY/YEARLY; end date cannot precede start date; inactive recurrences skipped; deterministic occurrence IDs prevent duplication |

## 3. Backend API Tests

Test endpoints via TestClient with a test database:

| Area | Test Cases |
|------|------------|
| Authentication | Registration succeeds; login returns tokens; logout invalidates; refresh issues new access token; /me returns current user; wrong credentials rejected; duplicate email rejected |
| Authorization | Unprotected access to room endpoints rejected; non-member cannot access room resources; owner-only actions rejected for members; member cannot edit another's expense |
| Rooms | Create room returns invite code; list rooms scoped to user; get room details; update room (owner); archive room |
| Members | Invite generates code; join with valid code; join with invalid/expired code rejected; already-joined rejected; update role; remove member |
| Expenses | Create personal + common expense; edit expense; delete/archive expense; personal expense does not create roommate debt; common expense creates participant shares |
| Splits | Equal/percentage/custom/shares splits validated; split mismatch returns 422 |
| Settlements | Create settlement; partial/full payment; reverse settlement; settlement history |
| Reports | Day/week/month/year/custom range filters; category and member breakdowns |

## 4. Database Tests

Test schema and integrity directly:

| Area | Test Cases |
|------|------------|
| Foreign keys | Orphaned records prevented; cascading behavior correct |
| Unique constraints | (room_id, user_id) membership unique; email unique; invite code unique |
| Cascading | Deleting/archiving a room does not orphan financial history (soft delete) |
| Migrations | Alembic upgrade head applies cleanly; downgrade supported |
| Data persistence | Records survive session; SQLite file persists locally |
| Rollback behavior | Failed expense creation rolls back entirely (no partial records) |

## 5. Frontend Tests

Test React components and forms:

| Area | Test Cases |
|------|------------|
| Login form | Valid credentials submit; invalid show error; empty fields show validation |
| Add expense form | Personal vs common selection; split method selection; participant shares validate; submit creates expense |
| Split calculator | Equal/percentage/custom/shares preview; rounding shown; totals match |
| Dashboard | Cards render; balances display; empty state when no expenses |
| Filters | Day/week/month/year/custom range filter expenses |
| Theme switch | Light/dark/system toggle persists preference |
| Validation messages | Zod errors displayed friendly |
| Responsive | Critical flows usable on mobile (360px+) |

## 6. End-to-End (E2E) Tests — Playwright

Critical E2E flow (must pass):

1. Register a new user
2. Create a room
3. Invite/join a roommate (via invite code)
4. Add a common expense
5. Apply equal split
6. Verify balances update
7. Add a settlement
8. Verify balance changes after settlement
9. Add a personal expense
10. Verify personal expense does not affect roommate balance
11. Create a recurring expense
12. Change theme (light ↔ dark)
13. Logout / login again
14. Verify database persistence (data still present)

## 7. Test Execution

Backend:
```
cd backend
pytest
```

Frontend:
```
cd frontend
npm run test
```

E2E:
```
cd frontend
npx playwright test
```

CI (GitHub Actions):
- On push: lint, type check, unit tests, integration tests, build frontend, build backend, migration verification
- On pull request: run complete test suite

## 8. Coverage Goals

- Backend split engine: 100% (financial logic must be fully covered)
- Backend API: high coverage on all auth-protected routes
- Database: migrations and integrity constraints covered
- Frontend: critical user flows covered
- E2E: full happy-path flow covered

## 9. Test Data

Deterministic seed data for development/tests:

Users: Prem, Rahul, Aman  
Room: Bilaspur Shared Flat  
Expenses: Rent ₹9,000; Electricity ₹1,500; Internet ₹799; Groceries ₹2,400; Cleaning ₹600

Deterministic IDs used in test fixtures where useful.
