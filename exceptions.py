"""
Custom application exceptions.

Raise AppError anywhere in the codebase instead of returning None or
letting generic Python errors bubble up. The global handler in main.py
will catch it and return a clean, consistent JSON error response.

Usage:
    raise AppError(404, "Item not found", "No item with id 99 exists")
    raise AppError(409, "Conflict", "An item with that name already exists")
    raise AppError(400, "Bad Request", "Price must be a positive number")
"""

from fastapi import status


class AppError(Exception):
    """
    Raise this instead of HTTPException throughout the app.

    Args:
        status_code: HTTP status code (e.g. 404, 400, 409)
        error:       Short error type label  (e.g. "Not Found", "Conflict")
        detail:      Human-readable message  (e.g. "Item with id 5 not found")
    """

    def __init__(self, status_code: int, error: str, detail: str) -> None:
        self.status_code = status_code
        self.error = error
        self.detail = detail
        super().__init__(detail)


# ── Convenience factory methods ───────────────────────────────────────────

def not_found(resource: str, identifier) -> AppError:
    """Return a ready-to-raise 404 AppError."""
    return AppError(
        status_code=status.HTTP_404_NOT_FOUND,
        error="Not Found",
        detail=f"{resource} with id {identifier} not found",
    )


def conflict(detail: str) -> AppError:
    """Return a ready-to-raise 409 AppError."""
    return AppError(
        status_code=status.HTTP_409_CONFLICT,
        error="Conflict",
        detail=detail,
    )


def bad_request(detail: str) -> AppError:
    """Return a ready-to-raise 400 AppError."""
    return AppError(
        status_code=status.HTTP_400_BAD_REQUEST,
        error="Bad Request",
        detail=detail,
    )
