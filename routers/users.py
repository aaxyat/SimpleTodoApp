from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from models import models
from database.database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext
import dotenv

environ = dotenv.dotenv_values()

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = environ.get("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

db_depends = Annotated[Session, Depends(get_db)]
user_depends = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6, max_length=50)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_depends, db: db_depends):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    usr = db.query(models.Users).filter(
        models.Users.id == user.get("id")).first()
    return ({
        "id": usr.id,
        "username": usr.username,
        "email": usr.email,
        "first_name": usr.first_name,
        "last_name": usr.last_name,
        "role": usr.role,
        "is_active": usr.is_active
    })


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_depends, db: db_depends, user_verification: UserVerification):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    usr = db.query(models.Users).filter(
        models.Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, usr.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Password")
    usr.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(usr)
    db.commit()
