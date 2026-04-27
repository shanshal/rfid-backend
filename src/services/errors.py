class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class InvalidTransitionError(DomainError):
    pass


class ValidationError(DomainError):
    pass
