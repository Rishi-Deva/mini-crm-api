from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    name: str
    phone: str | None = None


class ClientOut(ClientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
