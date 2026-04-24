from sqlalchemy.orm import Session


def define_room(db: Session, payload: dict, actor: str) -> None:
    # TODO:
    # 1) Validate room payload (name/code/active flag).
    # 2) Create or update room record.
    # 3) Add audit event for room definition changes.
    # 4) Return room entity/data for API response.
    raise NotImplementedError


def set_room_requirements(db: Session, room_id: int, requirements: list[dict], actor: str) -> None:
    # TODO:
    # 1) Validate room exists and is active.
    # 2) Replace current room requirements (normalized rows) in one transaction.
    # 3) Validate requirement schema (type, value, order, blocking flag).
    # 4) Add audit event describing requirement updates.
    # 5) Return persisted requirement rows for API response.
    raise NotImplementedError


def set_procedure_order(
    db: Session,
    procedure_payload: dict,
    ordered_room_ids: list[int],
    actor: str,
) -> None:
    # TODO:
    # 1) Create or update procedure record.
    # 2) Validate all room ids exist and are active.
    # 3) Persist procedure_steps as ordered normalized rows.
    # 4) Enforce unique step order per procedure.
    # 5) Add audit event for procedure order changes.
    # 6) Return procedure with ordered steps.
    raise NotImplementedError
