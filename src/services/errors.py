class DomainError(Exception):
    # TODO: Base exception for service-layer business errors.
    pass


class NotFoundError(DomainError):
    # TODO: Raise when required entity is missing.
    pass


class ConflictError(DomainError):
    # TODO: Raise on uniqueness and conflicting state.
    pass


class InvalidTransitionError(DomainError):
    # TODO: Raise when status/room transition is not allowed.
    pass


class ValidationError(DomainError):
    # TODO: Raise on invalid payload/domain fields.
    pass
