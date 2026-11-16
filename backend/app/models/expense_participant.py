import uuid
import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    expense_id: Mapped[str] = mapped_column(String(36), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    share_amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    shares: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    expense: Mapped["Expense"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="expense_participants")