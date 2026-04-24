from sqlalchemy.orm import Session


def log_movement_event(
    db: Session,
    instrument_id: int,
    from_room_id: int | None,
    to_room_id: int,
    actor: str,
    reason: str | None = None,
) -> None:
    # TODO:
    # 1) Validate instrument exists and is active.
    # 2) Validate destination room exists and is active.
    # 3) Validate movement is allowed by room requirements.
    # 4) Validate status transition constraints (if status changes with movement).
    # 5) Write append-only instrument_history event with UTC timestamp.
    # 6) Update instrument current room atomically with event insert.
    # 7) Return event id/data for route response.
    raise NotImplementedError
