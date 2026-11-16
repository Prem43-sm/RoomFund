from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseParticipantBase
from app.services.expense_split_service import compute_split, validate_participants
from app.services.audit_service import append_audit_log
import datetime

router = APIRouter(prefix="/rooms/{room_id}/expenses", tags=["expenses"])


def _require_membership(db: Session, room_id: str, user_id: str):
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.post("", response_model=ExpenseOut)
def create_expense(
    room_id: str,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id, Room.archived_at.is_(None)).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)

    if payload.expense_type != "COMMON":
        raise HTTPException(status_code=400, detail="Use the personal-payments endpoint for private records")
    participant_ids = [p.user_id for p in payload.participants]
    try:
        validate_participants(current_user.id, participant_ids)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    payer_id = current_user.id
    allowed_ids = {member.user_id for member in db.query(RoomMember).filter(RoomMember.room_id == room_id, RoomMember.status == "active").all()}
    if payer_id not in allowed_ids or not set(participant_ids).issubset(allowed_ids):
        raise HTTPException(status_code=422, detail="Payer and included members must be active workspace members")
    try:
        shares = compute_split(payload.amount_minor, payload.split_method, participant_ids, {"allocations": [p.model_dump() for p in payload.participants]})
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    expense = Expense(
        room_id=room_id,
        user_id=current_user.id,
        title=payload.title,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
        expense_type=payload.expense_type,
        category_id=payload.category_id,
        payer_id=payer_id,
        expense_date=payload.expense_date,
        split_method=payload.split_method,
        note=payload.note,
    )
    db.add(expense)
    db.flush()

    share_map = {s["user_id"]: s["share_amount_minor"] for s in shares}
    for p in payload.participants:
        db.add(
            ExpenseParticipant(
                expense_id=expense.id,
                user_id=p.user_id,
                share_amount_minor=share_map[p.user_id],
                percentage=p.percentage,
                shares=p.shares,
            )
        )

    append_audit_log(db, actor_id=current_user.id, room_id=room_id, action="SHARED_PAYMENT_CREATED", entity_type="shared_payment", entity_id=expense.id, after={"title": expense.title, "amount_minor": expense.amount_minor, "currency": expense.currency, "payer_id": current_user.id}, metadata={"visibility": "workspace"})

    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_membership(db, room_id, current_user.id)
    return (
        db.query(Expense)
        .filter(Expense.room_id == room_id, Expense.deleted_at.is_(None))
        .order_by(Expense.expense_date.desc())
        .all()
    )
