"""ORM Dictator module."""

DICTATOR = {}


def set(key, value):
    """Set a key in the Dictator."""
    global DICTATOR
    DICTATOR[key] = value


def soft_set(key, value):
    """Set a key in the Dictator only if it doesn't exist."""
    global DICTATOR
    DICTATOR.setdefault(key, value)


def get(key, default=None):
    """Get a key from the Dictator.

    :return: The value if it exists, default otherwise.
    """
    return DICTATOR[key] if key in DICTATOR else default
