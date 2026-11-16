from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.recurring_expense import RecurringExpense
from app.schemas.recurring import RecurringExpenseCreate, RecurringExpenseOut
import datetime

router = APIRouter(prefix="/rooms/{room_id}/recurring", tags=["recurring"])


def _require_membership(db: Session, room_id: str, user_id: str):
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.get("", response_model=list[RecurringExpenseOut])
def list_recurring(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    return (
        db.query(RecurringExpense)
        .filter(RecurringExpense.room_id == room_id)
        .order_by(RecurringExpense.next_occurrence.asc())
        .all()
    )


@router.post("", response_model=RecurringExpenseOut)
def create_recurring(
    room_id: str,
    payload: RecurringExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    recurring = RecurringExpense(
        room_id=room_id,
        created_by=current_user.id,
        title=payload.title,
        amount_minor=payload.amount_minor,
        expense_type=payload.expense_type,
        category_id=payload.category_id,
        payer_id=payload.payer_id,
        split_method=payload.split_method,
        frequency=payload.frequency,
        interval=payload.interval,
        start_date=payload.start_date,
        end_date=payload.end_date,
        next_occurrence=payload.next_occurrence,
        active=payload.active,
    )
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring