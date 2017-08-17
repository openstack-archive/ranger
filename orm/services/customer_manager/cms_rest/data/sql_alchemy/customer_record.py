from __builtin__ import int

from sqlalchemy import func

from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import (CmsUser, Customer,
                                                                            CustomerMetadata, CustomerRegion,
                                                                            Region, UserRole)
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class CustomerRecord:
    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__customers = Customer()
        # self.setRecordData(self.__customers)
        # self.__customers.Clear()
        self.__TableName = "customer"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def customer(self):
        return self.__customer

    @customer.setter
    def customer(self, customer):
        self.__customer = customer

    def insert(self, customer):
        try:
            self.session.add(customer)
        except Exception as exception:
            LOG.log_exception("Failed to insert Customer" + str(customer), exception)
            # LOG.error("Failed to insert customer" + str(customer) + " Exception:" + str(exception))
            raise

    def delete_by_primary_key(self, customer_id):
        result = self.session.connection().execute("delete from customer where id = %d" % (customer_id))
        return result

    def read_by_primary_key(self):
        return self.read_customer(self.__customer.id)

    def read_customer(self, customer_id):
        try:
            customer = self.session.query(Customer).filter(Customer.id == customer_id)
            return customer.first()

        except Exception as exception:
            message = "Failed to read_customer:customer_id: %d " % (customer_id)
            LOG.log_exception(message, exception)
            raise

    def read_customer_by_uuid(self, customer_uuid):
        try:
            customer = self.session.query(Customer).filter(Customer.uuid == customer_uuid)
            return customer.first()

        except Exception as exception:
            message = "Failed to read_customer:customer_uuid: %d " % customer_uuid
            LOG.log_exception(message, exception)
            raise

    def get_customer_id_from_uuid(self, uuid):
        result = self.session.connection().scalar("SELECT id from customer WHERE uuid = \"%s\"" % uuid)

        if result:
            return int(result)
        else:
            return None

    def delete_customer_by_uuid(self, uuid):
        try:
            result = self.session.query(Customer).filter(
                Customer.uuid == uuid).delete()
            return result

        except Exception as exception:
            message = "Failed to delete_customer_by_uuid: uuid: {0}".format(uuid)
            LOG.log_exception(message, exception)
            raise

    def _build_meta_query(self, metadata):
        """build query for having list of metadata
        get list of keys and list of values quereis
        :param metadata:
        :return:
        """
        metadata_values = [value.split(':')[1] for value in metadata if
                           ':' in value]
        query = [CustomerMetadata.field_key.in_(
            [key.split(':')[0] if ':' in key else key for key in metadata])]
        # check if search by only keys ..
        if metadata_values:
            query.append(CustomerMetadata.field_value.in_(
                [value.split(':')[1] if ':' in value else '' for value in
                 metadata]))
        return query

    def get_customers_by_criteria(self, **criteria):

        try:
            LOG.info("get_customers_by_criteria: criteria: {0}".format(criteria))
            region = criteria['region'] if 'region' in criteria else None
            user = criteria['user'] if 'user' in criteria else None
            rgroup = criteria['rgroup'] if 'rgroup' in criteria else None
            starts_with = criteria['starts_with'] if 'starts_with' in criteria else None
            contains = criteria['contains'] if 'contains' in criteria else None
            metadata = criteria['metadata'] if 'metadata' in criteria else None

            query = self.session.query(Customer)

            if metadata:
                query = query.join(CustomerMetadata).filter(
                    *self._build_meta_query(metadata)).group_by(
                    CustomerMetadata.customer_id).having(
                    func.count() == len(metadata))

            if starts_with:
                query = query.filter(
                    Customer.name.ilike("{}%".format(starts_with)))

            if contains:
                query = query.filter(
                    Customer.name.ilike("%{}%".format(contains)))

            if region:
                query = query.join(CustomerRegion).filter(CustomerRegion.customer_id == Customer.id)
                query = query.join(Region).filter(Region.id == CustomerRegion.region_id, Region.type == 'single', Region.name == region)

                if user:
                    query = query.join(UserRole, UserRole.customer_id == Customer.id).filter(UserRole.region_id == Region.id)
                    query = query.join(CmsUser).filter(CmsUser.id == UserRole.user_id, CmsUser.name == user)
            elif user:
                query = query.join(UserRole, UserRole.customer_id == Customer.id)
                query = query.join(CmsUser).filter(CmsUser.id == UserRole.user_id, CmsUser.name == user)

            if rgroup:
                if not region:  # avoid same CustomerRegion join twice
                    query = query.join(CustomerRegion).filter(CustomerRegion.customer_id == Customer.id)

                query = query.join(Region).filter(Region.id == CustomerRegion.region_id, Region.type == 'group', Region.name == rgroup)

                if user:
                    query = query.join(UserRole, UserRole.customer_id == Customer.id).filter(
                        UserRole.region_id == Region.id)
                    query = query.join(CmsUser).filter(CmsUser.id == UserRole.user_id, CmsUser.name == user)

            query = self.customise_query(query, criteria)
            return query.all()

        except Exception as exception:
            message = "Failed to get_customers_by_criteria: criteria: {0}".format(criteria)
            LOG.log_exception(message, exception)
            raise

    def customise_query(self, query, kw):
        start = int(kw['start']) if 'start' in kw else 0
        limit = int(kw['limit']) if 'limit' in kw else 0

        if start > 0:
            query = query.offset(start)

        if limit > 0:
            query = query.limit(limit)

        print str(query)
        return query
