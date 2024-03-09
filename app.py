
from fastapi import FastAPI

from models import models
from database.database import engine
from routers import auth, todos, admin, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)
