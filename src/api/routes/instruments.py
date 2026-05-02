from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.instrument import Instrument
from src.models.instrument_history import InstrumentHistory
from src.models.mqtt_scan_trace import MqttScanTrace
from src.models.room import Room
from src.services.errors import ConflictError, InvalidTransitionError, NotFoundError, ValidationError
from src.services.event_service import log_movement_event
from src.services.instrument_service import register_instrument, soft_delete_instrument

router = APIRouter(prefix="/instruments", tags=["instruments"])


# ---------- response schemas ----------

class InstrumentOut(BaseModel):
    id: int
    name: str
    rfid: str
    current_room: int
    status: str
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    model_config = {"from_attributes": True}


class InstrumentListOut(BaseModel):
    id: int
    rfid: str
    name: str
    status: str
    location: str | None
    updated_at: datetime | None


class HistoryEntryOut(BaseModel):
    id: int
    event_type: str
    recorded_at: datetime
    notes: str | None


class RecentScanOut(BaseModel):
    id: int
    device_id: str
    room: str
    received_at: datetime


class InstrumentDetailOut(BaseModel):
    id: int
    rfid: str
    name: str
    status: str
    location: str | None
    updated_at: datetime | None
    lifecycle_history: list[HistoryEntryOut]
    recent_scans: list[RecentScanOut]


# ---------- request schemas ----------

class InstrumentCreateIn(BaseModel):
    name: str
    rfid: str
    room_id: int | None = None
    location: str | None = None
    status: str = "available"


class RetireIn(BaseModel):
    notes: str | None = None


class TransferIn(BaseModel):
    to_room_id: int
    actor: str = "system"
    reason: str | None = None


# ---------- helpers ----------

def _get_room_name(db: Session, room_id: int | None, cache: dict) -> str | None:
    if room_id is None:
        return None
    if room_id not in cache:
        room = db.query(Room).filter(Room.id == room_id).first()
        cache[room_id] = room.name if room else None
    return cache[room_id]


def _latest_history_at(db: Session, instrument_id: int) -> datetime | None:
    row = (
        db.query(InstrumentHistory)
        .filter(InstrumentHistory.instrument_id == instrument_id)
        .order_by(InstrumentHistory.created_at.desc())
        .first()
    )
    return row.created_at if row else None


# ---------- routes ----------

@router.get("/", response_model=list[InstrumentListOut])
def list_instruments(db: Session = Depends(get_db)):
    instruments = (
        db.query(Instrument).filter(Instrument.deleted_at.is_(None)).all()
    )
    room_cache: dict[int, str | None] = {}
    result = []
    for instr in instruments:
        location = _get_room_name(db, instr.current_room, room_cache)
        updated_at = _latest_history_at(db, instr.id)
        result.append(
            InstrumentListOut(
                id=instr.id,
                rfid=instr.rfid,
                name=instr.name,
                status=instr.status,
                location=location,
                updated_at=updated_at,
            )
        )
    return result


@router.post("/", response_model=InstrumentOut, status_code=201)
def create_instrument(body: InstrumentCreateIn, actor: str = "system", db: Session = Depends(get_db)):
    room_id = body.room_id

    if room_id is None and body.location:
        room = (
            db.query(Room)
            .filter(Room.name == body.location, Room.deleted_at.is_(None))
            .first()
        )
        if room:
            room_id = room.id

    if room_id is None:
        first_room = db.query(Room).filter(Room.deleted_at.is_(None)).first()
        if first_room:
            room_id = first_room.id

    payload = {
        "name": body.name,
        "rfid": body.rfid,
        "room_id": room_id,
        "status": body.status.lower(),
    }

    try:
        instrument = register_instrument(db, payload, actor)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return instrument


@router.get("/{instrument_id}", response_model=InstrumentOut)
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):
    instrument = (
        db.query(Instrument)
        .filter(Instrument.id == instrument_id, Instrument.deleted_at.is_(None))
        .first()
    )
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {instrument_id} not found")
    return instrument


@router.get("/{instrument_id}/detail", response_model=InstrumentDetailOut)
def get_instrument_detail(instrument_id: int, db: Session = Depends(get_db)):
    instrument = (
        db.query(Instrument)
        .filter(Instrument.id == instrument_id, Instrument.deleted_at.is_(None))
        .first()
    )
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {instrument_id} not found")

    room_cache: dict[int, str | None] = {}
    location = _get_room_name(db, instrument.current_room, room_cache)

    history = (
        db.query(InstrumentHistory)
        .filter(InstrumentHistory.instrument_id == instrument_id)
        .order_by(InstrumentHistory.created_at.desc())
        .all()
    )
    updated_at = history[0].created_at if history else None

    lifecycle_history = [
        HistoryEntryOut(
            id=h.id,
            event_type=h.event_type,
            recorded_at=h.created_at,
            notes=h.extra.get("reason") if h.extra else None,
        )
        for h in history
    ]

    scan_traces = (
        db.query(MqttScanTrace)
        .filter(MqttScanTrace.rfid_uid == instrument.rfid)
        .order_by(MqttScanTrace.backend_received_at.desc())
        .limit(50)
        .all()
    )

    recent_scans = []
    for t in scan_traces:
        room_name = _get_room_name(db, t.to_room_id, room_cache) or "Unknown"
        recent_scans.append(
            RecentScanOut(
                id=t.id,
                device_id=t.device_mac,
                room=room_name,
                received_at=t.backend_received_at,
            )
        )

    return InstrumentDetailOut(
        id=instrument.id,
        rfid=instrument.rfid,
        name=instrument.name,
        status=instrument.status,
        location=location,
        updated_at=updated_at,
        lifecycle_history=lifecycle_history,
        recent_scans=recent_scans,
    )


@router.post("/{instrument_id}/retire", response_model=InstrumentOut)
def retire_instrument(
    instrument_id: int,
    body: RetireIn,
    actor: str = "system",
    db: Session = Depends(get_db),
):
    try:
        instrument = soft_delete_instrument(db, instrument_id, actor, body.notes)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return instrument


@router.post("/{instrument_id}/transfer", response_model=InstrumentOut)
def transfer_instrument(
    instrument_id: int,
    body: TransferIn,
    db: Session = Depends(get_db),
):
    instrument = (
        db.query(Instrument)
        .filter(Instrument.id == instrument_id, Instrument.deleted_at.is_(None))
        .first()
    )
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {instrument_id} not found")

    try:
        log_movement_event(
            db,
            instrument_id=instrument_id,
            from_room_id=instrument.current_room,
            to_room_id=body.to_room_id,
            actor=body.actor,
            reason=body.reason,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db.refresh(instrument)
    return instrument


@router.delete("/{instrument_id}", response_model=InstrumentOut)
def delete_instrument(
    instrument_id: int, actor: str = "system", reason: str | None = None, db: Session = Depends(get_db)
):
    try:
        instrument = soft_delete_instrument(db, instrument_id, actor, reason)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return instrument
