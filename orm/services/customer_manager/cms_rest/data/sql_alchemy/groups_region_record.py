from orm.services.customer_manager.cms_rest.data.sql_alchemy.group_record \
    import GroupRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models \
    import GroupRegion
from orm.services.customer_manager.cms_rest.data.sql_alchemy.region_record \
    import RegionRecord
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class GroupsRegionRecord:
    def __init__(self, session):

        # thie model uses for the parameters for any acceess methods - not
        # as instance of record in the table
        self.__groups_region = GroupRegion()
        self.__TableName = "groups_region"

        if (session):
            self.session = session

    def setDBSession(self, session):
        self.session = session

    @property
    def groups_region(self):
        return self.__groups_region

    @groups_region.setter
    def groups_region(self):
        self.__groups_region = GroupRegion()

    def insert(self, group_region):
        try:
            self.session.add(group_region)
        except Exception as exception:
            LOG.log_exception(
                "Failed to insert group_region" + str(group_region), exception)
            raise

    def get_regions_for_group(self, group_uuid):
        group_regions = []

        try:
            group_record = GroupRecord(self.session)
            group_id = group_record.get_group_id_from_uuid(group_uuid)
            query = self.session.query(GroupRegion).filter(
                GroupRegion.group_id == group_id)

            for group_region in query.all():
                group_regions.append(group_region)
            return group_regions

        except Exception as exception:
            message = "Failed to get_region_names_for_group: %d" % (group_id)
            LOG.log_exception(message, exception)
            raise

    def delete_region_for_group(self, group_uuid, region_name):
        # get region id by name
        region_record = RegionRecord(self.session)
        region_id = region_record.get_region_id_from_name(region_name)
        if region_id is None:
            raise ValueError(
                'region with the region name {0} not found'.format(
                    region_name))
        cmd = 'DELETE FROM groups_region WHERE group_id = %s and \
               region_id = %s'
        result = self.session.connection().execute(cmd,
                                                   (group_uuid, region_id))

        self.session.flush()

        if result.rowcount == 0:
            LOG.warn('region with the region name {0} not found'.format(
                region_name))
            raise ValueError(
                'region with the region name {0} not found'.format(
                    region_name))

        LOG.debug("num records deleted: " + str(result.rowcount))
        return result

    def delete_all_regions_for_group(self, group_id):
        # group_id can be a uuid (type of string) or id (type of int).
        # If group_id is uuid, then get id from uuid and use the id in the
        # next sql command
        if isinstance(group_id, basestring):
            group_record = GroupRecord(self.session)
            group_id = group_record.get_group_id_from_uuid(group_id)

        # not including default region which is -1
        cmd = 'DELETE FROM groups_region WHERE group_id = %s and \
               region_id <> -1'
        result = self.session.connection().execute(cmd, (group_id))
        return result
