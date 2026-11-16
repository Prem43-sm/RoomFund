import uuid
import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(nullable=False)
    monthly_rent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rent_due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    archived_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    members: Mapped[list["RoomMember"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="room", foreign_keys="Expense.room_id")
    settlements: Mapped[list["Settlement"]] = relationship(back_populates="room")
    recurring_expenses: Mapped[list["RecurringExpense"]] = relationship(back_populates="room")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    categories: Mapped[list["Category"]] = relationship(back_populates="room", cascade="all, delete-orphan")
