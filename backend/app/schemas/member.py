from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class MemberBase(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None


class MemberInvite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class MemberJoin(BaseModel):
    invite_code: str


class MemberOut(BaseModel):
    id: str
    room_id: str
    user_id: str
    role: str
    joined_at: str
    status: str

    class Config:
        from_attributes = True
