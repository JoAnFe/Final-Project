from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def encode_jwt(sub: str) -> str:
    payload = {"sub": sub, "exp": datetime.utcnow()+timedelta(hours=8)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

def require_user(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")