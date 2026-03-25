# File: llm_service/core/security.py
#
# Validazione JWT per proteggere gli endpoint del servizio.
# Il token viene verificato localmente usando la SECRET_KEY condivisa con api_gateway:
# non è necessaria una chiamata HTTP al servizio di autenticazione per ogni request.

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.config import settings

# tokenUrl è usato solo da Swagger UI per il flusso OAuth2 interattivo
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.AUTH_SERVICE_URL + "/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
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
        return username
    except JWTError:
        raise credentials_exception