from datetime import datetime

from pydantic import BaseModel


class MovementCreate(BaseModel):
    instrument_id: int
    from_room_id: int | None = None
    to_room_id: int
    actor: str
    reason: str | None = None
    procedure_id: int | None = None


class MovementOut(BaseModel):
    id: int
    instrument_id: int
    from_room_id: int | None = None
    to_room_id: int | None = None
    from_status: str | None = None
    to_status: str | None = None
    event_type: str
    created_at: datetime
    extra: dict | None = None

    model_config = {"from_attributes": True}
