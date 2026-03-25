# api_gateway/routers/auth.py
#
# Endpoint di autenticazione: registrazione (/signup) e login (/login).
# La registrazione non è esposta nel frontend — avviene solo via Swagger UI
# come scelta architetturale per sistemi SaMD: solo l'amministratore
# può creare nuovi account medico.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token
from models.domain import User
from models.schemas import UserCreate, UserResponse, Token

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username già registrato")

    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non validi",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
