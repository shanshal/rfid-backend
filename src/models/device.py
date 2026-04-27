from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    mac_address: Mapped[str] = mapped_column(String(150), index=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(default=None)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), index=True, nullable=True)
