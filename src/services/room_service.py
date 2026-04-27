from sqlalchemy.orm import Session

from src.models.enums import EventType
from src.models.procedure import Procedure
from src.models.procedure_step import ProcedureStep
from src.models.room import Room
from src.models.room_requirement import RoomRequirement
from src.services.audit_service import write_audit_event
from src.services.errors import NotFoundError, ValidationError


def define_room(db: Session, payload: dict, actor: str) -> Room:
    name = payload.get("name")
    if not name:
        raise ValidationError("Room name is required")

    room_id = payload.get("id")
    if room_id:
        room = db.query(Room).filter(Room.id == room_id, Room.deleted_at.is_(None)).first()
        if not room:
            raise NotFoundError(f"Room {room_id} not found")
        room.name = name
    else:
        room = Room(name=name)
        db.add(room)

    db.flush()

    write_audit_event(
        db,
        event_type=EventType.ROOM_DEFINED,
        actor=actor,
        payload={"room_id": room.id, "name": name},
    )
    db.commit()
    return room


def set_room_requirements(
    db: Session, room_id: int, requirements: list[dict], actor: str
) -> list[RoomRequirement]:
    room = db.query(Room).filter(Room.id == room_id, Room.deleted_at.is_(None)).first()
    if not room:
        raise NotFoundError(f"Room {room_id} not found")

    db.query(RoomRequirement).filter(RoomRequirement.room_id == room_id).delete()

    rows = []
    for req in requirements:
        req_type = req.get("requirement_type")
        req_value = req.get("requirement_value")
        if not req_type or not req_value:
            raise ValidationError("requirement_type and requirement_value are required")

        row = RoomRequirement(
            room_id=room_id,
            requirement_type=req_type,
            requirement_value=req_value,
            is_blocking=req.get("is_blocking", True),
            priority=req.get("priority", 0),
        )
        db.add(row)
        rows.append(row)

    db.flush()

    write_audit_event(
        db,
        event_type=EventType.REQUIREMENTS_UPDATED,
        actor=actor,
        payload={"room_id": room_id, "count": len(rows)},
    )
    db.commit()
    return rows


def set_procedure_order(
    db: Session,
    procedure_payload: dict,
    ordered_room_ids: list[int],
    actor: str,
) -> Procedure:
    name = procedure_payload.get("name")
    if not name:
        raise ValidationError("Procedure name is required")

    procedure = db.query(Procedure).filter(Procedure.name == name).first()
    if procedure:
        procedure.description = procedure_payload.get("description", procedure.description)
        procedure.is_active = procedure_payload.get("is_active", procedure.is_active)
    else:
        procedure = Procedure(
            name=name,
            description=procedure_payload.get("description"),
            is_active=procedure_payload.get("is_active", True),
        )
        db.add(procedure)
        db.flush()

    for rid in ordered_room_ids:
        room = db.query(Room).filter(Room.id == rid, Room.deleted_at.is_(None)).first()
        if not room:
            raise NotFoundError(f"Room {rid} not found")

    db.query(ProcedureStep).filter(ProcedureStep.procedure_id == procedure.id).delete()

    for order, rid in enumerate(ordered_room_ids, start=1):
        step = ProcedureStep(
            procedure_id=procedure.id,
            room_id=rid,
            step_order=order,
        )
        db.add(step)

    db.flush()

    write_audit_event(
        db,
        event_type=EventType.PROCEDURE_UPDATED,
        actor=actor,
        payload={
            "procedure_id": procedure.id,
            "name": name,
            "room_ids": ordered_room_ids,
        },
    )
    db.commit()
    return procedure
