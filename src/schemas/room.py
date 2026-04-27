from datetime import datetime

from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str


class RoomUpdate(BaseModel):
    id: int
    name: str


class RoomOut(BaseModel):
    id: int
    name: str
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    model_config = {"from_attributes": True}


class RoomRequirementIn(BaseModel):
    requirement_type: str
    requirement_value: str
    is_blocking: bool = True
    priority: int = 0


class RoomRequirementOut(BaseModel):
    id: int
    room_id: int
    requirement_type: str
    requirement_value: str
    is_blocking: bool
    priority: int

    model_config = {"from_attributes": True}
