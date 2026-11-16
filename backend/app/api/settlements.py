from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate, SettlementOut
import datetime

router = APIRouter(prefix="/rooms/{room_id}/settlements", tags=["settlements"])


def _require_membership(db: Session, room_id: str, user_id: str):
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.get("", response_model=list[SettlementOut])
def list_settlements(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    return (
        db.query(Settlement)
        .filter(Settlement.room_id == room_id)
        .order_by(Settlement.settlement_date.desc())
        .all()
    )


@router.post("", response_model=SettlementOut)
def create_settlement(
    room_id: str,
    payload: SettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    if payload.payer_id == payload.receiver_id:
        raise HTTPException(status_code=400, detail="Payer and receiver must differ")
    settlement = Settlement(
        room_id=room_id,
        payer_id=payload.payer_id,
        receiver_id=payload.receiver_id,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
        settlement_date=payload.settlement_date,
        payment_method=payload.payment_method,
        note=payload.note,
        status="completed",
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


@router.post("/{settlement_id}/reverse")
def reverse_settlement(
    room_id: str,
    settlement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    settlement = (
        db.query(Settlement)
        .filter(Settlement.id == settlement_id, Settlement.room_id == room_id)
        .first()
    )
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.status == "reversed":
        raise HTTPException(status_code=400, detail="Already reversed")
    settlement.status = "reversed"
    settlement.reversed_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return {"message": "Settlement reversed"}