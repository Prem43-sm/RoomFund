from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.schemas.room import RoomCreate, RoomUpdate, RoomOut
import uuid
import datetime

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _generate_invite_code() -> str:
    return uuid.uuid4().hex[:8].upper()


@router.post("", response_model=RoomOut)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_membership = db.query(RoomMember).filter(RoomMember.user_id == current_user.id, RoomMember.status == "active").first()
    if existing_membership:
        raise HTTPException(status_code=409, detail="You already belong to a shared workspace. Create a new workspace is not available here.")
    if db.query(Room).filter(Room.archived_at.is_(None)).first():
        raise HTTPException(status_code=403, detail="A RoomFund workspace already exists. Ask an admin to add your Gmail address.")
    room = Room(
        name=payload.name,
        description=payload.description,
        location=payload.location,
        currency=payload.currency,
        owner_id=current_user.id,
        invite_code=_generate_invite_code(),
        start_date=payload.start_date,
        monthly_rent=payload.monthly_rent,
        rent_due_day=payload.rent_due_day,
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    membership = RoomMember(
        room_id=room.id,
        user_id=current_user.id,
        role="OWNER",
        status="active",
    )
    db.add(membership)
    db.commit()
    return room


@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    memberships = (
        db.query(RoomMember)
        .filter(RoomMember.user_id == current_user.id, RoomMember.status == "active")
        .all()
    )
    room_ids = [m.room_id for m in memberships]
    if not room_ids:
        return []
    return db.query(Room).filter(Room.id.in_(room_ids), Room.archived_at.is_(None)).all()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == room_id, Room.archived_at.is_(None)).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    return room


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: str,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id, Room.archived_at.is_(None)).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    membership = db.query(RoomMember).filter(RoomMember.room_id == room_id, RoomMember.user_id == current_user.id, RoomMember.status == "active").first()
    if not membership or membership.role not in {"OWNER", "ADMIN"}:
        raise HTTPException(status_code=403, detail="Only the owner can update the room")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def archive_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can archive the room")
    room.archived_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return {"message": "Room archived"}
