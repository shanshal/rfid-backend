from enum import StrEnum


class InstrumentStatus(StrEnum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    STERILIZING = "sterilizing"
    CONTAMINATED = "contaminated"
    RETIRED = "retired"
