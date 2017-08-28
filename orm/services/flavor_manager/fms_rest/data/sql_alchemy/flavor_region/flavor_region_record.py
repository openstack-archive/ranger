from orm.services.flavor_manager.fms_rest.data.sql_alchemy.db_models import FlavorRegion
from orm.services.flavor_manager.fms_rest.logger import get_logger
from sqlalchemy import and_

LOG = get_logger(__name__)


class FlavorRegionRecord:

    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__flavor_regions = FlavorRegion()
        # self.setRecordData(self.__flavor_regions)
        # self.__flavor_regions.Clear()
        self.__TableName = "flavor_region"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor_region(self):
        return self.__flavor_region

    @flavor_region.setter
    def flavor_region(self, flavor_region):
        self.__flavor_region = flavor_region

    def insert(self, flavor_region):
        try:
            self.session.add(flavor_region)
        except Exception as exception:
            LOG.log_exception("Failed to insert FlavorRegion" + str(flavor_region), exception)
            # LOG.error("Failed to insert flavor_region" + str(flavor_region) + " Exception:" + str(exception))
            raise

    def get_flavor_region(self, flavor_internal_id, region_name):
        try:
            flavor_region = self.session.query(FlavorRegion).filter(and_(FlavorRegion.flavor_internal_id == flavor_internal_id,
                                                                         FlavorRegion.region_name == region_name))
            return flavor_region.first()

        except Exception as exception:
            message = "Failed to get_flavor_region:flavor_internal_id: {0}, region_name {1}".format(flavor_internal_id, region_name)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_regions_by_flavor_internal_id(self, flavor_internal_id):
        try:
            flavor_regions = self.session.query(FlavorRegion).filter(FlavorRegion.flavor_internal_id == flavor_internal_id)
            return flavor_regions.all()

        except Exception as exception:
            message = "Failed to get_flavor_regions_by_flavor_internal_id: flavor_internal_id: {0}".format(flavor_internal_id)
            LOG.log_exception(message, exception)
            raise

#     12880 ProCG uses this line - don't edit it
