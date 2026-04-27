from sqlalchemy.orm import Session

from src.models.enums import ALLOWED_STATUS_TRANSITIONS, InstrumentStatus
from src.models.instrument_history import InstrumentHistory
from src.models.procedure_step import ProcedureStep
from src.models.room_requirement import RoomRequirement
from src.services.errors import InvalidTransitionError, ValidationError


def validate_status_transition(current_status: str, next_status: str) -> None:
    try:
        current = InstrumentStatus(current_status)
    except ValueError:
        raise ValidationError(f"Unknown status: {current_status}")

    try:
        next_s = InstrumentStatus(next_status)
    except ValueError:
        raise ValidationError(f"Unknown status: {next_status}")

    allowed = ALLOWED_STATUS_TRANSITIONS[current]
    if next_s not in allowed:
        raise InvalidTransitionError(
            f"Transition from '{current}' to '{next_s}' is not allowed"
        )


def validate_room_transition(
    db: Session,
    instrument_id: int,
    instrument_status: str,
    from_room_id: int | None,
    to_room_id: int,
    procedure_id: int | None = None,
) -> None:
    requirements = (
        db.query(RoomRequirement)
        .filter(RoomRequirement.room_id == to_room_id)
        .order_by(RoomRequirement.priority)
        .all()
    )

    for req in requirements:
        if req.requirement_type == "status" and req.is_blocking:
            if instrument_status != req.requirement_value:
                raise InvalidTransitionError(
                    f"Room {to_room_id} requires status '{req.requirement_value}', "
                    f"instrument has '{instrument_status}'"
                )

    if procedure_id is not None:
        steps = (
            db.query(ProcedureStep)
            .filter(
                ProcedureStep.procedure_id == procedure_id,
                ProcedureStep.room_id == to_room_id,
            )
            .first()
        )

        if steps is None:
            raise InvalidTransitionError(
                f"Room {to_room_id} is not part of procedure {procedure_id}"
            )

        prior_steps = (
            db.query(ProcedureStep)
            .filter(
                ProcedureStep.procedure_id == procedure_id,
                ProcedureStep.step_order < steps.step_order,
            )
            .order_by(ProcedureStep.step_order)
            .all()
        )

        for prior in prior_steps:
            visited = (
                db.query(InstrumentHistory)
                .filter(
                    InstrumentHistory.instrument_id == instrument_id,
                    InstrumentHistory.to_room_id == prior.room_id,
                )
                .first()
            )
            if visited is None:
                raise InvalidTransitionError(
                    f"Instrument {instrument_id} must visit room {prior.room_id} "
                    f"(step {prior.step_order}) before room {to_room_id}"
                )
