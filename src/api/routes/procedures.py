from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.procedure import Procedure
from src.models.procedure_step import ProcedureStep
from src.schemas.procedure import ProcedureCreate, ProcedureOut, ProcedureStepOut
from src.services.errors import NotFoundError, ValidationError
from src.services.room_service import set_procedure_order

router = APIRouter(prefix="/procedures", tags=["procedures"])


@router.post("/", response_model=ProcedureOut, status_code=201)
def create_procedure(body: ProcedureCreate, actor: str, db: Session = Depends(get_db)):
    procedure_payload = {
        "name": body.name,
        "description": body.description,
        "is_active": body.is_active,
    }
    try:
        procedure = set_procedure_order(db, procedure_payload, body.room_ids, actor)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return procedure


@router.get("/", response_model=list[ProcedureOut])
def list_procedures(db: Session = Depends(get_db)):
    return db.query(Procedure).filter(Procedure.deleted_at.is_(None)).all()


@router.get("/{procedure_id}", response_model=ProcedureOut)
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    procedure = (
        db.query(Procedure)
        .filter(Procedure.id == procedure_id, Procedure.deleted_at.is_(None))
        .first()
    )
    if not procedure:
        raise HTTPException(status_code=404, detail=f"Procedure {procedure_id} not found")
    return procedure


@router.get("/{procedure_id}/steps", response_model=list[ProcedureStepOut])
def get_procedure_steps(procedure_id: int, db: Session = Depends(get_db)):
    procedure = (
        db.query(Procedure)
        .filter(Procedure.id == procedure_id, Procedure.deleted_at.is_(None))
        .first()
    )
    if not procedure:
        raise HTTPException(status_code=404, detail=f"Procedure {procedure_id} not found")
    return (
        db.query(ProcedureStep)
        .filter(ProcedureStep.procedure_id == procedure_id)
        .order_by(ProcedureStep.step_order)
        .all()
    )
