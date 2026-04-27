from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas.device import DeviceAssignRoomIn, DeviceOut
from src.services.device_service import assign_device_room, get_device, list_devices, list_pending_devices
from src.services.errors import NotFoundError

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/", response_model=list[DeviceOut])
def get_devices(db: Session = Depends(get_db)):
    return list_devices(db)


@router.get("/pending", response_model=list[DeviceOut])
def get_pending_devices(db: Session = Depends(get_db)):
    return list_pending_devices(db)


@router.get("/{device_id}", response_model=DeviceOut)
def get_device_by_id(device_id: int, db: Session = Depends(get_db)):
    try:
        return get_device(db, device_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{device_id}/assign-room", response_model=DeviceOut)
def assign_room(
    device_id: int,
    body: DeviceAssignRoomIn,
    actor: str,
    db: Session = Depends(get_db),
):
    try:
        return assign_device_room(
            db,
            device_id=device_id,
            room_id=body.room_id,
            actor=actor,
            name=body.name,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
