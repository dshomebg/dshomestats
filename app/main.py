from fastapi import FastAPI, Depends
from app.db import Base, engine, get_db
from app.models import User
from app.auth import get_current_user

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }
