from fms_rest.data.sql_alchemy.db_models import FlavorTenant
from fms_rest.logger import get_logger
from sqlalchemy import and_

LOG = get_logger(__name__)


class FlavorTenantRecord:

    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__flavorTenants = FlavorTenant()
        # self.setRecordData(self.__flavorTenants)
        # self.__flavorTenants.Clear()
        self.__TableName = "flavor_tenant"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor_tenant(self):
        return self.__flavorTenant

    @flavor_tenant.setter
    def flavor_tenant(self, flavorTenant):
        self.__flavorTenant = flavorTenant

    def insert(self, flavorTenant):
        try:
            self.session.add(flavorTenant)
        except Exception as exception:
            LOG.log_exception("Failed to insert FlavorTenant" + str(flavorTenant), exception)
            # LOG.error("Failed to insert flavorTenant" + str(flavorTenant) + " Exception:" + str(exception))
            raise

    def get_flavor_tenant(self, flavor_internal_id, tenant_id):
        try:
            flavor_tenant = self.session.query(FlavorTenant).filter(and_(FlavorTenant.flavor_internal_id == flavor_internal_id,
                                                                         FlavorTenant.tenant_id == tenant_id))
            return flavor_tenant.first()

        except Exception as exception:
            message = "Failed to get_flavor_tenant: flavor_internal_id: {0}, tenant_id {1}".format(flavor_internal_id, tenant_id)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_tenants_by_flavor_internal_id(self, flavor_internal_id):
        try:
            flavor_tenants = self.session.query(FlavorTenant).filter(FlavorTenant.flavor_internal_id == flavor_internal_id)
            return flavor_tenants.all()

        except Exception as exception:
            message = "Failed to get_flavor_tenants_by_flavor_internal_id: flavor_internal_id: {0}".format(flavor_internal_id)
            LOG.log_exception(message, exception)
            raise

#     12850 ProCG uses this line - don't edit it
