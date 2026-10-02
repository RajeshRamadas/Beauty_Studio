from typing import Generator, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def get_settings():
    return settings

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[UserModel]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except Exception:
        return None
    
    user = db.query(UserModel).filter((UserModel.id == user_id) | (UserModel.auth_subject == user_id)).first()
    return user

def get_current_user(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
) -> UserModel:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def is_admin(user: Optional[UserModel]) -> bool:
    if not user:
        return False
    admins = {e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()}
    return user.role == "admin" or (bool(user.email) and user.email.lower() in admins)


def get_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Catalogue management needs an admin account.")
    return current_user


def require_photo_consent(consent_version: str) -> str:
    """Photos are processed only after the user accepted the current consent text in the app."""
    if (consent_version or "").strip() != settings.PHOTO_CONSENT_VERSION:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Please review and accept how your photo is used before continuing.",
        )
    return settings.PHOTO_CONSENT_VERSION
