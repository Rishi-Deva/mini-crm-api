import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .db import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)


def make_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, ALGORITHM)


@router.post("/register", status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalars(
        select(models.User).where(models.User.username == data.username)
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Username already taken")
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    db.add(models.User(username=data.username, password_hash=hashed))
    db.commit()
    return {"username": data.username}


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.scalars(
        select(models.User).where(models.User.username == form.username)
    ).first()
    if user is None or not bcrypt.checkpw(
        form.password.encode(), user.password_hash.encode()
    ):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"access_token": make_token(user.username), "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2), db: Session = Depends(get_db)
) -> models.User:
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.scalars(
        select(models.User).where(models.User.username == username)
    ).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
