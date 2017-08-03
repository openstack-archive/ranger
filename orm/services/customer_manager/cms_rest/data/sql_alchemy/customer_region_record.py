from cms_rest.data.sql_alchemy.customer_record import CustomerRecord
from cms_rest.data.sql_alchemy.models import CustomerRegion
from cms_rest.data.sql_alchemy.region_record import RegionRecord
from cms_rest.logger import get_logger

LOG = get_logger(__name__)


class CustomerRegionRecord:
    def __init__(self, session):

        # thie model uses for the parameters for any acceess methods - not as instance of record in the table
        self.__customer_region = CustomerRegion()
        # self.setRecordData(self.__customers)
        # self.__customers.Clear()

        self.__TableName = "customer_region"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def customer_region(self):
        return self.__customer_region

    @customer_region.setter
    def customer_region(self):
        self.__customer_region = CustomerRegion()

    def insert(self, customer_region):
        try:
            self.session.add(customer_region)
        except Exception as exception:
            LOG.log_exception("Failed to insert customer_region" + str(customer_region), exception)
            raise

    def get_regions_for_customer(self, customer_uuid):
        customer_regions = []

        try:
            customer_record = CustomerRecord(self.session)
            customer_id = customer_record.get_customer_id_from_uuid(customer_uuid)
            query = self.session.query(CustomerRegion).filter(CustomerRegion.customer_id == customer_id)

            for customer_region in query.all():
                customer_regions.append(customer_region)
            return customer_regions

        except Exception as exception:
            message = "Failed to get_region_names_for_customer: %d" % (customer_id)
            LOG.log_exception(message, exception)
            raise

    def delete_region_for_customer(self, customer_id, region_name):
        # customer_id can be a uuid (type of string) or id (type of int)
        # if customer_id is uuid I get id from uuid and use the id in the next sql command
        if isinstance(customer_id, basestring):
            customer_record = CustomerRecord(self.session)
            customer_id = customer_record.get_customer_id_from_uuid(customer_id)
        # get region id by the name I got (region_name)
        region_record = RegionRecord(self.session)
        region_id = region_record.get_region_id_from_name(region_name)
        if region_id is None:
            raise ValueError(
                'region with the region name {0} not found'.format(
                    region_name))
        result = self.session.connection().execute(
            "delete from customer_region where customer_id = %d and region_id = %d" % (customer_id, region_id))
        self.session.flush()

        if result.rowcount == 0:
            LOG.warn('region with the region name {0} not found'.format(region_name))
            raise ValueError('region with the region name {0} not found'.format(region_name))

        LOG.debug("num records deleted: " + str(result.rowcount))
        return result

    def delete_all_regions_for_customer(self, customer_id):  # not including default region which is -1
        # customer_id can be a uuid (type of string) or id (type of int)
        # if customer_id is uuid I get id from uuid and use the id in the next sql command
        if isinstance(customer_id, basestring):
            customer_record = CustomerRecord(self.session)
            customer_id = customer_record.get_customer_id_from_uuid(customer_id)

        result = self.session.connection().execute(
            "delete from customer_region where customer_id = {} and region_id <> -1 ".format(customer_id))
        print "num records deleted from customer regions: " + str(result.rowcount)
        return result
