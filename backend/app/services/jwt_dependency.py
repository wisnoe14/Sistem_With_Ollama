from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.jwt_service import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/endpoints/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
