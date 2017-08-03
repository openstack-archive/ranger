from cms_rest.logic.error_base import ErrorStatus
from cms_rest.model.Model import Model
from orm_common.utils.cross_api_utils import (get_regions_of_group,
                                              set_utils_conf)
from pecan import conf
import wsme
from wsme import types as wtypes


class Enabled(Model):
    """enable model the customer

    """
    enabled = wsme.wsattr(bool, mandatory=True)

    def __init__(self, enabled=None):
        """Create a new enables class.

        :param enabled: customer status
        """
        self.enabled = enabled


class Compute(Model):
    """compute model the customer

    """
    instances = wsme.wsattr(wsme.types.text, mandatory=True)
    injected_files = wsme.wsattr(wsme.types.text, mandatory=True, name="injected-files")
    key_pairs = wsme.wsattr(wsme.types.text, mandatory=True, name="key-pairs")
    ram = wsme.wsattr(wsme.types.text, mandatory=True)
    vcpus = wsme.wsattr(wsme.types.text, mandatory=False)
    metadata_items = wsme.wsattr(wsme.types.text, mandatory=False, name="metadata-items")
    injected_file_content_bytes = wsme.wsattr(wsme.types.text, mandatory=False, name="injected-file-content-bytes")
    floating_ips = wsme.wsattr(wsme.types.text, mandatory=False, name="floating-ips")
    fixed_ips = wsme.wsattr(wsme.types.text, mandatory=False, name="fixed-ips")
    injected_file_path_bytes = wsme.wsattr(wsme.types.text, mandatory=False, name="injected-file-path-bytes")
    server_groups = wsme.wsattr(wsme.types.text, mandatory=False, name="server-groups")
    server_group_members = wsme.wsattr(wsme.types.text, mandatory=False, name="server-group-members")

    def __init__(self, instances='', injected_files='', key_pairs='', ram='',
                 vcpus=None, metadata_items=None, injected_file_content_bytes=None,
                 floating_ips='', fixed_ips='', injected_file_path_bytes='',
                 server_groups='', server_group_members=''):
        """
        Create a new compute instance.
        :param instances:
        :param injected_files:
        :param key_pairs:
        :param ram:
        :param vcpus:
        :param metadata_items:
        :param injected_file_content_bytes:
        :param floating_ips:
        :param fixed_ips:
        :param injected_file_path_bytes:
        :param server_groups:
        :param server_group_members:
        """
        self.instances = instances
        self.injected_files = injected_files
        self.key_pairs = key_pairs
        self.ram = ram
        if vcpus is None:
            self.vcpus = conf.quotas_default_values.compute.vcpus
        else:
            self.vcpus = vcpus
        if metadata_items is None:
            self.metadata_items = \
                conf.quotas_default_values.compute.metadata_items
        else:
            self.metadata_items = metadata_items
        if injected_file_content_bytes is None:
            self.injected_file_content_bytes = \
                conf.quotas_default_values.compute.injected_file_content_bytes
        else:
            self.injected_file_content_bytes = injected_file_content_bytes

        self.floating_ips = floating_ips
        self.fixed_ips = fixed_ips
        self.injected_file_path_bytes = injected_file_path_bytes
        self.server_groups = server_groups
        self.server_group_members = server_group_members


class Storage(Model):
    """storage info model for customer

    """
    gigabytes = wsme.wsattr(wsme.types.text, mandatory=True)
    snapshots = wsme.wsattr(wsme.types.text, mandatory=True)
    volumes = wsme.wsattr(wsme.types.text, mandatory=True)

    def __init__(self, gigabytes='', snapshots='', volumes=''):
        """
        create a new Storage instance.
        :param gigabytes:
        :param snapshots:
        :param volumes:
        """
        self.gigabytes = gigabytes
        self.snapshots = snapshots
        self.volumes = volumes


class Network(Model):
    """network model the customer

    """
    floating_ips = wsme.wsattr(wsme.types.text, mandatory=True, name="floating-ips")
    networks = wsme.wsattr(wsme.types.text, mandatory=True)
    ports = wsme.wsattr(wsme.types.text, mandatory=True)
    routers = wsme.wsattr(wsme.types.text, mandatory=True)
    subnets = wsme.wsattr(wsme.types.text, mandatory=True)
    security_groups = wsme.wsattr(wsme.types.text, mandatory=False, name="security-groups")
    security_group_rules = wsme.wsattr(wsme.types.text, mandatory=False, name="security-group-rules")
    health_monitor = wsme.wsattr(wsme.types.text, mandatory=False, name="health-monitor")
    member = wsme.wsattr(wsme.types.text, mandatory=False)
    nat_instance = wsme.wsattr(wsme.types.text, mandatory=False, name="nat-instance")
    pool = wsme.wsattr(wsme.types.text, mandatory=False)
    route_table = wsme.wsattr(wsme.types.text, mandatory=False, name="route-table")
    vip = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, floating_ips='', networks='', ports='', routers='',
                 subnets='', security_groups=None, security_group_rules=None,
                 health_monitor='', member='', nat_instance='',
                 pool='', route_table='', vip=''):

        """
        Create a new Network instance.
        :param floating_ips:  num of floating_ips
        :param networks:  num of networks
        :param ports:  num of ports
        :param routers:  num of routers
        :param subnets:  num of subnets
        :param security_groups: security groups
        :param security_group_rules: security group rules
        :param health_monitor:
        :param member:
        :param nat_instance:
        :param pool:
        :param route_table:
        :param vip:
        """
        self.floating_ips = floating_ips
        self.networks = networks
        self.ports = ports
        self.routers = routers
        self.subnets = subnets
        if security_groups is None:
            self.security_groups = conf.quotas_default_values.network.security_groups
        else:
            self.security_groups = security_groups
        if security_group_rules is None:
            self.security_group_rules = conf.quotas_default_values.network.security_group_rules
        else:
            self.security_group_rules = security_group_rules

        self.health_monitor = health_monitor
        self.member = member
        self.nat_instance = nat_instance
        self.pool = pool
        self.route_table = route_table
        self.vip = vip


class Quota(Model):
    """network model the customer

    """
    compute = wsme.wsattr([Compute], mandatory=False)
    storage = wsme.wsattr([Storage], mandatory=False)
    network = wsme.wsattr([Network], mandatory=False)

    def __init__(self, compute=None, storage=None, network=None):
        """Create a new compute.

        :param compute:  compute quota
        :param storage:  storage quota
        :param network:  network quota
        """
        self.compute = compute
        self.storage = storage
        self.network = network


class User(Model):
    """user model the customer

    """
    id = wsme.wsattr(wsme.types.text, mandatory=True)
    role = wsme.wsattr([str])

    def __init__(self, id="", role=[]):
        """Create a new compute.

        :param id:  user id
        :param role:  roles this use belong to
        """
        self.id = id
        self.role = role


class Region(Model):
    """network model the customer

    """
    name = wsme.wsattr(wsme.types.text, mandatory=True)
    type = wsme.wsattr(wsme.types.text, default="single", mandatory=False)
    quotas = wsme.wsattr([Quota], mandatory=False)
    users = wsme.wsattr([User], mandatory=False)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    error_message = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, name="", type="single", quotas=[], users=[], status="",
                 error_message=""):
        """Create a new compute.

        :param name:  region name
        :param type:  region type
        :param quotas:  quotas ( array of Quota)
        :param users:   array of users of specific region
        :param status: status of creation
        :param error_message: error message if status is error
        """

        self.name = name
        self.type = type
        self.quotas = quotas
        self.users = users
        self.status = status
        if error_message:
            self.error_message = error_message


class Customer(Model):
    """customer entity with all it's related data

    """
    description = wsme.wsattr(wsme.types.text, mandatory=True)
    enabled = wsme.wsattr(bool, mandatory=True)
    name = wsme.wsattr(wsme.types.text, mandatory=True)
    metadata = wsme.wsattr(wsme.types.DictType(str, str), mandatory=False)
    regions = wsme.wsattr([Region], mandatory=False)
    users = wsme.wsattr([User], mandatory=True)
    defaultQuotas = wsme.wsattr([Quota], mandatory=True)
    status = wsme.wsattr(wsme.types.text, mandatory=False)
    custId = wsme.wsattr(wsme.types.text, mandatory=False)
    uuid = wsme.wsattr(wsme.types.text, mandatory=False)

    def __init__(self, description="", enabled=False, name="", metadata={}, regions=[], users=[],
                 defaultQuotas=[], status="", custId="", uuid=None):
        """Create a new Customer.

        :param description:  Server name
        :param enabled:  I don't know
        :param status: status of creation
        """
        self.description = description
        self.enabled = enabled
        self.name = name
        self.metadata = metadata
        self.regions = regions
        self.users = users
        self.defaultQuotas = defaultQuotas
        self.status = status
        self.custId = custId
        if uuid is not None:
            self.uuid = uuid

    def validate_model(self, context=None):
        """
        this function check if the customer model meet the demands
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
                for group_region in group_regions:
                    regions_to_add.append(Region(name=group_region,
                                                 type='single',
                                                 quotas=region.quotas,
                                                 users=region.users))
                self.regions.remove(region)

        self.regions.extend(set(regions_to_add))  # remove duplicates if exist

    def get_regions_for_group(self, group_name):
        set_utils_conf(conf)
        regions = get_regions_of_group(group_name)
        return regions


""" Customer Result Handler """


class CustomerResult(Model):
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


class CustomerResultWrapper(Model):
    transaction_id = wsme.wsattr(wsme.types.text, mandatory=True)
    customer = wsme.wsattr(CustomerResult, mandatory=True)

    def __init__(self, transaction_id, id, links, updated, created):
        customer_result = CustomerResult(id, links, updated, created)
        self.transaction_id = transaction_id
        self.customer = customer_result


""" ****************************************************************** """

""" User Result Handler """


class UserResult(Model):
    id = wsme.wsattr(wsme.types.text, mandatory=True)
    added = wsme.wsattr(wsme.types.text, mandatory=False)
    links = wsme.wsattr({str: str}, mandatory=True)

    def __init__(self, id=None, added=None, links={}):
        self.id = id
        self.added = added
        self.links = links


class UserResultWrapper(Model):
    transaction_id = wsme.wsattr(wsme.types.text, mandatory=True)
    users = wsme.wsattr([UserResult], mandatory=True)

    def __init__(self, transaction_id, users):
        users_result = [UserResult(user['id'], user['added'], user['links']) for user in users]

        self.transaction_id = transaction_id
        self.users = users_result


class MetadataWrapper(Model):
    metadata = wsme.wsattr(wsme.types.DictType(str, str), mandatory=True)

    def __init__(self, metadata={}):
        self.metadata = metadata


""" ****************************************************************** """

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
        regions_result = [RegionResult(region['id'], region['added'], region['links']) for region in regions]

        self.transaction_id = transaction_id
        self.regions = regions_result


""" ****************************************************************** """

""" CustomerSummary is a DataObject and contains all the fields defined in CustomerSummary structure. """


class CustomerSummary(Model):
    name = wsme.wsattr(wsme.types.text)
    id = wsme.wsattr(wsme.types.text)
    description = wsme.wsattr(wsme.types.text)
    enabled = wsme.wsattr(bool, mandatory=True)
    num_regions = wsme.wsattr(int, mandatory=True)
    status = wsme.wsattr(wtypes.text, mandatory=True)
    regions = wsme.wsattr([str], mandatory=True)

    def __init__(self, name='', id='', description='',
                 enabled=True, status="", regions=[], num_regions=0):
        Model.__init__(self)

        self.name = name
        self.id = id
        self.description = description
        self.enabled = enabled
        self.num_regions = num_regions
        self.status = status
        self.regions = regions

    @staticmethod
    def from_db_model(sql_customer):
        regions = [region.region.name for region in
                   sql_customer.customer_customer_regions if
                   region.region_id != -1]
        # default region is -1 , check if -1 in customer list if yes it will return (true, flase) equal to (0, 1)
        num_regions = len(sql_customer.customer_customer_regions) - (-1 in [region.region_id for region in sql_customer.customer_customer_regions])
        customer = CustomerSummary()
        customer.id = sql_customer.uuid
        customer.name = sql_customer.name
        customer.description = sql_customer.description
        customer.enabled = bool(sql_customer.enabled)
        customer.num_regions = num_regions
        customer.regions = regions

        return customer


class CustomerSummaryResponse(Model):
    customers = wsme.wsattr([CustomerSummary], mandatory=True)

    def __init__(self):
        Model.__init__(self)
        self.customers = []


""" ****************************************************************** """
