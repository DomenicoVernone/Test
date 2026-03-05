from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # L'email o l'ID del medico
    username = Column(String, unique=True, index=True, nullable=False)
    # NON salveremo mai la password in chiaro, ma solo l'hash (Bcrypt)
    hashed_password = Column(String, nullable=False)

    