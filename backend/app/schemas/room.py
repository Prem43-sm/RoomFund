from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    currency: Optional[str] = "INR"
    start_date: date
    monthly_rent: Optional[int] = None
    rent_due_day: Optional[int] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    currency: Optional[str] = None
    monthly_rent: Optional[int] = None
    rent_due_day: Optional[int] = None


class RoomOut(RoomBase):
    id: str
    owner_id: str
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True
