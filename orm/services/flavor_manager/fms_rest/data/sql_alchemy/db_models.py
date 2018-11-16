from __builtin__ import reversed

from orm.services.flavor_manager.fms_rest.logger import get_logger
from orm.services.flavor_manager.fms_rest.logic.error_base import ErrorStatus

from oslo_db.sqlalchemy import models
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

LOG = get_logger(__name__)

Base = declarative_base()


def get_list_repr(list):
    text = "["
    for item in list:
        if len(text) > 1:
            text += ","
        text += item.__repr__()
    text += "]"
    return text


class FMSBaseModel(models.ModelBase):

    """Base class for FMS Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}


class Flavor(Base, FMSBaseModel):
    '''Flavor is a DataObject contains all the fields defined in Flavor table record.
    defined as SqlAlchemy model map to a table
    '''
    __tablename__ = "flavor"

    internal_id = Column(BigInteger, primary_key=True)
    id = Column(String)
    name = Column(String)
    alias = Column(String)
    description = Column(String)
    series = Column(String)
    ram = Column(Integer)
    vcpus = Column(Integer)
    disk = Column(Integer)
    swap = Column(Integer)
    ephemeral = Column(Integer)
    visibility = Column(String)
    flavor_extra_specs = relationship("FlavorExtraSpec",
                                      cascade="all, delete, delete-orphan")
    flavor_tags = relationship("FlavorTag",
                               cascade="all, delete, delete-orphan")
    flavor_options = relationship("FlavorOption",
                                  cascade="all, delete, delete-orphan")
    flavor_regions = relationship("FlavorRegion",
                                  cascade="all, delete, delete-orphan")
    flavor_tenants = relationship("FlavorTenant",
                                  cascade="all, delete, delete-orphan")

    def __repr__(self):
        text = "Flavor(internal_id={}, id={}, name={}, alias={}, description={}, " \
               "series={}, ram={}, vcpus={}, disk={}, swap={}, ephemeral={}," \
               "visibility={}, flavor_extra_specs={}, flavor_tags={}," \
               "flavor_options={},  flavor_regions={}, flavor_tenants={})". \
            format(self.internal_id,
                   self.id,
                   self.name,
                   self.alias,
                   self.description,
                   self.series,
                   self.ram,
                   self.vcpus,
                   self.disk,
                   self.swap,
                   self.ephemeral,
                   self.visibility,
                   get_list_repr(self.flavor_extra_specs),
                   get_list_repr(self.flavor_tags),
                   get_list_repr(self.flavor_options),
                   get_list_repr(self.flavor_regions),
                   get_list_repr(self.flavor_tenants))

        return text

    def todict(self):
        extra_specs = {}
        # don't send tags to rds server
        # tags = {}
        options = {}

        for extra_spec in self.flavor_extra_specs:
            extra_specs[extra_spec.key_name] = extra_spec.key_value

        for option in self.flavor_options:
            options[option.key_name] = option.key_value

        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            series=self.series,
            ram=self.ram,
            vcpus=self.vcpus,
            disk=self.disk,
            swap=self.swap,
            ephemeral=self.ephemeral,
            visibility=self.visibility,
            extra_specs=extra_specs,
            option=options,
            regions=self.get_regions_json(),
            tenants=[flavor_tenant.todict()
                     for flavor_tenant in self.flavor_tenants]
        )

    def get_regions_json(self):
        regions_json = []
        for flavor_region in self.flavor_regions:
            region_json = flavor_region.todict()
            regions_json.append(region_json)
        return regions_json

    @validates("series")
    def validate_series(self, key, series):
        if series not in ['ns', 'nd', 'nv', 'gv', 'p1', 'ss']:
            raise ValueError("Series must be one of: 'ns' 'nd' 'nv' 'gv' 'p1' 'ss'")
        return series

    def add_region(self, flavor_region):
        assert isinstance(flavor_region, FlavorRegion)
        try:
            LOG.debug("add region {0} to flavor {1}".format(str(flavor_region),
                                                            str(self)))
            self.flavor_regions.append(flavor_region)

        except Exception as exception:
            LOG.log_exception("Failed to add region {0} to flavor {1}".format(
                str(flavor_region), str(self)), exception)
            raise

    def remove_region(self, region_name):
        region_deleted_flag = False
        assert isinstance(region_name, basestring)
        try:
            LOG.debug("remove regions {0} from flavor {1}".format(region_name,
                                                                  str(self)))

            for region in reversed(self.flavor_regions):
                if region.region_name == region_name:
                    self.flavor_regions.remove(region)
                    region_deleted_flag = True

            if not region_deleted_flag:
                raise ErrorStatus(404,
                                  "Failed to remove region {0} from flavor id {1}".format(
                                      region_name, str(self.id)))

        except ErrorStatus as e:
            raise

        except Exception as exception:
            LOG.log_exception(
                "Failed to remove region {0} from flavor {1}".format(
                    region_name, str(self)), exception)
            raise

    def add_tags(self, flavor_tags):
        assert isinstance(flavor_tags, list) and all(isinstance(ft, FlavorTag) for ft in flavor_tags)
        try:
            LOG.debug("add tags {0} to flavor {1}".format(str(flavor_tags),
                                                          str(self)))
            for tag in flavor_tags:
                self.flavor_tags.append(tag)

        except Exception as exception:
            LOG.log_exception("Failed to add tags {0} to flavor {1}".format(
                str(flavor_tags), str(self)), exception)
            raise

    def replace_tags(self, flavor_tags):
        assert isinstance(flavor_tags, list) and all(isinstance(ft, FlavorTag) for ft in flavor_tags)
        try:
            LOG.debug("replace tags {0} for flavor {1}".format(str(flavor_tags),
                                                               str(self)))
            self.remove_all_tags()
            self.add_tags(flavor_tags)

        except Exception as exception:
            LOG.log_exception("Failed to replace tags {0} to flavor {1}".format(
                str(flavor_tags), str(self)), exception)
            raise

    def remove_all_tags(self):
        try:
            LOG.debug("remove all tags from flavor {}".format(str(self)))
            self.flavor_tags = []
        except Exception as exception:
            LOG.log_exception("Failed to remove all tags from flavor {}".format(str(self)), exception)
            raise

    def remove_tag(self, tag_name):
        deleted_flag = False
        assert isinstance(tag_name, basestring)
        try:
            LOG.debug("remove tag {0} from flavor {1}".format(tag_name,
                                                              str(self)))

            for tag in reversed(self.flavor_tags):
                if tag.key_name == tag_name:
                    self.flavor_tags.remove(tag)
                    deleted_flag = True

            if not deleted_flag:
                raise ErrorStatus(404,
                                  "Failed to remove tag {0} from flavor id {1}".format(
                                      tag_name, str(self.id)))

        except ErrorStatus as e:
            raise

        except Exception as exception:
            LOG.log_exception(
                "Failed to remove tag {0} from flavor {1}".format(
                    tag_name, str(self)), exception)
            raise

    def add_tenant(self, flavor_tenant):
        assert isinstance(flavor_tenant, FlavorTenant)
        try:
            LOG.debug("add tenant {0} to flavor {1}".format(str(flavor_tenant),
                                                            str(self)))
            self.flavor_tenants.append(flavor_tenant)

        except Exception as exception:
            LOG.log_exception(
                "Failed to add tenant {0} from flavor {1}".format(
                    str(flavor_tenant), str(self)), exception)
            raise

    def remove_tenant(self, tenant_id):
        deleted_flag = False
        assert isinstance(tenant_id, basestring)
        try:
            LOG.debug("remove tenants {0} from flavor {1}".format(tenant_id,
                                                                  str(self)))

            for tenant in reversed(self.flavor_tenants):
                if tenant.tenant_id == tenant_id:
                    self.flavor_tenants.remove(tenant)
                    deleted_flag = True

            if not deleted_flag:
                raise ErrorStatus(404,
                                  "tenant {0} does not exist for flavor id {1}".format(
                                      tenant_id, str(self.id)))

        except Exception as exception:
            LOG.log_exception(
                "Failed to remove tenant {0} from flavor {1}".format(
                    tenant_id, str(self)), exception)
            raise

    def add_extra_specs(self, extra_specs):
        LOG.debug("db: add extra specs {} to db".format(extra_specs))
        try:
            if isinstance(extra_specs, list):
                for extra_spec in extra_specs:
                    self.flavor_extra_specs.append(extra_spec)
            else:
                self.flavor_extra_specs.append(extra_specs)

        except Exception as exp:

            LOG.log_exception(
                "Failed to add extra spec {0} to flavor {1}".format(
                    str(extra_specs), str(self)), exp)
            raise

    def delete_all_extra_specs(self):
        LOG.debug("db: delete extra spec for this flavor")
        try:
            self.flavor_extra_specs = []

        except Exception as exp:
            LOG.log_exception("fail to remove extra spec", exp)
            raise

    def remove_extra_spec(self, extra_spec_key_name):
        deleted_flag = False
        assert isinstance(extra_spec_key_name, basestring)
        try:
            LOG.debug("remove extra_spec {} from flavor {}".format(extra_spec_key_name,
                                                                   str(self)))

            for extra_spec in reversed(self.flavor_extra_specs):
                if extra_spec.key_name == extra_spec_key_name:
                    self.flavor_extra_specs.remove(extra_spec)
                    deleted_flag = True

            if not deleted_flag:
                raise ErrorStatus(404,
                                  "extra spec {0} does not exist for flavor id {1}".format(
                                      extra_spec_key_name, str(self.id)))

        except ErrorStatus as e:
            raise

        except Exception as exception:
            LOG.log_exception(
                "Failed to remove extra_spec {0} from flavor {1}".format(extra_spec_key_name, str(self)), exception)
            raise

    def validate(self, type):
        ''' type can be "new" or "dirty" - comes from event
        '''

        if self.visibility == "public" and len(self.flavor_tenants) > 0:
            raise ValueError("tenants should not be specified for a public flavor")
        elif self.visibility == "private" and len(self.flavor_tenants) == 0:
            raise ValueError("Tenants must be specified for a private flavor")
        elif self.visibility not in ["private", "public"]:
            raise ValueError(
                "Flavor visibility can be 'public' or 'private',"
                "got {0}".format(self.visibility))

    def get_existing_region_names(self):
        existing_region_names = []
        for region in self.flavor_regions:
            existing_region_names.append(region.region_name)

        return existing_region_names


'''
' FlavorExtraSpec is a DataObject contains all fields defined in FlavorExtraSpec
' defined as SqlAlchemy model map to a table
'''


class FlavorExtraSpec(Base, FMSBaseModel):

    def __init__(self,
                 key_name=None,
                 key_value=None):

        Base.__init__(self)
        self.key_name = key_name
        self.key_value = key_value

    __tablename__ = "flavor_extra_spec"

    flavor_internal_id = Column(ForeignKey(u'flavor.internal_id'),
                                primary_key=True)
    key_name = Column(String, primary_key=True)
    key_value = Column(String)

    def __repr__(self):
        text = "FlavorExtraSpec(key_name={}, key_value={})".format(
            self.key_name, self.key_value)
        return text

    def todict(self):
        return dict(
            key_name=self.key_name,
            key_value=self.key_value
        )

    def __str__(self):
        extra_spec = "\"{0}\":\"{1}\"".format(self.key_name, self.key_value)
        return extra_spec


'''
' FlavorTag is a DataObject and contains all the fields defined in FlavorTag.
' defined as SqlAlchemy model map to a table
'''


class FlavorTag(Base, FMSBaseModel):
    def __init__(self, key_name=None, key_value=None):
        Base.__init__(self)
        self.key_name = key_name
        self.key_value = key_value

    __tablename__ = "flavor_tag"

    flavor_internal_id = Column(ForeignKey(u'flavor.internal_id'),
                                primary_key=True)
    key_name = Column(String, primary_key=True)
    key_value = Column(String)

    def __repr__(self):
        text = "FlavorTag(key_name={}, key_value={})".format(self.key_name,
                                                             self.key_value)
        return text

    def todict(self):
        return dict(
            key_name=self.key_name,
            key_value=self.key_value
        )

    def __str__(self):
        tags = "\"{0}\":\"{1}\"".format(self.key_name, self.key_value)
        return tags


'''
' FlavorOption is a DataObject contains all the fields defined in FlavorOption
' defined as SqlAlchemy model map to a table
'''


class FlavorOption(Base, FMSBaseModel):
    def __init__(self, key_name=None, key_value=None):
        Base.__init__(self)
        self.key_name = key_name
        self.key_value = key_value

    __tablename__ = "flavor_option"

    flavor_internal_id = Column(ForeignKey(u'flavor.internal_id'),
                                primary_key=True)
    key_name = Column(String, primary_key=True)
    key_value = Column(String)

    def __repr__(self):
        text = "FlavorOption(key_name={}, key_value={})".format(self.key_name,
                                                                self.key_value)
        return text

    def todict(self):
        return dict(
            key_name=self.key_name,
            key_value=self.key_value
        )

    def __str__(self):
        option = "\"{0}\":\"{1}\"".format(self.key_name, self.key_value)
        return option


'''
' FlavorRegion is a DataObject contains all the fields defined in FlavorRegion.
' defined as SqlAlchemy model map to a table
'''


class FlavorRegion(Base, FMSBaseModel):

    def __init__(self, region_name=None, region_type=None):
        Base.__init__(self)
        self.region_name = region_name
        self.region_type = region_type

    __tablename__ = "flavor_region"

    flavor_internal_id = Column(ForeignKey(u'flavor.internal_id'),
                                primary_key=True)
    region_name = Column(String, primary_key=True)
    region_type = Column(String)

    def __repr__(self):
        text = "FlavorRegion(flavor_internal_id='{}', region_name='{}', region_type='{}')".format(self.flavor_internal_id,
                                                                                                  self.region_name,
                                                                                                  self.region_type
                                                                                                  )
        return text

    def todict(self):
        return dict(
            name=self.region_name
        )


'''
' FlavorTenant is a DataObject contains all the fields defined in FlavorTenant.
' defined as SqlAlchemy model map to a table
'''


class FlavorTenant(Base, FMSBaseModel):
    def __init__(self, tenant_id=None):
        Base.__init__(self)
        self.tenant_id = tenant_id

    __tablename__ = "flavor_tenant"

    flavor_internal_id = Column(ForeignKey(u'flavor.internal_id'),
                                primary_key=True)
    tenant_id = Column(String, primary_key=True)

    def __repr__(self):
        text = "FlavorTenant(flavor_internal_id={}, tenant_id={})".format(
            self.flavor_internal_id, self.tenant_id)
        return text

    def todict(self):
        return dict(
            tenant_id=self.tenant_id
        )

# 1866 ProCG uses this line - don't edit it
