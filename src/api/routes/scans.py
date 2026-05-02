from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.instrument import Instrument
from src.models.mqtt_scan_trace import MqttScanTrace
from src.models.room import Room

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanOut(BaseModel):
    id: int
    rfid_tag: str | None
    instrument: str
    room: str
    timestamp: datetime | None


@router.get("/", response_model=list[ScanOut])
def list_scans(
    limit: int = Query(default=200, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    traces = (
        db.query(MqttScanTrace)
        .order_by(MqttScanTrace.backend_received_at.desc())
        .limit(limit)
        .all()
    )

    instrument_cache: dict[int, Instrument | None] = {}
    room_cache: dict[int, str | None] = {}

    def room_name_for(room_id: int | None) -> str | None:
        if room_id is None:
            return None
        if room_id not in room_cache:
            row = db.query(Room).filter(Room.id == room_id).first()
            room_cache[room_id] = row.name if row else None
        return room_cache[room_id]

    results = []
    for trace in traces:
        instrument_name = "Unknown"
        if trace.instrument_id:
            if trace.instrument_id not in instrument_cache:
                instrument_cache[trace.instrument_id] = (
                    db.query(Instrument)
                    .filter(Instrument.id == trace.instrument_id)
                    .first()
                )
            instr = instrument_cache[trace.instrument_id]
            if instr:
                instrument_name = instr.name

        # Prefer where the scan happened (to_room_id), then current room, else Unknown.
        room_name = room_name_for(trace.to_room_id)
        if room_name is None and trace.instrument_id:
            instr = instrument_cache.get(trace.instrument_id)
            if instr:
                room_name = room_name_for(instr.current_room)
        if room_name is None:
            room_name = "Unknown"

        results.append(
            ScanOut(
                id=trace.id,
                rfid_tag=trace.rfid_uid,
                instrument=instrument_name,
                room=room_name,
                timestamp=trace.scanned_at or trace.backend_received_at,
            )
        )

    return results
