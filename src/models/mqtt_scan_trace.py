from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class MqttScanTrace(Base):
    __tablename__ = "mqtt_scan_traces"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(200), index=True)
    device_mac: Mapped[str] = mapped_column(String(64), index=True)
    rfid_uid: Mapped[str | None] = mapped_column(String(64), default=None)
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    backend_received_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    handler_started_at: Mapped[datetime] = mapped_column(DateTime)
    handler_finished_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    outcome: Mapped[str] = mapped_column(String(64), index=True)
    instrument_id: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    from_room_id: Mapped[int | None] = mapped_column(Integer, default=None)
    to_room_id: Mapped[int | None] = mapped_column(Integer, default=None)
    error_code: Mapped[str | None] = mapped_column(String(64), default=None)
    error_detail: Mapped[str | None] = mapped_column(String(500), default=None)
    raw_topic: Mapped[str] = mapped_column(String(255))
    raw_payload: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
