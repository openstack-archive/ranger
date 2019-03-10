from pecan import request
from pecan import conf, request
import requests

from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.data.data_manager import DataManager
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import (DuplicateEntryError, ErrorStatus)
from orm.services.customer_manager.cms_rest.model.GroupModels import (GroupResultWrapper, GroupSummary,
                                                                      GroupSummaryResponse)

from orm.services.customer_manager.cms_rest.rds_proxy import RdsProxy
LOG = get_logger(__name__)


class GroupLogic(object):

    def build_full_group(self, group, uuid, datamanager):
        if any(char in ":" for char in group.name):
            raise ErrorStatus(400, "Group Name does not allow colon(:).")

        if group.name.strip() == '':
            raise ErrorStatus(400, "Group Name can not be blank.")

        sql_group = datamanager.add_group(group, uuid)

        sql_group_id = sql_group.uuid
        datamanager.add_group_region(sql_group_id, -1)

        self.add_regions_to_db(group.regions, sql_group_id, datamanager)

        return sql_group

    def add_regions_to_db(self, regions, sql_group_id, datamanager, default_users=[]):
        for region in regions:

            sql_region = datamanager.add_region(region)
            try:
                datamanager.add_group_region(sql_group_id, sql_region.id)
            except Exception as ex:
                if hasattr(ex, 'orig') and ex.orig[0] == 1062:
                    raise DuplicateEntryError(
                        'Error, duplicate entry, region ' + region.name + ' already associated with group')
                raise ex

    def create_group(self, group, uuid, transaction_id):
        datamanager = DataManager()
        try:
            group.handle_region_group()
            sql_group = self.build_full_group(group, uuid, datamanager)
            group_result_wrapper = build_response(uuid, transaction_id, 'create')

            if sql_group.group_regions and len(sql_group.group_regions) > 1:
                group_dict = sql_group.get_proxy_dict()
                for region in group_dict["regions"]:
                    region["action"] = "create"

                datamanager.flush()  # i want to get any exception created by this insert
                RdsProxy.send_group_dict(group_dict, transaction_id, "POST")
            else:
                LOG.debug("Group with no regions - wasn't send to RDS Proxy " + str(group))

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
            # old_group_dict = sql_group.get_proxy_dict()
            group_record.delete_by_primary_key(group_id)
            datamanager.flush()

            sql_group = self.build_full_group(group, group_uuid,
                                              datamanager)
            # new_group_dict = sql_group.get_proxy_dict()

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

        if sql_group.get_group_regions():
            resp = requests.get(conf.api.rds_server.base +
                                conf.api.rds_server.status +
                                sql_group.uuid, verify=conf.verify).json()

            for item in ret_group.regions:
                for status in resp['regions']:
                    if status['region'] == item.name:
                        item.status = status['status']
                        if status['error_msg']:
                            item.error_message = status['error_msg']
            ret_group.status = resp['status']
        else:
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
            uuids = ','.join(str("\'" + sql_group.uuid + "\'")
                             for sql_group in sql_groups if sql_group and sql_group.uuid)
            resource_status = group_record.get_groups_status_by_uuids(uuids)

            for sql_group in sql_groups:
                groups = GroupSummary.from_db_model(sql_group)

                if sql_group.uuid:
                    # rds_region list contains tuples - each containing the
                    # region associated  with the customer along with the
                    # region status
                    rds_region = resource_status.get(sql_group.uuid)

                    if rds_region and groups.regions:
                        # set customer.status to 'error' if any of the regions
                        # has an 'Error' status' else, if any region status
                        # shows 'Submitted' then set customer status to
                        # 'Pending'; otherwise customer status is 'Success'
                        error_status = [item for item in rds_region if item[1] == 'Error']
                        submitted_status = [item for item in rds_region if item[1] == 'Submitted']
                        success_status = [item for item in rds_region if item[1] == 'Success']

                        if len(error_status) > 0:
                            groups.status = 'Error'
                        elif len(submitted_status) > 0:
                            groups.status = 'Pending'
                        elif len(success_status) > 0:
                            groups.status = 'Success'
                    else:
                        groups.status = 'no regions'
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
