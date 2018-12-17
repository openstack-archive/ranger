from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import Region
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class RegionRecord:

    def __init__(self, session=None):

        # this model uses for the parameters for any access methods - not as instance of record in the table
        self.__region = Region()
        # self.setRecordData(self.region)
        # self.region.Clear()

        self.__TableName = "cms_region"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, region):
        self.__region = region

    def insert(self, region):
        try:
            self.session.add(region)
        except Exception as exception:
            LOG.log_exception("Failed to insert region" + str(region), exception)
            raise

    def get_region_id_from_name(self, region_name):
        result = self.session.connection().scalar("SELECT id from cms_region WHERE name = \"{}\"".format(region_name))  # nosec
        if result is not None:
            return int(result)
        return result
