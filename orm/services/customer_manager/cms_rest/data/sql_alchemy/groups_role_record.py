from orm.services.customer_manager.cms_rest.data.sql_alchemy.group_record \
    import GroupRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models \
    import GroupsRole
from orm.services.customer_manager.cms_rest.data.sql_alchemy.region_record \
    import RegionRecord
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class GroupsRoleRecord:
    def __init__(self, session):

        # thie model uses for the parameters for any acceess methods - not
        # as instance of record in the table
        self.__groups_role = GroupsRole()
        self.__TableName = "groups_role"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def groups_role(self):
        return self.__groups_role

    @groups_role.setter
    def groups_role(self):
        self.__groups_role = GroupsRole()

    def insert(self, groups_role):
        try:
            self.session.add(groups_role)
        except Exception as exception:
            LOG.log_exception(
                "Failed to insert groups_role" + str(groups_role), exception)
            raise

    def get_role_for_group_by_primary_key(self,
                                          group_uuid, region_name, role_id):
        region_record = RegionRecord(self.session)
        region_id = region_record.get_region_id_from_name(region_name)
        if region_id is None:
            raise ValueError(
                'region with the region name {0} not found'.format(
                    region_name))
        try:
            group = self.session.query(GroupsRole).filter(
                and_(
                    GroupsRole.group_id == group_uuid,
                    GroupsRole.role_id == role_id,
                    GroupsRole.region_id == region_id))
            return group.first()

        except Exception as exception:
            message = "Failed to get role by primary keys: group_uuid:%s  " \
                "role_id:%s  region_name:%s " % group_uuid, role_id, region_id
            LOG.log_exception(message, exception)
            raise

    def get_roles_for_group(self, group_uuid):
        groups_roles = []

        try:
            query = self.session.query(GroupsRole).filter(
                GroupsRole.group_id == group_uuid)

            for groups_role in query.all():
                groups_roles.append(groups_role)
            return groups_roles

        except Exception as exception:
            message = "Failed to get roles for group: %s" % (group_uuid)
            LOG.log_exception(message, exception)
            raise

    def remove_role_from_group(self, group_uuid, region_id, role_id):
        cmd = 'DELETE FROM groups_role WHERE group_id = %s and \
               region_id = %s and role_id = %s'
        result = self.session.connection().execute(cmd,
                                                   (group_uuid,
                                                    region_id,
                                                    role_id))

        self.session.flush()

        if result.rowcount == 0:
            LOG.warn('role with the role id {0} not found'.format(
                role_id))
            raise ValueError(
                'role with the role id {0} not found'.format(
                    role_id))

        LOG.debug("num records deleted: " + str(result.rowcount))
        return result

    def delete_all_roles_for_group(self, group_id):
        # group_id can be a uuid (type of string) or id (type of int).
        # If group_id is uuid, then get id from uuid and use the id in the
        # next sql command
        if isinstance(group_id, basestring):
            group_record = GroupRecord(self.session)
            group_id = group_record.get_group_id_from_uuid(group_id)

        # not including default region which is -1
        cmd = 'DELETE FROM groups_role WHERE group_id = %s and \
               region_id <> -1'
        result = self.session.connection().execute(cmd, (group_id,))
        return result
