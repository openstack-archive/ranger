from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
from orm.services.customer_manager.cms_rest.model.Model import Model
from orm.common.orm_common.utils.cross_api_utils import (get_regions_of_group,
                                                         set_utils_conf)
from pecan import conf
import wsme
from wsme import types as wtypes


""" Group Result Handler """
class Region(Model):
    """network model the group
    """
    def __init__(self, id):
        self.id = id

class Group(Model):
    """group entity with all it's related data
    """
    description = wsme.wsattr(wsme.types.text, mandatory=True)
    name = wsme.wsattr(wsme.types.text, mandatory=True)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    domainId = wsme.wsattr(int, mandatory=True)
    uuid = wsme.wsattr(wsme.types.text, mandatory=False)
    regions = wsme.wsattr([Region], mandatory=False)

    def __init__(self, description="", name="",
                 regions=[], status="", domainId=1, uuid=None):
        """Create a new Group.

        :param description:  Server name
        :param status: status of creation
        """
        self.description = description
        self.name = name
        self.status = status
        self.domainId = domainId
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
                    raise ErrorStatus(400, "region type is invalid for update, \'group\' can be only in create")

    def handle_region_group(self):
        regions_to_add = []
        for region in self.regions[:]:  # get copy of it to be able to delete from the origin
            if region.type == "group":
                group_regions = self.get_regions_for_group(region.name)
                if not group_regions:
                    raise ErrorStatus(404, 'Group {} Not found'.format(region.name))
                self.regions.remove(region)

        self.regions.extend(set(regions_to_add))  # remove duplicates if exist


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


""" GroupSummary is a DataObject and contains all the fields defined in GroupSummary structure. """


class GroupSummary(Model):
    name = wsme.wsattr(wsme.types.text)
    id = wsme.wsattr(wsme.types.text)
    description = wsme.wsattr(wsme.types.text)
    domain_id = wsme.wsattr(int, mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, name='', id='', description='',
                 status="", domain_id=0):
        Model.__init__(self)

        self.name = name
        self.id = id
        self.description = description
        self.status = status
        self.domain_id = domain_id

    @staticmethod
    def from_db_model(sql_group):
        group = GroupSummary()
        group.id = sql_group.uuid
        group.name = sql_group.name
        group.description = sql_group.description
        group.domain_id = sql_group.domain_id

        return group


class GroupSummaryResponse(Model):
    groups = wsme.wsattr([GroupSummary], mandatory=True)

    def __init__(self):
        Model.__init__(self)
        self.groups = []


""" ****************************************************************** """
