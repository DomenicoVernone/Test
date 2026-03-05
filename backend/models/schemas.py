from pydantic import BaseModel

# Modello per i dati in ingresso durante la registrazione
class UserCreate(BaseModel):
    username: str
    password: str

# Modello per i dati in uscita (NON restituiamo mai la password!)
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # Permette a Pydantic di leggere gli oggetti SQLAlchemy

# Modello per la risposta del Login (il Token JWT)
class Token(BaseModel):
    access_token: str
    token_type: str