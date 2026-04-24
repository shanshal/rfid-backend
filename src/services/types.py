from dataclasses import dataclass
from datetime import datetime


@dataclass
class MovementContext:
    # TODO: Use this typed payload for room movement operations.
    instrument_id: int
    from_room_id: int | None
    to_room_id: int
    actor: str
    occurred_at: datetime | None = None


@dataclass
class ProcedureOrderInput:
    # TODO: Use this typed payload for procedure room-order setup.
    procedure_name: str
    room_ids: list[int]
