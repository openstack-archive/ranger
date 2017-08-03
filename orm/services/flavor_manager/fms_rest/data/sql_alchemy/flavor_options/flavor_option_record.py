from fms_rest.data.sql_alchemy.db_models import FlavorOption
from fms_rest.logger import get_logger
from sqlalchemy import and_

LOG = get_logger(__name__)


class FlavorOptionRecord:
    def __init__(self, session):

        # this model is uses only for the parameters of access mothods,
        # not an instance of model in the database
        self.__flavor_option = FlavorOption()
        # self.setRecordData(self.__flavor_option)
        # self.__flavor_option.Clear()
        self.__TableName = "flavor_option"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor_option(self):
        return self.__flavor_option

    @flavor_option.setter
    def flavor_option(self, flavor_option):
        self.__flavor_option = flavor_option

    def insert(self, flavor_option):
        try:
            self.session.add(flavor_option)
        except Exception as exception:
            LOG.log_exception("Failed to insert FlavorOption" +
                              str(flavor_option), exception)
            raise

    def get_flavor_option(self, flavor_internal_id, key_name):
        try:
            flavor_option = self.session.query(FlavorOption).filter(
                and_(FlavorOption.flavor_internal_id == flavor_internal_id,
                     FlavorOption.key_name == key_name))
            return flavor_option.first()

        except Exception as exception:
            message = "Failed to get_flavor_option:flavor_internal_id:" \
                      "{0}, key_name {1}".format(flavor_internal_id, key_name)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_option_by_flavor_internal_id(self, flavor_internal_id):
        try:
            flavor_option = self.session.query(FlavorOption).filter(
                FlavorOption.flavor_internal_id == flavor_internal_id)
            return flavor_option.all()

        except Exception as exception:
            message = "Failed to " \
                      "get_flavor_option_by_flavor_internal_id:" \
                      "flavor_internal_id: {0}".format(flavor_internal_id)
            LOG.log_exception(message, exception)
            raise
