from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Model import Model
from orm.common.orm_common.utils.cross_api_utils import (get_regions_of_group,
                                                         set_utils_conf)
from pecan import conf
import wsme
from wsme import types as wtypes


class Region(Model):
    """network model the region
    """
    name = wsme.wsattr(wsme.types.text, mandatory=True)
    type = wsme.wsattr(wsme.types.text, default="single", mandatory=False)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    error_message = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, name="", type="single", users=[], status="",
                 error_message=""):
        """Create a new region.

        :param name:  region name
        :param type:  region type
        :param quotas:  quotas ( array of Quota)
        :param users:   array of users of specific region
        :param status: status of creation
        :param error_message: error message if status is error
        """

        self.name = name
        self.type = type
        self.users = users
        self.status = status
        if error_message:
            self.error_message = error_message


class Group(Model):
    """group entity with all it's related data
    """
    description = wsme.wsattr(wsme.types.text, mandatory=True)
    name = wsme.wsattr(wsme.types.text, mandatory=True)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    domainId = wsme.wsattr(int, mandatory=True)
    uuid = wsme.wsattr(wsme.types.text, mandatory=False)
    enabled = wsme.wsattr(bool, mandatory=True)
    regions = wsme.wsattr([Region], mandatory=False)

    def __init__(self, description="", name="", enabled=False,
                 regions=[], status="", domainId=1, uuid=None):
        """Create a new Group.

        :param description:  Server name
        :param status: status of creation
        """
        self.description = description
        self.name = name
        self.status = status
        self.domainId = domainId
        self.enabled = enabled
        self.regions = regions
        if uuid is not None:
            self.uuid = uuid

    def validate_model(self, context=None):
        """this function check if the group model meet the demands
        :param context: i.e. 'create 'update'
        :return: none
        """
        if context == "update":
            for region in self.regions:
                if region.type == "group":
                    raise ErrorStatus(400,
                                      "region type is invalid for update, "
                                      " \'group\' can be only in create")

    def handle_region_group(self):
        regions_to_add = []
        # get copy of it to be able to delete from the origin
        for region in self.regions[:]:
            if region.type == "group":
                group_regions = self.get_regions_for_group(region.name)
                if not group_regions:
                    raise ErrorStatus(
                        404, 'Group {} Not found'.format(region.name))
                self.regions.remove(region)
        # remove duplicates if exist
        self.regions.extend(set(regions_to_add))

    def get_regions_for_group(self, group_name):
        set_utils_conf(conf)
        regions = get_regions_of_group(group_name)
        return regions


class GroupResult(Model):
    id = wsme.wsattr(wsme.types.text, mandatory=True)
    updated = wsme.wsattr(wsme.types.text, mandatory=False)
    created = wsme.wsattr(wsme.types.text, mandatory=False)
    links = wsme.wsattr({str: str}, mandatory=True)

    def __init__(self, id, links={}, updated=None, created=None):
        self.id = id
        if updated:
            self.updated = updated
        elif created:
            self.created = created
        self.links = links


class GroupResultWrapper(Model):
    transaction_id = wsme.wsattr(wsme.types.text, mandatory=True)
    group = wsme.wsattr(GroupResult, mandatory=True)

    def __init__(self, transaction_id, id, links, updated, created):
        group_result = GroupResult(id, links, updated, created)
        self.transaction_id = transaction_id
        self.group = group_result


""" GroupSummary is a DataObject and contains all the fields
    defined in GroupSummary structure.
"""


class GroupSummary(Model):
    name = wsme.wsattr(wsme.types.text)
    id = wsme.wsattr(wsme.types.text)
    description = wsme.wsattr(wsme.types.text)
    domain_id = wsme.wsattr(int, mandatory=True)
    enabled = wsme.wsattr(bool, mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)
    regions = wsme.wsattr([str], mandatory=True)

    def __init__(self, name='', id='', description='',
                 status="", enabled=True, domain_id=1, regions=[]):
        Model.__init__(self)

        self.name = name
        self.id = id
        self.description = description
        self.enabled = enabled
        self.status = status
        self.domain_id = domain_id
        self.regions = regions

    @staticmethod
    def from_db_model(sql_group):
        regions = [region.region.name for region in
                   sql_group.group_regions if
                   region.region_id != -1]
        group = GroupSummary()
        group.id = sql_group.uuid
        group.name = sql_group.name
        group.description = sql_group.description
        group.enabled = bool(sql_group.enabled)
        group.domain_id = sql_group.domain_id
        group.regions = regions

        return group


class GroupSummaryResponse(Model):
    groups = wsme.wsattr([GroupSummary], mandatory=True)

    def __init__(self):
        Model.__init__(self)
        self.groups = []


""" Region Result Handler """


class RegionResult(Model):
    id = wsme.wsattr(wsme.types.text, mandatory=True)
    added = wsme.wsattr(wsme.types.text, mandatory=False)
    links = wsme.wsattr({str: str}, mandatory=True)

    def __init__(self, id, added=None, links={}):
        self.id = id
        self.added = added
        self.links = links


class RegionResultWrapper(Model):
    transaction_id = wsme.wsattr(wsme.types.text, mandatory=True)
    regions = wsme.wsattr([RegionResult], mandatory=True)

    def __init__(self, transaction_id, regions):
        regions_result = [RegionResult(region['id'],
                                       region['added'],
                                       region['links']) for region in regions]

        self.transaction_id = transaction_id
        self.regions = regions_result


""" ****************************************************************** """
