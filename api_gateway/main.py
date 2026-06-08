# api_gateway/main.py
import logging
import os

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create_all crea le tabelle mancanti (inclusa revoked_tokens)
# senza toccare le tabelle già esistenti
Base.metadata.create_all(bind=engine)

# Migration: aggiunge colonna 'role' se il DB esiste già senza di essa
# (SQLite non supporta IF NOT EXISTS su ALTER TABLE — gestiamo l'eccezione)
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
        conn.commit()
        logger.info("Migration: colonna 'role' aggiunta a users.")
    except Exception:
        pass  # colonna già presente — nessuna azione

# Migration: normalizza i valori di role da UPPERCASE (enum name) a lowercase (enum value)
with engine.connect() as conn:
    try:
        conn.execute(text("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'"))
        conn.execute(text("UPDATE users SET role = 'user' WHERE role = 'USER'"))
        conn.commit()
        logger.info("Migration: role normalizzato a lowercase.")
    except Exception as e:
        logger.warning(f"Migration role normalization skipped: {e}")

# Migration: aggiunge colonna 'email' se il DB esiste già senza di essa
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
        conn.commit()
        logger.info("Migration: colonna 'email' aggiunta a users.")
    except Exception:
        pass  # colonna già presente


def _seed_admin() -> None:
    """
    Crea il primo utente admin se non ne esiste nessuno.
    Credenziali da env: INITIAL_ADMIN_USERNAME / INITIAL_ADMIN_PASSWORD.
    Default per sviluppo: admin / Admin1234!
    """
    from models.domain import User, RevokedToken, PasswordResetToken
    from core.security import get_password_hash
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin1234!")
    db = SessionLocal()
    try:
        existing_by_name = db.query(User).filter(User.username == username).first()
        existing_by_role = db.query(User).filter(User.role == "admin").first()
        if existing_by_name and existing_by_name.role != "admin":
            # Fix: utente admin esiste ma ha ruolo errato
            existing_by_name.role = "admin"
            db.commit()
            logger.info(f"Admin seed: ruolo di '{username}' corretto a 'admin'.")
        elif not existing_by_name and not existing_by_role:
            admin = User(
                username=username,
                hashed_password=get_password_hash(password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info(f"Admin seed: utente '{username}' creato.")
        else:
            logger.info("Admin seed: utente admin già presente.")
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
