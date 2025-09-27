from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    class Config:
        orm_mode = True

class TrafficBase(BaseModel):
    year: int
    month: int
    organic: int = 0
    brand: int = 0
    facebook: int = 0
    facebook_paid: int = 0
    google_paid: int = 0
    other: int = 0

class TrafficCreate(TrafficBase):
    pass

class TrafficOut(TrafficBase):
    id: int
    class Config:
        orm_mode = True
