from sqlalchemy.orm import Session

from src.models.enums import EventType
from src.models.instrument import Instrument
from src.models.instrument_history import InstrumentHistory
from src.models.room import Room
from src.services.audit_service import write_audit_event
from src.services.errors import NotFoundError
from src.services.transition_service import validate_room_transition


def log_movement_event(
    db: Session,
    instrument_id: int,
    from_room_id: int | None,
    to_room_id: int,
    actor: str,
    reason: str | None = None,
    procedure_id: int | None = None,
) -> InstrumentHistory:
    instrument = (
        db.query(Instrument)
        .filter(Instrument.id == instrument_id, Instrument.deleted_at.is_(None))
        .first()
    )
    if not instrument:
        raise NotFoundError(f"Instrument {instrument_id} not found")

    room = db.query(Room).filter(Room.id == to_room_id, Room.deleted_at.is_(None)).first()
    if not room:
        raise NotFoundError(f"Room {to_room_id} not found")

    validate_room_transition(
        db=db,
        instrument_id=instrument_id,
        instrument_status=instrument.status,
        from_room_id=from_room_id,
        to_room_id=to_room_id,
        procedure_id=procedure_id,
    )

    history = InstrumentHistory(
        instrument_id=instrument_id,
        from_room_id=from_room_id,
        to_room_id=to_room_id,
        from_status=instrument.status,
        to_status=instrument.status,
        event_type=EventType.MOVED,
        extra={"reason": reason} if reason else None,
    )
    db.add(history)

    instrument.current_room = to_room_id
    db.flush()

    write_audit_event(
        db,
        event_type=EventType.MOVED,
        actor=actor,
        payload={
            "instrument_id": instrument_id,
            "from_room_id": from_room_id,
            "to_room_id": to_room_id,
        },
    )
    db.commit()
    return history
