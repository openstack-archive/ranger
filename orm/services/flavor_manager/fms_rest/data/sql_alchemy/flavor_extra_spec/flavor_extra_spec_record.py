from fms_rest.data.sql_alchemy.db_models import FlavorExtraSpec
from fms_rest.logger import get_logger
from sqlalchemy import and_

LOG = get_logger(__name__)


class FlavorExtraSpecRecord:

    def __init__(self, session):

        # this model is uses only for the parameters of access mothods,
        # not an instance of model in the database
        self.__flavor_extra_specs = FlavorExtraSpec()
        # self.setRecordData(self.__flavorExtraSpecs)
        # self.__flavorExtraSpecs.Clear()
        self.__TableName = "flavor_extra_spec"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor_extra_spec(self):
        return self.__flavor_extra_specs

    @flavor_extra_spec.setter
    def flavor_extra_spec(self, flavor_extra_specs):
        self.__flavor_extra_specs = flavor_extra_specs

    def insert(self, flavor_extra_specs):
        try:
            self.session.add(flavor_extra_specs)
        except Exception as exception:
            LOG.log_exception("Failed to insert FlavorExtraSpec" +
                              str(flavor_extra_specs), exception)
            raise

    def get_flavor_extra_spec(self, flavor_internal_id, key_name):
        try:
            flavor_extra_spec = self.session.query(FlavorExtraSpec).filter(
                and_(FlavorExtraSpec.flavor_internal_id == flavor_internal_id,
                     FlavorExtraSpec.key_name == key_name))
            return flavor_extra_spec.first()

        except Exception as exception:
            message = "Failed to get_flavor_extra_spec:flavor_internal_id:" \
                      "{0}, key_name {1}".format(flavor_internal_id, key_name)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_extra_specs_by_flavor_internal_id(self, flavor_internal_id):
        try:
            flavor_extra_specs = self.session.query(FlavorExtraSpec).filter(
                FlavorExtraSpec.flavor_internal_id == flavor_internal_id)
            return flavor_extra_specs.all()

        except Exception as exception:
            message = "Failed to " \
                      "get_flavor_extra_specs_by_flavor_internal_id:" \
                      "flavor_internal_id: {0}".format(flavor_internal_id)
            LOG.log_exception(message, exception)
            raise
