from wsme.rest.json import tojson
from wsme import types as wtypes


class Model(wtypes.DynamicBase):
    """Base class for FMS models.
    """

    def to_db_model(self):
        raise NotImplementedError("This function was not implemented")

    def tojson(self):
        return tojson(type(self), self)
