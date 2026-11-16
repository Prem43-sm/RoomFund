"""Balance engine.

Computes authoritative per-room and per-member balances from expenses and
settlements. Balances are expressed in integer minor units.
Positive balance => member should receive money.
Negative balance => member owes money.
Zero => settled.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.settlement import Settlement


def compute_room_balances(db: Session, room_id: str) -> List[Dict[str, Any]]:
    """Return per-member balance summary for a room."""
    # Query members
    from app.models.room_member import RoomMember
    from app.models.user import User

    members = db.query(RoomMember).filter(RoomMember.room_id == room_id).all()
    if not members:
        return []

    user_ids = [m.user_id for m in members]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    # Total paid by each member (as payer of common expenses)
    paid = (
        db.query(Expense.payer_id, func.sum(Expense.amount_minor).label("total_paid"))
        .filter(Expense.room_id == room_id)
        .filter(Expense.expense_type == "COMMON")
        .filter(Expense.deleted_at.is_(None))
        .group_by(Expense.payer_id)
        .all()
    )
    paid_map = {row.payer_id: row.total_paid or 0 for row in paid}

    # Total share owed by each member (participant shares of common expenses)
    shares = (
        db.query(ExpenseParticipant.user_id, func.sum(ExpenseParticipant.share_amount_minor).label("total_share"))
        .join(Expense, ExpenseParticipant.expense_id == Expense.id)
        .filter(Expense.room_id == room_id)
        .filter(Expense.expense_type == "COMMON")
        .filter(Expense.deleted_at.is_(None))
        .group_by(ExpenseParticipant.user_id)
        .all()
    )
    share_map = {row.user_id: row.total_share or 0 for row in shares}

    # Total settled (completed settlements) per member
    settled_paid = (
        db.query(Settlement.payer_id, func.sum(Settlement.amount_minor).label("total"))
        .filter(Settlement.room_id == room_id)
        .filter(Settlement.status == "completed")
        .group_by(Settlement.payer_id)
        .all()
    )
    settled_received = (
        db.query(Settlement.receiver_id, func.sum(Settlement.amount_minor).label("total"))
        .filter(Settlement.room_id == room_id)
        .filter(Settlement.status == "completed")
        .group_by(Settlement.receiver_id)
        .all()
    )
    settled_paid_map = {row.payer_id: row.total or 0 for row in settled_paid}
    settled_received_map = {row.receiver_id: row.total or 0 for row in settled_received}

    results = []
    for m in members:
        uid = m.user_id
        total_paid = paid_map.get(uid, 0)
        total_share = share_map.get(uid, 0)
        # net = paid - share - settled_paid + settled_received
        net = total_paid - total_share - settled_paid_map.get(uid, 0) + settled_received_map.get(uid, 0)
        results.append(
            {
                "user_id": uid,
                "name": users.get(uid, User(name="Unknown", email="")).name if users.get(uid) else "Unknown",
                "role": m.role,
                "total_paid_minor": total_paid,
                "total_share_minor": total_share,
                "net_balance_minor": net,
                "status": "receive" if net > 0 else ("owe" if net < 0 else "settled"),
            }
        )
    return results