from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.expense import Expense
from app.api import auth, rooms, members, expenses, balances, settlements, recurring, reports, personal_payments, activity
from app.schemas import room, user, expense, settlement, recurring as recurring_schema, member, auth as auth_schema

# Rebuild pydantic schemas to resolve forward references (required by Pydantic v2)
room.RoomOut.model_rebuild()
user.UserOut.model_rebuild()
expense.ExpenseOut.model_rebuild()
settlement.SettlementOut.model_rebuild()
recurring_schema.RecurringExpenseOut.model_rebuild()
member.MemberOut.model_rebuild()
auth_schema.Token.model_rebuild()

app = FastAPI(
    title="RoomFund API",
    description="Shared-room expense management API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(rooms.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(balances.router, prefix="/api")
app.include_router(settlements.router, prefix="/api")
app.include_router(recurring.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(personal_payments.router, prefix="/api")
app.include_router(activity.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "RoomFund API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/me/expenses")
def list_personal_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id, Expense.expense_type == "PERSONAL", Expense.deleted_at.is_(None))
        .order_by(Expense.expense_date.desc())
        .all()
    )
