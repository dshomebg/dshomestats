from sqlalchemy import Column, Integer, String
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True)
    hashed_password = Column(String(128))
    is_admin = Column(Integer, default=0)

class Traffic(Base):
    __tablename__ = "traffic"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    organic = Column(Integer, default=0)
    brand = Column(Integer, default=0)
    facebook = Column(Integer, default=0)
    facebook_paid = Column(Integer, default=0)
    google_paid = Column(Integer, default=0)
    other = Column(Integer, default=0)
