"""
Modulo di Sicurezza.
Centralizza l'hashing delle password (Bcrypt), la generazione dei token JWT
e le dipendenze per l'autorizzazione (guardie per le rotte protette).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import User

# Inizializza l'algoritmo di hashing bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Specifica a FastAPI dove si trova la rotta di login (usata per Swagger e validazione)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica che la password in chiaro corrisponda all'hash salvato nel DB."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera l'hash bcrypt per una nuova password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un nuovo token JWT firmato con la SECRET_KEY centralizzata."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Middleware di Autenticazione.
    Intercetta il token JWT dalla richiesta HTTP, lo decodifica e restituisce l'utente.
    Se il token è invalido, scaduto o l'utente non esiste, blocca la richiesta (401).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o token scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user