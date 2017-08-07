from cms_rest.data.sql_alchemy.models import Region
from cms_rest.logger import get_logger

LOG = get_logger(__name__)


class RegionRecord:

    def __init__(self, session=None):

        # this model uses for the parameters for any access methods - not as instance of record in the table
        self.__region = Region()
        # self.setRecordData(self.region)
        # self.region.Clear()

        self.__TableName = "region"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, region):
        self.__regionn = region

    def insert(self, region):
        try:
            self.session.add(region)
        except Exception as exception:
            LOG.log_exception("Failed to insert region" + str(region), exception)
            raise

    def get_region_id_from_name(self, region_name):
        result = self.session.connection().scalar("SELECT id from region WHERE name = \"%s\"" % (region_name))
        if result is not None:
            return int(result)
        return result
