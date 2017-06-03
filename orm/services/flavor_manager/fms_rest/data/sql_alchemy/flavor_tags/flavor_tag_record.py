from sqlalchemy import and_
from fms_rest.data.sql_alchemy.db_models import FlavorTag

from fms_rest.logger import get_logger

LOG = get_logger(__name__)


class FlavorTagRecord:
    def __init__(self, session):

        # this model is uses only for the parameters of access mothods,
        # not an instance of model in the database
        self.__flavor_tag = FlavorTag()
        # self.setRecordData(self.FlavorTag)
        # self.__flavorTag.Clear()
        self.__TableName = "flavor_extra_spec"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor_extra_spec(self):
        return self.__flavor_tag

    @flavor_extra_spec.setter
    def flavor_extra_spec(self, flavor_tag):
        self.__flavor_tag = flavor_tag

    def insert(self, flavor_tag):
        try:
            self.session.add(flavor_tag)
        except Exception as exception:
            LOG.log_exception("Failed to insert FlavorTag" +
                              str(flavor_tag), exception)
            raise

    def get_flavor_extra_spec(self, flavor_internal_id, key_name):
        try:
            flavor_extra_spec = self.session.query(FlavorTag).filter(
                and_(FlavorTag.flavor_internal_id == flavor_internal_id,
                     FlavorTag.key_name == key_name))
            return flavor_extra_spec.first()

        except Exception as exception:
            message = "Failed to get_flavor_extra_spec:flavor_internal_id:" \
                      "{0}, key_name {1}".format(flavor_internal_id, key_name)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_tag_by_flavor_internal_id(self, flavor_internal_id):
        try:
            flavor_tag = self.session.query(FlavorTag).filter(
                FlavorTag.flavor_internal_id == flavor_internal_id)
            return flavor_tag.all()

        except Exception as exception:
            message = "Failed to " \
                      "get_flavor_tag_by_flavor_internal_id:" \
                      "flavor_internal_id: {0}".format(flavor_internal_id)
            LOG.log_exception(message, exception)
            raise
