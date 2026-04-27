from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.room import Room
from src.schemas.room import (
    RoomCreate,
    RoomOut,
    RoomRequirementIn,
    RoomRequirementOut,
    RoomUpdate,
)
from src.services.errors import NotFoundError, ValidationError
from src.services.room_service import define_room, set_room_requirements

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomOut, status_code=201)
def create_room(body: RoomCreate, actor: str, db: Session = Depends(get_db)):
    payload = body.model_dump()
    try:
        room = define_room(db, payload, actor)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return room


@router.put("/", response_model=RoomOut)
def update_room(body: RoomUpdate, actor: str, db: Session = Depends(get_db)):
    payload = body.model_dump()
    try:
        room = define_room(db, payload, actor)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return room


@router.get("/", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(Room).filter(Room.deleted_at.is_(None)).all()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id, Room.deleted_at.is_(None)).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return room


@router.put("/{room_id}/requirements", response_model=list[RoomRequirementOut])
def update_room_requirements(
    room_id: int,
    body: list[RoomRequirementIn],
    actor: str,
    db: Session = Depends(get_db),
):
    requirements = [r.model_dump() for r in body]
    try:
        rows = set_room_requirements(db, room_id, requirements, actor)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return rows
