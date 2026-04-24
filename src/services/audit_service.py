from sqlalchemy.orm import Session


def write_audit_event(db: Session, event_type: str, actor: str, payload: dict) -> None:
    # TODO:
    # 1) Normalize and validate event payload.
    # 2) Persist append-only audit row with UTC timestamp.
    # 3) Ensure this function can be reused by all services.
    # 4) Keep transaction behavior compatible with caller service.
    raise NotImplementedError
