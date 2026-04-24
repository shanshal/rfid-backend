def validate_status_transition(current_status: str, next_status: str) -> None:
    # TODO:
    # 1) Define canonical status enum and allowed transition map.
    # 2) Reject unknown statuses.
    # 3) Reject disallowed transitions with domain exception.
    # 4) Allow no-op transitions only when explicitly requested.
    raise NotImplementedError


def validate_room_transition(
    instrument_id: int,
    from_room_id: int | None,
    to_room_id: int,
    procedure_id: int | None = None,
) -> None:
    # TODO:
    # 1) Validate destination room requirements.
    # 2) If procedure_id is set, enforce ordered room progression.
    # 3) Reject transitions that skip required procedure steps.
    # 4) Return cleanly when transition is valid.
    raise NotImplementedError
