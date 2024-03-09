from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from models import models
from database.database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depends = Annotated[Session, Depends(get_db)]
user_depends = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_depends, db: db_depends):

    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todos = db.query(models.Todos).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos


@router.delete("/todo/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(user: user_depends, db: db_depends, todo_id: int = Path(ge=1)):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
