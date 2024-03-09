from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from models import models
from database.database import SessionLocal
from starlette import status


router = APIRouter(
    prefix="/api/todos",
    tags=["todos"]
)


def get_db():
    """
    Returns a database session.

    Returns:
        SessionLocal: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depends = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    """
    Represents a request for creating a new todo item.

    Attributes:
        title (str): The title of the todo item. Must have a minimum length of 3 characters.
        description (str): The description of the todo item. Must have a minimum length of 1 character and a maximum length of 100 characters.
        priority (int): The priority of the todo item. Must be a value between 1 and 5 (inclusive).
        completed (bool): Indicates whether the todo item is completed or not.
    """
    title: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(ge=1, le=5)
    completed: bool

# Get Routes


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_depends):
    """
    Retrieve all todos from the database.

    Args:
        db: The database dependency.

    Returns:
        A list of all todos in the database.

    Raises:
        HTTPException: If no todos are found in the database.
    """
    if db.query(models.Todos).all() is None:
        raise HTTPException(status_code=404, detail="No todos found")
    return db.query(models.Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_depends, todo_id: int = Path(ge=1)):
    """
    Retrieve a todo item by its ID.

    Parameters:
    - db: The database dependency.
    - todo_id: The ID of the todo item to retrieve.

    Returns:
    - The todo item with the specified ID.

    Raises:
    - HTTPException 404: If the todo item with the specified ID is not found.
    """
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model

# Post Routes


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_todo(db: db_depends, todo: TodoRequest):
    """
    Create a new todo item.

    Args:
        db (Database): The database dependency.
        todo (TodoRequest): The request body containing the todo item details.

    Returns:
        None

    Raises:
        None
    """
    todo_model = models.Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()


# Put Routes

@router.put("update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_by_id(db: db_depends,
                            todo_request: TodoRequest,
                            todo_id: int = Path(ge=1)):
    """
    Update a todo item by its ID.

    Args:
        db (Database): The database dependency.
        todo_request (TodoRequest): The updated todo item data.
        todo_id (int, optional): The ID of the todo item to be updated. Defaults to Path(ge=1).

    Raises:
        HTTPException: If the todo item with the given ID is not found.

    Returns:
        None
    """
    todo_model = db.query(models.Todos).filter(
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
async def delete_todo_by_id(db: db_depends, todo_id: int = Path(ge=1)):
    """
    Delete a todo by its ID.

    Args:
        db (Database): The database dependency.
        todo_id (int): The ID of the todo to be deleted.

    Raises:
        HTTPException: If the todo with the given ID is not found.

    Returns:
        None
    """
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
