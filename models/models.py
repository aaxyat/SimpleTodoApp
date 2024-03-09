from database.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Users(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address of the user.
        username (str): The username of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates whether the user is active or not.
        role (str): The role of the user in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    """
    Represents a todo item.

    Attributes:
        id (int): The unique identifier of the todo item.
        title (str): The title of the todo item.
        description (str): The description of the todo item.
        priority (int): The priority of the todo item.
        completed (bool): Indicates whether the todo item is completed or not.
        owner_id (int): The ID of the user who owns the todo item.
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
