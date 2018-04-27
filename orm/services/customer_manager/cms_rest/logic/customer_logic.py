import pecan
from pecan import conf, request
import requests

from orm.common.orm_common.utils import utils
from orm.common.orm_common.utils.cross_api_utils import (get_regions_of_group,
                                                         set_utils_conf)
from orm.services.customer_manager.cms_rest.data.data_manager import DataManager
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import CustomerMetadata, UserRole
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.logic.error_base import (DuplicateEntryError, ErrorStatus,
                                                                     NotFound)
from orm.services.customer_manager.cms_rest.model.Models import (CustomerResultWrapper, CustomerSummary,
                                                                 CustomerSummaryResponse,
                                                                 RegionResultWrapper, UserResultWrapper)
from orm.services.customer_manager.cms_rest.rds_proxy import RdsProxy

LOG = get_logger(__name__)


class CustomerLogic(object):
    def build_full_customer(self, customer, uuid, datamanager):
        if any(char in ":" for char in customer.name):
            raise ErrorStatus(400, "Customer Name does not allow colon(:).")

        if customer.name.strip() == '':
            raise ErrorStatus(400, "Customer Name can not be blank.")

        sql_customer = datamanager.add_customer(customer, uuid)

        for key, value in customer.metadata.iteritems():
            metadata = CustomerMetadata(field_key=key, field_value=value)
            sql_customer.customer_metadata.append(metadata)

        sql_customer_id = sql_customer.id
        datamanager.add_customer_region(sql_customer_id, -1)

        default_users_requested = customer.users

        default_region_users =\
            self.add_default_user_db(datamanager, default_users_requested, [], sql_customer_id)
        default_quotas = []
        for quota in customer.defaultQuotas:
            sql_quota = datamanager.add_quota(sql_customer_id, -1, quota)
            default_quotas.append(sql_quota)

        self.add_regions_to_db(customer.regions, sql_customer_id, datamanager, default_region_users)
        return sql_customer

    def add_regions_to_db(self, regions, sql_customer_id, datamanager, default_users=[]):
        for region in regions:

            sql_region = datamanager.add_region(region)
            try:
                datamanager.add_customer_region(sql_customer_id, sql_region.id)
            except Exception as ex:
                if hasattr(ex, 'orig') and ex.orig[0] == 1062:
                    raise DuplicateEntryError(
                        'Error, duplicate entry, region ' + region.name + ' already associated with customer')
                raise ex

            self.add_user_and_roles_to_db(region.users, default_users,
                                          sql_customer_id, sql_region.id, datamanager)

            for quota in region.quotas:
                datamanager.add_quota(sql_customer_id, sql_region.id, quota)

                # NOTE: if region has no quotas there is no need to update
                # the default quotas in that region
                # if len(region.quotas) == 0:
                #     for quota in customer.defaultQuotas:
                #         datamanager.add_quota(sql_customer_id,
                # sql_region.id, quota)
                # else:
                #     for quota in region.quotas:
                #         datamanager.add_quota(sql_customer_id,
                # sql_region.id, quota)

    def add_default_user_db(self, datamanager, default_users_requested, existing_default_users_roles, sql_customer_id):
        default_region_users = []
        default_users_dic = {}

        for sql_user in existing_default_users_roles:
            default_users_dic[sql_user.name] = sql_user

        for user in default_users_requested:
            is_default_user_exist = user.id in default_users_dic.keys()
            if not is_default_user_exist:
                sql_user = datamanager.add_user(user)
                default_region_users.append(sql_user)
                sql_user.sql_roles = []
                for role in user.role:
                    sql_role = datamanager.add_role(role)
                    sql_user.sql_roles.append(sql_role)
            else:
                sql_user = default_users_dic.get(user.id)
                new_sql_roles = []
                for role in user.role:
                    role_match = False
                    for sql_role in sql_user.sql_roles:
                        if sql_role.name == role:
                            role_match = True
                            break
                    if not role_match:
                        sql_role = datamanager.add_role(role)
                        new_sql_roles.append(sql_role)
                if new_sql_roles:
                    sql_user.sql_roles = new_sql_roles
                    default_region_users.append(sql_user)

        for sql_user in default_region_users:
            for sql_role in sql_user.sql_roles:
                datamanager.add_user_role(sql_user.id, sql_role.id,
                                          sql_customer_id, -1)
        return default_region_users

    def add_user_and_roles_to_db(self, users, sql_default_users, sql_customer_id, sql_region_id, datamanager):
        users_roles = []
        default_users_dic = {}

        for sql_user in sql_default_users:
            default_users_dic[sql_user.name] = sql_user
            for role in sql_user.sql_roles:
                users_roles.append((sql_user, role))

        # Default user will be given priority over region user
        for user in users:
            is_default_user_in_region = user.id in default_users_dic.keys()
            if not is_default_user_in_region:
                sql_user = datamanager.add_user(user)
                for role in user.role:
                    sql_role = datamanager.add_role(role)
                    users_roles.append((sql_user, sql_role))
            else:
                sql_user = default_users_dic.get(user.id)
                for role in user.role:
                    role_match = False
                    for sql_role in sql_user.sql_roles:
                        if sql_role.name == role:
                            role_match = True
                            break
                    if not role_match:
                        sql_role = datamanager.add_role(role)
                        users_roles.append((sql_user, sql_role))

        for user_role in users_roles:
            datamanager.add_user_role(user_role[0].id, user_role[1].id,
                                      sql_customer_id, sql_region_id)

    def create_customer(self, customer, uuid, transaction_id):
        datamanager = DataManager()
        try:
            customer.handle_region_group()
            sql_customer = self.build_full_customer(customer, uuid, datamanager)
            customer_result_wrapper = build_response(uuid, transaction_id, 'create')

            if sql_customer.customer_customer_regions and len(sql_customer.customer_customer_regions) > 1:
                customer_dict = sql_customer.get_proxy_dict()
                for region in customer_dict["regions"]:
                    region["action"] = "create"

                datamanager.flush()  # i want to get any exception created by this insert
                RdsProxy.send_customer_dict(customer_dict, transaction_id, "POST")
            else:
                LOG.debug("Customer with no regions - wasn't send to RDS Proxy " + str(customer))

            datamanager.commit()

        except Exception as exp:
            LOG.log_exception("CustomerLogic - Failed to CreateCustomer", exp)
            datamanager.rollback()
            raise

        return customer_result_wrapper

    def update_customer(self, customer, customer_uuid, transaction_id):
        datamanager = DataManager()
        try:
            customer.validate_model('update')
            customer_record = datamanager.get_record('customer')
            cutomer_id = customer_record.get_customer_id_from_uuid(
                customer_uuid)

            sql_customer = customer_record.read_customer_by_uuid(customer_uuid)
            if not sql_customer:
                raise ErrorStatus(404, 'customer {0} was not found'.format(customer_uuid))
            old_customer_dict = sql_customer.get_proxy_dict()
            customer_record.delete_by_primary_key(cutomer_id)
            datamanager.flush()

            sql_customer = self.build_full_customer(customer, customer_uuid,
                                                    datamanager)
            new_customer_dict = sql_customer.get_proxy_dict()
            new_customer_dict["regions"] = self.resolve_regions_actions(old_customer_dict["regions"],
                                                                        new_customer_dict["regions"])

            customer_result_wrapper = build_response(customer_uuid, transaction_id, 'update')
            datamanager.flush()  # i want to get any exception created by this insert
            if not len(new_customer_dict['regions']) == 0:
                RdsProxy.send_customer_dict(new_customer_dict, transaction_id, "PUT")
            datamanager.commit()

            return customer_result_wrapper

        except Exception as exp:
            LOG.log_exception("CustomerLogic - Failed to CreateCustomer", exp)
            datamanager.rollback()
            raise

    def resolve_regions_actions(self, old_regions_dict, new_regions_dict):
        for region in new_regions_dict:
            old_region = next((r for r in old_regions_dict if r["name"] == region["name"]), None)
            if old_region:
                region["action"] = "modify"
            else:
                region["action"] = "create"

        for region in old_regions_dict:
            new_region = next((r for r in new_regions_dict if r["name"] == region["name"]), None)
            if not new_region:
                region["action"] = "delete"
                new_regions_dict.append(region)

        return new_regions_dict

    def add_users(self, customer_uuid, region_name, users, transaction_id, p_datamanager=None):
        datamanager = None
        try:
            if p_datamanager is None:
                datamanager = DataManager()
                datamanager.begin_transaction()
            else:
                datamanager = p_datamanager

            region_id = datamanager.get_region_id_by_name(region_name)
            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)

            if customer_id is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            if region_id is None:
                raise ErrorStatus(404, "region {} not found".format(region_name))

            customer_record = datamanager.get_record('customer')
            customer = customer_record.read_customer(customer_id)
            defaultRegion = customer.get_default_customer_region()
            default_users_roles = defaultRegion.customer_region_user_roles if defaultRegion else []
            default_users = []
            for default_user in default_users_roles:
                if default_user.user not in default_users:
                    default_users.append(default_user.user)
                    default_user.user.sql_roles = []
                default_user.user.sql_roles.append(default_user.role)

            self.add_user_and_roles_to_db(users, default_users,
                                          customer_id, region_id, datamanager)
            timestamp = utils.get_time_human()
            datamanager.flush()  # i want to get any exception created by this insert
            RdsProxy.send_customer(customer, transaction_id, "PUT")
            if p_datamanager is None:
                datamanager.commit()

            base_link = '{0}{1}/'.format(conf.server.host_ip,
                                         pecan.request.path)

            result_users = [{'id': user.id, 'added': timestamp,
                             'links': {'self': base_link + user.id}} for user in
                            users]
            user_result_wrapper = UserResultWrapper(
                transaction_id=transaction_id, users=result_users)

            return user_result_wrapper
        except Exception as exception:
            if 'Duplicate' in exception.message:
                raise ErrorStatus(409, exception.message)
            datamanager.rollback()
            LOG.log_exception("Failed to add_users", exception)
            raise exception

    def replace_users(self, customer_uuid, region_name, users, transaction_id):
        datamanager = None
        try:
            datamanager = DataManager()
            datamanager.begin_transaction()

            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)
            if customer_id is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            region_id = datamanager.get_region_id_by_name(region_name)
            if region_id is None:
                raise ErrorStatus(404, "region {} not found".format(region_name))

            # delete older default user
            user_role_record = datamanager.get_record('user_role')
            user_role_record.delete_all_users_from_region(customer_uuid, region_name)  # -1 is default region
            result = self.add_users(customer_uuid, region_name, users, transaction_id, datamanager)
            datamanager.commit()
            return result

        except Exception as exception:
            datamanager.rollback()
            LOG.log_exception("Failed to replace_default_users", exception)
            raise

    def delete_users(self, customer_uuid, region_id, user_id, transaction_id):
        datamanager = DataManager()
        try:
            user_role_record = datamanager.get_record('user_role')

            customer = datamanager.get_customer_by_uuid(customer_uuid)
            if customer is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            result = user_role_record.delete_user_from_region(customer_uuid,
                                                              region_id,
                                                              user_id)
            if result.rowcount == 0:
                '''
                when result.rowcount returns 0, this indicates that the region user marked
                for deletion also exists - and has the same exact roles - in the default user
                level.   Since default_user supersedes region user, use 'delete_default_user'
                instead of 'delete_user' command.
                '''
                message = "Cannot use 'delete_user' as user '%s' exists and has " \
                          "the exact same roles in both the default and '%s' "\
                          "region levels for customer %s. "\
                          "Use 'delete_default_user' instead." \
                          % (user_id, region_id, customer_uuid)
                raise ErrorStatus(400, message)

            RdsProxy.send_customer(customer, transaction_id, "PUT")
            datamanager.commit()

            LOG.info("User {0} from region {1} in customer {2} deleted".
                     format(user_id, region_id, customer_uuid))

        except NotFound as e:
            datamanager.rollback()
            LOG.log_exception("Failed to delete_users, user not found",
                              e.message)
            raise NotFound("Failed to delete users,  %s not found" %
                           e.message)
        except Exception as exception:
            datamanager.rollback()
            LOG.log_exception("Failed to delete_users", exception)
            raise exception

    def add_default_users(self, customer_uuid, users, transaction_id, p_datamanager=None):
        datamanager = None
        try:
            if p_datamanager is None:
                datamanager = DataManager()
                datamanager.begin_transaction()
            else:
                datamanager = p_datamanager

            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)

            if customer_id is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            customer_record = datamanager.get_record('customer')
            customer = customer_record.read_customer(customer_id)
            defaultRegion = customer.get_default_customer_region()
            existing_default_users_roles = defaultRegion.customer_region_user_roles if defaultRegion else []
            default_users = []
            for default_user in existing_default_users_roles:
                if default_user.user not in default_users:
                    default_users.append(default_user.user)
                    default_user.user.sql_roles = []
                default_user.user.sql_roles.append(default_user.role)

            default_region_users = \
                self.add_default_user_db(datamanager, users, default_users, customer_id)

            regions = customer.get_real_customer_regions()

            for region in regions:
                self.add_user_and_roles_to_db(users, default_region_users,
                                              customer_id, region.region_id, datamanager)

            timestamp = utils.get_time_human()
            datamanager.flush()  # i want to get any exception created by this insert
            if len(customer.customer_customer_regions) > 1:
                RdsProxy.send_customer(customer, transaction_id, "PUT")

            if p_datamanager is None:
                datamanager.commit()

            base_link = '{0}{1}/'.format(conf.server.host_ip,
                                         pecan.request.path)

            result_users = [{'id': user.id, 'added': timestamp,
                             'links': {'self': base_link + user.id}} for user in
                            users]
            user_result_wrapper = UserResultWrapper(
                transaction_id=transaction_id, users=result_users)

            return user_result_wrapper

        except Exception as exception:
            datamanager.rollback()
            if 'Duplicate' in exception.message:
                raise ErrorStatus(409, exception.message)
            LOG.log_exception("Failed to add_default_users", exception)
            raise

    def replace_default_users(self, customer_uuid, users, transaction_id):
        datamanager = None
        try:
            datamanager = DataManager()
            datamanager.begin_transaction()

            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)
            if customer_id is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            # delete older default user
            user_role_record = datamanager.get_record('user_role')
            user_role_record.delete_all_users_from_region(customer_uuid, -1)  # -1 is default region
            result = self.add_default_users(customer_uuid, users, transaction_id, datamanager)
            datamanager.commit()
            return result

        except Exception as exception:
            datamanager.rollback()
            LOG.log_exception("Failed to replace_default_users", exception)
            raise

    def delete_default_users(self, customer_uuid, user_id, transaction_id):
        datamanager = DataManager()
        try:
            customer = datamanager.get_customer_by_uuid(customer_uuid)
            if customer is None:
                raise ErrorStatus(404, "customer {} does not exist".format(customer_uuid))

            user_role_record = datamanager.get_record('user_role')
            result = user_role_record.delete_user_from_region(customer_uuid,
                                                              'DEFAULT',
                                                              user_id)
            if result.rowcount == 0:
                raise NotFound("user {} ".format(user_id))
            datamanager.flush()

            if len(customer.customer_customer_regions) > 1:
                RdsProxy.send_customer(customer, transaction_id, "PUT")

            datamanager.commit()

            LOG.info("User {0} from region {1} in customer {2} deleted".
                     format(user_id, 'DEFAULT', customer_uuid))

        except NotFound as e:
            datamanager.rollback()
            LOG.log_exception("Failed to delete_users, user not found",
                              e.message)
            raise NotFound("Failed to delete user(s),  %s not found" %
                           e.message)

        except Exception as exp:
            datamanager.rollback()
            raise exp

    def add_regions(self, customer_uuid, regions, transaction_id):
        datamanager = DataManager()
        customer_record = datamanager.get_record('customer')
        try:
            # TODO DataBase action
            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)
            if customer_id is None:
                raise ErrorStatus(404,
                                  "customer with id {} does not exist".format(
                                      customer_uuid))

            sql_customer = customer_record.read_customer_by_uuid(customer_uuid)

            defaultRegion = sql_customer.get_default_customer_region()
            existing_default_users_roles = defaultRegion.customer_region_user_roles if defaultRegion else []
            default_users = []
            for default_user in existing_default_users_roles:
                if default_user.user not in default_users:
                    default_users.append(default_user.user)
                    default_user.user.sql_roles = []
                default_user.user.sql_roles.append(default_user.role)

            self.add_regions_to_db(regions, customer_id, datamanager, default_users)

            datamanager.commit()

            datamanager.session.expire(sql_customer)

            sql_customer = datamanager.get_customer_by_id(customer_id)

            new_customer_dict = sql_customer.get_proxy_dict()

            for region in new_customer_dict["regions"]:
                new_region = next((r for r in regions if r.name == region["name"]), None)
                if new_region:
                    region["action"] = "create"
                else:
                    region["action"] = "modify"

            timestamp = utils.get_time_human()
            RdsProxy.send_customer_dict(new_customer_dict, transaction_id, "POST")

            base_link = '{0}{1}/'.format(conf.server.host_ip,
                                         pecan.request.path)

            result_regions = [{'id': region.name, 'added': timestamp,
                               'links': {'self': base_link + region.name}} for
                              region in regions]
            region_result_wrapper = RegionResultWrapper(
                transaction_id=transaction_id, regions=result_regions)

            return region_result_wrapper
        except Exception as exp:
            datamanager.rollback()
            raise

    def replace_regions(self, customer_uuid, regions, transaction_id):
        datamanager = DataManager()
        customer_record = datamanager.get_record('customer')
        customer_region = datamanager.get_record('customer_region')
        try:
            customer_id = datamanager.get_customer_id_by_uuid(customer_uuid)
            if customer_id is None:
                raise ErrorStatus(404,
                                  "customer with id {} does not exist".format(
                                      customer_uuid))

            old_sql_customer = customer_record.read_customer_by_uuid(customer_uuid)
            if old_sql_customer is None:
                raise ErrorStatus(404,
                                  "customer with id {} does not exist".format(
                                      customer_id))
            old_customer_dict = old_sql_customer.get_proxy_dict()
            defaultRegion = old_sql_customer.get_default_customer_region()
            existing_default_users_roles = defaultRegion.customer_region_user_roles if defaultRegion else []
            default_users = []
            for default_user in existing_default_users_roles:
                if default_user.user not in default_users:
                    default_users.append(default_user.user)
                    default_user.user.sql_roles = []
                default_user.user.sql_roles.append(default_user.role)
            datamanager.session.expire(old_sql_customer)

            customer_region.delete_all_regions_for_customer(customer_id)

            self.add_regions_to_db(regions, customer_id, datamanager, default_users)
            timestamp = utils.get_time_human()

            new_sql_customer = datamanager.get_customer_by_id(customer_id)

            new_customer_dict = new_sql_customer.get_proxy_dict()

            datamanager.flush()  # i want to get any exception created by this insert

            new_customer_dict["regions"] = self.resolve_regions_actions(old_customer_dict["regions"],
                                                                        new_customer_dict["regions"])

            RdsProxy.send_customer_dict(new_customer_dict, transaction_id, "PUT")
            datamanager.commit()

            base_link = '{0}{1}/'.format(conf.server.host_ip,
                                         pecan.request.path)

            result_regions = [{'id': region.name, 'added': timestamp,
                               'links': {'self': base_link + region.name}} for
                              region in regions]
            region_result_wrapper = RegionResultWrapper(
                transaction_id=transaction_id, regions=result_regions)

            return region_result_wrapper
        except Exception as exp:
            datamanager.rollback()
            raise exp

    def delete_region(self, customer_id, region_id, transaction_id, on_success_by_rds,
                      force_delete):
        datamanager = DataManager()
        try:
            customer_region = datamanager.get_record('customer_region')

            sql_customer = datamanager.get_customer_by_uuid(customer_id)
            if on_success_by_rds and sql_customer is None:
                return
            if sql_customer is None:
                raise ErrorStatus(404,
                                  "customer with id {} does not exist".format(
                                      customer_id))
            customer_dict = sql_customer.get_proxy_dict()

            customer_region.delete_region_for_customer(customer_id, region_id)
            datamanager.flush()  # Get any exception created by this insert

            if on_success_by_rds:
                datamanager.commit()
                LOG.debug("Region {0} in customer {1} deleted".format(region_id,
                                                                      customer_id))
            else:
                region = next((r.region for r in sql_customer.customer_customer_regions if r.region.name == region_id), None)
                if region:
                    if region.type == 'group':
                        set_utils_conf(conf)
                        regions = get_regions_of_group(region.name)
                    else:
                        regions = [region_id]
                for region in customer_dict['regions']:
                    if region['name'] in regions:
                        region['action'] = 'delete'

                RdsProxy.send_customer_dict(customer_dict, transaction_id, "PUT")
                if force_delete:
                    datamanager.commit()
                else:
                    datamanager.rollback()

        except Exception as exp:
            datamanager.rollback()
            raise

        finally:
            datamanager.close()

    def get_customer(self, customer):

        datamanager = DataManager()

        sql_customer = datamanager.get_customer_by_uuid_or_name(customer)

        if not sql_customer:
            raise ErrorStatus(404, 'customer: {0} not found'.format(customer))

        ret_customer = sql_customer.to_wsme()
        if sql_customer.get_real_customer_regions():
            # if we have regions in sql_customer

            resp = requests.get(conf.api.rds_server.base +
                                conf.api.rds_server.status +
                                sql_customer.uuid, verify=conf.verify).json()

            for item in ret_customer.regions:
                for status in resp['regions']:
                    if status['region'] == item.name:
                        item.status = status['status']
                        if status['error_msg']:
                            item.error_message = status['error_msg']
            ret_customer.status = resp['status']
        else:
            ret_customer.status = 'no regions'

        return ret_customer

    def get_customer_list_by_criteria(self, region, user, starts_with, contains,
                                      metadata, start=0, limit=0):
        datamanager = DataManager()
        customer_record = datamanager.get_record('customer')
        sql_customers = customer_record.get_customers_by_criteria(region=region,
                                                                  user=user,
                                                                  starts_with=starts_with,
                                                                  contains=contains,
                                                                  metadata=metadata,
                                                                  start=start,
                                                                  limit=limit)
        response = CustomerSummaryResponse()
        if sql_customers:
            uuids = ','.join(str("\'" + sql_customer.uuid + "\'")
                             for sql_customer in sql_customers if sql_customer and sql_customer.uuid)
            resource_status_dict = customer_record.get_customers_status_by_uuids(uuids)

            for sql_customer in sql_customers:
                customer = CustomerSummary.from_db_model(sql_customer)
                if sql_customer.uuid:
                    status = resource_status_dict.get(sql_customer.uuid)
                    customer.status = not status and 'no regions' or status
                response.customers.append(customer)
        return response

    def enable(self, customer_uuid, enabled, transaction_id):
        try:
            datamanager = DataManager()

            customer_record = datamanager.get_record('customer')
            sql_customer = customer_record.read_customer_by_uuid(customer_uuid)

            if not sql_customer:
                raise ErrorStatus(404, 'customer: {0} not found'.format(customer_uuid))

            sql_customer.enabled = 1 if enabled.enabled else 0

            RdsProxy.send_customer(sql_customer, transaction_id, "PUT")

            datamanager.flush()  # get any exception created by this action
            datamanager.commit()

            customer_result_wrapper = build_response(customer_uuid, transaction_id, 'update')

            return customer_result_wrapper

        except Exception as exp:
            datamanager.rollback()
            raise exp

    def delete_customer_by_uuid(self, customer_id):
        datamanager = DataManager()

        try:
            datamanager.begin_transaction()
            customer_record = datamanager.get_record('customer')

            sql_customer = customer_record.read_customer_by_uuid(customer_id)
            if sql_customer is None:
                raise ErrorStatus(404, "Customer '{0}' not found".format(customer_id))

            real_regions = sql_customer.get_real_customer_regions()
            if len(real_regions) > 0:
                # Do not delete a customer that still has some regions
                raise ErrorStatus(405,
                                  "Cannot delete a customer that has regions. "
                                  "Please delete the regions first and then "
                                  "delete the customer.")
            else:
                expected_status = 'Success'
                invalid_status = 'N/A'
                # Get status from RDS
                resp = RdsProxy.get_status(sql_customer.uuid)
                if resp.status_code == 200:
                    status_resp = resp.json()
                    if 'status' in status_resp.keys():
                        LOG.debug(
                            'RDS returned status: {}'.format(
                                status_resp['status']))
                        status = status_resp['status']
                    else:
                        # Invalid response from RDS
                        LOG.error('Response from RDS did not contain status')
                        status = invalid_status
                elif resp.status_code == 404:
                    # Customer not found in RDS, that means it never had any regions
                    # So it is OK to delete it
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
                    raise ErrorStatus(500, "Could not get customer status")
                elif status != expected_status:
                    raise ErrorStatus(409,
                                      "The customer has not been deleted "
                                      "successfully from all of its regions "
                                      "(either the deletion failed on one of the "
                                      "regions or it is still in progress)")

            # OK to delete
            customer_record.delete_customer_by_uuid(customer_id)

            datamanager.flush()  # i want to get any exception created by this delete
            datamanager.commit()
        except Exception as exp:
            LOG.log_exception("CustomerLogic - Failed to delete customer", exp)
            datamanager.rollback()
            raise


def build_response(customer_uuid, transaction_id, context):
    """
        this function generate th customer action response JSON
    :param customer_uuid:
    :param transaction_id:
    :param context: create or update
    :return:
    """
    # The link should point to the customer itself (/v1/orm/customers/{id})
    link_elements = request.url.split('/')
    base_link = '/'.join(link_elements)
    if context == 'create':
        base_link = base_link + '/' + customer_uuid

    timestamp = utils.get_time_human()
    customer_result_wrapper = CustomerResultWrapper(
        transaction_id=transaction_id,
        id=customer_uuid,
        updated=None,
        created=timestamp,
        links={'self': base_link})
    return customer_result_wrapper
