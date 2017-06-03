"""model module."""
from rms.services import error_base
from pecan import conf


class Address(object):
    """address class."""

    def __init__(self, country=None, state=None, city=None,
                 street=None, zip=None):
        """

        :param country:
        :param state:
        :param city:
        :param street:
        :param zip:
        """
        self.country = country
        self.state = state
        self.city = city
        self.street = street
        self.zip = zip


class EndPoint(object):
    """class method endpoints body."""

    def __init__(self, publicurl=None, type=None):
        """init function.

        :param public_url: field
        :param type: field
        :return:
        """
        self.type = type
        self.publicurl = publicurl


class RegionData(object):
    """class method json header."""

    def __init__(self, status=None, id=None, name=None, clli=None,
                 ranger_agent_version=None, design_type=None, location_type=None,
                 vlcp_name=None, open_stack_version=None,
                 address=Address(), metadata={}, endpoints=[EndPoint()]):
        """

        :param status:
        :param id:
        :param name:
        :param clli:
        :param ranger_agent_version:
        :param design_type:
        :param location_type:
        :param vlcp_name:
        :param open_stack_version:
        :param address:
        :param metadata:
        :param endpoints:
        """
        self.status = status
        self.id = id
        # make id and name always the same
        self.name = self.id
        self.clli = clli
        self.ranger_agent_version = ranger_agent_version
        self.metadata = metadata
        self.endpoints = endpoints
        self.design_type = design_type
        self.location_type = location_type
        self.vlcp_name = vlcp_name
        self.open_stack_version = open_stack_version
        self.address = address

    def _validate_end_points(self, endpoints_types_must_have):
        ep_duplicate = []
        for endpoint in self.endpoints:
            if endpoint.type not in ep_duplicate:
                ep_duplicate.append(endpoint.type)
            else:
                raise error_base.InputValueError(
                    message="Invalid endpoints. Duplicate endpoint "
                            "type {}".format(endpoint.type))
            try:
                endpoints_types_must_have.remove(endpoint.type)
            except:
                pass
        if len(endpoints_types_must_have) > 0:
            raise error_base.InputValueError(
                message="Invalid endpoints. Endpoint type '{}' "
                        "is missing".format(endpoints_types_must_have))

    def _validate_status(self, allowed_status):
        if self.status not in allowed_status:
            raise error_base.InputValueError(
                message="Invalid status. Region status must be "
                        "one of {}".format(allowed_status))
        return

    def _validate_model(self):
        allowed_status = conf.region_options.allowed_status_values[:]
        endpoints_types_must_have = conf.region_options.endpoints_types_must_have[:]
        self._validate_status(allowed_status)
        self._validate_end_points(endpoints_types_must_have)
        return

    def _to_db_model_dict(self):
        end_points = []

        for endpoint in self.endpoints:
            ep = {}
            ep['type'] = endpoint.type
            ep['url'] = endpoint.publicurl
            end_points.append(ep)

        db_model_dict = {}
        db_model_dict['region_id'] = self.id
        db_model_dict['name'] = self.name
        db_model_dict['address_state'] = self.address.state
        db_model_dict['address_country'] = self.address.country
        db_model_dict['address_city'] = self.address.city
        db_model_dict['address_street'] = self.address.street
        db_model_dict['address_zip'] = self.address.zip
        db_model_dict['region_status'] = self.status
        db_model_dict['ranger_agent_version'] = self.ranger_agent_version
        db_model_dict['open_stack_version'] = self.open_stack_version
        db_model_dict['design_type'] = self.design_type
        db_model_dict['location_type'] = self.location_type
        db_model_dict['vlcp_name'] = self.vlcp_name
        db_model_dict['clli'] = self.clli
        db_model_dict['end_point_list'] = end_points
        db_model_dict['meta_data_dict'] = self.metadata
        return db_model_dict


class Regions(object):
    """main json header."""

    def __init__(self, regions=[RegionData()]):
        """init function.

        :param regions:
        :return:
        """
        self.regions = regions


class Groups(object):
    """main json header."""

    def __init__(self, id=None, name=None,
                 description=None, regions=[]):
        """init function.

        :param regions:
        :return:
        """
        self.id = id
        self.name = name
        self.description = description
        self.regions = regions

    def _to_db_model_dict(self):
        db_dict = {}
        db_dict['group_name'] = self.name
        db_dict['group_description'] = self.description
        db_dict['group_regions'] = self.regions
        return db_dict


class GroupsWrraper(object):
    """list of groups."""

    def __init__(self, groups=None):
        """

        :param groups:
        """
        if groups is None:
            self.groups = []
        else:
            self.groups = groups
