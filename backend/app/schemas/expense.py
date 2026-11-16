from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ExpenseParticipantBase(BaseModel):
    user_id: str
    share_amount_minor: int = Field(ge=0)
    percentage: Optional[float] = None
    shares: Optional[float] = None


class ExpenseParticipantOut(ExpenseParticipantBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    title: str
    amount_minor: int = Field(gt=0)
    currency: str = "INR"
    expense_type: str  # PERSONAL / COMMON
    category_id: Optional[str] = None
    payer_id: Optional[str] = None
    expense_date: date
    split_method: str  # EQUAL / PERCENTAGE / CUSTOM / SHARES
    note: Optional[str] = None


class PersonalPaymentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    amount_minor: int = Field(gt=0)
    currency: str = "INR"
    expense_date: date
    description: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    participants: List[ExpenseParticipantBase]


class ExpenseOut(ExpenseBase):
    id: str
    room_id: Optional[str]
    user_id: str
    participants: List[ExpenseParticipantOut]
    created_at: datetime

    class Config:
        from_attributes = True
