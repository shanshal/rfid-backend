from enum import StrEnum


class InstrumentStatus(StrEnum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    STERILIZING = "sterilizing"
    CONTAMINATED = "contaminated"
    RETIRED = "retired"


ALLOWED_STATUS_TRANSITIONS: dict[InstrumentStatus, set[InstrumentStatus]] = {
    InstrumentStatus.AVAILABLE: {InstrumentStatus.IN_USE},
    InstrumentStatus.IN_USE: {InstrumentStatus.STERILIZING, InstrumentStatus.CONTAMINATED},
    InstrumentStatus.STERILIZING: {InstrumentStatus.AVAILABLE},
    InstrumentStatus.CONTAMINATED: {InstrumentStatus.RETIRED},
    InstrumentStatus.RETIRED: set(),
}


class EventType(StrEnum):
    CREATED = "created"
    MOVED = "moved"
    STATUS_CHANGED = "status_changed"
    DELETED = "deleted"
    ROOM_DEFINED = "room_defined"
    REQUIREMENTS_UPDATED = "requirements_updated"
    PROCEDURE_UPDATED = "procedure_updated"
