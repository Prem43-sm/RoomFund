from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.room import Room
from app.models.room_member import RoomMember
from app.models.invitation import Invitation
from app.schemas.member import MemberInvite, MemberJoin
import uuid
import datetime

router = APIRouter(prefix="/rooms/{room_id}/members", tags=["members"])


def _require_membership(db: Session, room_id: str, user_id: str) -> RoomMember:
    member = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    return member


@router.get("")
def list_members(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_membership(db, room_id, current_user.id)
    members = db.query(RoomMember).filter(RoomMember.room_id == room_id).all()
    output = [{"id": m.id, "user_id": m.user_id, "name": m.user.name, "email": m.user.email, "role": m.role, "status": m.status, "joined_at": m.joined_at} for m in members]
    invitations = db.query(Invitation).filter(Invitation.room_id == room_id, Invitation.used_at.is_(None), Invitation.expires_at > datetime.datetime.now(datetime.timezone.utc)).all()
    for invite in invitations:
        output.append({"id": invite.id, "user_id": None, "name": "Invited member", "email": invite.email, "role": "MEMBER", "status": "invited", "joined_at": None})
    return output


@router.post("/invite")
def invite_member(
    room_id: str,
    payload: MemberInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    membership = _require_membership(db, room_id, current_user.id)
    if membership.role not in {"OWNER", "ADMIN"}:
        raise HTTPException(status_code=403, detail="Only the owner can invite")
    email = str(payload.email).strip().lower()
    if db.query(Invitation).filter(Invitation.room_id == room_id, Invitation.email == email, Invitation.used_at.is_(None)).first():
        raise HTTPException(status_code=409, detail="This Gmail is already invited")
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user and db.query(RoomMember).filter(RoomMember.room_id == room_id, RoomMember.user_id == existing_user.id).first():
        raise HTTPException(status_code=409, detail="This Gmail is already a workspace member")
    invite = Invitation(
        room_id=room_id,
        inviter_id=current_user.id,
        invite_code=uuid.uuid4().hex[:8].upper(),
        email=email,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    )
    db.add(invite)
    db.commit()
    return {"invite_code": invite.invite_code, "email": invite.email, "name": payload.name, "status": "invited"}


@router.post("/join")
def join_room(
    room_id: str,
    payload: MemberJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = (
        db.query(Invitation)
        .filter(Invitation.invite_code == payload.invite_code, Invitation.expires_at > datetime.datetime.now(datetime.timezone.utc), Invitation.used_at.is_(None))
        .first()
    )
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")
    existing = (
        db.query(RoomMember)
        .filter(RoomMember.room_id == invite.room_id, RoomMember.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already a member of this room")
    membership = RoomMember(room_id=invite.room_id, user_id=current_user.id, role="MEMBER", status="active")
    db.add(membership)
    invite.used_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return {"message": "Joined room", "room_id": invite.room_id}


@router.patch("/{member_id}")
def update_member(
    room_id: str,
    member_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can change roles")
    member = db.query(RoomMember).filter(RoomMember.id == member_id, RoomMember.room_id == room_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = role
    db.commit()
    return {"message": "Role updated"}


@router.delete("/{member_id}")
def remove_member(
    room_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can remove members")
    member = db.query(RoomMember).filter(RoomMember.id == member_id, RoomMember.room_id == room_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Owner cannot remove themselves")
    member.status = "left"
    db.commit()
    return {"message": "Member removed"}
    if invite.email and invite.email.strip().lower() != current_user.email.strip().lower():
        raise HTTPException(status_code=403, detail="This invitation belongs to a different Gmail address")
