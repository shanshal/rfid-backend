from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ScanEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=200)
    device_mac: str = Field(min_length=1, max_length=64)
    rfid_uid: str = Field(min_length=1, max_length=64)
    scanned_at: datetime | None = None


class StatusEvent(BaseModel):
    device_mac: str = Field(min_length=1, max_length=64)
    status: Literal["online", "alive", "offline"]
    uptime_ms: int | None = None
    rssi: int | None = None
    firmware: str | None = None
    at: datetime | None = None
