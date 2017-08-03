import logging

import oslo_db
from data_models import (Group, GroupRegion, Region, RegionEndPoint,
                         RegionMetaData)
from oslo_db.sqlalchemy import session as db_session
from rms.model import model as PythonModels
from rms.services import error_base as ServiceBase
from rms.storage.base_data_manager import (BaseDataManager,
                                           DuplicateEntryError, EntityNotFound)
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.sql import or_

Base = declarative_base()
logger = logging.getLogger(__name__)


class DataManager(BaseDataManager):

    def __init__(self, url, max_retries, retries_interval):
        self._engine_facade = db_session.EngineFacade(url,
                                                      max_retries=max_retries,
                                                      retry_interval=retries_interval)

    def add_region(self,
                   region_id,
                   name,
                   address_state,
                   address_country,
                   address_city,
                   address_street,
                   address_zip,
                   region_status,
                   ranger_agent_version,
                   open_stack_version,
                   design_type,
                   location_type,
                   vlcp_name,
                   clli,
                   # a list of dictionaries of format
                   # {"type":"", "url":"", "description":""
                   end_point_list,
                   # a dictionary of key,value pairs
                   # {"key":"value", }
                   meta_data_dict,
                   description=""):
        """ add a new region to the `region` table
        add also the regions give meta_data and end_points to the `region_end_point` and
        `region_meta_data` tables if given.
        handle duplicate errors if raised
        """
        try:
            session = self._engine_facade.get_session()
            with session.begin():
                region = Region(region_id=region_id,
                                name=name,
                                address_state=address_state,
                                address_country=address_country,
                                address_city=address_city,
                                address_street=address_street,
                                address_zip=address_zip,
                                region_status=region_status,
                                ranger_agent_version=ranger_agent_version,
                                open_stack_version=open_stack_version,
                                design_type=design_type,
                                location_type=location_type,
                                vlcp_name=vlcp_name,
                                clli=clli,
                                description=description)

                if end_point_list is not None:
                    for end_point in end_point_list:
                        region_end_point = RegionEndPoint(
                            end_point_type=end_point["type"],
                            public_url=end_point["url"])
                        region.end_points.append(region_end_point)

                if meta_data_dict is not None:
                    for k, v in meta_data_dict.iteritems():
                        for list_item in v:
                            region.meta_data.append(
                                RegionMetaData(region_id=region_id,
                                               meta_data_key=k,
                                               meta_data_value=list_item))

                session.add(region)
        except oslo_db.exception.DBDuplicateEntry as e:
            logger.warning("Duplicate entry: {}".format(str(e)))
            raise DuplicateEntryError("Region {} already "
                                      "exist".format(region_id))

    def update_region(self,
                      region_to_update,
                      region_id,
                      name,
                      address_state,
                      address_country,
                      address_city,
                      address_street,
                      address_zip,
                      region_status,
                      ranger_agent_version,
                      open_stack_version,
                      design_type,
                      location_type,
                      vlcp_name,
                      clli,
                      # a list of dictionaries of format
                      # {"type":"", "url":"", "description":""
                      end_point_list,
                      # a list of dictionaries of format
                      # {"key":"", "value":"", "description":""
                      meta_data_dict,
                      description=""):
        """ add a new region to the `region` table
        add also the regions give meta_data and end_points to the `region_end_point` and
        `region_meta_data` tables if given.
        handle duplicate errors if raised
        """
        try:
            session = self._engine_facade.get_session()
            with session.begin():
                # remove all childs as with update need to replace them
                session.query(RegionMetaData).filter_by(region_id=region_to_update).delete()
                session.query(RegionEndPoint).filter_by(region_id=region_to_update).delete()

                record = session.query(Region).filter_by(region_id=region_to_update).first()
                if record is not None:
                    #   record.region_id = region_id  # ignore id and name when update
                    #   record.name = name
                    record.address_state = address_state
                    record.address_country = address_country
                    record.address_city = address_city
                    record.address_street = address_street
                    record.address_zip = address_zip
                    record.region_status = region_status
                    record.ranger_agent_version = ranger_agent_version
                    record.open_stack_version = open_stack_version
                    record.design_type = design_type
                    record.location_type = location_type
                    record.vlcp_name = vlcp_name
                    record.clli = clli
                    record.description = description

                    if end_point_list is not None:
                        for end_point in end_point_list:
                            region_end_point = RegionEndPoint(
                                end_point_type=end_point["type"],
                                public_url=end_point["url"]
                            )
                            record.end_points.append(region_end_point)

                    if meta_data_dict is not None:
                        for k, v in meta_data_dict.iteritems():
                            for list_item in v:
                                record.meta_data.append(
                                    RegionMetaData(region_id=region_id,
                                                   meta_data_key=k,
                                                   meta_data_value=list_item))
                else:
                    raise EntityNotFound("Region {} not found".format(
                        region_to_update))
        except EntityNotFound as exp:
            logger.exception(
                "fail to update entity with id {} not found".format(
                    region_to_update))
            raise ServiceBase.NotFoundError(message=exp.message)
        except Exception as exp:
            logger.exception("fail to update region {}".format(str(exp)))
            raise

    def delete_region(self, region_id):
        # delete a region from `region` table and also the region's
        # entries from `region_meta_data` and `region_end_points` tables
        session = self._engine_facade.get_session()
        with session.begin():
            session.query(Region).filter_by(region_id=region_id).delete()

    def get_all_regions(self):
        return self.get_regions(None, None, None)

    def get_regions(self,
                    region_filters_dict,
                    meta_data_dict,
                    end_point_dict):
        logger.debug("Get regions")
        records_model = []
        session = self._engine_facade.get_session()
        with session.begin():
            records = session.query(Region)
            if region_filters_dict is not None:
                records = records.filter_by(**region_filters_dict)

            if meta_data_dict is not None:
                regions = self._get_regions_for_meta_data_dict(meta_data_dict,
                                                               session)
                query = []
                query.append((Region.region_id.in_(regions)))
                records = records.filter(*query)

            if end_point_dict is not None:
                records = records.join(RegionEndPoint).\
                    filter_by(**end_point_dict)
            if records is not None:
                for record in records:
                    records_model.append(record.to_wsme())
            return records_model

    def _get_regions_for_meta_data_dict(self, meta_data_dict, session):
        result_lists = []
        for key in meta_data_dict['meta_data_keys']:
            md_q = session.query(RegionMetaData). \
                filter(RegionMetaData.meta_data_key == key).all()
            temp_result_list = []
            if md_q is not None:
                for record in md_q:
                    temp_result_list.append(record.region_id)
            result_lists.append(set(temp_result_list))
            logger.debug(set(temp_result_list))
        for item in meta_data_dict['meta_data_pairs']:
            md_q = session.query(RegionMetaData). \
                filter(RegionMetaData.meta_data_key == item['metadata_key'],
                       RegionMetaData.meta_data_value == item['metadata_value']).all()
            temp_result_list = []
            if md_q is not None:
                for record in md_q:
                    temp_result_list.append(record.region_id)
            result_lists.append(set(temp_result_list))
            logger.debug(set(temp_result_list))

        result = []
        if result_lists:
            result = result_lists[0]
            for l in result_lists:
                result = result.intersection(l)
        else:
            result = None
        logger.debug(result)
        return result

    def get_region_by_id_or_name(self, region_id_or_name):
        logger.debug("Get region by id or name: {}".format(region_id_or_name))
        try:

            session = self._engine_facade.get_session()
            with session.begin():
                record = session.query(Region)
                record = record.filter(or_(Region.region_id == region_id_or_name,
                                           Region.name == region_id_or_name))
                if record.first():
                    return record.first().to_wsme()
                return None

        except Exception as exp:
            logger.exception("DB error filtering by id/name")
            raise

    def add_meta_data_to_region(self, region_id,
                                metadata_dict):
        """add metadata
        :param region_id:
        :param metadata_dict:
        :return:
        """
        session = self._engine_facade.get_session()
        try:
            with session.begin():
                record = session.query(Region).\
                    filter_by(region_id=region_id).first()

                if record is not None:
                    region_metadata = []
                    for k, v in metadata_dict.iteritems():
                        for list_item in v:
                            region_metadata.append(RegionMetaData(region_id=region_id,
                                                                  meta_data_key=k,
                                                                  meta_data_value=list_item))
                    session.add_all(region_metadata)
                    return record.to_wsme()
                else:
                    logger.error("Region {} does not exist. "
                                 "Meta Data was not added!".format(region_id))
                    return None

        except oslo_db.exception.DBDuplicateEntry as e:
            logger.warning("Duplicate entry: {}".format(str(e)))
            raise error_base.ConflictError(message="Duplicate metadata value "
                                           "in region {}".format(region_id))

    def update_region_meta_data(self, region_id,
                                metadata_dict):
        """Replace existing metadata for given region_id
        :param region_id:
        :param metadata_dict:
        :return:
        """
        session = self._engine_facade.get_session()
        with session.begin():

            record = session.query(Region). \
                filter_by(region_id=region_id).first()
            if not record:
                msg = "Region {} not found".format(region_id)
                logger.info(msg)
                raise error_base.NotFoundError(message=msg)

            session.query(RegionMetaData).\
                filter_by(region_id=region_id).delete()

            region_metadata = []
            for k, v in metadata_dict.iteritems():
                for list_item in v:
                    region_metadata.append(RegionMetaData(region_id=region_id,
                                                          meta_data_key=k,
                                                          meta_data_value=list_item))

            session.add_all(region_metadata)
            return record.to_wsme()

    def delete_region_metadata(self, region_id, key):
        session = self._engine_facade.get_session()
        with session.begin():
            record = session.query(Region). \
                filter_by(region_id=region_id).first()

            if not record:
                msg = "Region {} not found".format(region_id)
                logger.info(msg)
                raise error_base.NotFoundError(message=msg)

            session.query(RegionMetaData).filter_by(region_id=region_id,
                                                    meta_data_key=key).delete()

    def update_region_status(self, region_id, region_status):
        try:
            session = self._engine_facade.get_session()
            with session.begin():

                record = session.query(Region).filter_by(region_id=region_id).first()
                if record is not None:
                    record.region_status = region_status
                else:
                    msg = "Region {} not found".format(region_id)
                    logger.info(msg)
                    raise error_base.NotFoundError(message=msg)
                return record.region_status

        except Exception as exp:
            logger.exception("failed to update region {}".format(str(exp)))
            raise
    """
    def add_end_point_to_region(self,
                                region_id,
                                end_point_type,
                                end_point_url,
                                description):
        session = self._engine_facade.get_session()
        try:
            with session.begin():
                record = session.query(Region).filter_by(region_id=region_id).\
                    first()
                if record is not None:
                        session.add(
                            RegionEndPoint(region_id=region_id,
                                           end_point_type=end_point_type,
                                           public_url=end_point_url,
                                           description=description))
                else:
                    logger.error("Region {} does not exist. "
                                 "End point was not added !".format(region_id))

        except oslo_db.exception.DBDuplicateEntry as e:
            logger.warning("Duplicate entry: {}".format(str(e)))
            raise SQLDBError("Duplicate entry error")

    def remove_end_point_from_region(self,
                                     region_id,
                                     end_point_type):
        session = self._engine_facade.get_session()
        with session.begin():
            session.query(Region).filter_by(region_id=region_id,
                                            end_point_type=end_point_type).\
                delete()
    """

    # Handle group management operations
    def add_group(self,
                  group_id,
                  group_name,
                  group_description,
                  region_ids_list):
        session = self._engine_facade.get_session()
        try:
            with session.begin():
                session.add(Group(group_id=group_id,
                                  name=group_name,
                                  description=group_description))

                session.flush()  # add the groupe if not rollback

                if region_ids_list is not None:
                    group_regions = []
                    for region_id in region_ids_list:
                        group_regions.append(GroupRegion(group_id=group_id,
                                                         region_id=region_id))
                    session.add_all(group_regions)
        except oslo_db.exception.DBReferenceError as e:
            logger.error("Reference error: {}".format(str(e)))
            raise error_base.InputValueError("Reference error")
        except oslo_db.exception.DBDuplicateEntry as e:
            logger.error("Duplicate entry: {}".format(str(e)))
            raise error_base.ConflictError("Duplicate entry error")

    def delete_group(self, group_id):
        session = self._engine_facade.get_session()
        with session.begin():
            session.query(Group).filter_by(group_id=group_id).delete()

    def get_all_groups(self):
        logger.debug("DB- Get all groups")
        records_model = PythonModels.GroupsWrraper()
        session = self._engine_facade.get_session()
        with session.begin():
            groups = session.query(Group)
            for a_group in groups:
                group_model = PythonModels.Groups()
                group_model.id = a_group.group_id
                group_model.name = a_group.name
                group_model.description = a_group.description
                regions = []
                group_regions = session.query(GroupRegion).\
                    filter_by(group_id=a_group.group_id)
                for group_region in group_regions:
                    regions.append(group_region.region_id)

                group_model.regions = regions
                records_model.groups.append(group_model)
            return records_model

    def update_group(self, group_id, group_name, group_description,
                     group_regions):
        try:
            session = self._engine_facade.get_session()
            with session.begin():
                # in update scenario delete all child records
                session.query(GroupRegion).filter_by(
                    group_id=group_id).delete()

                group_record = session.query(Group).filter_by(
                    group_id=group_id).first()
                if group_record is None:
                    raise error_base.NotFoundError(
                        message="Group {} not found".format(group_id))
                # only desc and regions can be changed
                group_record.description = group_description
                group_record.name = group_name
                regions = []
                for region_id in group_regions:
                    regions.append(GroupRegion(region_id=region_id,
                                               group_id=group_id))
                session.add_all(regions)

        except error_base.NotFoundError as exp:
            logger.error(exp.message)
            raise
        except oslo_db.exception.DBReferenceError as e:
            logger.error("Reference error: {}".format(str(e)))
            raise error_base.InputValueError("Reference error")
        except Exception as exp:
            logger.error("failed to update group {}".format(group_id))
            logger.exception(exp)
            raise
        return

    def get_group(self, group_id):
        logger.debug("Get group by name")
        group_model = None
        session = self._engine_facade.get_session()
        with session.begin():
            a_group = session.query(Group).filter_by(group_id=group_id)\
                .first()
            if a_group is not None:
                group_model = {"id": a_group.group_id,
                               "name": a_group.name,
                               "description": a_group.description}
                regions = []
                group_regions = session.query(GroupRegion). \
                    filter_by(group_id=a_group.group_id)
                for group_region in group_regions:
                    regions.append(group_region.region_id)
                group_model["regions"] = regions
            return group_model

    """
    def add_region_to_group(self,
                            group_id,
                            region_id):
        session = self._engine_facade.get_session()
        try:
            with session.begin():
                session.add(GroupRegion(group_id=group_id,
                                        region_id=region_id))
        except oslo_db.exception.DBReferenceError as e:
            logger.error("Refernce error: {}".format(str(e)))
            raise SQLDBError("Reference error")
        except oslo_db.exception.DBDuplicateEntry as e:
            logger.error("Duplicate entry: {}".format(str(e)))
            raise SQLDBError("Duplicate entry error")

    def remove_region_from_group(self,
                                 group_id,
                                 region_id):
        session = self._engine_facade.get_session()
        with session.begin():
            session.query(GroupRegion).filter_by(group_id=group_id,
                                                 region_id=region_id).delete()
    """
