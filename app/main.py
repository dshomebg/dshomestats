from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import Base, engine, get_db
from app.models import User, Traffic
from app.schemas import UserOut, TrafficCreate, TrafficOut
from app.auth import get_current_user

app = FastAPI(
    title="Traffic API",
    description="Модул за трафик с пера по месеци и години",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)

@app.post("/traffic", response_model=TrafficOut)
def upsert_traffic(item: TrafficCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admins only")
    traffic = db.query(Traffic).filter(Traffic.year==item.year, Traffic.month==item.month).first()
    if not traffic:
        traffic = Traffic(**item.dict())
        db.add(traffic)
    else:
        for key, value in item.dict().items():
            setattr(traffic, key, value)
    db.commit()
    db.refresh(traffic)
    return traffic

@app.get("/traffic", response_model=TrafficOut)
def get_traffic(year: int, month: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    traffic = db.query(Traffic).filter(Traffic.year==year, Traffic.month==month).first()
    if not traffic:
        raise HTTPException(404, "No data for this period")
    return traffic

@app.get("/traffic/all", response_model=List[TrafficOut])
def get_all_traffic(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Traffic).order_by(Traffic.year, Traffic.month).all()
