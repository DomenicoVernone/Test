import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


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


class RegisterResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)
