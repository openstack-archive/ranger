import wsme

from orm.common.orm_common.utils.cross_api_utils import (set_utils_conf,
                                                         get_regions_of_group,
                                                         validate_description)
from orm.services.flavor_manager.fms_rest.data.sql_alchemy import db_models
from orm.services.flavor_manager.fms_rest.data.wsme.model import Model
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus

from oslo_config import cfg
from pecan import conf, request


class TenantWrapper(Model):
    """user model the customer

    """
    tenants = wsme.wsattr([str], mandatory=False)

    def __init__(self, tenants=[]):  # pragma: no cover
        """region array

        :param tenants: array of tenants
        """

        self.tenants = tenants


class ExtraSpecsWrapper(Model):
    """extra spec model."""

    os_extra_specs = wsme.wsattr(wsme.types.DictType(str, str),
                                 mandatory=False)
    extra_specs = wsme.wsattr(wsme.types.DictType(str, str),
                              mandatory=False, name="extra-specs")

    def __init__(self, os_extra_specs={}, extra_specs={}):
        """init func."""

        # self.extra_specs = extra_specs
        if extra_specs:
            self.extra_specs = extra_specs
        if os_extra_specs:
            self.os_extra_specs = os_extra_specs

    def to_db_model(self):
        extra_spec = []
        autogen_es = cfg.CONF.flavor_series_metadata.autogen_extra_specs
        for key, value in self.os_extra_specs.iteritems():
            if key in autogen_es:
                continue
            extra_spec_rec = db_models.FlavorExtraSpec()
            extra_spec_rec.key_name = key
            extra_spec_rec.key_value = value
            extra_spec.append(extra_spec_rec)

        return extra_spec

    def _get_extra_specs_urlpath(self):
        # return the way to return extra specs depends on url used
        return '{}'.format(request.upath_info).split("/")[-1].strip()

    @staticmethod
    def from_db_model(os_extra_specs):
        extra_spec_method = ExtraSpecsWrapper()._get_extra_specs_urlpath()
        extra_specs = ExtraSpecsWrapper()
        setattr(extra_specs, extra_spec_method, {})
        for extra_spec in os_extra_specs:
            getattr(extra_specs,
                    extra_spec_method,
                    None)[extra_spec.key_name] = extra_spec.key_value
        return extra_specs


class TagsWrapper(Model):
    """Tags model."""

    tags = wsme.wsattr(wsme.types.DictType(str, str), mandatory=True)

    def __init__(self, tags={}):
        """init func."""

        self.tags = tags

    def to_db_model(self):
        tag = []

        for key, value in self.tags.iteritems():
            tags_rec = db_models.FlavorTag()
            tags_rec.key_name = key
            tags_rec.key_value = value
            tag.append(tags_rec)

        return tag

    @staticmethod
    def from_db_model(tags):
        my_tags = TagsWrapper()
        for tag in tags:
            my_tags.tags[tag.key_name] = tag.key_value

        return my_tags


class Region(Model):
    """network model the customer

    """
    name = wsme.wsattr(str, mandatory=True)
    type = wsme.wsattr(str, default="single", mandatory=False)
    status = wsme.wsattr(str, mandatory=False)
    error_message = wsme.wsattr(str, mandatory=False)

    def __init__(self, name="", type="single", status="", error_message=""):
        """region array

        :param name:  region names
        :param type:  region type
        :param status:  region creation status
        :param error_message:  region creation error status message
        """

        self.name = name
        self.type = type
        self.status = status
        if error_message:
            self.error_message = error_message

    def to_db_model(self):
        if self.name == '' or self.name.isspace():
            raise ErrorStatus(400, 'Cannot add region with empty name')
        region_rec = db_models.FlavorRegion()
        region_rec.region_name = self.name
        region_rec.region_type = self.type

        return region_rec


class RegionWrapper(Model):  # pragma: no cover
    """regions model

    """
    regions = wsme.wsattr([Region], mandatory=False)

    def __init__(self, regions=[]):
        """init

        :param regions: array of regions
        """

        self.regions = regions


class Flavor(Model):
    """flavor entity with all it's related data

    """
    id = wsme.wsattr(wsme.types.text, mandatory=False)
    name = wsme.wsattr(wsme.types.text, mandatory=False)
    alias = wsme.wsattr(wsme.types.text, mandatory=False)
    description = wsme.wsattr(wsme.types.text, mandatory=False)
    series = wsme.wsattr(wsme.types.text, mandatory=True)
    ram = wsme.wsattr(wsme.types.text, mandatory=True)
    vcpus = wsme.wsattr(wsme.types.text, mandatory=True)
    disk = wsme.wsattr(wsme.types.text, mandatory=True)
    swap = wsme.wsattr(wsme.types.text, mandatory=False)
    ephemeral = wsme.wsattr(wsme.types.text, mandatory=False)
    regions = wsme.wsattr(wsme.types.ArrayType(Region), mandatory=False)
    visibility = wsme.wsattr(wsme.types.text, mandatory=True)
    tenants = wsme.wsattr(wsme.types.ArrayType(str), mandatory=False)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    tag = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False)
    options = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False)
    extra_specs = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False,
                              name="extra-specs")

    def __init__(self,
                 id="",
                 name="",
                 alias=None,
                 description="",
                 series="",
                 ram="0",
                 vcpus="0",
                 disk="0",
                 swap="0",
                 ephemeral="0",
                 extra_specs={},
                 tag={},
                 options={},
                 regions=[],
                 visibility="",
                 tenants=[],
                 status=""):
        """Create a new Flavor.

        :param id: flavor UUID
        :param name: name extracted from flavor parameters
        :param description: flavor description
        :param series:  series possible
        :param ram: RAM in MB
        :param vcpus:
        :param disk: Disk in GB
        :param swap: is optional and default is 0
        :param ephemeral: is optional and default is 0, size in GB
        :param extra_spec: key-value dictionary
        :param tags: key-value dictionary
        :param options: key-value dictionary
        :param regions:
        :param visibility:
        :param tenants:
        :param status: status of creation
        """
        self.id = id
        self.name = name
        if alias is not None:
            self.alias = alias
        self.description = description
        self.series = series
        self.ram = ram
        self.vcpus = vcpus
        self.disk = disk
        self.swap = swap
        self.ephemeral = ephemeral
        self.extra_specs = extra_specs
        self.tag = tag
        self.options = options
        self.regions = regions
        self.visibility = visibility
        self.tenants = tenants
        self.status = status

    def validate_model(self, context=None):
        series_metadata = {}
        valid_numa = []
        valid_vnf = []

        if self.series:
            valid_flavor_series = cfg.CONF.fms.flavor_series
            if self.series not in valid_flavor_series:
                raise ErrorStatus(400, "Series possible values are {}".format(
                                  valid_flavor_series))
        else:
            raise ErrorStatus(400, "Series not specified.")

        if self.series in cfg.CONF['flavor_series_metadata']:
            series_metadata = cfg.CONF['flavor_series_metadata'][self.series]
        else:
            raise ErrorStatus(400, "Cannot retrieve requested flavor"
                              " series metadata.")

        if 'valid_options_numa' in series_metadata:
            valid_numa = [x for x in
                          series_metadata['valid_options_numa'].split(',')]

        if 'valid_options_vnf' in series_metadata:
            valid_vnf = [x for x in
                         series_metadata['valid_options_vnf'].split(',')]

        # validate that input entries are valid
        try:
            # flavor option values must be either 'true' or 'false' (in quotes)

            if self.options:
                option_values = self.options.values()
                invalid_opt_vals = [x for x in option_values if (x.lower()
                                    not in ['true', 'false'])]
                if invalid_opt_vals:
                    raise ErrorStatus(400, "All flavor option values must have"
                                      " a value of 'true' or 'false'")

            # validate series and set flavor vcpu and vram limits
            requested_numa = [n for n in valid_numa if n in
                              self.options.keys() and
                              self.options[n].lower() == 'true']

            if requested_numa:
                vcpu_limit = int(series_metadata['vcpu_limit'])
                vram_limit = int(series_metadata['vram_limit'])
            else:
                vcpu_limit = int(series_metadata['alt_vcpu_limit'])
                vram_limit = int(series_metadata['alt_vram_limit'])

            # determine other flavor limits
            swap_file_limit = cfg.CONF.fms.flavor_swap_file_limit
            ephemeral_limit = cfg.CONF.fms.flavor_ephemeral_limit

            isValid = validate_description(self.description)
            if not isValid:
                raise ErrorStatus(400, "Flavor description does not allow"
                                  " special characters: only dashes,"
                                  " commas, and period allowed.")
            if not self.ram.isdigit():
                raise ErrorStatus(400, "ram must be a number")
            if not self.vcpus.isdigit():
                raise ErrorStatus(400, "vcpus must be a number")
            if not self.validInt(self.disk):
                raise ErrorStatus(400, "disk must be a number")
            if not self.swap.isdigit():
                raise ErrorStatus(400, "swap must be a number")
            if self.ephemeral and not self.ephemeral.isdigit():
                raise ErrorStatus(400, "ephemeral must be a number")
            if int(self.ram) not in range(1024, vram_limit + 1, 1024):
                raise ErrorStatus(400,
                                  "ram value is out of range. Expected range"
                                  " is 1024(1GB)-%6d(%3dGB) and must be a"
                                  " multiple of 1024" %
                                  (vram_limit, vram_limit / 1024))
            if int(self.vcpus) not in range(1, vcpu_limit + 1):
                raise ErrorStatus(400, "vcpus value is out of range. Expected"
                                  "range is 1-%2d" % (vcpu_limit))
            if int(self.disk) < 0:
                raise ErrorStatus(400, "disk cannot be less than zero")

            if not self.ephemeral:
                self.ephemeral = "0"
            elif (self.ephemeral and
                  int(self.ephemeral) not in range(0, ephemeral_limit + 1)):
                raise ErrorStatus(400,
                                  "ephemeral value is out of range. Expected"
                                  " range is 0-%5d(%2dTB)" %
                                  (ephemeral_limit, ephemeral_limit / 1000))

            if int(self.swap) not in range(0, swap_file_limit + 1, 1024):
                raise ErrorStatus(400,
                                  "swap value is out of range. Expected"
                                  " range is 0-%6d(%3dGB) and must be a"
                                  " multiple of 1024" %
                                  (swap_file_limit, swap_file_limit / 1024))
        except ValueError:
            raise ErrorStatus(400, "ram, vcpus, disk, ephemeral and swap must"
                              " be integers")

        for symbol, value in self.extra_specs.iteritems():
            if symbol == 'numa_override' and value not in valid_numa:
                raise ErrorStatus(400,
                                  "Invalid value. numa_override possible"
                                  " values: " + str(valid_numa))
            if symbol == 'vlan_category' and value not in valid_vnf:
                raise ErrorStatus(400,
                                  "Invalid value. vlan_category possible"
                                  " values: " + str(valid_vnf))

        # region  type can be group only in create flavor!!
        if not context == "create":
            for region in self.regions:
                if region.type == "group":
                    raise ErrorStatus(400,
                                      "region type \'group\' is invalid in"
                                      " this action, \'group\' can be only"
                                      " in create flavor action")

    def to_db_model(self):
        flavor = db_models.Flavor()
        extra_spec = []
        tags = []
        options = []
        regions = []
        tenants = []
        autogen_es = cfg.CONF.flavor_series_metadata.autogen_extra_specs

        for symbol, value in self.extra_specs.iteritems():
            if symbol in autogen_es:
                continue
            es = db_models.FlavorExtraSpec()
            es.key_name = symbol
            es.key_value = value
            extra_spec.append(es)

        if self.series:
            extra_spec.extend(self.get_extra_spec_needed())

        for symbol, value in self.tag.iteritems():
            tag = db_models.FlavorTag()
            tag.key_name = symbol
            tag.key_value = value
            tags.append(tag)

        for symbol, value in self.options.iteritems():
            option = db_models.FlavorOption()
            option.key_name = symbol
            option.key_value = value.lower()
            options.append(option)

        for region in self.regions:
            regions.append(region.to_db_model())

        for tenant in self.tenants:
            tenant_rec = db_models.FlavorTenant()
            tenant_rec.tenant_id = tenant
            tenants.append(tenant_rec)

        flavor.id = self.id
        flavor.name = self.name
        if self.alias is not wsme.Unset:
            flavor.alias = self.alias
        flavor.description = self.description
        flavor.series = self.series
        flavor.ram = int(self.ram)
        flavor.vcpus = int(self.vcpus)
        flavor.disk = int(self.disk)
        flavor.swap = int(self.swap)
        flavor.ephemeral = int(self.ephemeral)
        flavor.visibility = self.visibility

        flavor.flavor_extra_specs = extra_spec
        flavor.flavor_tags = tags
        flavor.flavor_options = options
        flavor.flavor_regions = regions
        flavor.flavor_tenants = tenants

        return flavor

    @staticmethod
    def from_db_model(sql_flavor):
        flavor = Flavor()
        flavor.id = sql_flavor.id
        flavor.series = sql_flavor.series
        flavor.description = sql_flavor.description
        flavor.ram = str(sql_flavor.ram)
        flavor.ephemeral = str(sql_flavor.ephemeral)
        flavor.visibility = sql_flavor.visibility
        flavor.vcpus = str(sql_flavor.vcpus)
        flavor.swap = str(sql_flavor.swap)
        flavor.disk = str(sql_flavor.disk)
        flavor.name = sql_flavor.name
        if sql_flavor.alias is not None:
            flavor.alias = sql_flavor.alias

        for tenant in sql_flavor.flavor_tenants:
            flavor.tenants.append(tenant.tenant_id)

        for sql_region in sql_flavor.flavor_regions:
            region = Region()
            region.name = sql_region.region_name
            region.type = sql_region.region_type
            flavor.regions.append(region)

        for extra_spec in sql_flavor.flavor_extra_specs:
            flavor.extra_specs[extra_spec.key_name] = extra_spec.key_value

        for tag in sql_flavor.flavor_tags:
            flavor.tag[tag.key_name] = tag.key_value

        for option in sql_flavor.flavor_options:
            flavor.options[option.key_name] = option.key_value

        return flavor

    def get_extra_spec_needed(self):
        extra_spec_needed = []
        requested_options = []
        mixed_options = {}
        series_metadata = cfg.CONF['flavor_series_metadata'][self.series]

        # Retreive default extra specs and mixed options for series
        for f_key, f_val in series_metadata.items():
            if f_key.startswith("es_default_"):
                es = db_models.FlavorExtraSpec(key_name_value=f_val)
                extra_spec_needed.append(es)
            if f_key.startswith("es_mixed_"):
                mixed_es_trimmed = f_key.replace('es_mixed_', '')
                mixed_options[mixed_es_trimmed] = f_val

        # Evaluate numa options
        if 'valid_options_numa' in series_metadata:
            valid_numa = [x for x in
                          series_metadata['valid_options_numa'].split(',')]

            option_numa = [n for n in valid_numa if n in
                           self.options.keys() and
                           self.options[n].lower() == 'true']

            if not option_numa:
                es = db_models.FlavorExtraSpec(
                    key_name_value=series_metadata['es_alt_numa_nodes'])
                extra_spec_needed.append(es)
            else:
                es = db_models.FlavorExtraSpec(
                    key_name_value=series_metadata['es_numa_nodes'])
                extra_spec_needed.append(es)
                requested_options.extend(option_numa)

        # Evaluate pci options
        if 'valid_options_pci' in series_metadata:
            valid_pci = [x for x in
                         series_metadata['valid_options_pci'].split(',')]

            option_pci = [n for n in valid_pci if n in
                          self.options.keys() and
                          self.options[n].lower() == 'true']

            if option_pci:
                requested_options.extend(option_pci)

        # Evalulate mixed options
        assorted_opts = []
        for mixed_key, mixed_value in mixed_options.items():
            assorted_opts = [z for z in mixed_key.split('_')]

            mixed_present = True
            for opt in assorted_opts:
                mixed_present &= True if opt in requested_options else False

            if mixed_present:
                es = db_models.FlavorExtraSpec(key_name_value=mixed_value)
                extra_spec_needed.append(es)

        # convert the key_value to a string to avoid/fix pecan json
        # rendering error in update extra_specs
        i = 0
        while i < len(extra_spec_needed):
            extra_spec_needed[i].key_value = str(
                extra_spec_needed[i].key_value)
            i += 1

        return extra_spec_needed

    def get_as_summary_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description
        )

    def handle_region_groups(self):
        regions_to_add = []
        # get copy of it to be able to delete from the origin
        for region in self.regions[:]:
            if region.type == "group":
                group_regions = self.get_regions_for_group(region.name)
                if group_regions is None:
                    raise ValueError("Group {} not found".format(region.name))
                for group_region in group_regions:
                    regions_to_add.append(Region(name=group_region,
                                                 type='single'))
                self.regions.remove(region)

        # remove duplicates if exist
        self.regions.extend(set(regions_to_add))

    def get_regions_for_group(self, group_name):
        set_utils_conf(conf)
        regions = get_regions_of_group(group_name)
        return regions

    def validInt(self, check_value):
        try:
            int(check_value)
        except ValueError:
            return False
        return True


class FlavorWrapper(Model):
    """flavor model

    """
    flavor = wsme.wsattr(Flavor, mandatory=True, name='flavor')

    def __init__(self, flavor=Flavor()):
        """init

        :param flavor: flavor dict
        """

        self.flavor = flavor

    def to_db_model(self):
        return self.flavor.to_db_model()

    def validate_model(self):
        return self.flavor.validate_model()

    def get_extra_spec_needed(self):
        return self.flavor.get_extra_spec_needed()

    @staticmethod
    def from_db_model(sql_flavor):
        flavors = FlavorWrapper()
        flavors.flavor = Flavor.from_db_model(sql_flavor)
        return flavors


'''
' FlavorSummary a DataObject contains all the fields defined in FlavorSummary.
'''


class FlavorSummary(Model):
    name = wsme.wsattr(wsme.types.text)
    id = wsme.wsattr(wsme.types.text)
    description = wsme.wsattr(wsme.types.text)
    visibility = wsme.wsattr(wsme.types.text)

    def __init__(self, name='', id='', description='', visibility=''):
        Model.__init__(self)

        self.name = name
        self.id = id
        self.description = description
        self.visibility = visibility

    @staticmethod
    def from_db_model(sql_flavor):
        flavor = FlavorSummary()
        flavor.id = sql_flavor.id
        flavor.name = sql_flavor.name
        flavor.description = sql_flavor.description
        flavor.visibility = sql_flavor.visibility

        return flavor


class FlavorSummaryResponse(Model):
    flavors = wsme.wsattr([FlavorSummary], mandatory=True)

    def __init__(self):  # pragma: no cover
        Model.__init__(self)
        self.flavors = []


class FlavorListFullResponse(Model):
    flavors = wsme.wsattr([Flavor], mandatory=True)

    def __init__(self):  # pragma: no cover
        Model.__init__(self)
        self.flavors = []
