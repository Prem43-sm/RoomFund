# RoomFund — API Documentation

## 1. Overview

RoomFund exposes a RESTful JSON API built with FastAPI. OpenAPI documentation is automatically available at:

- `/docs` — Swagger UI
- `/redoc` — ReDoc

Base path: `/api`

All monetary amounts in requests and responses are expressed as **integer minor units** (e.g., ₹1,000 = 100000 paise). All timestamps are ISO 8601 UTC.

## 2. Authentication

Endpoints marked **Auth required** need a valid JWT access token, sent as:

```
Authorization: Bearer <access_token>
```

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Register a new user |
| POST | `/api/auth/login` | No | Log in; returns access + refresh token |
| POST | `/api/auth/logout` | Yes | Log out / invalidate session |
| POST | `/api/auth/refresh` | No | Refresh access token using refresh token |
| GET | `/api/auth/me` | Yes | Get current user profile |
| POST | `/api/auth/forgot-password` | No | Initiate password reset |
| POST | `/api/auth/reset-password` | No | Reset password with token |

### Register Request
```json
{
  "name": "Prem",
  "email": "prem@example.com",
  "password": "securepassword123"
}
```

### Register Response
```json
{
  "id": "uuid",
  "name": "Prem",
  "email": "prem@example.com",
  "currency": "INR",
  "timezone": "Asia/Kolkata",
  "theme": "system",
  "created_at": "2026-01-01T00:00:00Z"
}
```

### Login Request
```json
{
  "email": "prem@example.com",
  "password": "securepassword123"
}
```

### Login Response
```json
{
  "access_token": "jwt.access.token",
  "refresh_token": "jwt.refresh.token",
  "token_type": "bearer"
}
```

## 3. Rooms

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms` | Yes | List user's rooms |
| POST | `/api/rooms` | Yes | Create a room |
| GET | `/api/rooms/{room_id}` | Yes | Get room details |
| PATCH | `/api/rooms/{room_id}` | Yes | Update room (owner only) |
| DELETE | `/api/rooms/{room_id}` | Yes | Archive/delete room (owner only) |

### Create Room Request
```json
{
  "name": "Bilaspur Shared Flat",
  "description": "Our shared apartment",
  "currency": "INR",
  "start_date": "2026-01-01",
  "monthly_rent": 900000,
  "rent_due_day": 5,
  "room_type": "Flat"
}
```

### Create Room Response
```json
{
  "id": "uuid",
  "name": "Bilaspur Shared Flat",
  "invite_code": "ABCD1234",
  "owner_id": "uuid",
  "created_at": "2026-01-01T00:00:00Z"
}
```

## 4. Members

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/members` | Yes | List room members |
| POST | `/api/rooms/{room_id}/members/invite` | Yes | Invite / generate invite code |
| POST | `/api/rooms/{room_id}/join` | Yes | Join room via invite code |
| PATCH | `/api/rooms/{room_id}/members/{member_id}` | Yes | Update member role (owner/admin) |
| DELETE | `/api/rooms/{room_id}/members/{member_id}` | Yes | Remove member (owner/admin) |

### Join Room Request
```json
{
  "invite_code": "ABCD1234"
}
```

## 5. Expenses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/expenses` | Yes | List room expenses |
| POST | `/api/rooms/{room_id}/expenses` | Yes | Create an expense |
| GET | `/api/expenses/{expense_id}` | Yes | Get expense detail |
| PATCH | `/api/expenses/{expense_id}` | Yes | Update an expense |
| DELETE | `/api/expenses/{expense_id}` | Yes | Archive/delete an expense |

### Personal Expenses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/me/expenses` | Yes | List current user's personal expenses |
| POST | `/api/me/expenses` | Yes | Create a personal expense |

### Create Common Expense Request
```json
{
  "title": "Groceries",
  "amount_minor": 240000,
  "currency": "INR",
  "expense_type": "COMMON",
  "category_id": "uuid",
  "payer_id": "uuid",
  "expense_date": "2026-01-15",
  "split_method": "EQUAL",
  "note": "Weekly groceries",
  "participants": [
    { "user_id": "uuid", "share_amount_minor": 80000 },
    { "user_id": "uuid", "share_amount_minor": 80000 },
    { "user_id": "uuid", "share_amount_minor": 80000 }
  ]
}
```

## 6. Balances

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/balances` | Yes | Get per-member balances |
| GET | `/api/rooms/{room_id}/settlement-suggestions` | Yes | Get optimized settlement suggestions |

### Balances Response
```json
{
  "room_id": "uuid",
  "members": [
    {
      "user_id": "uuid",
      "name": "Prem",
      "total_paid_minor": 200000,
      "total_share_minor": 80000,
      "net_balance_minor": 120000,
      "status": "receive"
    },
    {
      "user_id": "uuid",
      "name": "Rahul",
      "total_paid_minor": 50000,
      "total_share_minor": 80000,
      "net_balance_minor": -30000,
      "status": "owe"
    }
  ]
}
```

## 7. Settlements

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/settlements` | Yes | List room settlements |
| POST | `/api/rooms/{room_id}/settlements` | Yes | Record a settlement |
| PATCH | `/api/settlements/{settlement_id}` | Yes | Update a settlement |
| POST | `/api/settlements/{settlement_id}/reverse` | Yes | Reverse a settlement |

### Create Settlement Request
```json
{
  "payer_id": "uuid",
  "receiver_id": "uuid",
  "amount_minor": 30000,
  "currency": "INR",
  "settlement_date": "2026-01-16",
  "payment_method": "UPI",
  "note": "Partial settlement"
}
```

## 8. Recurring Expenses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/recurring` | Yes | List recurring expenses |
| POST | `/api/rooms/{room_id}/recurring` | Yes | Create a recurring expense |
| PATCH | `/api/recurring/{id}` | Yes | Update a recurring expense |
| DELETE | `/api/recurring/{id}` | Yes | Delete a recurring expense |

### Create Recurring Expense Request
```json
{
  "title": "Rent",
  "amount_minor": 900000,
  "expense_type": "COMMON",
  "category_id": "uuid",
  "payer_id": "uuid",
  "split_method": "EQUAL",
  "frequency": "MONTHLY",
  "interval": 1,
  "start_date": "2026-01-01",
  "end_date": null,
  "next_occurrence": "2026-02-01",
  "active": true
}
```

## 9. Reports

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/rooms/{room_id}/reports` | Yes | General room report |
| GET | `/api/rooms/{room_id}/reports/monthly` | Yes | Monthly breakdown |
| GET | `/api/rooms/{room_id}/reports/category` | Yes | Category distribution |
| GET | `/api/rooms/{room_id}/reports/member` | Yes | Per-member breakdown |

### Report Filters (query params)
- `start_date`, `end_date` — custom date range
- `category` — filter by category
- `member` — filter by member
- `expense_type` — personal / common

## 10. Error Response Format

All errors return a consistent JSON body:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Split amounts do not equal the total.",
    "details": {}
  }
}
```

### Common Error Codes
| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Not a room member or insufficient role |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Duplicate invite code, already joined, etc. |
| `UNPROCESSABLE_ENTITY` | 422 | Business rule violation (split mismatch) |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

## 11. Security Requirements

- Every protected endpoint verifies: authenticated user, room membership, correct ownership/role, resource permissions
- Prevents IDOR, unauthorized room access, unauthorized expense editing, mass assignment
- CORS restricted to configured frontend origins
- Room IDs supplied by the frontend are never trusted without authorization checks
