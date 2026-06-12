# Auth Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add public registration, forgot-password and reset-password flows (backend + frontend), and harden the existing Login page.

**Architecture:** Backend gets three new public endpoints (`/register`, `/forgot-password`, `/reset-password`) in the existing FastAPI auth router; SQLite DB gets `email` column on `users` and a new `password_reset_tokens` table via the existing inline-migration pattern in `main.py`. Frontend gets three new pages (Register, ForgotPassword, ResetPassword) mirroring Login's exact Tailwind style, plus Login itself is updated with security links and a client-side lockout.

**Tech Stack:** FastAPI + SQLAlchemy + SQLite (backend), React + React Router v6 + Tailwind CSS + Lucide React + Axios (frontend), Docker Compose for restart.

---

> ⚠️ **Important note on `/signup`:** The existing `POST /signup` endpoint uses `require_admin` — any unauthenticated caller gets 401. It **cannot** be used for public self-registration. Task 2 adds a separate public `POST /register` endpoint. The user said "no backend changes needed for registration" but this is the minimal fix required.

---

## File Map

| Action | File |
|--------|------|
| Modify | `api_gateway/models/domain.py` |
| Modify | `api_gateway/models/schemas.py` |
| Modify | `api_gateway/routers/auth.py` |
| Modify | `api_gateway/main.py` |
| Modify | `frontend/src/pages/Login.jsx` |
| Create | `frontend/src/pages/Register.jsx` |
| Create | `frontend/src/pages/ForgotPassword.jsx` |
| Create | `frontend/src/pages/ResetPassword.jsx` |
| Modify | `frontend/src/App.jsx` |

---

## Task 1: Add `email` column and `PasswordResetToken` model

**Files:**
- Modify: `api_gateway/models/domain.py`
- Modify: `api_gateway/main.py`

- [ ] **Step 1: Update domain.py**

Replace the contents of `api_gateway/models/domain.py` with:

```python
import enum
import secrets
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum
from core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.USER,
        nullable=False,
        server_default="user",
    )
    email = Column(String, unique=True, nullable=True)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
```

- [ ] **Step 2: Add inline migration for `email` column in main.py**

In `api_gateway/main.py`, after the existing role-normalization migration block (after line ~43) and before `_seed_admin()`, add:

```python
# Migration: aggiunge colonna 'email' se il DB esiste già senza di essa
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
        conn.commit()
        logger.info("Migration: colonna 'email' aggiunta a users.")
    except Exception:
        pass  # colonna già presente
```

Also add the import of `PasswordResetToken` to the existing imports section at the top of main.py so `create_all` picks it up:

```python
from models.domain import User, RevokedToken, PasswordResetToken  # add PasswordResetToken
```

- [ ] **Step 3: Commit**

```bash
git add api_gateway/models/domain.py api_gateway/main.py
git commit -m "feat(backend): add email column to users and PasswordResetToken model"
```

---

## Task 2: Add public `/register` endpoint

**Files:**
- Modify: `api_gateway/models/schemas.py`
- Modify: `api_gateway/routers/auth.py`

- [ ] **Step 1: Update schemas.py — add RegisterRequest**

No change needed to `UserCreate` since it already validates username + password + optional email. But we want a distinct type for the public endpoint. Append to `api_gateway/models/schemas.py`:

```python
class RegisterResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Add `POST /register` to auth.py**

In `api_gateway/routers/auth.py`, add the import for `PasswordResetToken` at the top (inside the existing domain import line):

```python
from models.domain import User, RevokedToken, PasswordResetToken
```

Then add the new endpoint after the `/signup` block (around line 64):

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add api_gateway/models/schemas.py api_gateway/routers/auth.py
git commit -m "feat(backend): add public POST /register endpoint"
```

---

## Task 3: Add `/forgot-password` and `/reset-password` endpoints

**Files:**
- Modify: `api_gateway/models/schemas.py`
- Modify: `api_gateway/routers/auth.py`

- [ ] **Step 1: Add request schemas to schemas.py**

Append to `api_gateway/models/schemas.py`:

```python
class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La password deve essere di almeno 8 caratteri")
        if not re.search(r'[A-Z]', v):
            raise ValueError("La password deve contenere almeno una lettera maiuscola")
        if not re.search(r'[0-9]', v):
            raise ValueError("La password deve contenere almeno un numero")
        return v
```

- [ ] **Step 2: Add the two endpoints to auth.py**

Add imports at the top of auth.py (alongside existing imports):

```python
import logging
import secrets
from datetime import datetime, timedelta, timezone
```

(If `datetime` and `timezone` are already imported, just add `secrets` and `logging`.)

Then add at the end of auth.py, before the admin endpoints:

```python
logger = logging.getLogger(__name__)

# ── Password dimenticata ──────────────────────────────────────────────────────

@router.post("/forgot-password")
@limiter.limit("3/hour")
def forgot_password(
    request: Request,
    body: "ForgotPasswordRequest",
    db: Session = Depends(get_db),
):
    """
    Risponde sempre con 200 e stesso messaggio — non rivela se l'email esiste.
    Per ora stampa il token nel log invece di inviare una email.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        # Invalida token non ancora usati per questo utente
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
    body: "ResetPasswordRequest",
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
```

Update the schemas import at the top of auth.py to include the new types:

```python
from models.schemas import Token, UserCreate, UserResponse, RefreshResponse, ForgotPasswordRequest, ResetPasswordRequest
```

- [ ] **Step 3: Commit**

```bash
git add api_gateway/models/schemas.py api_gateway/routers/auth.py
git commit -m "feat(backend): add forgot-password and reset-password endpoints"
```

---

## Task 4: Update Login.jsx

**Files:**
- Modify: `frontend/src/pages/Login.jsx`

Changes:
1. Any 401/400/422 → always shows "Credenziali non valide" (never the backend's specific message)
2. Failed-attempt counter with 60s lockout stored in `localStorage`
3. Link "Password dimenticata?" under password field
4. Link "Prima volta? Richiedi accesso" under submit button

- [ ] **Step 1: Replace Login.jsx**

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, User, ShieldAlert } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const FAIL_KEY = 'login_fails';
const LOCK_KEY = 'login_locked_until';
const MAX_FAILS = 3;
const LOCK_SECONDS = 60;

export default function Login({ theme }) {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [lockSecondsLeft, setLockSecondsLeft] = useState(0);
    const timerRef = useRef(null);
    const navigate = useNavigate();

    // Check lockout on mount and keep countdown alive
    useEffect(() => {
        const tick = () => {
            const until = parseInt(localStorage.getItem(LOCK_KEY) || '0');
            const left = Math.ceil((until - Date.now()) / 1000);
            if (left > 0) {
                setLockSecondsLeft(left);
            } else {
                setLockSecondsLeft(0);
                clearInterval(timerRef.current);
            }
        };
        tick();
        timerRef.current = setInterval(tick, 1000);
        return () => clearInterval(timerRef.current);
    }, []);

    const recordFail = () => {
        const fails = parseInt(localStorage.getItem(FAIL_KEY) || '0') + 1;
        localStorage.setItem(FAIL_KEY, String(fails));
        if (fails >= MAX_FAILS) {
            const until = Date.now() + LOCK_SECONDS * 1000;
            localStorage.setItem(LOCK_KEY, String(until));
            localStorage.setItem(FAIL_KEY, '0');
        }
    };

    const clearFails = () => {
        localStorage.removeItem(FAIL_KEY);
        localStorage.removeItem(LOCK_KEY);
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await api.post('/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });
            clearFails();
            login(response.data.access_token);
            navigate('/dashboard');
        } catch (err) {
            recordFail();
            setError('Credenziali non valide');
        } finally {
            setIsLoading(false);
        }
    };

    const isLocked = lockSecondsLeft > 0;
    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const iconClass = 'text-slate-400';
    const linkClass = isDark ? 'text-blue-400 hover:text-blue-300' : 'text-clinical-primary hover:text-blue-700';

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Clinical Twin</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Accesso riservato al personale medico autorizzato
                    </p>
                </div>

                {(error || isLocked) && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400 animate-in fade-in slide-in-from-top-2">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">
                            {isLocked ? `Riprova tra ${lockSecondsLeft}s...` : error}
                        </span>
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-5">
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Identificativo Medico
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <User className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="Inserisci il tuo username..."
                            />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="••••••••"
                            />
                        </div>
                        <div className="flex justify-end pt-1">
                            <Link to="/forgot-password" className={`text-xs font-medium ${linkClass}`}>
                                Password dimenticata?
                            </Link>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || isLocked || !username || !password}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                            ${isLoading || isLocked || !username || !password
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                            }`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Autenticazione...
                            </>
                        ) : (
                            'Accedi al Sistema'
                        )}
                    </button>
                </form>

                <p className={`text-center text-sm mt-6 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                    Prima volta?{' '}
                    <Link to="/register" className={`font-semibold ${linkClass}`}>
                        Richiedi accesso
                    </Link>
                </p>

                <p className={`text-center text-xs mt-6 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Progetto di Ricerca Accademica • Uso Esclusivo di Ricerca (RUO)
                </p>
            </div>
        </div>
    );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Login.jsx
git commit -m "feat(frontend): harden Login with lockout and add register/forgot-password links"
```

---

## Task 5: Create Register.jsx

**Files:**
- Create: `frontend/src/pages/Register.jsx`

- [ ] **Step 1: Create the file**

```jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, User, Mail, ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import api from '../services/api';

const checks = (pwd) => [
    { label: 'Minimo 8 caratteri', ok: pwd.length >= 8 },
    { label: 'Almeno una maiuscola', ok: /[A-Z]/.test(pwd) },
    { label: 'Almeno un numero', ok: /[0-9]/.test(pwd) },
];

export default function Register({ theme }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [usernameError, setUsernameError] = useState('');
    const navigate = useNavigate();

    const passwordChecks = checks(password);
    const allPasswordChecksOk = passwordChecks.every((c) => c.ok);
    const isFormValid =
        username.trim() &&
        password &&
        allPasswordChecksOk &&
        password === confirm;

    const handleRegister = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setUsernameError('');

        try {
            await api.post('/register', {
                username: username.trim(),
                password,
                email: email.trim() || undefined,
            });
            navigate('/login', { state: { message: 'Account creato. Accedi ora.' } });
        } catch (err) {
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            if (status === 400 && typeof detail === 'string' && detail.toLowerCase().includes('username')) {
                setUsernameError('Identificativo già in uso');
            } else if (status === 422 && detail) {
                const msg = Array.isArray(detail) ? detail[0]?.msg : detail;
                setError(msg || 'Dati non validi');
            } else {
                setError('Impossibile connettersi al server. Riprova più tardi.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const iconClass = 'text-slate-400';
    const linkClass = isDark
        ? 'text-blue-400 hover:text-blue-300'
        : 'text-clinical-primary hover:text-blue-700';

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Crea Account</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Registrazione personale medico
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400 animate-in fade-in slide-in-from-top-2">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">{error}</span>
                    </div>
                )}

                <form onSubmit={handleRegister} className="space-y-5">
                    {/* Username */}
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Identificativo Medico
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <User className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => { setUsername(e.target.value); setUsernameError(''); }}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass} ${usernameError ? 'border-red-400 focus:ring-red-400' : ''}`}
                                placeholder="es. dr.rossi"
                            />
                        </div>
                        {usernameError && (
                            <p className="text-xs text-red-500 font-medium pt-1 animate-in fade-in">{usernameError}</p>
                        )}
                    </div>

                    {/* Email */}
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Email <span className={`font-normal ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>(opzionale)</span>
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Mail className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="dr.rossi@ospedale.it"
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="••••••••"
                            />
                        </div>
                        {password && (
                            <ul className="pt-2 space-y-1">
                                {passwordChecks.map((c) => (
                                    <li key={c.label} className="flex items-center gap-2 text-xs" style={{ transition: 'color 0.2s' }}>
                                        {c.ok
                                            ? <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
                                            : <XCircle className="w-4 h-4 text-red-400 shrink-0" />}
                                        <span className={c.ok ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}>
                                            {c.label}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Confirm Password */}
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Conferma Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="password"
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass} ${confirm && password !== confirm ? 'border-red-400 focus:ring-red-400' : ''}`}
                                placeholder="••••••••"
                            />
                        </div>
                        {confirm && password !== confirm && (
                            <p className="text-xs text-red-500 font-medium pt-1 animate-in fade-in">Le password non coincidono</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !isFormValid}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                            ${isLoading || !isFormValid
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                            }`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Creazione account...
                            </>
                        ) : (
                            'Crea Account'
                        )}
                    </button>
                </form>

                <p className={`text-center text-sm mt-6 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                    Hai già un accesso?{' '}
                    <Link to="/login" className={`font-semibold ${linkClass}`}>
                        Accedi
                    </Link>
                </p>
            </div>
        </div>
    );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Register.jsx
git commit -m "feat(frontend): add Register page with real-time password validation"
```

---

## Task 6: Create ForgotPassword.jsx

**Files:**
- Create: `frontend/src/pages/ForgotPassword.jsx`

- [ ] **Step 1: Create the file**

```jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Mail } from 'lucide-react';
import api from '../services/api';

export default function ForgotPassword({ theme }) {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await api.post('/forgot-password', { email: email.trim() });
        } catch (_) {
            // Always show success to avoid email enumeration
        } finally {
            setIsLoading(false);
            setSubmitted(true);
        }
    };

    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const linkClass = isDark
        ? 'text-blue-400 hover:text-blue-300'
        : 'text-clinical-primary hover:text-blue-700';

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Password Dimenticata</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Inserisci l'email associata al tuo account
                    </p>
                </div>

                {submitted ? (
                    <div className="text-center space-y-4 animate-in fade-in">
                        <div className="p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl">
                            <p className={`text-sm font-medium ${isDark ? 'text-green-300' : 'text-green-700'}`}>
                                Se l'email è registrata riceverai le istruzioni entro pochi minuti.
                                Controlla anche la cartella spam.
                            </p>
                        </div>
                        <Link to="/login" className={`block text-sm font-semibold ${linkClass}`}>
                            Torna al login
                        </Link>
                    </div>
                ) : (
                    <>
                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="space-y-1">
                                <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                                    Email
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="w-5 h-5 text-slate-400" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                        placeholder="dr.rossi@ospedale.it"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading || !email.trim()}
                                className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                                    ${isLoading || !email.trim()
                                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                        : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                                    }`}
                            >
                                {isLoading ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Invio in corso...
                                    </>
                                ) : (
                                    'Invia Istruzioni'
                                )}
                            </button>
                        </form>

                        <p className={`text-center text-sm mt-6 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                            <Link to="/login" className={`font-semibold ${linkClass}`}>
                                Torna al login
                            </Link>
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/ForgotPassword.jsx
git commit -m "feat(frontend): add ForgotPassword page"
```

---

## Task 7: Create ResetPassword.jsx

**Files:**
- Create: `frontend/src/pages/ResetPassword.jsx`

- [ ] **Step 1: Create the file**

```jsx
import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Activity, Lock, CheckCircle2, XCircle, ShieldAlert } from 'lucide-react';
import api from '../services/api';

const checks = (pwd) => [
    { label: 'Minimo 8 caratteri', ok: pwd.length >= 8 },
    { label: 'Almeno una maiuscola', ok: /[A-Z]/.test(pwd) },
    { label: 'Almeno un numero', ok: /[0-9]/.test(pwd) },
];

export default function ResetPassword({ theme }) {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token') || '';

    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [tokenInvalid, setTokenInvalid] = useState(!token);
    const navigate = useNavigate();

    const passwordChecks = checks(password);
    const allOk = passwordChecks.every((c) => c.ok);
    const isFormValid = password && allOk && password === confirm;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        try {
            await api.post('/reset-password', { token, new_password: password });
            navigate('/login', { state: { message: 'Password aggiornata. Accedi con le nuove credenziali.' } });
        } catch (err) {
            const status = err.response?.status;
            if (status === 400) {
                setTokenInvalid(true);
            } else {
                setError('Impossibile connettersi al server. Riprova più tardi.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const linkClass = isDark
        ? 'text-blue-400 hover:text-blue-300'
        : 'text-clinical-primary hover:text-blue-700';

    if (tokenInvalid) {
        return (
            <div className={`min-h-screen flex items-center justify-center p-4 ${pageBgClass}`}>
                <div className={`w-full max-w-md p-8 rounded-2xl border text-center space-y-4 ${cardClass}`}>
                    <ShieldAlert className="w-12 h-12 text-red-400 mx-auto" />
                    <h2 className="text-xl font-bold">Link non valido o scaduto</h2>
                    <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Il link per il reset della password è scaduto o è già stato usato.
                    </p>
                    <Link to="/forgot-password" className={`block text-sm font-semibold ${linkClass}`}>
                        Richiedi un nuovo link
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Nuova Password</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Scegli una password sicura per il tuo account
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Nuova Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="w-5 h-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="••••••••"
                            />
                        </div>
                        {password && (
                            <ul className="pt-2 space-y-1">
                                {passwordChecks.map((c) => (
                                    <li key={c.label} className="flex items-center gap-2 text-xs" style={{ transition: 'color 0.2s' }}>
                                        {c.ok
                                            ? <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
                                            : <XCircle className="w-4 h-4 text-red-400 shrink-0" />}
                                        <span className={c.ok ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}>
                                            {c.label}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Conferma Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="w-5 h-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass} ${confirm && password !== confirm ? 'border-red-400 focus:ring-red-400' : ''}`}
                                placeholder="••••••••"
                            />
                        </div>
                        {confirm && password !== confirm && (
                            <p className="text-xs text-red-500 font-medium pt-1 animate-in fade-in">Le password non coincidono</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !isFormValid}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                            ${isLoading || !isFormValid
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                            }`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Aggiornamento...
                            </>
                        ) : (
                            'Aggiorna Accesso'
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/ResetPassword.jsx
git commit -m "feat(frontend): add ResetPassword page with token-from-URL flow"
```

---

## Task 8: Update App.jsx routing + Login state message

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/pages/Login.jsx` (add state-message banner)

- [ ] **Step 1: Update App.jsx**

Replace the contents of `frontend/src/App.jsx` with:

```jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './routes/ProtectedRoute';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

- [ ] **Step 2: Add success-message banner to Login.jsx**

In Login.jsx, add `useLocation` import:

```jsx
import { useNavigate, Link, useLocation } from 'react-router-dom';
```

Add near the top of the component:

```jsx
const location = useLocation();
const successMessage = location.state?.message || '';
```

Add the success banner just before the error banner (inside the JSX, before the `{(error || isLocked) && ...}` block):

```jsx
{successMessage && (
    <div className="mb-6 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl flex items-center gap-3 text-green-600 dark:text-green-400 animate-in fade-in slide-in-from-top-2">
        <CheckCircle2 className="w-5 h-5 shrink-0" />
        <span className="text-sm font-semibold">{successMessage}</span>
    </div>
)}
```

Also add `CheckCircle2` to the lucide-react import in Login.jsx:

```jsx
import { Activity, Lock, User, ShieldAlert, CheckCircle2 } from 'lucide-react';
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.jsx frontend/src/pages/Login.jsx
git commit -m "feat(frontend): add routing for register/forgot-password/reset-password and success banner on login"
```

---

## Task 9: Restart and smoke-test

- [ ] **Step 1: Restart modified containers**

```bash
docker compose restart api_gateway frontend
```

Wait ~10 seconds for services to come up.

- [ ] **Step 2: Verify backend endpoints**

```bash
# /register — should return 201
curl -s -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testdoc","password":"Doctor1234","email":"test@test.it"}' | jq

# /forgot-password — should return 200 with generic message
curl -s -X POST http://localhost:8000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.it"}' | jq

# Check docker logs for the reset token
docker compose logs api_gateway | grep "RESET TOKEN"
```

Expected output for register:
```json
{"id": 2, "username": "testdoc", "role": "user"}
```

Expected output for forgot-password:
```json
{"message": "Se l'email è registrata riceverai le istruzioni a breve."}
```

- [ ] **Step 3: Test each frontend page**

| URL | What to verify |
|-----|----------------|
| `http://localhost:5173/register` | Weak password → red X checks; strong password → green ticks; mismatched confirm → error; valid form → submit enabled |
| `http://localhost:5173/forgot-password` | Any email → form disappears, green success message appears |
| `http://localhost:5173/login` | "Password dimenticata?" link visible; "Richiedi accesso" link visible; 3 bad logins → 60s countdown; correct login → dashboard |
| `http://localhost:5173/reset-password` (no token) | "Link non valido" screen shown immediately |
| `/reset-password?token=<value from logs>` | Form shown; valid password → redirect to login with success message |

- [ ] **Step 4: Register a duplicate username**

Visit `/register`, enter the same `testdoc` username → should show "Identificativo già in uso" under the username field.
