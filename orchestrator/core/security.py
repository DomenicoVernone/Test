# orchestrator/core/security.py
#
# Validazione leggera del token JWT: decodifica e verifica la firma
# usando la SECRET_KEY condivisa con api_gateway, senza replicare
# la logica di login. L'autenticazione vera e propria è delegata
# all'api_gateway — questo servizio si limita a verificare i token.

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import User

# tokenUrl punta all'api_gateway — usato da Swagger UI per il flusso OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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