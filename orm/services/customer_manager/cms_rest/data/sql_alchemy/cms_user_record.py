from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import CmsUser
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class CmsUserRecord:

    def __init__(self, session=None):

        # this model uses for the parameters for any access methods - not as instance of record in the table
        self.__cms_user = CmsUser()
        # self.setRecordData(self.cms_user)
        # self.cms_user.Clear()

        self.__TableName = "cms_user"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def cms_user(self):
        return self.__cms_user

    @cms_user.setter
    def cms_user(self, cms_user):
        self.__cms_usern = cms_user

    def insert(self, cms_user):
        try:
            self.session.add(cms_user)
        except Exception as exception:
            LOG.log_exception("Failed to insert cms_user", exception)
            # LOG.error("Failed to insert cms_user" + str(cms_user)+" Exception:" + str(exception))
            raise

    def get_cms_user_id_from_name(self, cms_user_name):
        result = self.session.connection().scalar("SELECT id from cms_user WHERE name = \"%s\"", (cms_user_name,))
        if result is not None:
            return int(result)
        return result
