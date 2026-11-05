class AuthError(Exception):
    """Raised when a request has no authenticated user."""


def require_auth(handler):
    def wrapped(request, db):
        if getattr(request, "user", None) is None:
            raise AuthError("authentication required")
        return handler(request, db)

    return wrapped
