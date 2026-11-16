from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr
    currency: Optional[str] = "INR"
    timezone: Optional[str] = "Asia/Kolkata"
    theme: Optional[str] = "system"


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True