from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.instrument_history import InstrumentHistory
from src.schemas.movement import MovementCreate, MovementOut
from src.services.errors import InvalidTransitionError, NotFoundError
from src.services.event_service import log_movement_event

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("/", response_model=MovementOut, status_code=201)
def create_movement(body: MovementCreate, db: Session = Depends(get_db)):
    try:
        history = log_movement_event(
            db,
            instrument_id=body.instrument_id,
            from_room_id=body.from_room_id,
            to_room_id=body.to_room_id,
            actor=body.actor,
            reason=body.reason,
            procedure_id=body.procedure_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return history


@router.get("/instrument/{instrument_id}", response_model=list[MovementOut])
def get_instrument_history(instrument_id: int, db: Session = Depends(get_db)):
    return (
        db.query(InstrumentHistory)
        .filter(InstrumentHistory.instrument_id == instrument_id)
        .order_by(InstrumentHistory.created_at.desc())
        .all()
    )
