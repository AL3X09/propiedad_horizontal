from datetime import datetime, timedelta, timezone
import json
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from propiedad_horizontal.app.core.config import settings

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_minutes: Optional[int] = None, extra_claims: Optional[dict] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.JWT_EXPIRES_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None