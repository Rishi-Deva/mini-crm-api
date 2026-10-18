from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    name: str
    phone: str | None = None


class ClientOut(ClientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DealStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    closed = "closed"


class DealCreate(BaseModel):
    client_id: int
    title: str
    amount: float = Field(default=0, ge=0)
    status: DealStatus = DealStatus.new


class DealOut(DealCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
