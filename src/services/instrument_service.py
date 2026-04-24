from sqlalchemy.orm import Session


def register_instrument(db: Session, payload: dict, actor: str) -> None:
    # TODO:
    # 1) Validate payload shape (name, rfid, room_id, initial_status).
    # 2) Ensure RFID is present and globally unique.
    # 3) Ensure room exists and is active.
    # 4) Ensure initial status is valid.
    # 5) Create instrument row in a single transaction.
    # 6) Append creation event via audit/event service.
    # 7) Return created entity or identifier for route response.
    raise NotImplementedError


def soft_delete_instrument(db: Session, instrument_id: int, actor: str, reason: str | None = None) -> None:
    # TODO:
    # 1) Load instrument by id and reject if missing.
    # 2) Reject if already soft-deleted.
    # 3) Set deleted_at (UTC) and deleted_by.
    # 4) Persist update in transaction.
    # 5) Append deletion event with reason metadata.
    # 6) Ensure normal queries exclude soft-deleted records.
    raise NotImplementedError
