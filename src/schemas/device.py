from datetime import datetime

from pydantic import BaseModel


class DeviceAssignRoomIn(BaseModel):
    room_id: int
    name: str | None = None


class DeviceOut(BaseModel):
    id: int
    name: str
    mac_address: str
    room_id: int | None = None
    last_activity_at: datetime | None = None

    model_config = {"from_attributes": True}
