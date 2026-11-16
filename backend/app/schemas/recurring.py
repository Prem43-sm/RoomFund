from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class RecurringExpenseBase(BaseModel):
    title: str
    amount_minor: int
    expense_type: str
    category_id: Optional[str] = None
    payer_id: Optional[str] = None
    split_method: str
    frequency: str
    interval: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    next_occurrence: date
    active: bool = True


class RecurringExpenseCreate(RecurringExpenseBase):
    pass


class RecurringExpenseOut(RecurringExpenseBase):
    id: str
    room_id: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True