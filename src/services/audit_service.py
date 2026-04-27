from sqlalchemy.orm import Session

from src.models.audit_event import AuditEvent


def write_audit_event(db: Session, event_type: str, actor: str, payload: dict) -> AuditEvent:
    event = AuditEvent(event_type=event_type, actor=actor, payload=payload)
    db.add(event)
    db.flush()
    return event
