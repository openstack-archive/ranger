from cms_rest.data.sql_alchemy.models import *
from cms_rest.data.sql_alchemy.customer_record import CustomerRecord
from cms_rest.data.sql_alchemy.cms_user_record import CmsUserRecord
from cms_rest.data.sql_alchemy.region_record import RegionRecord
from cms_rest.logic.error_base import NotFound

from cms_rest.logger import get_logger
LOG = get_logger(__name__)


class UserRoleRecord:

    def __init__(self, session=None):

        # this model uses for the parameters for any access methods - not as instance of record in the table
        self.__user_role = UserRole()
        # self.setRecordData(self.user_role)
        # self.user_role.Clear()

        self.__TableName = "user_role"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def user_role(self):
        return self.__user_role

    @user_role.setter
    def user_role(self, user_role):
        self.__user_rolen = user_role

    def insert(self, user_role):
        try:
            self.session.add(user_role)
        except Exception as exception:
            LOG.log_exception("Failed to insert user_role" + str(user_role), exception)
            raise

    def delete_user_from_region(self, customer_id, region_id, user_id):
        # customer_id can be a uuid (type of string) or id (type of int)
        # if customer_id is uuid I get id from uuid and use the id in the next sql command
        if isinstance(customer_id, basestring):
            customer_record = CustomerRecord(self.session)
            customer_id = customer_record.get_customer_id_from_uuid(customer_id)

        if isinstance(region_id, basestring):
            region_query = region_id
            region_record = RegionRecord(self.session)
            region_id = region_record.get_region_id_from_name(region_id)
            if region_id is None:
                raise NotFound("region %s is not found" % region_query)

        if isinstance(user_id, basestring):
            user_query = user_id
            cms_user_record = CmsUserRecord(self.session)
            user_id = cms_user_record.get_cms_user_id_from_name(user_id)
            if user_id is None:
                raise NotFound("user %s is not found" % user_query)

        result = self.session.connection().execute("delete from user_role where customer_id = %d and region_id = %d and user_id = %d" % (customer_id, region_id, user_id))
        print "num records deleted: " + str(result.rowcount)
        return result

    def delete_all_users_from_region(self, customer_id, region_id):
        # customer_id can be a uuid (type of string) or id (type of int)
        # if customer_id is uuid I get id from uuid and use the id in the next sql command
        if isinstance(customer_id, basestring):
            customer_record = CustomerRecord(self.session)
            customer_id = customer_record.get_customer_id_from_uuid(customer_id)

        if isinstance(region_id, basestring):
            region_record = RegionRecord(self.session)
            region_id = region_record.get_region_id_from_name(region_id)

        result = self.session.connection().execute(
            "delete from user_role where customer_id = {} and region_id = {}".format(customer_id, region_id))

        print "num records deleted: " + str(result.rowcount)
        return result
