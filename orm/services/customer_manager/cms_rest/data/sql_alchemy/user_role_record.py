from orm.services.customer_manager.cms_rest.data.sql_alchemy.cms_user_record import CmsUserRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.customer_record import CustomerRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import *
from orm.services.customer_manager.cms_rest.data.sql_alchemy.region_record import RegionRecord
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import NotFound

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
                raise NotFound("region {} ".format(region_query))

        if isinstance(user_id, basestring):
            user_query = user_id
            cms_user_record = CmsUserRecord(self.session)
            user_id = cms_user_record.get_cms_user_id_from_name(user_id)
            if user_id is None:
                raise NotFound("user {} ".format(user_query))

            # additional logic for delete_user only: check if the provided user id
            # is associated with the customer and region in cms delete_user request
            elif region_id > -1:
                user_check = "SELECT DISTINCT user_id from user_role " \
                             "WHERE customer_id =%d AND region_id =%d " \
                             "AND user_id =%d" % (customer_id, region_id, user_id)

                result = self.session.connection().execute(user_check)
                if result.rowcount == 0:
                    raise NotFound("user {} ".format(user_query))

        if region_id == -1:
            delete_query = "DELETE ur FROM user_role ur,user_role u " \
                           "where ur.user_id=u.user_id and ur.role_id=u.role_id " \
                           "and ur.customer_id = u.customer_id and u.region_id =-1 " \
                           "and ur.customer_id = %d and ur.user_id=%d" % (customer_id, user_id)
        else:
            # modify query to correctly determine that the provided region user and its role(s)
            # do NOT match that of the default user; otherwise delete user is NOT permitted
            delete_query = "DELETE ur FROM user_role as ur LEFT JOIN user_role AS u " \
                           "ON ur.customer_id = u.customer_id and u.user_id=ur.user_id " \
                           "and u.region_id=-1  and ur.role_id = u.role_id where ur.customer_id = %d " \
                           "and ur.region_id= %d and ur.user_id =%d and u.role_id IS NULL" \
                           % (customer_id, region_id, user_id)

        result = self.session.connection().execute(delete_query)
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
        if region_id == -1:
            delete_query = "DELETE ur FROM user_role ur,user_role u " \
                           "where ur.user_id=u.user_id and ur.role_id=u.role_id " \
                           "and ur.customer_id = u.customer_id and u.region_id =-1 " \
                           "and ur.customer_id = %d" % (customer_id)
        else:
            delete_query = "DELETE ur FROM user_role as ur LEFT JOIN user_role AS u " \
                           "ON ur.customer_id = u.customer_id and u.user_id=ur.user_id " \
                           "and u.region_id=-1 where ur.customer_id = %d and ur.region_id= %d " \
                           "and ur.role_id !=IFNULL(u.role_id,'')" \
                           % (customer_id, region_id)

        result = self.session.connection().execute(delete_query)

        print "num records deleted: " + str(result.rowcount)
        return result
