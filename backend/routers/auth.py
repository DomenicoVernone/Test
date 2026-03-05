from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token
from models.domain import User
from models.schemas import UserCreate, UserResponse, Token

# Creiamo un router specifico per l'autenticazione
router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuovo medico nel sistema."""
    
    # 1. Controlla se l'utente esiste già
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username o Email già registrata")
    
    # 2. Genera l'hash della password
    hashed_pw = get_password_hash(user.password)
    
    # 3. Salva nel database
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica un medico e restituisce un token JWT."""
    
    # 1. Cerca l'utente nel DB
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 2. Verifica la correttezza della password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non validi",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Genera il token JWT
    access_token = create_access_token(data={"sub": user.username})
    
    # FastAPI si aspetta esattamente questa struttura per lo standard OAuth2
    return {"access_token": access_token, "token_type": "bearer"}