from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.models import User
from app.auth import get_current_user

app = FastAPI()

# Позволи заявки от всички адреси (или само от твоите)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Може да сложиш само твоя домейн/IP за по-голяма сигурност
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }
