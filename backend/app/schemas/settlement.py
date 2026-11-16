from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class SettlementBase(BaseModel):
    payer_id: str
    receiver_id: str
    amount_minor: int = Field(gt=0)
    currency: str = "INR"
    settlement_date: date
    payment_method: Optional[str] = None
    note: Optional[str] = None


class SettlementCreate(SettlementBase):
    pass


class SettlementOut(SettlementBase):
    id: str
    room_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True