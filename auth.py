from fastapi import FastAPI

app = FastAPI()


@app.get("/api/auth")
async def get_user():
    return {"user": "Authenticated User"}
