from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class RoomRequirement(Base):
    __tablename__ = "room_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    requirement_type: Mapped[str] = mapped_column(String(100), index=True)
    requirement_value: Mapped[str] = mapped_column(String(255))
    is_blocking: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
