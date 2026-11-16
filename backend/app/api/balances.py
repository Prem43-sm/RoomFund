from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.room import Room
from app.models.room_member import RoomMember
from app.services.balance_service import compute_room_balances

router = APIRouter(prefix="/rooms/{room_id}", tags=["balances"])


def _require_membership(db: Session, room_id: str, user_id: str):
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.get("/balances")
def get_balances(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    return {"room_id": room_id, "members": compute_room_balances(db, room_id)}


@router.get("/settlement-suggestions")
def get_settlement_suggestions(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    _require_membership(db, room_id, current_user.id)
    balances = compute_room_balances(db, room_id)
    creditors = [b for b in balances if b["net_balance_minor"] > 0]
    debtors = [b for b in balances if b["net_balance_minor"] < 0]
    suggestions = []
    i = j = 0
    creditors = sorted(creditors, key=lambda b: b["net_balance_minor"], reverse=True)
    debtors = sorted(debtors, key=lambda b: b["net_balance_minor"])
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        amount = min(-debtor["net_balance_minor"], creditor["net_balance_minor"])
        if amount > 0:
            suggestions.append(
                {
                    "from": debtor["user_id"],
                    "from_name": debtor["name"],
                    "to": creditor["user_id"],
                    "to_name": creditor["name"],
                    "amount_minor": amount,
                }
            )
        debtors[i]["net_balance_minor"] += amount
        creditors[j]["net_balance_minor"] -= amount
        if debtors[i]["net_balance_minor"] == 0:
            i += 1
        if creditors[j]["net_balance_minor"] == 0:
            j += 1
    return {"room_id": room_id, "suggestions": suggestions}