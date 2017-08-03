"""DB actions wrapper module."""
import logging

from rms.model.model import Groups, Regions
from rms.services import error_base
from rms.storage import base_data_manager, data_manager_factory

LOG = logging.getLogger(__name__)


def get_regions_data(url_parms):
    """get region from db.

    :param url_parms: the parameters got in the url to make the query
    :return: region model for json output
    :raise: NoContentError( status code 404)
    """
    region_dict, metadata_dict, end_point = url_parms._build_query()
    db = data_manager_factory.get_data_manager()
    regions = db.get_regions(region_dict, metadata_dict, end_point)
    if not regions:
        raise error_base.NotFoundError(message="No regions found for the given search parameters")
    return Regions(regions)


def get_region_by_id_or_name(region_id_or_name):
    """get region by id

    :param region_id_or_name:
    :return: region object (wsme format)
    """
    LOG.debug("LOGIC:- get region data by id or name {}".format(region_id_or_name))
    try:
        db = data_manager_factory.get_data_manager()
        region = db.get_region_by_id_or_name(region_id_or_name)

        if not region:
            raise error_base.NotFoundError(message="Region {} not found".format(region_id_or_name))

    except Exception as exp:
        LOG.exception("error in get region by id/name")
        raise

    return region


def update_region(region_id, region):
    """update region
    :param region:
    :return:
    """
    LOG.debug("logic:- update region {}".format(region))
    try:

        region = region._to_clean_python_obj()
        region._validate_model()
        region_dict = region._to_db_model_dict()

        db = data_manager_factory.get_data_manager()
        db.update_region(region_to_update=region_id, **region_dict)
        LOG.debug("region {} updated".format(region_id))
        result = get_region_by_id_or_name(region_id)

    except error_base.NotFoundError as exp:
        LOG.exception("fail to update region {}".format(exp.message))
        raise
    except Exception as exp:
        LOG.exception("fail to update region {}".format(exp))
        raise
    return result


def delete_region(region_id):
    """delete region

    :param region_id:
    :return:
    """
    LOG.debug("logic:- delete region {}".format(region_id))
    try:
        db = data_manager_factory.get_data_manager()
        db.delete_region(region_id)
        LOG.debug("region deleted")
    except Exception as exp:
        LOG.exception("fail to delete region {}".format(exp))
        raise
    return


def create_full_region(full_region):
    """create region logic.

    :param full_region obj:
    :return:
    :raise: input value error(status code 400)
    """
    LOG.debug("logic:- save region ")
    try:

        full_region = full_region._to_clean_python_obj()
        full_region._validate_model()

        full_region_db_dict = full_region._to_db_model_dict()
        LOG.debug("region to save {}".format(full_region_db_dict))
        db = data_manager_factory.get_data_manager()
        db.add_region(**full_region_db_dict)
        LOG.debug("region added")
        result = get_region_by_id_or_name(full_region.id)

    except error_base.InputValueError as exp:
        LOG.exception("error in save region {}".format(exp.message))
        raise
    except base_data_manager.DuplicateEntryError as exp:
        LOG.exception("error in save region {}".format(exp.message))
        raise error_base.ConflictError(message=exp.message)
    except Exception as exp:
        LOG.exception("error in save region {}".format(exp.message))
        raise

    return result


def add_region_metadata(region_id, metadata_dict):
    LOG.debug("Add metadata: {} to region id : {}".format(metadata_dict,
                                                          region_id))
    try:
        db = data_manager_factory.get_data_manager()
        result = db.add_meta_data_to_region(region_id, metadata_dict)
        if not result:
            raise error_base.NotFoundError(message="Region {} not found".format(region_id))
        else:
            return result.metadata

    except Exception as exp:
        LOG.exception("Error getting metadata for region id:".format(region_id))
        raise


def update_region_metadata(region_id, metadata_dict):
    LOG.debug("Update metadata to region id : {}. "
              "New metadata: {}".format(region_id, metadata_dict))
    try:
        db = data_manager_factory.get_data_manager()
        result = db.update_region_meta_data(region_id, metadata_dict)
        if not result:
            raise error_base.NotFoundError(message="Region {} not "
                                                   "found".format(region_id))
        else:
            return result.metadata

    except Exception as exp:
        LOG.exception("Error getting metadata for region id:".format(region_id))
        raise


def delete_metadata_from_region(region_id, metadata_key):
    LOG.info("Delete metadata key: {} from region id : {}."
             .format(metadata_key, region_id))
    try:
        db = data_manager_factory.get_data_manager()
        db.delete_region_metadata(region_id, metadata_key)

    except Exception as exp:
        LOG.exception("Error getting metadata for region id:".format(region_id))
        raise


def get_groups_data(name):
    """get group from db.

    :param name: groupe name
    :return: groupe object with its regions
    :raise: NoContentError( status code 404)
    """
    db = data_manager_factory.get_data_manager()
    groups = db.get_group(name)
    if not groups:
        raise error_base.NotFoundError(message="Group {} not found".format(name))
    return Groups(**groups)


def get_all_groups():
    """list all groups

    :return:
    """
    try:
        LOG.debug("logic - get all groups")
        db = data_manager_factory.get_data_manager()
        all_groups = db.get_all_groups()
        LOG.debug("logic - got all groups {}".format(all_groups))

    except Exception as exp:
        LOG.error("fail to get all groups")
        LOG.exception(exp)
        raise

    return all_groups


def delete_group(group_id):
    """delete group

    :param group_id:
    :return:
    """
    LOG.debug("delete group logic")
    try:

        db = data_manager_factory.get_data_manager()
        LOG.debug("delete group id {} from db".format(group_id))
        db.delete_group(group_id)

    except Exception as exp:
        LOG.exception(exp)
        raise
    return


def create_group_in_db(group_id, group_name, description, regions):
    """Create a region group in the database.

    :param group_id: The ID of the group to create
    :param group_name: The name of the group to create
    :param description: The group description
    :param regions: A list of regions inside the group
    :raise: GroupExistsError (status code 400) if the group already exists
    """
    try:
        manager = data_manager_factory.get_data_manager()
        manager.add_group(group_id, group_name, description, regions)
    except error_base.ConflictError:
        LOG.exception("Group {} already exists".format(group_id))
        raise error_base.ConflictError(
            message="Group {} already exists".format(group_id))
    except error_base.InputValueError:
        LOG.exception("Some of the regions not found")
        raise error_base.NotFoundError(
            message="Some of the regions not found")


def update_group(group, group_id):
    result = None
    LOG.debug("update group logic")
    try:
        group = group._to_python_obj()
        db_manager = data_manager_factory.get_data_manager()
        LOG.debug("update group to {}".format(group._to_db_model_dict()))
        db_manager.update_group(group_id=group_id, **group._to_db_model_dict())
        LOG.debug("group updated")
        # make sure it updated
        groups = db_manager.get_group(group_id)

    except error_base.NotFoundError:
        LOG.error("Group {} not found")
        raise
    except error_base.InputValueError:
        LOG.exception("Some of the regions not found")
        raise error_base.NotFoundError(
            message="Some of the regions not found")
    except Exception as exp:
        LOG.error("Failed to update group {}".format(group.group_id))
        LOG.exception(exp)
        raise

    return Groups(**groups)


def update_region_status(region_id, new_status):
    """Update region.

    :param region_id:
    :param new_status:
    :return:
    """
    LOG.debug("Update region id: {} status to: {}".format(region_id,
                                                          new_status))
    try:
        db = data_manager_factory.get_data_manager()
        result = db.update_region_status(region_id, new_status)
        return result

    except Exception as exp:
        LOG.exception("Error updating status for region id:".format(region_id))
        raise
