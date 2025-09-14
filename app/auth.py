from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.settings import settings
from app.database import get_db
from app import models

# ----------------- Password hashing -----------------
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)

# ----------------- JWT -----------------
# tokenUrl="" -> Swagger'da sadece Bearer token kutusu çıkar
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    """JWT access token üretir."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # sub her zaman string olmalı
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ----------------- Dependencies -----------------
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """JWT token'i çöz, DB'den user'i bul, geri döndür."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        uid: str | None = payload.get("sub")   # sub string olarak gelir
        if uid is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = db.query(models.User).filter(models.User.id == int(uid)).first()
    if not user:
        raise cred_exc
    return user

def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    """Sadece admin rolüne izin verir."""
    if user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
