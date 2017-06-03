"""Base model module."""
from wsme.rest.json import tojson
from wsme import types as wtypes


class Model(wtypes.DynamicBase):
    """Base class for IMS models."""

    def to_db_model(self):
        """Get the object's DB model."""
        raise NotImplementedError("This function was not implemented")

    def tojson(self):
        """Get the object's JSON representation."""
        return tojson(type(self), self)
