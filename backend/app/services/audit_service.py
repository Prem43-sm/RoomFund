"""Append-only audit writer. Audit records are never updated or deleted by the API."""
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def append_audit_log(db: Session, *, actor_id: str, room_id: str | None, action: str, entity_type: str, entity_id: str, before: dict | None = None, after: dict | None = None, metadata: dict | None = None) -> AuditLog:
    previous = db.query(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).first()
    previous_hash = previous.record_hash if previous else None
    payload = json.dumps({"previous_hash": previous_hash, "actor_id": actor_id, "room_id": room_id, "action": action, "entity_type": entity_type, "entity_id": entity_id, "before": before, "after": after, "metadata": metadata, "timestamp": datetime.now(timezone.utc).isoformat()}, sort_keys=True, separators=(",", ":"))
    event = AuditLog(user_id=actor_id, room_id=room_id, action=action, entity_type=entity_type, entity_id=entity_id, metadata_json=json.dumps(metadata or {}), before_data=json.dumps(before) if before else None, after_data=json.dumps(after) if after else None, previous_hash=previous_hash, record_hash=hashlib.sha256(payload.encode()).hexdigest())
    db.add(event)
    return event
