from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_current_user, router as auth_router
from .db import Base, engine, get_db

Base.metadata.create_all(engine)
app = FastAPI(title="Mini CRM")
app.include_router(auth_router)
protected = [Depends(get_current_user)]


def get_client_or_404(db: Session, client_id: int) -> models.Client:
    client = db.get(models.Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def get_deal_or_404(db: Session, deal_id: int) -> models.Deal:
    deal = db.get(models.Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


# ---------- Clients ----------


@app.post("/clients", response_model=schemas.ClientOut, status_code=201, dependencies=protected)
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = models.Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.get("/clients", response_model=list[schemas.ClientOut], dependencies=protected)
def list_clients(db: Session = Depends(get_db)):
    return db.scalars(select(models.Client)).all()


@app.put("/clients/{client_id}", response_model=schemas.ClientOut, dependencies=protected)
def update_client(
    client_id: int, data: schemas.ClientCreate, db: Session = Depends(get_db)
):
    client = get_client_or_404(db, client_id)
    client.name = data.name
    client.phone = data.phone
    db.commit()
    db.refresh(client)
    return client


@app.delete("/clients/{client_id}", status_code=204, dependencies=protected)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = get_client_or_404(db, client_id)
    has_deals = db.scalars(
        select(models.Deal).where(models.Deal.client_id == client_id)
    ).first()
    if has_deals:
        raise HTTPException(
            status_code=409, detail="Client has deals, delete them first"
        )
    db.delete(client)
    db.commit()


# ---------- Deals ----------


@app.post("/deals", response_model=schemas.DealOut, status_code=201, dependencies=protected)
def create_deal(data: schemas.DealCreate, db: Session = Depends(get_db)):
    get_client_or_404(db, data.client_id)
    deal = models.Deal(**data.model_dump(mode="json"))
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@app.get("/deals", response_model=list[schemas.DealOut], dependencies=protected)
def list_deals(
    status: schemas.DealStatus | None = None, db: Session = Depends(get_db)
):
    query = select(models.Deal)
    if status is not None:
        query = query.where(models.Deal.status == status.value)
    return db.scalars(query).all()


@app.put("/deals/{deal_id}", response_model=schemas.DealOut, dependencies=protected)
def update_deal(
    deal_id: int, data: schemas.DealCreate, db: Session = Depends(get_db)
):
    deal = get_deal_or_404(db, deal_id)
    get_client_or_404(db, data.client_id)
    for field, value in data.model_dump(mode="json").items():
        setattr(deal, field, value)
    db.commit()
    db.refresh(deal)
    return deal


@app.delete("/deals/{deal_id}", status_code=204, dependencies=protected)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    db.delete(get_deal_or_404(db, deal_id))
    db.commit()
