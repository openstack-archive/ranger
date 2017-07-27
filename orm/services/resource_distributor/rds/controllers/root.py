"""controller moudle."""
from rds.controllers.v1 import root as v1


class RootController(object):
    """api controller."""

    v1 = v1.V1Controller()
