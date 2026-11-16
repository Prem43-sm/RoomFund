from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.models.user import User
from app.models.invitation import Invitation
from app.models.room_member import RoomMember
import datetime
from app.schemas.auth import UserRegister, UserLogin, Token, TokenData

router = APIRouter(prefix="", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", response_model=dict)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=email,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.flush()
    invite = db.query(Invitation).filter(Invitation.email == email, Invitation.used_at.is_(None), Invitation.expires_at > datetime.datetime.now(datetime.timezone.utc)).order_by(Invitation.created_at.desc()).first()
    if invite:
        db.add(RoomMember(room_id=invite.room_id, user_id=user.id, role="MEMBER", status="active"))
        invite.used_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "message": "Registered successfully"}


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email).strip().lower(), User.deleted_at.is_(None)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@router.post("/refresh", response_model=dict)
def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = create_access_token({"sub": payload.get("sub")})
    return {"access_token": access_token}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "currency": current_user.currency,
        "timezone": current_user.timezone,
        "theme": current_user.theme,
    }
