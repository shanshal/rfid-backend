from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base

class InstrumentHistory(Base):
    __tablename__ = "instrument_history"

    # Table: instrument_history
    # Properties:
    # - id: primary key
    # - instrument_id: foreign key to instruments
    # - from_room_id: optional source room foreign key
    # - to_room_id: optional destination room foreign key
    # - from_status: previous status
    # - to_status: new status
    # - event_type: event category
    # - created_at: UTC timestamp
    # - metadata: optional JSON details

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)

    # TODO: Instrument history is append-only event logging.
    # TODO: Store UTC timestamps for all events.
    # TODO: Track transitions with constrained status changes.
