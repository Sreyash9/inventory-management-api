class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class ConflictError(Exception):
    """Raised when a request would violate a uniqueness/business constraint."""


class ValidationError(Exception):
    """Raised when a request is well-formed but violates a business rule."""
