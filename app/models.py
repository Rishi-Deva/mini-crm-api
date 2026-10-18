from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30), default=None)
