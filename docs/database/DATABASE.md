# RoomFund — Database Design

## 1. Overview

RoomFund uses a relational database with full foreign-key integrity. SQLite is used for local development and testing; PostgreSQL is supported for production via SQLAlchemy dialect. All monetary values are stored as **integer minor units (paise)**. All timestamps are **UTC**.

Alembic manages schema migrations. No manual schema changes are made outside of migration tracking.

## 2. Schema Reference

### Table: users
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID / Integer PK | No | Primary key |
| name | String | No | |
| email | String | No | Unique |
| password_hash | String | No | Never plain text |
| avatar_url | String | Yes | |
| currency | String | No | Default INR |
| timezone | String | No | |
| theme | String | No | light/dark/system |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |
| deleted_at | DateTime | Yes | Soft delete |

### Table: rooms
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID / Integer PK | No | |
| name | String | No | Required, length-limited |
| description | String | Yes | |
| currency | String | No | |
| owner_id | FK users.id | No | |
| invite_code | String | No | Unique, generated on creation |
| start_date | Date | No | Room start date |
| monthly_rent | Integer (minor) | Yes | Optional |
| rent_due_day | Integer | Yes | Day of month (1-31) |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |
| archived_at | DateTime | Yes | Soft archive |

### Table: room_members
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | No | |
| user_id | FK users.id | No | |
| role | String | No | OWNER / ADMIN / MEMBER |
| joined_at | DateTime | No | |
| status | String | No | active / invited / left |

**Constraint:** Unique (room_id, user_id)

### Table: categories
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | Yes | Nullable = global category |
| name | String | No | Rent, Electricity, Water, Internet, Gas, Groceries, Cleaning, Maintenance, Furniture, Household, Transport, Food, Entertainment, Other |
| type | String | No | PERSONAL / COMMON / BOTH |
| icon | String | Yes | Lucide icon name |
| created_at | DateTime | No | |

### Table: expenses
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | Yes | Nullable for personal expenses |
| user_id | FK users.id | No | Creator |
| title | String | No | |
| amount_minor | Integer | No | Stored in minor units |
| currency | String | No | |
| expense_type | String | No | PERSONAL / COMMON |
| category_id | FK categories.id | Yes | |
| payer_id | FK users.id | Yes | Who paid (for common expenses) |
| expense_date | Date | No | |
| split_method | String | No | EQUAL / PERCENTAGE / CUSTOM / SHARES |
| note | String | Yes | |
| attachment_url | String | Yes | |
| recurring_id | FK recurring_expenses.id | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |
| deleted_at | DateTime | Yes | Soft delete |

### Table: expense_participants
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| expense_id | FK expenses.id | No | |
| user_id | FK users.id | No | |
| share_amount_minor | Integer | No | |
| percentage | Numeric | Yes | For percentage split |
| shares | Numeric | Yes | For shares/units split |
| created_at | DateTime | No | |

### Table: settlements
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | No | |
| payer_id | FK users.id | No | Person paying |
| receiver_id | FK users.id | No | Person receiving |
| amount_minor | Integer | No | |
| currency | String | No | |
| settlement_date | Date | No | |
| payment_method | String | Yes | |
| note | String | Yes | |
| status | String | No | pending / completed / reversed |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |
| reversed_at | DateTime | Yes | Soft reversal |

### Table: recurring_expenses
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | No | |
| created_by | FK users.id | No | |
| title | String | No | |
| amount_minor | Integer | No | |
| expense_type | String | No | COMMON / PERSONAL |
| category_id | FK categories.id | Yes | |
| payer_id | FK users.id | Yes | |
| split_method | String | No | |
| frequency | String | No | ONE_TIME / DAILY / WEEKLY / MONTHLY / YEARLY |
| interval | Integer | Yes | Multiplier for frequency |
| start_date | Date | No | |
| end_date | Date | Yes | Optional |
| next_occurrence | Date | No | Indexed |
| active | Boolean | No | Default true |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Table: invitations
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| room_id | FK rooms.id | No | |
| inviter_id | FK users.id | No | |
| invite_code | String | No | Unique |
| email | String | Yes | Optional targeted email |
| expires_at | DateTime | No | |
| used_at | DateTime | Yes | |
| created_at | DateTime | No | |

### Table: payment_methods
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| user_id | FK users.id | No | |
| name | String | No | |
| created_at | DateTime | No | |

### Table: attachments
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| expense_id | FK expenses.id | No | |
| file_url | String | No | |
| file_name | String | No | |
| mime_type | String | No | MIME validation |
| size | Integer | No | Size limit enforced |
| created_at | DateTime | No | |

### Table: audit_logs
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | PK | No | |
| user_id | FK users.id | Yes | |
| room_id | FK rooms.id | Yes | |
| action | String | No | |
| entity_type | String | No | |
| entity_id | String | No | |
| metadata_json | JSON | Yes | |
| created_at | DateTime | No | |

## 3. Indexes

Required indexes (per specification section 29):

- `expenses(room_id)`
- `expenses(user_id)`
- `expenses(expense_date)`
- `expenses(payer_id)`
- `settlements(settlement_date)`
- `settlements(room_id)`
- `recurring_expenses(next_occurrence)`
- `room_members(room_id)`
- `room_members(user_id)`
- `expense_participants(expense_id)`

## 4. Database Rules

1. Foreign keys ON
2. Proper cascading behavior; no orphaned participants
3. Monetary values stored as integer minor units
4. Unique constraints enforced (room membership, invite code, email)
5. Soft delete financial records where appropriate (deleted_at / reversed_at / archived_at)
6. Never store money as floating point
7. All timestamps in UTC

## 5. Relationships Summary

- `users` 1:N `room_members` (a user can be in many rooms)
- `rooms` 1:N `room_members` (a room has many members)
- `rooms` 1:N `expenses`
- `rooms` 1:N `settlements`
- `rooms` 1:N `recurring_expenses`
- `rooms` 1:N `invitations`
- `rooms` 1:N `categories`
- `users` 1:N `expenses` (creator)
- `users` 1:N `settlements` (as payer/receiver)
- `users` 1:N `expense_participants`
- `expenses` 1:N `expense_participants`
- `expenses` 1:N `attachments`
- `categories` 1:N `expenses`
- `recurring_expenses` 1:N `expenses` (generated occurrences)

## 6. Soft Delete / Archive Strategy

- `users.deleted_at` — user soft delete
- `rooms.archived_at` — room archive (read-only, history preserved)
- `expenses.deleted_at` — expense soft delete (no destructive financial history removal)
- `settlements.reversed_at` — settlement reversal (original preserved, reversal recorded)
- `room_members.status` — active / invited / left (no hard removal of membership history)

## 7. Seed Data (Development)

Users: Prem, Rahul, Aman  
Room: Bilaspur Shared Flat  
Expenses: Rent ₹9,000; Electricity ₹1,500; Internet ₹799; Groceries ₹2,400; Cleaning ₹600

Deterministic IDs used in test fixtures where useful.

