from pecan import request
from pecan import conf, request
import requests

from orm.common.orm_common.utils import utils
from orm.common.orm_common.utils.cross_api_utils import (get_regions_of_group,
                                                         set_utils_conf)

from orm.services.customer_manager.cms_rest.data.data_manager import \
    DataManager
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import (
    DuplicateEntryError, ErrorStatus)
from orm.services.customer_manager.cms_rest.model.GroupModels import (
    GroupResultWrapper,
    RoleResultWrapper,
    GroupSummary,
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

    def add_regions_to_db(self, regions, sql_group_id,
                          datamanager, default_users=[]):
        for region in regions:

            sql_region = datamanager.add_region(region)
            try:
                datamanager.add_group_region(sql_group_id, sql_region.id)
            except Exception as ex:
                if hasattr(ex, 'orig') and ex.orig[0] == 1062:
                    raise DuplicateEntryError(
                        'Error, duplicate entry, region ' +
                        region.name +
                        ' already associated with group')
                raise ex

    def assign_roles(self,
                     group_id,
                     role_assignments,
                     transaction_id):

        datamanager = DataManager()
        try:
            region_record = datamanager.get_record('groups_region')
            groups_regions = region_record.get_regions_for_group(group_id)
            cms_role_record = datamanager.get_record('cms_role')
            for role_assignment in role_assignments:
                for role in role_assignment.roles:
                    role_id = cms_role_record.get_cms_role_id_from_name(role)
                    for group_region in groups_regions:
                        region_id = group_region.region_id
                        # Need to check either domain or project but not both
                        if role_assignment.domain_name:
                            datamanager.add_groups_role_on_domain(
                                group_id,
                                role_id,
                                region_id,
                                role_assignment.domain_name)
                        elif role_assignment.project:
                            project_id = datamanager.get_customer_id_by_uuid(
                                role_assignment.project)
                            datamanager.add_groups_role_on_project(
                                group_id,
                                role_id,
                                region_id,
                                project_id)

            roles = [{'roles': role_assignment.roles,
                      'domain': role_assignment.domain_name,
                      'project': role_assignment.project}
                     for role_assignment in role_assignments]

            role_result_wrapper = build_response(group_id,
                                                 transaction_id,
                                                 'role_assignment',
                                                 roles=roles)
            datamanager.commit()
            return role_result_wrapper

        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to Assign Role(s)", exp)
            datamanager.rollback()
            raise

    def unassign_roles(self,
                       group_id,
                       role_assignments,
                       transaction_id,
                       on_success_by_rds):

        datamanager = DataManager()
        try:
            region_record = datamanager.get_record('groups_region')
            groups_regions = region_record.get_regions_for_group(group_id)
            groups_role = datamanager.get_record('groups_role')
            sql_group = datamanager.get_group_by_uuid_or_name(group_id)

            if on_success_by_rds and sql_group is None:
                return
            if sql_group is None:
                raise ErrorStatus(
                    404,
                    "group with id {} does not exist".format(group_id))

            cms_role_record = datamanager.get_record('cms_role')

            for role_assignment in role_assignments:
                for role in role_assignment.roles:
                    role_id = cms_role_record.get_cms_role_id_from_name(role)
                    for group_region in groups_regions:
                        region_id = group_region.region_id

                        if role_assignment.domain_name:
                            role_record = datamanager.get_record(
                                'groups_domain_role')
                            role_record.remove_domain_role_from_group(
                                group_id,
                                region_id,
                                role_assignment.domain_name,
                                role_id)
                            groups_role.remove_role_from_group(
                                group_id,
                                role_id)
                        elif role_assignment.project:
                            project_id = datamanager.get_customer_id_by_uuid(
                                role_assignment.project)
                            role_record = datamanager.get_record(
                                'groups_customer_role')
                            role_record.remove_customer_role_from_group(
                                group_id,
                                region_id,
                                project_id,
                                role_id)
                            groups_role.remove_role_from_group(
                                group_id,
                                role_id)

            datamanager.flush()

            roles = [{'roles': role_assignment.roles,
                      'domain': role_assignment.domain_name,
                      'project': role_assignment.project}
                     for role_assignment in role_assignments]

            role_result_wrapper = build_response(group_id,
                                                 transaction_id,
                                                 'role_assignment',
                                                 roles=roles)

            # Rds not working yet, over-ride here so as to commit
            on_success_by_rds = True
            if on_success_by_rds:
                datamanager.commit()
                # LOG.debug("Roles {0} in group {1} deleted".format(region_id,
                #                                                   group_id))
        except Exception as exp:
            datamanager.rollback()
            raise

        finally:
            datamanager.close()
        return role_result_wrapper

    def create_group(self, group, uuid, transaction_id):
        datamanager = DataManager()
        try:
            group.handle_region_group()
            sql_group = self.build_full_group(group, uuid, datamanager)
            group_result_wrapper = build_response(uuid,
                                                  transaction_id,
                                                  'create_group')
            if sql_group.group_regions and len(sql_group.group_regions) > 1:
                group_dict = sql_group.get_proxy_dict()
                for region in group_dict["regions"]:
                    region["action"] = "create"

                datamanager.flush()
                RdsProxy.send_group_dict(group_dict, transaction_id, "POST")
            else:
                LOG.debug(
                    "Group with no regions - wasn't send to RDS Proxy " +
                    str(group))

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
                raise ErrorStatus(
                    404, 'group {0} was not found'.format(group_uuid))
            # old_group_dict = sql_group.get_proxy_dict()
            group_record.delete_by_primary_key(group_id)
            datamanager.flush()

            sql_group = self.build_full_group(group, group_uuid,
                                              datamanager)
            # new_group_dict = sql_group.get_proxy_dict()

            group_result_wrapper = build_response(group_uuid,
                                                  transaction_id,
                                                  'update_group')
            datamanager.flush()
            datamanager.commit()

            return group_result_wrapper

        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to CreateGroup", exp)
            datamanager.rollback()
            raise

    def delete_region(self, group_id, region_id, transaction_id,
                      on_success_by_rds, force_delete):
        datamanager = DataManager()
        try:
            group_region = datamanager.get_record('groups_region')
            sql_group = datamanager.get_group_by_uuid_or_name(group_id)
            if on_success_by_rds and sql_group is None:
                return
            if sql_group is None:
                raise ErrorStatus(
                    404,
                    "group with id {} does not exist".format(group_id))

            group_dict = sql_group.get_proxy_dict()
            group_region.delete_region_for_group(group_id, region_id)
            datamanager.flush()

            if on_success_by_rds:
                datamanager.commit()
                LOG.debug("Region {0} in group {1} deleted".format(region_id,
                                                                   group_id))
            else:
                region = next((r.region for r in sql_group.group_regions
                              if r.region.name == region_id), None)
                if region:
                    if region.type == 'group':
                        set_utils_conf(conf)
                        regions = get_regions_of_group(region.name)
                    else:
                        regions = [region_id]
                for region in group_dict['regions']:
                    if region['name'] in regions:
                        region['action'] = 'delete'

                RdsProxy.send_group_dict(group_dict, transaction_id, "PUT")
                if force_delete:
                    datamanager.commit()
                else:
                    datamanager.rollback()

        except Exception as exp:
            datamanager.rollback()
            raise

        finally:
            datamanager.close()

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
        sql_groups = group_record.get_groups_by_criteria(
            region=region,
            user=user,
            starts_with=starts_with,
            contains=contains,
            start=start,
            limit=limit)
        response = GroupSummaryResponse()
        if sql_groups:
            uuids = [sql_group.uuid for sql_group in sql_groups
                     if sql_group and sql_group.uuid]

            sql_in = ', '.join(list(map(lambda arg: "'%s'" % arg, uuids)))
            resource_status = group_record.get_groups_status_by_uuids(sql_in)

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
                        error_status = [item for item in rds_region
                                        if item[1] == 'Error']
                        submitted_status = [item for item in rds_region
                                            if item[1] == 'Submitted']
                        success_status = [item for item in rds_region
                                          if item[1] == 'Success']

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
                raise ErrorStatus(
                    404, "Group '{0}' not found".format(group_id))

            regions = sql_group.get_group_regions()
            if len(regions) > 0:
                # Do not delete a group that still has region(s)
                raise ErrorStatus(405,
                                  "Cannot delete a group that has region(s). "
                                  "Please delete the region(s) first and then "
                                  "delete the group.")
            else:
                expected_status = 'Success'
                invalid_status = 'N/A'
                # Get status from RDS
                resp = RdsProxy.get_status(sql_group.uuid)
                if resp.status_code == 200:
                    status_resp = resp.json()
                    if 'status' in status_resp.keys():
                        LOG.debug('RDS returned status: {}'.format(
                                  status_resp['status']))
                        status = status_resp['status']
                    else:
                        # Invalid response from RDS
                        LOG.error('Response from RDS did not contain status')
                        status = invalid_status
                elif resp.status_code == 404:
                    # Group not found in RDS, that means it never has any
                    # region(s). So it is OK to delete it.
                    LOG.debug(
                        'Resource not found in RDS, so it is OK to delete')
                    status = expected_status
                else:
                    # Invalid status code from RDS
                    log_message = 'Invalid response code from RDS: {}'.format(
                        resp.status_code)
                    log_message = log_message.replace('\n', '_').replace('\r',
                                                                         '_')
                    LOG.warning(log_message)
                    status = invalid_status

                if status == invalid_status:
                    raise ErrorStatus(500, "Could not get group status")
                elif status != expected_status:
                    raise ErrorStatus(
                        409,
                        "The group has not been deleted "
                        "successfully from all of its regions "
                        "(either the deletion failed on one of the "
                        "regions or it is still in progress)")

            # OK to delete
            group_record.delete_group_by_uuid(group_id)
            datamanager.flush()
            datamanager.commit()
        except Exception as exp:
            LOG.log_exception("GroupLogic - Failed to delete group", exp)
            datamanager.rollback()
            raise


def build_response(self, group_uuid, transaction_id, context, roles=[]):
    """this function generate th group action response JSON
    :param group_uuid:
    :param transaction_id:
    :param context:
    :param roles:
    :return:
    """
    timestamp = utils.get_time_human()
    # The link should point to the group itself (/v1/orm/groups/{id})
    link_elements = request.url.split('/')
    base_link = '/'.join(link_elements)
    if context == 'create_group' or context == 'update_group':
        if context == 'create_group':
            base_link = base_link + group_uuid

        group_result_wrapper = GroupResultWrapper(
            transaction_id=transaction_id,
            id=group_uuid,
            updated=None,
            created=timestamp,
            links={'self': base_link})

        return group_result_wrapper

    elif context == 'role_assignment':
        role_result_wrapper = RoleResultWrapper(
            transaction_id=transaction_id,
            roles=roles,
            links={'self': base_link},
            created=timestamp)

        return role_result_wrapper
    else:
        return None
