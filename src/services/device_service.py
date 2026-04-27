from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.device import Device
from src.models.room import Room
from src.services.audit_service import write_audit_event
from src.services.errors import NotFoundError


def normalize_mac_address(mac_address: str) -> str:
    return mac_address.strip().upper()


def get_or_create_pending_device(db: Session, mac_address: str) -> tuple[Device, bool]:
    normalized = normalize_mac_address(mac_address)
    device = (
        db.query(Device)
        .filter(func.lower(Device.mac_address) == normalized.lower())
        .first()
    )
    if device:
        return device, False

    device = Device(name=f"Scanner-{normalized}", mac_address=normalized, room_id=None)
    db.add(device)
    db.flush()
    write_audit_event(
        db,
        event_type="device_discovered",
        actor=f"scanner:{normalized}",
        payload={"device_id": device.id, "mac_address": normalized},
    )
    return device, True


def list_devices(db: Session) -> list[Device]:
    return db.query(Device).order_by(Device.id.desc()).all()


def list_pending_devices(db: Session) -> list[Device]:
    return db.query(Device).filter(Device.room_id.is_(None)).order_by(Device.id.desc()).all()


def get_device(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise NotFoundError(f"Device {device_id} not found")
    return device


def assign_device_room(
    db: Session,
    device_id: int,
    room_id: int,
    actor: str,
    name: str | None = None,
) -> Device:
    device = get_device(db, device_id)
    room = db.query(Room).filter(Room.id == room_id, Room.deleted_at.is_(None)).first()
    if not room:
        raise NotFoundError(f"Room {room_id} not found")

    device.room_id = room_id
    if name:
        device.name = name
    db.flush()

    write_audit_event(
        db,
        event_type="device_room_assigned",
        actor=actor,
        payload={"device_id": device.id, "room_id": room_id},
    )
    db.commit()
    return device
