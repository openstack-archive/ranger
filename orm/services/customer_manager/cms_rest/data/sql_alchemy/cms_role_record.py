from orm.services.customer_manager.cms_rest.data.sql_alchemy.models \
    import CmsRole
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class CmsRoleRecord:

    def __init__(self, session=None):

        # this model uses for the parameters for any access methods -
        # not as instance of record in the table
        self.__cms_role = CmsRole()

        self.__TableName = "cms_role"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def cms_role(self):
        return self.__cms_role

    @cms_role.setter
    def cms_role(self, cms_role):
        self.__cms_role = cms_role

    def insert(self, cms_role):
        try:
            self.session.add(cms_role)
        except Exception as exception:
            LOG.log_exception("Failed to insert cms_role", exception)
            raise

    def get_cms_role_id_from_name(self, cms_role_name):
        cmd = "SELECT id from cms_role WHERE name = %s"
        result = self.session.connection().scalar(cmd, (cms_role_name,))

        if result is not None:
            return int(result)
        return result
