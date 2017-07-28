from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from oslo_db.sqlalchemy import models
import logging

LOG = logging.getLogger(__name__)


class UUIDBaseModel(models.ModelBase):

    """Base class from UUID models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}


class UUID(declarative_base(), UUIDBaseModel):
    __tablename__ = 'uuids'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True)
    uuid_type = Column(String, nullable=True, unique=True)
