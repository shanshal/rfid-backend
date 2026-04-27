from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.instrument import Instrument
from src.schemas.instrument import InstrumentCreate, InstrumentOut
from src.services.errors import ConflictError, NotFoundError, ValidationError
from src.services.instrument_service import register_instrument, soft_delete_instrument

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.post("/", response_model=InstrumentOut, status_code=201)
def create_instrument(body: InstrumentCreate, actor: str, db: Session = Depends(get_db)):
    payload = body.model_dump()
    try:
        instrument = register_instrument(db, payload, actor)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return instrument


@router.get("/", response_model=list[InstrumentOut])
def list_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).filter(Instrument.deleted_at.is_(None)).all()


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


@router.delete("/{instrument_id}", response_model=InstrumentOut)
def delete_instrument(
    instrument_id: int, actor: str, reason: str | None = None, db: Session = Depends(get_db)
):
    try:
        instrument = soft_delete_instrument(db, instrument_id, actor, reason)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return instrument
