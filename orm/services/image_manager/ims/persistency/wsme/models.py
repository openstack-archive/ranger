"""Image model module."""
from ims.logic.error_base import ErrorStatus
from ims.persistency.sql_alchemy import db_models
from ims.persistency.wsme.base import Model
from orm_common.utils.cross_api_utils import (get_regions_of_group,
                                              set_utils_conf)
from pecan import conf, request
import wsme


class Metadata(Model):
    """region metadata model
    """
    checksum = wsme.wsattr(wsme.types.text, mandatory=False)
    size = wsme.wsattr(wsme.types.text, mandatory=False)
    virtual_size = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, checksum='', size='', virtual_size=''):
        """region metadata model

        :param checksum:  image checksum
        :param size:  image size
        :param virtual_size: image virtual size in lcp
        """

        self.checksum = checksum
        self.size = size
        self.virtual_size = virtual_size


class MetadataWrapper(Model):
    """region metadata model
    """
    metadata = wsme.wsattr(Metadata, mandatory=False)

    def __init__(self, metadata=Metadata()):
        """region metadata model

        :param metadata:  metadata class
        """

        self.metadata = metadata


class Region(Model):

    name = wsme.wsattr(str, mandatory=True)
    type = wsme.wsattr(str, default="single", mandatory=False)

    # Output-only fields
    status = wsme.wsattr(str, mandatory=False)
    checksum = wsme.wsattr(wsme.types.text, mandatory=False)
    size = wsme.wsattr(wsme.types.text, mandatory=False)
    virtual_size = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, name="", type="single", status="", checksum='',
                 size='', virtual_size=''):
        """region array

        :param name:  region names
        :param type:  region type single/group
        :param status:  region creation status
        :param checksum:  image checksum
        :param size:  image size
        :param virtual_size: image virtual size in lcp
        """

        self.name = name
        self.type = type
        self.status = status
        self.checksum = checksum
        self.size = size
        self.virtual_size = virtual_size

    def to_db_model(self):
        region_rec = db_models.ImageRegion()
        region_rec.region_name = self.name
        region_rec.region_type = self.type
        region_rec.checksum = self.checksum
        region_rec.size = self.size
        region_rec.virtual_size = self.virtual_size

        return region_rec


class RegionWrapper(Model):  # pragma: no cover
    """regions model
    """
    regions = wsme.wsattr([Region], mandatory=False)

    def __init__(self, regions=[]):
        """
        :param regions: array of regions
        """
        self.regions = regions


class CustomerWrapper(Model):  # pragma: no cover
    """customers model
    """
    customers = wsme.wsattr(wsme.types.ArrayType(str), mandatory=False)

    def __init__(self, customers=[]):
        """
        :param regions: array of regions
        """
        self.customers = customers


class Image(Model):
    """Image entity with all its related data."""

    default_min_ram = 1024
    default_min_disk = 1
    default_protected = False

    name = wsme.wsattr(wsme.types.text, mandatory=True)
    enabled = wsme.wsattr(bool, mandatory=False)
    url = wsme.wsattr(wsme.types.text, mandatory=True)
    visibility = wsme.wsattr(wsme.types.text, mandatory=True)
    disk_format = wsme.wsattr(wsme.types.text, mandatory=True,
                              name='disk-format')
    container_format = wsme.wsattr(wsme.types.text, mandatory=True,
                                   name='container-format')
    min_disk = wsme.wsattr(wsme.types.IntegerType(minimum=0), mandatory=False,
                           default=default_min_disk, name='min-disk')
    min_ram = wsme.wsattr(wsme.types.IntegerType(minimum=0), mandatory=False,
                          default=default_min_ram, name='min-ram')
    tags = wsme.wsattr(wsme.types.ArrayType(str), mandatory=False)
    properties = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False)
    regions = wsme.wsattr(wsme.types.ArrayType(Region), mandatory=False)
    customers = wsme.wsattr(wsme.types.ArrayType(str), mandatory=False)
    owner = wsme.wsattr(wsme.types.text, mandatory=False)
    schema = wsme.wsattr(wsme.types.text, mandatory=False)
    protected = wsme.wsattr(bool, mandatory=False, default=default_protected)

    # Output-only fields
    id = wsme.wsattr(wsme.types.text, mandatory=False)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    created_at = wsme.wsattr(wsme.types.IntegerType(minimum=0),
                             mandatory=False, name='created-at')
    updated_at = wsme.wsattr(wsme.types.IntegerType(minimum=0),
                             mandatory=False, name='updated-at')
    locations = wsme.wsattr(wsme.types.ArrayType(str), mandatory=False)
    self_link = wsme.wsattr(wsme.types.text, mandatory=False, name='self')
    file = wsme.wsattr(wsme.types.text, mandatory=False)
    links = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False)

    def __init__(self,
                 id='',
                 name='',
                 enabled=True,
                 url='',
                 visibility='',
                 disk_format='',
                 container_format='',
                 min_disk=default_min_disk,
                 min_ram=default_min_ram,
                 tags=[],
                 properties={},
                 regions=[],
                 customers=[],
                 status='',
                 created_at=0,
                 updated_at=0,
                 locations=[],
                 self_link='',
                 protected=default_protected,
                 file='',
                 owner='',
                 schema='',
                 links={}):
        """Create a new Image.

        :param id: Image UUID
        :param name: Image name
        :param url: Image URL
        :param visibility: Image visibility (public | private)
        :param disk_format: Image file format
        :param container_format: Image container format
        :param min_disk: Minimum disk size required
        :param min_ram: Minimum RAM required
        :param tags: Image tags
        :param properties: Image properties
        :param regions: Regions to use the image
        :param customers: Customers to use the image
        :param owner: Image owner
        :param schema: Image schema
        :param protected: Is the image protected from deletion
        """
        self.id = id
        self.name = name
        self.enabled = enabled
        self.url = url
        self.visibility = visibility
        self.disk_format = disk_format
        self.container_format = container_format
        self.min_disk = min_disk
        self.min_ram = min_ram
        self.tags = tags
        self.properties = properties
        self.regions = regions
        self.customers = customers

        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.locations = locations
        self.self_link = self_link
        self.protected = protected
        self.file = file
        self.owner = owner
        self.schema = schema
        self.links = links

    def validate_model(self, context=None):
        # Validate visibility
        if self.visibility == 'public' and self.customers:
            raise ErrorStatus(400,
                              'Visibility is public but some customers were'
                              ' specified!')
        elif self.visibility == 'private' and not self.customers:
            raise ErrorStatus(400,
                              'Visibility is private but no customers were'
                              ' specified!')

        # Validate disk format
        valid_disk_formats = ('ami', 'ari', 'aki', 'vhd', 'vmdk', 'raw',
                              'qcow2', 'vdi', 'iso',)
        if self.disk_format not in valid_disk_formats:
            raise ErrorStatus(400, 'Invalid disk format!')

        # validate customer input unique
        customer_input = set()
        for customer in self.customers:
            if customer in customer_input:
                raise ErrorStatus(400, "customer {} exist more than one".format(customer))
            customer_input.add(customer)
        # Validate container format
        valid_container_formats = ('ami', 'ari', 'aki', 'bare', 'ovf', 'ova',
                                   'docker')
        if self.container_format not in valid_container_formats:
            raise ErrorStatus(400, 'Invalid container format! {}'.format(self.container_format))

        # Validate min-disk and min-ram (wsme automatically converts booleans
        # to int, and isinstance(False, int) returns True, so that is how we
        # validate the type)
        if 'min-disk' in request.json['image'] and not type(
                request.json['image']['min-disk']) == int:
            raise ErrorStatus(400, 'min-disk must be an integer!')
        if 'min-ram' in request.json['image'] and not type(
                request.json['image']['min-ram']) == int:
            raise ErrorStatus(400, 'min-ram must be an integer!')

        if self.min_disk != wsme.Unset and int(self.min_disk) > 2147483646 or int(self.min_disk) < 0:
            raise ErrorStatus(400,
                              'value must be positive less than 2147483646')
        if self.min_ram != wsme.Unset and int(self.min_ram) > 2147483646 or int(self.min_ram) < 0:
            raise ErrorStatus(400,
                              'value must be positive less than 2147483646')
        if context == "update":
            for region in self.regions:
                if region.type == "group":
                    raise ErrorStatus(400, "region {} type is invalid for update, \'group\' can be only in create".format(region.name))

    def to_db_model(self):
        image = db_models.Image()
        tags = []
        properties = []
        customers = []
        regions = []

        for tag in self.tags:
            tag_rec = db_models.ImageTag()
            tag_rec.tag = tag
            tags.append(tag_rec)

        for key, value in self.properties.iteritems():
            prop = db_models.ImageProperty()
            prop.key_name = key
            prop.key_value = value
            properties.append(prop)

        for region in self.regions:
            regions.append(region.to_db_model())

        for customer in self.customers:
            customer_rec = db_models.ImageCustomer()
            customer_rec.customer_id = customer
            customers.append(customer_rec)

        image.id = self.id
        image.name = self.name
        image.enabled = self.enabled
        image.url = self.url
        image.visibility = self.visibility
        image.disk_format = self.disk_format
        image.container_format = self.container_format
        image.min_disk = self.min_disk
        image.min_ram = self.min_ram
        image.status = self.status
        image.created_at = self.created_at
        image.updated_at = self.updated_at
        image.locations = self.locations
        image.self_link = self.self_link
        image.protected = self.protected
        image.file = self.file
        image.owner = self.owner
        image.schema = self.schema
        image.links = self.links

        image.tags = tags
        image.properties = properties
        image.regions = regions
        image.customers = customers

        return image

    @staticmethod
    def from_db_model(sql_image):
        image = Image()
        image.id = sql_image.id
        image.name = sql_image.name
        image.enabled = sql_image.enabled == 1
        image.url = sql_image.url
        image.visibility = sql_image.visibility
        image.disk_format = sql_image.disk_format
        image.container_format = sql_image.container_format
        image.min_disk = sql_image.min_disk
        image.min_ram = sql_image.min_ram
        image.protected = sql_image.protected == 1
        image.owner = sql_image.owner
        image.schema = sql_image.schema
        image.created_at = sql_image.created_at
        image.updated_at = sql_image.updated_at

        for attribute in ('status', 'self_link', 'file'):
            setattr(image, attribute, getattr(sql_image, attribute, ''))

        for attribute in ('created_at', 'updated_at'):
            setattr(image, attribute, getattr(sql_image, attribute, 0))

        setattr(image, 'locations', getattr(sql_image, 'locations', []))
        setattr(image, 'links', getattr(sql_image, 'links', {}))

        image.customers = []
        for customer in sql_image.customers:
            image.customers.append(customer.customer_id)

        image.regions = []
        for sql_region in sql_image.regions:
            region = Region()
            region.name = sql_region.region_name
            region.type = sql_region.region_type
            region.checksum = sql_region.checksum
            region.size = sql_region.size
            region.virtual_size = sql_region.virtual_size
            image.regions.append(region)

        image.tags = []
        for tag in sql_image.tags:
            image.tags.append(tag.tag)

        image.properties = {}
        for prop in sql_image.properties:
            image.properties[prop.key_name] = prop.key_value

        return image

    def handle_region_group(self):
        regions_to_add = []
        for region in self.regions[:]:  # get copy of it to be able to delete from the origin
            if region.type == "group":
                group_regions = self.get_regions_for_group(region.name)
                if group_regions is None:
                    raise ErrorStatus(404, "Group {} does not exist".format(region.name))
                for group_region in group_regions:
                    regions_to_add.append(Region(name=group_region, type='single'))
                self.regions.remove(region)

        self.regions.extend(set(regions_to_add))  # remove duplicates if exist

    def get_regions_for_group(self, group_name):
        set_utils_conf(conf)
        regions = get_regions_of_group(group_name)
        return regions


class ImageWrapper(Model):
    """image model

    """
    image = wsme.wsattr(Image, mandatory=True, name='image')

    def __init__(self, image=Image()):
        """

        :param image: image dict
        """

        self.image = image

    def to_db_model(self):
        return self.image.to_db_model()

    def validate_model(self, context=None):
        return self.image.validate_model(context)

    def handle_region_group(self):
        return self.image.handle_region_group()

    def get_extra_spec_needed(self):
        return self.image.get_extra_spec_needed()

    @staticmethod
    def from_db_model(sql_image):
        image = ImageWrapper()
        image.image = Image.from_db_model(sql_image)
        return image


'''
' ImageSummary a DataObject contains all the fields defined in ImageSummary.
'''


class ImageSummary(Model):
    name = wsme.wsattr(wsme.types.text)
    id = wsme.wsattr(wsme.types.text)
    visibility = wsme.wsattr(wsme.types.text)

    def __init__(self, name='', id='', visibility=''):
        Model.__init__(self)

        self.name = name
        self.id = id
        self.visibility = visibility

    @staticmethod
    def from_db_model(sql_image):
        image = ImageSummary()
        image.id = sql_image.id
        image.name = sql_image.name
        image.visibility = sql_image.visibility

        return image


class ImageSummaryResponse(Model):
    images = wsme.wsattr([ImageSummary], mandatory=True)

    def __init__(self):  # pragma: no cover
        Model.__init__(self)
        self.images = []


class Enabled(Model):
    enabled = wsme.wsattr(bool, mandatory=True)

    def __init__(self, enabled=None):  # pragma: no cover
        Model.__init__(self)
        self.enabled = enabled
