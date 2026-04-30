from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.mqtt_scan_trace import MqttScanTrace
from src.schemas.device import DeviceAssignRoomIn, DeviceOut, DeviceRegisterIn
from src.schemas.diagnostics import ScanTraceOut
from src.services.device_service import (
    assign_device_room,
    get_device,
    list_devices,
    list_pending_devices,
    register_device,
)
from src.services.errors import NotFoundError

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/", response_model=list[DeviceOut])
def get_devices(db: Session = Depends(get_db)):
    return list_devices(db)


@router.post("/register", response_model=DeviceOut, status_code=201)
def create_or_update_device(body: DeviceRegisterIn, actor: str, db: Session = Depends(get_db)):
    try:
        return register_device(
            db,
            mac_address=body.mac_address,
            actor=actor,
            name=body.name,
            room_id=body.room_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pending", response_model=list[DeviceOut])
def get_pending_devices(db: Session = Depends(get_db)):
    return list_pending_devices(db)


@router.get("/{device_id}", response_model=DeviceOut)
def get_device_by_id(device_id: int, db: Session = Depends(get_db)):
    try:
        return get_device(db, device_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{device_id}/logs", response_model=list[ScanTraceOut])
def get_device_logs(device_id: int, limit: int = 100, db: Session = Depends(get_db)):
    try:
        device = get_device(db, device_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    safe_limit = max(1, min(limit, 500))
    return (
        db.query(MqttScanTrace)
        .filter(MqttScanTrace.device_mac == device.mac_address)
        .order_by(MqttScanTrace.backend_received_at.desc())
        .limit(safe_limit)
        .all()
    )


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
