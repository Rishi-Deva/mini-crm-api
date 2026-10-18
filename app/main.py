from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .db import Base, engine, get_db

Base.metadata.create_all(engine)
app = FastAPI(title="Mini CRM")


def get_or_404(db: Session, client_id: int) -> models.Client:
    client = db.get(models.Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.post("/clients", response_model=schemas.ClientOut, status_code=201)
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = models.Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.get("/clients", response_model=list[schemas.ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.scalars(select(models.Client)).all()


@app.put("/clients/{client_id}", response_model=schemas.ClientOut)
def update_client(
    client_id: int, data: schemas.ClientCreate, db: Session = Depends(get_db)
):
    client = get_or_404(db, client_id)
    client.name = data.name
    client.phone = data.phone
    db.commit()
    db.refresh(client)
    return client


@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, client_id))
    db.commit()
