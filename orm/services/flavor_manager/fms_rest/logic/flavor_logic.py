import uuid

from fms_rest.data.sql_alchemy.db_models import FlavorRegion, FlavorTenant
from fms_rest.data.wsme.models import (ExtraSpecsWrapper, Flavor,
                                       FlavorListFullResponse, FlavorWrapper,
                                       Region, RegionWrapper, TagsWrapper,
                                       TenantWrapper)
from fms_rest.logger import get_logger
from fms_rest.logic.error_base import ConflictError, ErrorStatus, NotFoundError
from orm_common.injector import injector

LOG = get_logger(__name__)

di = injector.get_di()


@di.dependsOn('data_manager')
def create_flavor(flavor, flavor_uuid, transaction_id):
    DataManager = di.resolver.unpack(create_flavor)
    datamanager = DataManager()

    try:
        flavor.flavor.handle_region_groups()
        flavor.flavor.validate_model("create")
        flavor.flavor.id = flavor_uuid
        if not flavor.flavor.ephemeral or flavor.flavor.ephemeral.isspace():
            flavor.flavor.ephemeral = '0'
        flavor.flavor.name = calculate_name(flavor)
        LOG.debug("Flavor name is [{}] ".format(flavor.flavor.name))

        sql_flavor = flavor.to_db_model()

        flavor_rec = datamanager.get_record('flavor')

        datamanager.begin_transaction()

        flavor_rec.insert(sql_flavor)
        datamanager.flush()  # i want to get any exception created by this insert
        existing_region_names = []
        send_to_rds_if_needed(sql_flavor, existing_region_names, "post", transaction_id)

        datamanager.commit()

        ret_flavor = get_flavor_by_uuid(flavor_uuid)
        return ret_flavor

    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to CreateFlavor", exp)
        datamanager.rollback()
        if "Duplicate entry" in str(exp.message):
            raise ConflictError(409, "Flavor {} already exists".format(flavor.flavor.name))
        raise
    finally:
        datamanager.close()


@di.dependsOn('rds_proxy')
def send_to_rds_if_needed(sql_flavor, existing_region_names, http_action, transaction_id):
    rds_proxy = di.resolver.unpack(send_to_rds_if_needed)
    if (sql_flavor.flavor_regions and len(sql_flavor.flavor_regions) > 0) or len(existing_region_names) > 0:
        flavor_dict = sql_flavor.todict()
        update_region_actions(flavor_dict, existing_region_names, http_action)
        LOG.debug("Flavor is valid to send to RDS - sending to RDS Proxy ")
        rds_proxy.send_flavor(flavor_dict, transaction_id, http_action)
    else:
        LOG.debug("Flavor with no regions - wasn't sent to RDS Proxy " + str(sql_flavor))


@di.dependsOn('data_manager')
def update_flavor(flavor, flavor_uuid, transaction_id):  # pragma: no cover
    DataManager = di.resolver.unpack(update_flavor)
    datamanager = DataManager()

    try:
        flavor.validate_model("update")

        sql_flavor = flavor.to_db_model()
        sql_flavor.id = flavor_uuid
        sql_flavor.name = calculate_name(flavor)
        LOG.debug("Flavor name is [{}] ".format(sql_flavor.name))

        datamanager.begin_transaction()
        flavor_rec = datamanager.get_record('flavor')
        db_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if db_flavor is None:
            raise Exception("Flavor {0} not found".format(flavor_uuid))

        existing_region_names = db_flavor.get_existing_region_names()

        flavor_rec.delete_by_uuid(flavor_uuid)
        del(db_flavor)

        flavor_rec.insert(sql_flavor)
        datamanager.flush()  # i want to get any exception created by this insert method

        send_to_rds_if_needed(sql_flavor, existing_region_names, "put", transaction_id)

        datamanager.commit()

        ret_flavor = get_flavor_by_uuid(flavor_uuid)
        return ret_flavor

    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to update flavor", exp)
        datamanager.rollback()
        raise
    finally:
        datamanager.close()


@di.dependsOn('rds_proxy')
@di.dependsOn('data_manager')
def delete_flavor_by_uuid(flavor_uuid):  # , transaction_id):
    rds_proxy, DataManager = di.resolver.unpack(delete_flavor_by_uuid)
    datamanager = DataManager()

    try:
        datamanager.begin_transaction()
        flavor_rec = datamanager.get_record('flavor')

        sql_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if sql_flavor is None:
            # The flavor does not exist, so the delete operation is
            # considered successful
            return

        existing_region_names = sql_flavor.get_existing_region_names()
        if len(existing_region_names) > 0:
            # Do not delete a flavor that still has some regions
            msg = "Cannot delete a flavor that has regions. " \
                  "Please delete the regions first and then " \
                  "delete the flavor."
            LOG.info(msg)
            raise ErrorStatus(405, msg)
        else:
            expected_status = 'Success'
            invalid_status = 'N/A'
            # Get status from RDS
            resp = rds_proxy.get_status(sql_flavor.id)
            if resp.status_code == 200:
                status_resp = resp.json()
                if 'status' in status_resp.keys():
                    LOG.debug(
                        'RDS returned status: {}'.format(status_resp['status']))
                    status = status_resp['status']
                else:
                    # Invalid response from RDS
                    LOG.warning('Response from RDS did not contain status')
                    status = invalid_status
            elif resp.status_code == 404:
                # Flavor not found in RDS, that means it never had any regions
                # So it is OK to delete it
                LOG.debug('Resource not found in RDS, so it is OK to delete')
                status = expected_status
            else:
                # Invalid status code from RDS
                LOG.warning('Invalid response code from RDS: {}'.format(
                    resp.status_code))
                status = invalid_status

            if status == invalid_status:
                LOG.error('Invalid flavor status received from RDS')
                raise ErrorStatus(500, "Invalid flavor status received from RDS")
            elif status != expected_status:
                msg = "The flavor has not been deleted " \
                      "successfully from all of its regions " \
                      "(either the deletion failed on one of the " \
                      "regions or it is still in progress)"
                LOG.error('Invalid flavor status received from RDS')
                raise ErrorStatus(409, msg)

        # OK to delete
        flavor_rec.delete_by_uuid(flavor_uuid)

        datamanager.flush()  # i want to get any exception created by this delete
        datamanager.commit()
    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to delete flavor", exp)
        datamanager.rollback()
        raise
    finally:
        datamanager.close()


@di.dependsOn('data_manager')
def add_regions(flavor_uuid, regions, transaction_id):
    DataManager = di.resolver.unpack(add_regions)
    datamanager = DataManager()

    try:
        flavor_rec = datamanager.get_record('flavor')
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if not sql_flavor:
            raise ErrorStatus(404, 'flavor id {0} not found'.format(flavor_uuid))

        existing_region_names = sql_flavor.get_existing_region_names()

        for region in regions.regions:
            if region.name == '' or region.name.isspace():
                raise ErrorStatus(400, 'Cannot add region with an empty name')
            if region.type == "group":
                raise ErrorStatus(400, 'Adding \'group\' type region is supported only when creating a flavor')
            db_region = FlavorRegion(region_name=region.name, region_type='single')
            sql_flavor.add_region(db_region)

        datamanager.flush()  # i want to get any exception created by previous actions against the database

        send_to_rds_if_needed(sql_flavor, existing_region_names, "put", transaction_id)

        datamanager.commit()

        flavor = get_flavor_by_uuid(flavor_uuid)
        ret = RegionWrapper(regions=flavor.flavor.regions)
        return ret

    except ErrorStatus as exp:
        LOG.log_exception("FlavorLogic - Failed to update flavor", exp)
        datamanager.rollback()
        raise exp
    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to add regions", exp)
        datamanager.rollback()
        if "conflicts with persistent instance" in str(exp.message):
            raise ConflictError(409, "One or more regions already exists in Flavor")
        raise exp
    finally:
        datamanager.close()


@di.dependsOn('data_manager')
def delete_region(flavor_uuid, region_name, transaction_id):
    DataManager = di.resolver.unpack(delete_region)
    datamanager = DataManager()

    try:
        flavor_rec = datamanager.get_record('flavor')
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if not sql_flavor:
            raise ErrorStatus(404, 'flavor id {0} not found'.format(flavor_uuid))

        existing_region_names = sql_flavor.get_existing_region_names()

        sql_flavor.remove_region(region_name)

        datamanager.flush()  # i want to get any exception created by previous actions against the database
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put", transaction_id)

        datamanager.commit()

    except ErrorStatus as exp:
        LOG.log_exception("FlavorLogic - Failed to update flavor", exp)
        datamanager.rollback()
        raise exp
    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to delete region", exp)
        datamanager.rollback()
        raise exp
    finally:
        datamanager.close()


@di.dependsOn('data_manager')
def add_tenants(flavor_uuid, tenants, transaction_id):
    DataManager = di.resolver.unpack(add_tenants)
    datamanager = DataManager()

    try:
        flavor_rec = datamanager.get_record('flavor')
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if not sql_flavor:
            raise ErrorStatus(404, 'Flavor id {0} not found'.format(flavor_uuid))

        if sql_flavor.visibility == "public":
            raise ErrorStatus(405, 'Cannot add tenant to a public flavor')

        existing_region_names = sql_flavor.get_existing_region_names()

        for tenant in tenants.tenants:
            if not isinstance(tenant, basestring):
                raise ValueError("tenant type must be a string type, got {} type".format(type(tenant)))

            db_tenant = FlavorTenant(tenant_id=tenant)
            sql_flavor.add_tenant(db_tenant)

        datamanager.flush()  # i want to get any exception created by previous actions against the database
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put", transaction_id)
        datamanager.commit()

        flavor = get_flavor_by_uuid(flavor_uuid)
        ret = TenantWrapper(tenants=flavor.flavor.tenants)
        return ret

    except (ErrorStatus, ValueError) as exp:
        LOG.log_exception("FlavorLogic - Failed to update flavor", exp)
        datamanager.rollback()
        raise
    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Failed to add tenants", exp)
        if "conflicts with persistent instance" in str(exp.message):
            raise ConflictError(409, "One or more tenants already exist")
        raise
    finally:
        datamanager.close()


@di.dependsOn('data_manager')
def delete_tenant(flavor_uuid, tenant_id, transaction_id):
    DataManager = di.resolver.unpack(delete_tenant)
    datamanager = DataManager()

    try:
        flavor_rec = datamanager.get_record('flavor')
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_uuid)
        if not sql_flavor:
            raise ErrorStatus(404, 'flavor id {0} not found'.format(flavor_uuid))
        # if trying to delete the only one tenant then return value error
        if sql_flavor.visibility == "public":
            raise ValueError("{} is a public flavor, delete tenant action is not relevant".format(flavor_uuid))

        if len(sql_flavor.flavor_tenants) == 1 and sql_flavor.flavor_tenants[0].tenant_id == tenant_id:
            raise ValueError(
                'Private flavor must have at least one tenant')

        existing_region_names = sql_flavor.get_existing_region_names()
        sql_flavor.remove_tenant(tenant_id)

        datamanager.flush()  # i want to get any exception created by previous actions against the database
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put", transaction_id)
        datamanager.commit()

    except ErrorStatus as exp:
        LOG.log_exception("FlavorLogic - Failed to update flavor", exp)
        datamanager.rollback()
        raise
    except Exception as exp:
        LOG.log_exception("FlavorLogic - Failed to delete tenant", exp)
        datamanager.rollback()
        raise
    finally:
        datamanager.close()


def extra_spec_in_default(extra_spec, default_extra_specs):
    for default_extra_spec in default_extra_specs:
        if extra_spec == default_extra_spec.key_name:
            return True
    return False


@di.dependsOn('data_manager')
def get_extra_specs_uuid(flavor_id, transaction_id):
    DataManager = di.resolver.unpack(get_extra_specs_uuid)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - get extra specs")
        datamanager.begin_transaction()

        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, 'flavor id {0} not found'.format(
                flavor_id))

        result = ExtraSpecsWrapper.from_db_model(sql_flavor.flavor_extra_specs)

    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor Not Found", exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor Not Found", exp)
        raise
    finally:
        datamanager.close()

    return result


@di.dependsOn('data_manager')
def delete_extra_specs(flavor_id, transaction_id, extra_spec=None):
    DataManager = di.resolver.unpack(delete_extra_specs)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - delete extra specs")
        datamanager.begin_transaction()

        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, 'flavor id {0} not found'.format(
                flavor_id))

        existing_region_names = sql_flavor.get_existing_region_names()
        # calculate default flavor extra
        flavor_wrapper = FlavorWrapper.from_db_model(sql_flavor)
        default_extra_specs = flavor_wrapper.get_extra_spec_needed()
        # check if delete all or one
        if extra_spec:
            if not extra_spec_in_default(extra_spec, default_extra_specs):
                sql_flavor.remove_extra_spec(extra_spec)
            else:
                raise ErrorStatus(400,
                                  "Bad request, this key cannot be deleted")
        else:
            sql_flavor.delete_all_extra_specs()
            sql_flavor.add_extra_specs(default_extra_specs)

        datamanager.flush()  # i want to get any exception created by previous actions against the database
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put",
                              transaction_id)
        datamanager.commit()

    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor not found", exp)
        raise

    except ErrorStatus as exp:
        datamanager.rollback()
        LOG.log_exception("error in adding extra specs", exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - fail to delete extra spec", exp)
        raise
    finally:
        datamanager.close()

    return


@di.dependsOn('data_manager')
@di.dependsOn('rds_proxy')
def get_tags(flavor_uuid):
    DataManager, rds_proxy = di.resolver.unpack(get_flavor_by_uuid)

    datamanager = DataManager()
    flavor_record = datamanager.get_record('flavor')

    sql_flavor = flavor_record.get_flavor_by_id(flavor_uuid)

    if not sql_flavor:
        raise ErrorStatus(404, 'flavor id {0} not found'.format(flavor_uuid))

    flavor_wrapper = FlavorWrapper.from_db_model(sql_flavor)
    datamanager.close()

    return flavor_wrapper.flavor.tag


@di.dependsOn('data_manager')
def delete_tags(flavor_id, tag, transaction_id):
    DataManager = di.resolver.unpack(delete_tags)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - delete tags")
        datamanager.begin_transaction()

        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, 'flavor id {0} not found'.format(flavor_id))

        if tag:
            sql_flavor.remove_tag(tag)
        else:
            sql_flavor.remove_all_tags()

        datamanager.flush()
        datamanager.commit()

    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor not found", exp)
        raise

    except ErrorStatus as exp:
        if exp.status_code == 404:
            LOG.log_exception("FlavorLogic - Tag not found", exp)
            # Do not raise an exception if the tag was not found
            return
        else:
            LOG.log_exception("FlavorLogic - failed to delete tags", exp)
            raise

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - failed to delete tags", exp)
        raise
    finally:
        datamanager.close()


@di.dependsOn('data_manager')
def update_tags(flavor_id, tags, transaction_id):
    DataManager = di.resolver.unpack(update_tags)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - update tags")
        datamanager.begin_transaction()
        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, "flavor id {} not found".format(
                flavor_id))

        tags_models = tags.to_db_model()
        sql_flavor.replace_tags(tags_models)

        datamanager.flush()
        datamanager.commit()

        # create return json to wsme
        result = TagsWrapper.from_db_model(tags_models)
    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("flavor id {} not found".format(flavor_id), exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("failed to update tags", exp)
        raise
    finally:
        datamanager.close()

    return result


@di.dependsOn('data_manager')
def add_extra_specs(flavor_id, extra_specs, transaction_id):
    DataManager = di.resolver.unpack(add_extra_specs)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - add extra specs")
        datamanager.begin_transaction()

        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, 'flavor id {0} not found'.format(
                flavor_id))

        existing_region_names = sql_flavor.get_existing_region_names()
        extra_specs_model = extra_specs.to_db_model()

        sql_flavor.add_extra_specs(extra_specs_model)
        datamanager.flush()  # i want to get any exception created by previous actions against the database
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put",
                              transaction_id)
        datamanager.commit()

        # create return json to wsme
        result = ExtraSpecsWrapper.from_db_model(sql_flavor.flavor_extra_specs)
    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor Not Found", exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        if "conflicts with persistent instance" in str(exp.message):
            raise ConflictError(409, "one or all extra specs {} already exists".format(extra_specs.os_extra_specs))
        LOG.log_exception("FlavorLogic - fail to add extra spec", exp)
        raise
    finally:
        datamanager.close()

    return result


@di.dependsOn('data_manager')
def update_extra_specs(flavor_id, extra_specs, transaction_id):
    DataManager = di.resolver.unpack(update_extra_specs)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - update extra specs")
        datamanager.begin_transaction()
        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, "flavor id {} not found".format(
                flavor_id))

        extra_specs_models = extra_specs.to_db_model()
        existing_region_names = sql_flavor.get_existing_region_names()

        # remove old extra specs
        sql_flavor.delete_all_extra_specs()
        # calculate default flavor extra
        flavor_wrapper = FlavorWrapper.from_db_model(sql_flavor).to_db_model()
        default_extra_specs = flavor_wrapper.flavor_extra_specs

        # add default extra specs to user extra specs and add to DB
        extra_specs_models += default_extra_specs
        sql_flavor.add_extra_specs(extra_specs_models)

        # get exception if there is any from previous action with the database
        datamanager.flush()
        send_to_rds_if_needed(sql_flavor, existing_region_names, "put",
                              transaction_id)
        LOG.debug("extra specs updated and sent to rds")
        datamanager.commit()

        # create return json to wsme
        result = ExtraSpecsWrapper.from_db_model(extra_specs_models)
    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("flavor id {} not found".format(flavor_id), exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        LOG.log_exception("failed to update extra specs", exp)
        raise
    finally:
        datamanager.close()

    return result


@di.dependsOn('data_manager')
@di.dependsOn('rds_proxy')
def get_flavor_by_uuid(flavor_uuid):
    DataManager, rds_proxy = di.resolver.unpack(get_flavor_by_uuid)

    datamanager = DataManager()
    flavor_record = datamanager.get_record('flavor')

    sql_flavor = flavor_record.get_flavor_by_id(flavor_uuid)

    if not sql_flavor:
        raise ErrorStatus(404, 'flavor id {0} not found'.format(flavor_uuid))

    flavor_wrapper = FlavorWrapper.from_db_model(sql_flavor)

    update_region_statuses(flavor_wrapper.flavor, sql_flavor)
    return flavor_wrapper


@di.dependsOn('data_manager')
def add_tags(flavor_id, tags, transaction_id):
    DataManager = di.resolver.unpack(add_tags)
    datamanager = DataManager()

    try:
        LOG.debug("LOGIC - add tags")
        datamanager.begin_transaction()

        flavor_rec = datamanager.get_record("flavor")
        sql_flavor = flavor_rec.get_flavor_by_id(flavor_id)

        if not sql_flavor:
            raise NotFoundError(404, 'flavor id {0} not found'.format(
                flavor_id))

        tags_model = tags.to_db_model()
        sql_flavor.add_tags(tags_model)

        datamanager.flush()
        datamanager.commit()

        # create return json to wsme
        result = TagsWrapper.from_db_model(sql_flavor.flavor_tags)
    except NotFoundError as exp:
        datamanager.rollback()
        LOG.log_exception("FlavorLogic - Flavor Not Found", exp)
        raise

    except Exception as exp:
        datamanager.rollback()
        if "conflicts with persistent instance" in str(exp.message):
            raise ConflictError(409, "one or all tags {} already exists".format(
                tags.tags))
        LOG.log_exception("FlavorLogic - fail to add tags", exp)
        raise
    finally:
        datamanager.close()

    return result


@di.dependsOn('data_manager')
@di.dependsOn('rds_proxy')
def get_flavor_by_uuid_or_name(flavor_uuid_or_name):
    DataManager, rds_proxy = di.resolver.unpack(get_flavor_by_uuid)

    datamanager = DataManager()

    try:

        flavor_record = datamanager.get_record('flavor')

        sql_flavor = flavor_record.get_flavor_by_id_or_name(flavor_uuid_or_name)

        if not sql_flavor:
            raise ErrorStatus(404, 'flavor with id or name {0} not found'.format(flavor_uuid_or_name))

        flavor_wrapper = FlavorWrapper.from_db_model(sql_flavor)

        update_region_statuses(flavor_wrapper.flavor, sql_flavor)
    except Exception as exp:
        LOG.log_exception("Failed to get_flavor_by_uuid_or_name", exp)
        raise
    finally:
        datamanager.close()

    return flavor_wrapper


@di.dependsOn('rds_proxy')
def update_region_statuses(flavor, sql_flavor):
    rds_proxy = di.resolver.unpack(update_region_statuses)

    # remove the regions comes from database and return the regions which return from rds,
    # because there might be group region there (in the db) and in the response from the
    # rds we will have a list of all regions belong to this group
    flavor.regions[:] = []
    resp = rds_proxy.get_status(sql_flavor.id)
    if resp.status_code == 200:
        status_resp = resp.json()
        if sql_flavor.flavor_regions and len(sql_flavor.flavor_regions) > 0:
            if 'regions' in status_resp.keys():
                for region_status in status_resp['regions']:
                    flavor.regions.append(
                        Region(name=region_status['region'], type="single",
                               status=region_status['status'],
                               error_message=region_status['error_msg']))

        if 'status' in status_resp.keys():
            flavor.status = status_resp['status']
    elif resp.status_code == 404:
        flavor.status = "Success"
    else:
        flavor.status = "N/A"


@di.dependsOn('data_manager')
@di.dependsOn('rds_proxy')
def get_flavor_list_by_params(visibility, region, tenant, series, starts_with, contains, alias):
    DataManager, rds_proxy = di.resolver.unpack(get_flavor_list_by_params)

    datamanager = DataManager()

    try:
        flavor_record = datamanager.get_record('flavor')
        sql_flavors = flavor_record.get_flavors_by_criteria(visibility=visibility,
                                                            region=region,
                                                            tenant=tenant,
                                                            series=series,
                                                            starts_with=starts_with,
                                                            contains=contains,
                                                            alias=alias)

        response = FlavorListFullResponse()
        for sql_flavor in sql_flavors:
            flavor = Flavor.from_db_model(sql_flavor)
            update_region_statuses(flavor, sql_flavor)
            response.flavors.append(flavor)
    except Exception as exp:
        LOG.log_exception("Fail to get_flavor_list_by_params", exp)
        raise
    finally:
        datamanager.close()

    return response


def calculate_name(flavor):
    name = "{0}.c{1}r{2}d{3}".format(flavor.flavor.series, flavor.flavor.vcpus,
                                     int(flavor.flavor.ram) / 1024,
                                     flavor.flavor.disk)

    swap = getattr(flavor.flavor, 'swap', 0)
    if swap and int(swap):
        name += '{}{}'.format('s', int(swap) / 1024)

    ephemeral = getattr(flavor.flavor, 'ephemeral', 0)
    if ephemeral and int(ephemeral):
        name += '{}{}'.format('e', ephemeral)

    if len(flavor.flavor.options) > 0:
        name += '.'
        for key in sorted(flavor.flavor.options.iterkeys()):
            name += key

    return name


def update_region_actions(flavor_dict, existing_region_names, action="put"):
    if action == "delete":
        set_regions_action(flavor_dict, "delete")
    elif action == "post":
        set_regions_action(flavor_dict, "create")
    else:  # put
        for region in flavor_dict["regions"]:
            if region["name"] in existing_region_names:
                region["action"] = "modify"
            else:
                region["action"] = "create"

        # add deleted regions
        for exist_region_name in existing_region_names:
            if region_name_exist_in_regions(exist_region_name, flavor_dict["regions"]):
                continue
            else:
                flavor_dict["regions"].append({"name": exist_region_name, "action": "delete"})


def region_name_exist_in_regions(region_name, regions):
    for region in regions:
        if region["name"] == region_name:
            return True
    return False


def set_regions_action(flavor_dict, action):
    for region in flavor_dict["regions"]:
        region["action"] = action


def get_fixed_uuid(uuid_to_fix):
    """Fix a version 4 UUID."""
    try:
        new_uuid = uuid.UUID(uuid_to_fix, version=4)
        if (uuid_to_fix == new_uuid.hex) or (uuid_to_fix == str(new_uuid)):
            # It is a version 4 UUID, remove its dashes
            return new_uuid.hex
    except ValueError:
        # Not a UUID (of any version)
        pass

    raise ErrorStatus(400, 'Flavor ID must be a version 4 UUID!')
