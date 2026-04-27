from datetime import datetime, timezone

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class InstrumentHistory(Base):
    __tablename__ = "instrument_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    from_room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), default=None)
    to_room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), default=None)
    from_status: Mapped[str | None] = mapped_column(String(50), default=None)
    to_status: Mapped[str | None] = mapped_column(String(50), default=None)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    extra: Mapped[dict | None] = mapped_column(JSON, default=None)
