from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.expense import Expense
from datetime import date

router = APIRouter(prefix="/rooms/{room_id}/reports", tags=["reports"])


def _require_membership(db: Session, room_id: str, user_id: str):
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.get("")
def get_report(
    room_id: str,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    query = db.query(Expense).filter(Expense.room_id == room_id, Expense.deleted_at.is_(None))
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    expenses = query.all()
    total = sum(e.amount_minor for e in expenses)
    return {
        "room_id": room_id,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "total_minor": total,
        "expense_count": len(expenses),
    }