from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.auth import verify_password
from app.services.jwt_service import create_access_token
from app.model.users import User
from app.database.database import get_db
from sqlalchemy.orm import Session
router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(users: UserLogin, db: Session = Depends(get_db)):
    db_iconnet = db.query(User).filter(User.email == users.email).first()
    if not db_iconnet or not verify_password(users.password, db_iconnet.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Create JWT token
    access_token = create_access_token({"sub": db_iconnet.email, "name": db_iconnet.name})
    return {
        "success": True,
        "name": getattr(db_iconnet, "name", ""),
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }
