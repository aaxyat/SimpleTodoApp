from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from models import models
from database.database import SessionLocal
from starlette import status
from .auth import get_current_user


router = APIRouter(
    prefix="/api/todos",
    tags=["todos"]
)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depends = Annotated[Session, Depends(get_db)]
user_depends = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):

    title: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(ge=1, le=5)
    completed: bool

# Get Routes


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_depends, db: db_depends):

    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todos = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_depends, db: db_depends, todo_id: int = Path(ge=1)):

    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).filter(
        models.Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model

# Post Routes


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_todo(user: user_depends, db: db_depends, todo: TodoRequest):

    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = models.Todos(**todo.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


# Put Routes

@router.put("update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_by_id(user: user_depends,
                            db: db_depends,
                            todo_request: TodoRequest,
                            todo_id: int = Path(ge=1)):

    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).filter(
        models.Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()


# Delete Routes
@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(user: user_depends, db: db_depends, todo_id: int = Path(ge=1)):

    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).filter(
        models.Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
