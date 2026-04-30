from datetime import datetime

from pydantic import BaseModel


class DeviceAssignRoomIn(BaseModel):
    room_id: int
    name: str | None = None


class DeviceRegisterIn(BaseModel):
    mac_address: str
    name: str | None = None
    room_id: int | None = None


class DeviceOut(BaseModel):
    id: int
    name: str
    mac_address: str
    room_id: int | None = None
    last_activity_at: datetime | None = None
    local_ip: str | None = None
    scan_topic: str | None = None
    status_topic: str | None = None
    mqtt_host: str | None = None
    mqtt_port: int | None = None
    firmware: str | None = None
    last_status: str | None = None

    model_config = {"from_attributes": True}
