import uuid
import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(30), default="password", nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    theme: Mapped[str] = mapped_column(String(20), default="system", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room_members: Mapped[list["RoomMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="creator", foreign_keys="Expense.user_id")
    settlements_paid: Mapped[list["Settlement"]] = relationship(
        back_populates="payer", foreign_keys="Settlement.payer_id"
    )
    settlements_received: Mapped[list["Settlement"]] = relationship(
        back_populates="receiver", foreign_keys="Settlement.receiver_id"
    )
    expense_participants: Mapped[list["ExpenseParticipant"]] = relationship(back_populates="user")
    invitations_sent: Mapped[list["Invitation"]] = relationship(back_populates="inviter", foreign_keys="Invitation.inviter_id")
    recurring_expenses: Mapped[list["RecurringExpense"]] = relationship(back_populates="created_by_user", foreign_keys="RecurringExpense.created_by")
    payment_methods: Mapped[list["PaymentMethod"]] = relationship(back_populates="user")
