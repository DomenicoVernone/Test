# JWT / BOLA / BFLA / Mass Assignment Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hardening completo del sistema di autenticazione e autorizzazione: JWT con scadenza breve + refresh + blacklist, sistema di ruoli user/admin, protezione BOLA su tutti gli endpoint, timing attack protection e validazione password strength.

**Architecture:** Il database SQLite è condiviso tra `api_gateway` e `orchestrator` sullo stesso volume Docker. La blacklist JWT e la colonna `role` vengono aggiunte al DB condiviso. `api_gateway` è l'unico servizio che emette token; `orchestrator` li valida leggendo dalla stessa SECRET_KEY e dalla stessa tabella RevokedToken. RS256 è escluso (ambiente embedded, un solo emittente) — si usa HS256 con chiave ≥ 64 char.

**Tech Stack:** FastAPI, python-jose, passlib/bcrypt, SQLAlchemy, SQLite, pydantic v2, slowapi (già installato)

---

## File Map

| File | Azione | Responsabilità |
|---|---|---|
| `api_gateway/.env` | Modifica | Nuova SECRET_KEY ≥ 64 chars |
| `orchestrator/.env` | Modifica | Stessa SECRET_KEY |
| `api_gateway/core/config.py` | Modifica | Validator SECRET_KEY, EXPIRE 15min, REFRESH 7gg |
| `api_gateway/models/domain.py` | Modifica | Aggiunge colonna `role`, tabella `RevokedToken` |
| `orchestrator/models/domain.py` | Modifica | Sync colonna `role` |
| `api_gateway/models/schemas.py` | Modifica | Password strength, email optional, role in response |
| `orchestrator/models/schemas.py` | Modifica | Rimuove `owner_id` da TaskResponse |
| `api_gateway/core/security.py` | Modifica | jti, sub=user_id, refresh token, blacklist, timing fix, bcrypt rounds |
| `orchestrator/core/security.py` | Modifica | sub=user_id, blacklist check |
| `api_gateway/routers/auth.py` | Modifica | /logout, /refresh, /admin/users, timing fix, /signup → admin |
| `orchestrator/routers/analyze.py` | Modifica | Endpoint admin delete task |
| `api_gateway/main.py` | Modifica | Startup: migration colonna role + seed admin |

---

## Task 1 — Genera SECRET_KEY forte e aggiorna config

**Files:**
- Modify: `api_gateway/.env`
- Modify: `orchestrator/.env`
- Modify: `api_gateway/core/config.py`
- Modify: `orchestrator/core/config.py`

- [ ] **Step 1.1: Genera una SECRET_KEY di 64+ caratteri**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Esempio output: a3f8...64chars
```

Copia l'output. Aggiorna `api_gateway/.env`:
```
SECRET_KEY=<il-valore-generato-64-chars>
DATABASE_URL=sqlite:////shared_db/clinical_twin.db
CORS_ORIGINS=["http://localhost:5173","http://localhost:8001","http://localhost:8002","http://localhost:8003"]
```

E `orchestrator/.env` (stesso valore):
```
SECRET_KEY=<stesso-valore>
DATABASE_URL=sqlite:////shared_db/clinical_twin.db
MODEL_SERVICE_URL=http://model_service:8000
NEXTFLOW_WORKER_URL=http://nextflow_worker:8000
AUTH_SERVICE_URL=http://api_gateway:8000
SHARED_VOLUME_DIR=/shared_data
USE_MOCK=false
TEST_MODE=false
```

- [ ] **Step 1.2: Aggiorna `api_gateway/core/config.py`**

```python
import os
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:////shared_db/clinical_twin.db")
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173"])

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strength(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError(
                f"SECRET_KEY deve essere >= 64 caratteri (attuale: {len(v)})"
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
```

- [ ] **Step 1.3: Aggiorna `orchestrator/core/config.py`** — aggiungi `REFRESH_TOKEN_EXPIRE_DAYS` e validator:

```python
# orchestrator/core/config.py
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:////shared_db/clinical_twin.db")
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    MODEL_SERVICE_URL: str = Field(default="http://model_service:8000")
    NEXTFLOW_WORKER_URL: str = Field(default="http://nextflow_worker:8000")
    AUTH_SERVICE_URL: str = Field(default="http://api_gateway:8000")
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")
    USE_MOCK: bool = Field(default=False)
    TEST_MODE: bool = Field(default=False)
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173"])

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strength(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError(
                f"SECRET_KEY deve essere >= 64 caratteri (attuale: {len(v)})"
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def NIFTI_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "nifti")

    @property
    def FEATURES_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "features")

    @property
    def RESULTS_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "results")


settings = Settings()
```

- [ ] **Step 1.4: Verifica che i container partano con la nuova chiave**

```bash
docker compose restart api_gateway orchestrator
docker logs clinical_api_gateway --tail 5
# Atteso: nessun errore di validazione SECRET_KEY
```

---

## Task 2 — Domain Models: colonna role + tabella RevokedToken

**Files:**
- Modify: `api_gateway/models/domain.py`
- Modify: `orchestrator/models/domain.py`

- [ ] **Step 2.1: Aggiorna `api_gateway/models/domain.py`**

```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, server_default="user")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```

- [ ] **Step 2.2: Aggiorna `orchestrator/models/domain.py`** — sync role column:

```python
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, server_default="user")

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    progress = Column(Float, default=0.0)
    model_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks")
```

---

## Task 3 — Schema updates

**Files:**
- Modify: `api_gateway/models/schemas.py`
- Modify: `orchestrator/models/schemas.py`

- [ ] **Step 3.1: Aggiorna `api_gateway/models/schemas.py`**

```python
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_safe(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_.\-]{3,50}$', v):
            raise ValueError(
                "Username non valido. Usa solo lettere, numeri, . _ - (3-50 caratteri)"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La password deve essere di almeno 8 caratteri")
        if not re.search(r'[A-Z]', v):
            raise ValueError("La password deve contenere almeno una lettera maiuscola")
        if not re.search(r'[0-9]', v):
            raise ValueError("La password deve contenere almeno un numero")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
```

- [ ] **Step 3.2: Aggiorna `orchestrator/models/schemas.py`** — rimuovi `owner_id` da TaskResponse:

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    filename: str
    model_name: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    filename: str
    status: str
    progress: float
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # owner_id rimosso: non deve essere esposto al client
    model_config = ConfigDict(from_attributes=True)
```

---

## Task 4 — JWT security functions

**Files:**
- Modify: `api_gateway/core/security.py`

- [ ] **Step 4.1: Riscrivi `api_gateway/core/security.py`**

```python
# api_gateway/core/security.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import User, RevokedToken

# Bcrypt con 12 rounds espliciti — default passlib è già 12
# ma rendiamo la configurazione esplicita e auditabile
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Hash dummy pre-calcolato per il timing-safe login
# Calcolato una volta sola all'avvio — evita variazioni di tempo
# rivelabili quando l'username non esiste
_DUMMY_HASH: str = pwd_context.hash("__dummy_password_for_timing_protection__")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Autentica username/password con protezione da timing attack.
    verify_password viene chiamato SEMPRE — anche se l'utente non esiste —
    così il tempo di risposta è costante indipendentemente dall'esistenza
    dell'username, impedendo user enumeration tramite side-channel.
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
```

---

## Task 5 — Auth router: logout, refresh, admin endpoints

**Files:**
- Modify: `api_gateway/routers/auth.py`

- [ ] **Step 5.1: Riscrivi `api_gateway/routers/auth.py`**

```python
# api_gateway/routers/auth.py
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

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
from models.domain import User
from models.schemas import Token, UserCreate, UserResponse, RefreshResponse

router = APIRouter(tags=["Authentication"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 giorni in secondi


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
def refresh_token(
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
    new_access = create_access_token(user)
    new_refresh = create_refresh_token(user)
    # Ruota il refresh token: revoca il vecchio, emette uno nuovo
    if jti:
        from datetime import datetime, timezone
        from models.domain import RevokedToken
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.commit()
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
    token: str = Depends(__import__("fastapi.security", fromlist=["OAuth2PasswordBearer"]).OAuth2PasswordBearer(tokenUrl="/login")),
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
```

Note: il `logout` endpoint usa direttamente `oauth2_scheme` dall'import — va pulito. Vedi step successivo.

- [ ] **Step 5.2: Fix import OAuth2PasswordBearer nel logout**

Sostituisci il logout con versione pulita — usa la dipendenza già presente:

```python
from fastapi.security import OAuth2PasswordBearer as _OAuth2
_oauth2 = _OAuth2(tokenUrl="/login")

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
```

---

## Task 6 — Orchestrator security sync

**Files:**
- Modify: `orchestrator/core/security.py`

- [ ] **Step 6.1: Aggiorna `orchestrator/core/security.py`** — usa `user_id` da `sub`, aggiunge blacklist check:

```python
# orchestrator/core/security.py
from datetime import datetime, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import User, RevokedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o token scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        jti: Optional[str] = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Controlla blacklist dal DB condiviso
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocato. Effettua nuovamente il login.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: privilegi insufficienti",
        )
    return current_user
```

---

## Task 7 — Admin task endpoint nell'orchestrator

**Files:**
- Modify: `orchestrator/routers/analyze.py`

- [ ] **Step 7.1: Aggiungi endpoint admin a `orchestrator/routers/analyze.py`**

Aggiungi in fondo al file (dopo l'endpoint `get_nifti_file`):

```python
from core.security import require_admin   # aggiunta all'import

@router.delete("/admin/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Elimina qualsiasi task. Solo admin."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    db.delete(task)
    db.commit()
```

---

## Task 8 — Startup migration + seed admin

**Files:**
- Modify: `api_gateway/main.py`

- [ ] **Step 8.1: Aggiorna `api_gateway/main.py`** per eseguire migration e seed:

```python
# api_gateway/main.py
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from core.database import engine, Base, SessionLocal
from core.config import settings
from core.limiter import limiter
from routers import auth

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

# Migration: aggiunge colonna 'role' se il DB esiste già senza di essa
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
        conn.commit()
        logger.info("Migration: colonna 'role' aggiunta.")
    except Exception:
        pass  # colonna già presente

def _seed_admin():
    """
    Crea il primo utente admin all'avvio se non ne esiste nessuno.
    Le credenziali si leggono da INITIAL_ADMIN_USERNAME / INITIAL_ADMIN_PASSWORD.
    Default per sviluppo: admin / Admin1234!
    """
    from models.domain import User
    from core.security import get_password_hash
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin1234!")
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.role == "admin").first():
            admin = User(
                username=username,
                hashed_password=get_password_hash(password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info(f"Admin seed: utente '{username}' creato.")
    finally:
        db.close()

_seed_admin()

_dev = os.getenv("ENV") == "development"

app = FastAPI(
    title="Clinical Twin — API Gateway",
    description="Autenticazione e gestione JWT",
    version="1.0.0",
    docs_url="/docs" if _dev else None,
    redoc_url="/redoc" if _dev else None,
    openapi_url="/openapi.json" if _dev else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["server"] = "webserver"
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["x-xss-protection"] = "1; mode=block"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "api_gateway"}
```

- [ ] **Step 8.2: Aggiungi `SessionLocal` a `api_gateway/core/database.py`**

Verifica che esista `SessionLocal`. Se non presente, aggiungilo:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Task 9 — Rebuild e test completo

- [ ] **Step 9.1: Rebuild e avvio**

```bash
cd C:\Users\dvern\Desktop\Tirocinio\Tesi-FTD
docker compose up --build -d api_gateway orchestrator
docker compose ps
```

- [ ] **Step 9.2: Login con admin e ottieni token**

```bash
TOKEN_ADMIN=$(curl -s -X POST http://localhost:8006/login \
  -d "username=admin&password=Admin1234!" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Admin token: ${TOKEN_ADMIN:0:40}..."
```

- [ ] **Step 9.3: Test BFLA — crea userA e userB tramite admin**

```bash
# Crea userA (solo admin può farlo)
curl -s -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"username":"userA","password":"TestA1234!"}'
# Atteso: 201

# userA NON è admin — tenta /admin/users
TOKEN_A=$(curl -s -X POST http://localhost:8006/login \
  -d "username=userA&password=TestA1234!" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8006/admin/users -H "Authorization: Bearer $TOKEN_A"
# Atteso: 403
```

- [ ] **Step 9.4: Test JWT blacklist (logout)**

```bash
# Ottieni token userA
TOKEN_A=$(...)

# Accede normalmente
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8001/analyze/status/19 \
  -H "Authorization: Bearer $TOKEN_A"
# Atteso: 200 o 404 (task non trovato ma auth ok)

# Logout
curl -s -X POST http://localhost:8006/logout \
  -H "Authorization: Bearer $TOKEN_A" -w "%{http_code}"
# Atteso: 204

# Tenta di riusare il token revocato
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8001/analyze/status/19 \
  -H "Authorization: Bearer $TOKEN_A"
# Atteso: 401 (Token revocato)
```

- [ ] **Step 9.5: Test BOLA — userB non vede task di userA**

```bash
# Crea userB
curl -s -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"username":"userB","password":"TestB1234!"}'

TOKEN_B=$(curl -s -X POST http://localhost:8006/login \
  -d "username=userB&password=TestB1234!" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# userB tenta di accedere al task 19 di userA
curl -s http://localhost:8001/analyze/status/19 \
  -H "Authorization: Bearer $TOKEN_B"
# Atteso: 404 (Task non trovato)
```

- [ ] **Step 9.6: Test mass assignment — role ignorato**

```bash
curl -s -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"username":"hacker2","password":"Hack1234!","role":"admin","is_admin":true}'

# Verifica ruolo nel DB
docker exec clinical_api_gateway python3 -c "
from core.database import SessionLocal
from models.domain import User
db = SessionLocal()
u = db.query(User).filter_by(username='hacker2').first()
print('Ruolo:', u.role if u else 'utente non trovato')
"
# Atteso: Ruolo: user
```

- [ ] **Step 9.7: Test rate limiting**

```bash
for i in $(seq 1 6); do
  curl -s -o /dev/null -w "Req $i: %{http_code}\n" \
    -X POST http://localhost:8006/login \
    -d "username=x&password=Wrong123!" \
    -H "Content-Type: application/x-www-form-urlencoded"
done
# Atteso: prime 3-5 = 401, poi 429
```

- [ ] **Step 9.8: Aggiorna `docs/API_SECURITY_TEST_REPORT.md`** con tabella finale 13/13

---

## Self-Review Checklist

- [x] JWT1 (scadenza 15min): Task 1, config.py `ACCESS_TOKEN_EXPIRE_MINUTES=15`
- [x] JWT2 (refresh token): Task 5, `/refresh` endpoint + httpOnly cookie
- [x] JWT3 (jti + blacklist + logout): Task 4 `_build_token`, Task 5 `/logout`, Tasks 4/6 `_check_not_revoked`
- [x] JWT4 (SECRET_KEY ≥ 64): Task 1, validator in config.py
- [x] JWT5 (sub = user_id): Task 4 `create_access_token`, Task 6 orchestrator security
- [x] BOLA (owner_id su tutti endpoint): già fatto sessione precedente + Task 7 admin delete
- [x] BFLA (ruoli user/admin): Task 2 domain, Task 4 `require_admin`, Task 5 /admin/users
- [x] BFLA (/admin/* protetti): Task 5 e Task 7
- [x] MA1 (schema input/output): Task 3, UserResponse espone role, rimuove owner_id da TaskResponse
- [x] MA2 (role/is_admin ignorati): UserCreate non ha campo role → mai passato al costruttore User
- [x] HC1 (bcrypt rounds ≥ 12): Task 4, `bcrypt__rounds=12` esplicito
- [x] HC2 (timing attack): Task 4, `authenticate_user` con `_DUMMY_HASH`
- [x] HC3 (password strength): Task 3, `password_strength` validator
