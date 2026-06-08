# api_gateway/routers/auth.py
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.limiter import limiter
from core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    require_admin,
    revoke_token,
    _decode_token,
    _check_not_revoked,
)
from models.domain import User, RevokedToken, PasswordResetToken
from models.schemas import Token, UserCreate, UserResponse, RefreshResponse, RegisterResponse, ForgotPasswordRequest, ResetPasswordRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 giorni in secondi
_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=False,   # True in produzione (HTTPS)
        samesite="strict",
        max_age=_COOKIE_MAX_AGE,
        path="/",
    )


# ── Registrazione — solo admin ──────────────────────────────────────────────

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def create_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Crea un nuovo utente. Richiede token admin."""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username già registrato")
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ── Registrazione pubblica ────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """Registrazione pubblica: crea un account utente base (ruolo: user)."""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username già registrato")
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        email=user.email or None,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non validi",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 15 * 60,
    }


# ── Refresh token ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias=_REFRESH_COOKIE),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token mancante",
        )
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token non valido")
    jti = payload.get("jti")
    if jti:
        _check_not_revoked(jti, db)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    # Ruota il refresh token: revoca il vecchio, emette uno nuovo
    if jti:
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.commit()
    new_access = create_access_token(user)
    new_refresh = create_refresh_token(user)
    _set_refresh_cookie(response, new_refresh)
    return {
        "access_token": new_access,
        "token_type": "bearer",
        "expires_in": 15 * 60,
    }


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    token: str = Depends(_oauth2),
    refresh_token: Optional[str] = Cookie(default=None, alias=_REFRESH_COOKIE),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    revoke_token(token, db)
    if refresh_token:
        try:
            revoke_token(refresh_token, db)
        except Exception:
            pass
    response.delete_cookie(key=_REFRESH_COOKIE)


# ── Password dimenticata ──────────────────────────────────────────────────────

@router.post("/forgot-password")
@limiter.limit("3/hour")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Risponde sempre 200 — non rivela se l'email esiste. Logga il token al posto dell'email."""
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({"used": True})
        db.commit()
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at))
        db.commit()
        logger.info(f"RESET TOKEN per {body.email}: {token}")
    return {"message": "Se l'email è registrata riceverai le istruzioni a breve."}


@router.post("/reset-password")
@limiter.limit("5/hour")
def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == body.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > now,
        )
        .first()
    )
    if not reset_token:
        raise HTTPException(status_code=400, detail="Token non valido o scaduto")
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token non valido o scaduto")
    user.hashed_password = get_password_hash(body.new_password)
    reset_token.used = True
    db.commit()
    return {"message": "Password aggiornata"}


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get("/admin/users", response_model=list[UserResponse])
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista tutti gli utenti. Solo admin."""
    return db.query(User).all()


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Elimina un utente. Solo admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    db.delete(user)
    db.commit()
