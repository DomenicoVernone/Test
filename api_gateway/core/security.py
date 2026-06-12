# api_gateway/core/security.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import User, RevokedToken

# 12 rounds espliciti — configurazione auditabile
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Hash dummy pre-calcolato una volta sola: usato nel login quando
# l'utente non esiste per rendere il tempo di risposta costante
# e impedire user enumeration tramite timing side-channel.
_DUMMY_HASH: str = pwd_context.hash("__dummy_password_for_timing_protection__")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Autentica con protezione timing: verify_password viene chiamato SEMPRE,
    anche se l'utente non esiste, così il tempo di risposta è costante.
    """
    user = db.query(User).filter(User.username == username).first()
    hash_to_check = user.hashed_password if user else _DUMMY_HASH
    if not verify_password(password, hash_to_check):
        return None
    return user


def _build_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    now = datetime.now(timezone.utc)
    payload.update({
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user: User) -> str:
    return _build_token(
        {"sub": str(user.id), "username": user.username, "role": user.role},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user: User) -> str:
    return _build_token(
        {"sub": str(user.id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide o token scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _check_not_revoked(jti: str, db: Session) -> None:
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocato. Effettua nuovamente il login.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = _decode_token(token)
    user_id: Optional[str] = payload.get("sub")
    jti: Optional[str] = payload.get("jti")
    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide o token scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _check_not_revoked(jti, db)
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide o token scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: privilegi insufficienti",
        )
    return current_user


def revoke_token(token: str, db: Session) -> None:
    """Aggiunge il jti del token alla blacklist nel DB condiviso."""
    payload = _decode_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.commit()
