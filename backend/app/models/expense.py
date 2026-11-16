import uuid
import datetime
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    expense_type: Mapped[str] = mapped_column(String(20), nullable=False)  # PERSONAL / COMMON
    category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    payer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    expense_date: Mapped[datetime.date] = mapped_column(nullable=False, index=True)
    split_method: Mapped[str] = mapped_column(String(20), nullable=False)  # EQUAL / PERCENTAGE / CUSTOM / SHARES
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    recurring_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("recurring_expenses.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped["Room | None"] = relationship(back_populates="expenses", foreign_keys=[room_id])
    creator: Mapped["User"] = relationship(back_populates="expenses", foreign_keys=[user_id])
    category: Mapped["Category | None"] = relationship(back_populates="expenses")
    payer: Mapped["User | None"] = relationship(foreign_keys=[payer_id])
    participants: Mapped[list["ExpenseParticipant"]] = relationship(back_populates="expense", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="expense", cascade="all, delete-orphan")