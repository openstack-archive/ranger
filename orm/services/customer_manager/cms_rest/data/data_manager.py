import logging

from orm.services.customer_manager.cms_rest.data.sql_alchemy.customer_record \
    import CustomerRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.customer_region_record import CustomerRegionRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.group_record \
    import GroupRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.groups_region_record import GroupsRegionRecord
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models \
    import (CmsRole, CmsUser, Customer,
            Groups, GroupRegion,
            CustomerRegion, Quota,
            QuotaFieldDetail, Region,
            UserRole)
from orm.services.customer_manager.cms_rest.data.sql_alchemy.user_role_record \
    import UserRoleRecord
from orm.services.customer_manager.cms_rest.logic.error_base import ErrorStatus
import oslo_db
from oslo_db.sqlalchemy import session as db_session
from pecan import conf
from sqlalchemy.event import listen
from sqlalchemy import or_

LOG = logging.getLogger(__name__)


# event handling
def on_before_flush(session, flush_context, instances):
    print("on_before_flush:", str(flush_context))
    for model in session.new:
        if hasattr(model, "validate"):
            model.validate("new")

    for model in session.dirty:
        if hasattr(model, "validate"):
            model.validate("dirty")


class DataManager(object):

    def __init__(self, connection_string=None):

        if not connection_string:
            connection_string = conf.database.connection_string

        self._engine_facade = db_session.EngineFacade(connection_string,
                                                      autocommit=False)
        self._session = None
        listen(self.session, 'before_flush', on_before_flush)
        self.image_record = None

    def get_engine(self):
        return self._engine_facade.get_engine()

    @property
    def engine(self):
        return self.get_engine()

    def get_session(self):
        if not self._session:
            self._session = self._engine_facade.get_session()
        return self._session

    @property
    def session(self):
        return self.get_session()

    def flush(self):
        try:
            self.session.flush()
        except oslo_db.exception.DBDuplicateEntry as exception:
            raise ErrorStatus(
                409.2, 'Duplicate Entry {0} already exist'.format(
                    exception.columns))
        except Exception:
            raise

    def commit(self):
        self.session.commit()

    def expire_all(self):
        self.session.expire_all()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def begin_transaction(self):
        pass
        # no need to begin transaction - the transaction is open automatically

    def get_all_cms_users(self, start=0, limit=0):
        cms_users = self.session.query(CmsUser)
        return cms_users.all()

    def get_customer_by_id(self, customer_id):
        customer = self.session.query(Customer).filter(
            Customer.id == customer_id)
        return customer.first()

    def get_customer_by_uuid(self, uuid):
        customer = self.session.query(Customer).filter(Customer.uuid == uuid)
        return customer.first()

    def get_customer_by_name(self, name):
        customer = self.session.query(Customer).filter(Customer.name == name)
        return customer.first()

    def get_customer_by_uuid_or_name(self, cust):
        customer = self.session.query(Customer).filter(
            or_(Customer.uuid == cust,
                Customer.name == cust))

        return customer.first()

    def get_group_by_uuid_or_name(self, grp):
        group = self.session.query(Groups).filter(
            or_(Groups.uuid == grp,
                Groups.name == grp))

        return group.first()

    def get_quota_by_id(self, quota_id):
        quota = self.session.query(Quota).filter(Quota.id == quota_id)
        return quota.first()

    def get_record(self, record_name):
        if record_name == "Customer" or record_name == "customer":
            if not hasattr(self, "customer_record"):
                self.customer_record = CustomerRecord(self.session)
            return self.customer_record

        if record_name == "Group" or record_name == "group":
            if not hasattr(self, "group_record"):
                self.group_record = GroupRecord(self.session)
            return self.group_record

        if record_name == "CustomerRegion" or record_name == "customer_region":
            if not hasattr(self, "customer_region_record"):
                self.customer_region_record = CustomerRegionRecord(
                    self.session)
            return self.customer_region_record

        if record_name == "GroupRegion" or record_name == "group_region":
            if not hasattr(self, "groups_region_record"):
                self.groups_region_record = GroupsRegionRecord(
                    self.session)
            return self.groups_region_record

        if record_name == "UserRole" or record_name == "user_role":
            if not hasattr(self, "user_role_record"):
                self.user_role_record = UserRoleRecord(self.session)
            return self.user_role_record
        return None

    def add_user(self, user):
        db_user = self.session.query(CmsUser).filter(
            CmsUser.name == user.id).first()
        if not (db_user is None):
            return db_user

        db_user = CmsUser(name=user.id)
        self.session.add(db_user)
        self.flush()

        return db_user

    def add_role(self, role):
        db_role = self.session.query(CmsRole).filter(
            CmsRole.name == role).first()
        if not (db_role is None):
            return db_role

        db_role = CmsRole(name=role)
        self.session.add(db_role)
        self.flush()

        return db_role

    def add_quota(self, customer_id, region_id, quota):
        quota_attrs = ['compute', 'storage', 'network']
        for quota_type in quota_attrs:
            quota_by_type = getattr(quota, quota_type)
            if len(quota_by_type) == 0:
                continue

            sql_quota = Quota(
                customer_id=customer_id,
                region_id=region_id,
                quota_type=quota_type
            )
            self.session.add(sql_quota)
            self.flush()

            # FIXME: next line assumes that only one quota of each type is
            # available and thus quota_by_type[0] is used
            for field_key, field_value in DataManager.get_dict_from_quota(
                    quota_by_type[0], quota_type).items():
                sql_quota_field_detail = QuotaFieldDetail(
                    quota_id=sql_quota.id,
                    field_key=field_key,
                    field_value=field_value
                )
                self.session.add(sql_quota_field_detail)

        self.flush()

    def add_customer(self, customer, uuid):
        sql_customer = Customer(
            uuid=uuid,
            name=customer.name,
            enabled=customer.enabled,
            description=customer.description
        )

        self.session.add(sql_customer)
        self.flush()

        return sql_customer

    def add_group(self, group, uuid):
        sql_group = Groups(
            uuid=uuid,
            name=group.name,
            domain_id=1,
            enabled=group.enabled,
            description=group.description
        )

        self.session.add(sql_group)
        self.flush()

        return sql_group

    def add_user_role(self, user_id, role_id, customer_id, region_id,
                      adding=False):
        try:
            sql_user_role = self.session.query(UserRole).filter(
                UserRole.customer_id == customer_id,
                UserRole.user_id == user_id,
                UserRole.region_id == region_id,
                UserRole.role_id == role_id).first()
            if sql_user_role:
                if adding:
                    raise Exception('Duplicate User Role')
                return sql_user_role

            sql_user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                customer_id=customer_id,
                region_id=region_id
            )

            self.session.add(sql_user_role)
            self.flush()

            return sql_user_role
        except Exception as exception:
            raise

    def add_customer_region(self, customer_id, region_id):
        customer_region = CustomerRegion(
            customer_id=customer_id,
            region_id=region_id
        )

        self.session.add(customer_region)
        self.flush()

    def add_region(self, region):
        db_region = self.session.query(Region).filter(
            Region.name == region.name).first()
        if not (db_region is None):
            return db_region

        db_region = Region(name=region.name, type=region.type)
        self.session.add(db_region)
        self.flush()

        return db_region

    def add_group_region(self, group_id, region_id):
        group_region = GroupRegion(
            group_id=group_id,
            region_id=region_id
        )

        self.session.add(group_region)
        self.flush()

    def add_region(self, region):
        db_region = self.session.query(Region).filter(
            Region.name == region.name).first()
        if not (db_region is None):
            return db_region

        db_region = Region(name=region.name, type=region.type)
        self.session.add(db_region)
        self.flush()

        return db_region

    def get_region_id_by_name(self, name):
        region_id = self.session.query(Region.id).filter(
            Region.name == name).scalar()

        return region_id

    def get_customer_id_by_uuid(self, uuid):
        customer_id = self.session.query(Customer.id).filter(
            Customer.uuid == uuid).scalar()

        return customer_id

    @classmethod
    def get_dict_from_quota(cls, quota, quota_type):
        types = {
            'compute': ['instances', 'injected_files', 'key_pairs', 'ram',
                        'vcpus', 'metadata_items',
                        'injected_file_content_bytes', 'floating_ips',
                        'fixed_ips', 'injected_file_path_bytes',
                        'server_groups', 'server_group_members'
                        ],
            'storage': ['gigabytes', 'snapshots', 'volumes'],
            'network': ['floating_ips', 'networks', 'ports', 'routers',
                        'subnets', 'security_groups', 'security_group_rules',
                        'health_monitors', 'members', 'nat_instance', 'pools',
                        'route_table', 'vips'
                        ]
        }

        quota_dict = {}
        for attr in types[quota_type]:
            quota_dict[attr] = getattr(quota, attr)

        return quota_dict
