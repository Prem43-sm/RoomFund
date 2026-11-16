"""Private payment routes. Every query is scoped to the authenticated user."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import PersonalPaymentCreate, ExpenseOut
from app.services.audit_service import append_audit_log

router = APIRouter(prefix="/personal-payments", tags=["personal payments"])


@router.get("", response_model=list[ExpenseOut])
def list_personal_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Expense).filter(Expense.user_id == current_user.id, Expense.expense_type == "PERSONAL", Expense.deleted_at.is_(None)).order_by(Expense.expense_date.desc()).all()


@router.post("", response_model=ExpenseOut)
def create_personal_payment(payload: PersonalPaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = Expense(room_id=None, user_id=current_user.id, payer_id=current_user.id, title=payload.title, amount_minor=payload.amount_minor, currency=payload.currency, expense_type="PERSONAL", expense_date=payload.expense_date, split_method="PERSONAL", note=payload.description)
    db.add(payment)
    db.flush()
    append_audit_log(db, actor_id=current_user.id, room_id=None, action="PERSONAL_PAYMENT_CREATED", entity_type="personal_payment", entity_id=payment.id, after={"title": payment.title, "amount_minor": payment.amount_minor, "currency": payment.currency}, metadata={"visibility": "private"})
    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}")
def delete_personal_payment(payment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Expense).filter(Expense.id == payment_id, Expense.user_id == current_user.id, Expense.expense_type == "PERSONAL", Expense.deleted_at.is_(None)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Personal payment not found")
    payment.deleted_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    append_audit_log(db, actor_id=current_user.id, room_id=None, action="PERSONAL_PAYMENT_DELETED", entity_type="personal_payment", entity_id=payment.id, before={"title": payment.title, "amount_minor": payment.amount_minor}, metadata={"visibility": "private"})
    db.commit()
    return {"message": "Personal payment deleted"}
