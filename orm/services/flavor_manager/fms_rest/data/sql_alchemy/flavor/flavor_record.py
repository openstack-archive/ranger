from orm.services.flavor_manager.fms_rest.data.sql_alchemy.db_models import (Flavor,
                                                                             FlavorRegion,
                                                                             FlavorTag,
                                                                             FlavorTenant)
from orm.services.flavor_manager.fms_rest.logger import get_logger

from sqlalchemy.sql import or_

LOG = get_logger(__name__)


class FlavorRecord:

    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__flavors = Flavor()
        # self.setRecordData(self.__flavors)
        # self.__flavors.Clear()
        self.__TableName = "flavor"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def flavor(self):
        return self.__flavor

    @flavor.setter
    def flavor(self, flavor):
        self.__flavor = flavor

    def insert(self, flavor):
        try:
            self.session.add(flavor)
        except Exception as exception:
            LOG.log_exception("Failed to insert Flavor" + str(flavor), exception)
            # LOG.error("Failed to insert flavor" + str(flavor) + " Exception:" + str(exception))
            raise

    def get_flavor(self, internal_id):
        try:
            flavor = self.session.query(Flavor).filter(Flavor.internal_id == internal_id)
            return flavor.first()

        except Exception as exception:
            message = "Failed to get_flavor:internal_id: {0}".format(internal_id)
            LOG.log_exception(message, exception)
            raise

    def delete_by_uuid(self, flavor_uuid):
        try:
            cmd = 'DELETE FROM flavor WHERE id = %s'
            result = self.session.connection().execute(cmd, (flavor_uuid,))
            return result

        except Exception as exception:
            message = "Failed to delete_by_uuid: flavor_uuid: {0}".format(flavor_uuid)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_by_id(self, id):
        try:
            flavor = self.session.query(Flavor).filter(Flavor.id == id)
            return flavor.first()

        except Exception as exception:
            message = "Failed to get_flavor_by_id: id: {0}".format(id)
            LOG.log_exception(message, exception)
            raise

    def get_flavor_by_id_or_name(self, id_or_name):
        try:
            flavor = self.session.query(Flavor).filter(or_(Flavor.id == id_or_name, Flavor.name == id_or_name))
            return flavor.first()

        except Exception as exception:
            message = "Failed to get_flavor_by_id_or_name: id or name: {0}".format(id_or_name)
            LOG.log_exception(message, exception)
            raise

    def get_flavors_by_series(self, series, **kw):
        try:
            query = self.session.query(Flavor).filter(Flavor.series == series)
            self.customise_query(query, kw)
            return query.all()

        except Exception as exception:
            message = "Failed to get_flavors_by_series: series: {0}".format(series)
            LOG.log_exception(message, exception)
            raise

    def get_all_flavors(self, **kw):
        try:
            query = self.session.query(Flavor)
            query = self.customise_query(query, kw)
            return query.all()

        except Exception as exception:
            message = "Failed to get_all_flavors"
            LOG.log_exception(message, exception)
            raise

    def customise_query(self, query, kw):
        start = int(kw['start']) if 'start' in kw else 0
        limit = int(kw['limit']) if 'limit' in kw else 0

        if start > 0:
            query = query.offset(start)

        if limit > 0:
            query = query.limit(limit)

        return query

    def get_count_of_flavors_by_series(self, series):
        try:
            query = self.session.query(Flavor).filter(Flavor.series == series)
            return query.count()

        except Exception as exception:
            message = "Failed to get_count_of_flavors_by_series: series: {0}".format(series)
            LOG.log_exception(message, exception)
            raise

    def get_flavors_by_visibility(self, visibility, **kw):
        try:
            query = self.session.query(Flavor).filter(Flavor.visibility == visibility)
            query = self.customise_query(query, kw)
            return query.all()

        except Exception as exception:
            message = "Failed to get_flavors_by_visibility: visibility: {0}".format(visibility)
            LOG.log_exception(message, exception)
            raise

    def get_count_of_flavors_by_visibility(self, visibility, **kw):
        try:
            query = self.session.query(Flavor).filter(Flavor.visibility == visibility)
            query = self.customise_query(query, kw)
            return query.get_count()

        except Exception as exception:
            message = "Failed to get_count_of_flavors_by_visibility: visibility: {0}".format(visibility)
            LOG.log_exception(message, exception)
            raise

    def get_flavors_status_by_uuids(self, uuid_str):
        cmd = ('SELECT id, resource_id, region, status FROM '
               'rds_resource_status_view WHERE resource_id IN %s')
        results = self.session.connection().execute(cmd, (uuid_str,))

        flvr_region_dict = {}

        if results:
            resource_status_dict = dict((id, (resource_id, region, status)) for id, resource_id, region, status in results)
            # using resource_status_dict, create flvr_region_dict with resource_id as key and (region, status) as value
            for v in resource_status_dict.values():
                if v[0] in flvr_region_dict:
                    flvr_region_dict[v[0]].append(v[1:])
                else:
                    flvr_region_dict[v[0]] = [v[1:]]

            results.close()
        return flvr_region_dict

    def get_flavors_by_criteria(self, **criteria):
        try:

            LOG.debug("get_flavors_by_criteria: criteria: {0}".format(criteria))
            visibility = criteria['visibility'] if 'visibility' in criteria else None
            region = criteria['region'] if 'region' in criteria else None
            tenant = criteria['tenant'] if 'tenant' in criteria else None
            series = criteria['series'] if 'series' in criteria else None
            vm_type = criteria['vm_type'] if 'vm_type' in criteria else None
            vnf_name = criteria['vnf_name'] if 'vnf_name' in criteria else None
            starts_with = criteria['starts_with'] if 'starts_with' in criteria else None
            contains = criteria['contains'] if 'contains' in criteria else None
            alias = criteria['alias'] if 'alias' in criteria else None

            query = self.session.query(Flavor)

            if alias:
                query = query.filter(Flavor.alias == alias)

            if contains:
                query = query.filter(Flavor.name.ilike("%{}%".format(contains)))

            if starts_with:
                query = query.filter(Flavor.name.ilike("{}%".format(starts_with)))

            if region:
                query = query.join(FlavorRegion).filter(FlavorRegion.flavor_internal_id == Flavor.internal_id,
                                                        FlavorRegion.region_name == region)
            if tenant:
                query = query.join(FlavorTenant).filter(FlavorTenant.flavor_internal_id == Flavor.internal_id,
                                                        FlavorTenant.tenant_id == tenant)
            if vm_type:
                query = query.join(FlavorTag).filter(FlavorTag.flavor_internal_id == Flavor.internal_id,
                                                     FlavorTag.key_name == 'vm_type',
                                                     FlavorTag.key_value == vm_type)
            if vnf_name:
                query = query.join(FlavorTag).filter(FlavorTag.flavor_internal_id == Flavor.internal_id,
                                                     FlavorTag.key_name == 'vnf_name',
                                                     FlavorTag.key_value == vnf_name)
            if visibility:
                query = query.filter(Flavor.visibility == visibility)

            if series:
                query = query.filter(Flavor.series == series)

            query = self.customise_query(query, criteria)
            return query.all()

        except Exception as exception:
            message = "Failed to get_flavors_by_criteria: criteria: {0}".format(criteria)
            LOG.log_exception(message, exception)
            raise
