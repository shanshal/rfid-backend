from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.enums import EventType, InstrumentStatus
from src.models.instrument import Instrument
from src.models.room import Room
from src.services.audit_service import write_audit_event
from src.services.errors import ConflictError, NotFoundError, ValidationError


def register_instrument(db: Session, payload: dict, actor: str) -> Instrument:
    name = payload.get("name")
    rfid = payload.get("rfid")
    room_id = payload.get("room_id")
    status = payload.get("status", InstrumentStatus.AVAILABLE)

    if not name or not rfid or room_id is None:
        raise ValidationError("name, rfid, and room_id are required")

    try:
        InstrumentStatus(status)
    except ValueError:
        raise ValidationError(f"Invalid status: {status}")

    existing = db.query(Instrument).filter(Instrument.rfid == rfid).first()
    if existing:
        raise ConflictError(f"RFID '{rfid}' is already in use")

    room = db.query(Room).filter(Room.id == room_id, Room.deleted_at.is_(None)).first()
    if not room:
        raise NotFoundError(f"Room {room_id} not found")

    instrument = Instrument(
        name=name,
        rfid=rfid,
        current_room=room_id,
        status=status,
    )
    db.add(instrument)
    db.flush()

    write_audit_event(
        db,
        event_type=EventType.CREATED,
        actor=actor,
        payload={"instrument_id": instrument.id, "rfid": rfid, "room_id": room_id},
    )
    db.commit()
    return instrument


def soft_delete_instrument(
    db: Session, instrument_id: int, actor: str, reason: str | None = None
) -> Instrument:
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not instrument:
        raise NotFoundError(f"Instrument {instrument_id} not found")

    if instrument.deleted_at is not None:
        raise ConflictError(f"Instrument {instrument_id} is already deleted")

    instrument.deleted_at = datetime.now(timezone.utc)
    instrument.deleted_by = actor
    db.flush()

    write_audit_event(
        db,
        event_type=EventType.DELETED,
        actor=actor,
        payload={"instrument_id": instrument_id, "reason": reason},
    )
    db.commit()
    return instrument
