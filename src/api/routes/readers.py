from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.room import Room
from src.services.device_service import list_devices, register_device
from src.services.errors import NotFoundError

router = APIRouter(prefix="/readers", tags=["readers"])


class ReaderOut(BaseModel):
    id: int
    device_id: str
    name: str
    location: str | None
    event_type: str | None
    active: bool
    last_seen_at: datetime | None


class ReaderCreate(BaseModel):
    device_id: str
    name: str | None = None
    location: str | None = None


def _make_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@router.get("/", response_model=list[ReaderOut])
def list_readers(db: Session = Depends(get_db)):
    devices = list_devices(db)
    now = datetime.now(timezone.utc)

    result = []
    room_cache: dict[int, Room] = {}
    for device in devices:
        room_name = None
        if device.room_id:
            if device.room_id not in room_cache:
                room_cache[device.room_id] = (
                    db.query(Room).filter(Room.id == device.room_id).first()
                )
            room = room_cache[device.room_id]
            if room:
                room_name = room.name

        last_activity = _make_aware(device.last_activity_at)
        active = last_activity is not None and (now - last_activity).total_seconds() < 30

        result.append(
            ReaderOut(
                id=device.id,
                device_id=device.mac_address,
                name=device.name,
                location=room_name,
                event_type=None,
                active=active,
                last_seen_at=last_activity,
            )
        )
    return result


@router.post("/", response_model=ReaderOut, status_code=201)
def create_reader(body: ReaderCreate, actor: str = "system", db: Session = Depends(get_db)):
    room_id = None
    room_name = None
    if body.location:
        room = (
            db.query(Room)
            .filter(Room.name == body.location, Room.deleted_at.is_(None))
            .first()
        )
        if room:
            room_id = room.id
            room_name = room.name

    try:
        device = register_device(
            db,
            mac_address=body.device_id,
            actor=actor,
            name=body.name,
            room_id=room_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    now = datetime.now(timezone.utc)
    last_activity = _make_aware(device.last_activity_at)
    active = last_activity is not None and (now - last_activity).total_seconds() < 30

    return ReaderOut(
        id=device.id,
        device_id=device.mac_address,
        name=device.name,
        location=room_name,
        event_type=None,
        active=active,
        last_seen_at=last_activity,
    )
