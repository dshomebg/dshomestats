from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db import Base, engine, get_db
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from app.auth import get_current_user, get_password_hash, authenticate_user, create_access_token

app = FastAPI(
    title="FastAPI",
    description="Само 1 админ и 1 юзер, без регистрация.",
    version="0.1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# --- Initial users (admin and user) ---
def create_initial_users():
    db = next(get_db())
    admin = db.query(User).filter(User.username == "admin").first()
    user = db.query(User).filter(User.username == "user").first()
    changed = False
    if not admin:
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_admin=True
        )
        db.add(admin)
        changed = True
    if not user:
        user = User(
            username="user",
            hashed_password=get_password_hash("user123"),
            is_admin=False
        )
        db.add(user)
        changed = True
    if changed:
        db.commit()

create_initial_users()

# --- Login endpoint ---
@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Public endpoint (everyone can access) ---
@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Admin-only endpoint example ---
@app.get("/admin/users", response_model=list[UserOut])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only!")
    return db.query(User).all()
