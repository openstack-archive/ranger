from pecan import request

from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.data.data_manager import DataManager
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import (ErrorStatus)
from orm.services.customer_manager.cms_rest.model.GroupModels import (GroupResultWrapper, GroupSummary,
                                                                      GroupSummaryResponse)

LOG = get_logger(__name__)


class GroupLogic(object):

    def build_full_group(self, group, uuid, datamanager):
        if any(char in ":" for char in group.name):
            raise ErrorStatus(400, "Group Name does not allow colon(:).")

        if group.name.strip() == '':
            raise ErrorStatus(400, "Group Name can not be blank.")

        sql_group = datamanager.add_group(group, uuid)

        return sql_group

    def create_group(self, group, uuid, transaction_id):
        datamanager = DataManager()
        try:
            group.handle_region_group()
            sql_group = self.build_full_group(group, uuid, datamanager)
            group_result_wrapper = build_response(uuid, transaction_id, 'create')

            datamanager.commit()

        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to CreateGroup", exp)
            datamanager.rollback()
            raise

        return group_result_wrapper

    def update_group(self, group, group_uuid, transaction_id):
        datamanager = DataManager()
        try:
            group.validate_model('update')
            group_record = datamanager.get_record('group')
            group_id = group_record.get_group_id_from_uuid(
                group_uuid)

            sql_group = group_record.read_group_by_uuid(group_uuid)
            if not sql_group:
                raise ErrorStatus(404, 'group {0} was not found'.format(group_uuid))
            old_group_dict = sql_group.get_proxy_dict()
            group_record.delete_by_primary_key(group_id)
            datamanager.flush()

            sql_group = self.build_full_group(group, group_uuid,
                                              datamanager)
            new_group_dict = sql_group.get_proxy_dict()

            group_result_wrapper = build_response(group_uuid, transaction_id, 'update')
            datamanager.flush()  # i want to get any exception created by this insert
            datamanager.commit()

            return group_result_wrapper

        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to CreateGroup", exp)
            datamanager.rollback()
            raise

    def get_group(self, group):

        datamanager = DataManager()

        sql_group = datamanager.get_group_by_uuid_or_name(group)

        if not sql_group:
            raise ErrorStatus(404, 'group: {0} not found'.format(group))

        ret_group = sql_group.to_wsme()
        ret_group.status = 'no regions'

        return ret_group

    def get_group_list_by_criteria(self, region, user, starts_with, contains,
                                      start=0, limit=0):
        datamanager = DataManager()
        group_record = datamanager.get_record('group')
        sql_groups = group_record.get_groups_by_criteria(region=region,
                                                         user=user,
                                                         starts_with=starts_with,
                                                         contains=contains,
                                                         start=start,
	                                                     limit=limit)
        response = GroupSummaryResponse()
        if sql_groups:
            for sql_group in sql_groups:
                groups = GroupSummary.from_db_model(sql_group)
                response.groups.append(groups)
        return response

    def delete_group_by_uuid(self, group_id):
        datamanager = DataManager()

        try:
            datamanager.begin_transaction()
            group_record = datamanager.get_record('group')

            sql_group = group_record.read_group_by_uuid(group_id)
            if sql_group is None:
                raise ErrorStatus(404, "Group '{0}' not found".format(group_id))

            # OK to delete
            group_record.delete_group_by_uuid(group_id)

            datamanager.flush()  # i want to get any exception created by this delete
            datamanager.commit()
        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to delete group", exp)
            datamanager.rollback()
            raise


def build_response(group_uuid, transaction_id, context):
    """this function generate th group action response JSON
    :param group_uuid:
    :param transaction_id:
    :param context: create or update
    :return:
    """
    # The link should point to the group itself (/v1/orm/groups/{id})
    link_elements = request.url.split('/')
    base_link = '/'.join(link_elements)
    if context == 'create':
        base_link = base_link + '/' + group_uuid

    timestamp = utils.get_time_human()
    group_result_wrapper = GroupResultWrapper(
        transaction_id=transaction_id,
        id=group_uuid,
        updated=None,
        created=timestamp,
        links={'self': base_link})
    return group_result_wrapper
