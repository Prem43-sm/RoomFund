from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.room_member import RoomMember
from app.models.user import User

router = APIRouter(prefix="/activity", tags=["activity log"])


@router.get("")
def list_activity(room_id: str, limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(RoomMember).filter(RoomMember.room_id == room_id, RoomMember.user_id == current_user.id, RoomMember.status == "active").first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a workspace member")
    events = db.query(AuditLog).filter((AuditLog.room_id == room_id) | ((AuditLog.room_id.is_(None)) & (AuditLog.user_id == current_user.id))).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return [{"id": event.id, "action": event.action, "entity_type": event.entity_type, "entity_id": event.entity_id, "metadata": event.metadata_json, "created_at": event.created_at, "actor": {"id": event.user_id, "name": event.user.name if getattr(event, "user", None) else "Member"}} for event in events]


@router.api_route("/{log_id}", methods=["PATCH", "DELETE"])
def reject_audit_mutation(log_id: str, current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=403, detail="Activity logs are immutable")
