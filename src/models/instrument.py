from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base
from src.models.enums import InstrumentStatus


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    rfid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    current_room: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default=InstrumentStatus.AVAILABLE, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    deleted_by: Mapped[str | None] = mapped_column(String(100), default=None)
