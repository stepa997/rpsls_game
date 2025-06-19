from fastapi import APIRouter, Depends, HTTPException, status, Request
from auth.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from db.get_db import get_db_from_env
from db.models import User
from schemas.models import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

get_session = get_db_from_env()


@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate):
    with get_session() as session:
        if session.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@router.post("/login")
def login(user: UserLogin, request: Request):
    with get_session() as session:
        db_user = session.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        request.session["user"] = {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "is_admin": db_user.is_admin,
        }

        token = create_access_token({"sub": str(db_user.id)})
        return {
            "access_token": token,
            "token_type": "bearer",
            "is_admin": db_user.is_admin,
        }


@router.get("/guest")
def guest_login():
    guest_data = {"sub": "guest"}
    token = create_access_token(guest_data)
    return {"access_token": token, "token_type": "bearer", "guest": True}


@router.get("/me")
def get_me(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
