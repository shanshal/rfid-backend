from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base

class Instrument(Base):
    __tablename__ = "instruments"

    # Table: instruments
    # Properties:
    # - id: primary key
    # - name: human-readable instrument name
    # - rfid: required unique RFID identifier
    # - room_id: current location (foreign key to rooms)
    # - status: enum with constrained transitions
    # - deleted_at: soft delete timestamp

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    rfid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # TODO: RFID is required at creation time and must be unique per instrument.
    # TODO: Current location is a room foreign key only (no sub-locations).
    # TODO: Status is an enum with constrained transitions.
    # TODO: Kits relation is many-to-many via a join/association table.
    # TODO: Soft delete applies to instruments to preserve traceability.
