from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class RoomRequirement(Base):
    __tablename__ = "room_requirements"

    # Table: room_requirements
    # Properties:
    # - id: primary key
    # - room_id: foreign key to rooms.id
    # - requirement_type: requirement category (sterilized, approved_device, etc.)
    # - requirement_value: requirement content/value
    # - is_blocking: whether failure blocks transition
    # - priority: evaluation order

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    requirement_type: Mapped[str] = mapped_column(String(100), index=True)
    requirement_value: Mapped[str] = mapped_column(String(255))

    # TODO: Add is_blocking and priority columns.
