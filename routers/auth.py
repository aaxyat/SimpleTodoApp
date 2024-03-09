from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models import models
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import dotenv

environ = dotenv.dotenv_values()

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = environ.get("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class CreateUserRequest(BaseModel):
    """
    Represents a request to create a new user.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The password of the user.
        role (str): The role of the user.
    """
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    """
    Represents a token object.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token.
    """
    access_token: str
    token_type: str


def get_db():
    """
    Returns a database session.

    Yields:
        SessionLocal: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depends = Annotated[Session, Depends(get_db)]


def is_user_authenticated(username: str, password: str, db: Session):
    """
    Check if the user is authenticated by verifying the provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        db (Session): The database session.

    Returns:
        Union[models.Users, bool]: The authenticated user object if authentication is successful,
        otherwise False.
    """
    user = db.query(models.Users).filter(
        models.Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    """
    Creates an access token for the given username and user ID.

    Args:
        username (str): The username of the user.
        user_id (int): The ID of the user.
        expires_delta (timedelta): The time delta for the token expiration.

    Returns:
        str: The generated access token.
    """
    encode = {
        "sub": username,
        "id": user_id
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Retrieves the current user based on the provided authentication token.

    Args:
        token (str): The authentication token.

    Returns:
        dict: A dictionary containing the username and user ID of the current user.

    Raises:
        HTTPException: If the authentication credentials are invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_depends,
                      create_user_request: CreateUserRequest):
    """
    Creates a new user.

    Args:
        db (Session): The database session.
        create_user_request (CreateUserRequest): The request body containing the user details.

    Returns:
        None
    """
    create_user_model = models.Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_depends):
    """
    Authenticates a user and generates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Database): The database connection.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    user = is_user_authenticated(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Couldn't Validate User.")
    token = create_access_token(
        user.username, user.id, timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer"}
