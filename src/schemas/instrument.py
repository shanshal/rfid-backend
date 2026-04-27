from datetime import datetime

from pydantic import BaseModel

from src.models.enums import InstrumentStatus


class InstrumentCreate(BaseModel):
    name: str
    rfid: str
    room_id: int
    status: InstrumentStatus = InstrumentStatus.AVAILABLE


class InstrumentOut(BaseModel):
    id: int
    name: str
    rfid: str
    current_room: int
    status: str
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    model_config = {"from_attributes": True}
