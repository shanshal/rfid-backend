from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class Room(Base):
    __tablename__ = "rooms"

    # Table: rooms
    # Properties:
    # - id: primary key
    # - name: room name/label
    # - code: optional room code
    # - deleted_at: optional soft delete timestamp

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)

    # TODO: Instruments reference rooms as their current location.
    # TODO: No room sub-location model is planned.
    # TODO: A room can be linked to many devices.
    # TODO: Movement requirements are enforced through transition rules and event logs.
