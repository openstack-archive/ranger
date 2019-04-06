from orm.services.customer_manager.cms_rest.data.sql_alchemy.group_record \
    import GroupRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models \
    import GroupsDomainRole
from orm.services.customer_manager.cms_rest.data.sql_alchemy.region_record \
    import RegionRecord
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class GroupsDomainRoleRecord:
    def __init__(self, session):

        # thie model uses for the parameters for any acceess methods - not
        # as instance of record in the table
        self.__groups_domain_role = GroupsDomainRole()
        self.__TableName = "groups_domain_role"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def groups_domain_role(self):
        return self.__groups_domain_role

    @groups_domain_role.setter
    def groups_domain_role(self):
        self.__groups_domain_role = GroupsDomainRole()

    def insert(self, groups_domain_role):
        try:
            self.session.add(groups_domain_role)
        except Exception as exception:
            LOG.log_exception(
                "Failed to insert groups_domain_role" +
                str(groups_domain_role), exception)
            raise

    def get_group_domain_role_by_keys(self,
                                      group_uuid,
                                      region_name,
                                      domain,
                                      role_id):
        region_record = RegionRecord(self.session)
        region_id = region_record.get_region_id_from_name(region_name)
        if region_id is None:
            raise ValueError(
                'region with the region name {0} not found'.format(
                    region_name))
        try:
            group = self.session.query(GroupsDomainRole).filter(
                and_(
                    GroupsDomainRole.group_id == group_uuid,
                    GroupsDomainRole.domain_name == domain,
                    GroupsDomainRole.region_id == region_id,
                    GroupsDomainRole.role_id == role_id))
            return group.first()

        except Exception as exception:
            message = "Failed to get group/domain by primary keys: " \
                " group_uuid:%s domain:%s  region_name:%s role_id: %s" \
                % group_uuid, domain, region_id, role_id
            LOG.log_exception(message, exception)
            raise

    def get_domain_roles_for_group(self, group_uuid):
        groups_domain_roles = []

        try:
            query = self.session.query(GroupsDomainRole).filter(
                GroupsDomainRole.group_id == group_uuid)

            for groups_domain_role in query.all():
                groups_domain_roles.append(groups_domain_role)
            return groups_domain_roles

        except Exception as exception:
            message = "Failed to get domains for group: %s" % (group_uuid)
            LOG.log_exception(message, exception)
            raise

    def remove_domain_role_from_group(self,
                                      group_uuid,
                                      region_id,
                                      domain,
                                      role_id):
        cmd = 'DELETE FROM groups_domain_role WHERE group_id = %s and \
               region_id = %s and domain_name = %s and role_id = %s'
        result = self.session.connection().execute(cmd,
                                                   (group_uuid,
                                                    region_id,
                                                    domain,
                                                    role_id))

        self.session.flush()

        if result.rowcount == 0:
            LOG.warn('domain with domain name {0} not found'.format(
                domain))
            raise ValueError(
                'domain with domain name {0} not found'.format(
                    customer_uuid))

        LOG.debug("num records deleted: " + str(result.rowcount))
        return result

    def delete_all_customers_from_group(self, group_id):
        # group_id can be a uuid (type of string) or id (type of int).
        # If group_id is uuid, then get id from uuid and use the id in the
        # next sql command
        if isinstance(group_id, basestring):
            group_record = GroupRecord(self.session)
            group_id = group_record.get_group_id_from_uuid(group_id)

        # not including default region which is -1
        cmd = 'DELETE FROM groups_domain_role WHERE group_id = %s and \
               region_id <> -1'
        result = self.session.connection().execute(cmd, (group_id,))
        return result
