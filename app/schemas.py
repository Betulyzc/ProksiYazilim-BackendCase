from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.models import UserRole, NoteStatus

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: UserRole = UserRole.AGENT  # default

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True  

class NoteCreateIn(BaseModel):
    raw_text: str = Field(min_length=1, max_length=10_000)

class NoteOut(BaseModel):
    id: int
    user_id: int
    raw_text: str
    summary: str | None
    status: NoteStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
