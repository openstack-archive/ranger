from orm.services.customer_manager.cms_rest.data.sql_alchemy.base import Base
import orm.services.customer_manager.cms_rest.model.GroupModels as GroupWsmeModels
import orm.services.customer_manager.cms_rest.model.Models as WsmeModels
from oslo_db.sqlalchemy import models

from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import relationship
import wsme


class CMSBaseModel(models.ModelBase):
    """Base class from CMS Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

'''
' CmsDomain is a DataObject and contains all the fields defined in cms_domain table record.
' defined as SqlAlchemy model map to a table
'''


class CmsDomain(Base, CMSBaseModel):
    __tablename__ = 'cms_domain'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            id=self.id,
            name=self.name
        )


'''
' Groups is a DataObject and contains all the fields defined in Groups table record.
' defined as SqlAlchemy model map to a table
'''


class Groups(Base, CMSBaseModel):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), nullable=False, unique=True)
    domain_id = Column(Integer, ForeignKey('cms_domain.id'), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    enabled = Column(SmallInteger, nullable=False)
    group_domain = relationship("CmsDomain", viewonly=True,
                                primaryjoin="and_(CmsDomain.id==Groups.domain_id)")
    group_regions = relationship("GroupRegion", cascade="all, delete, delete-orphan")

    def __json__(self):
        return dict(
            uuid=self.uuid,
            name=self.name,
            description=self.description,
            domain_id=self.domain_id,
            enabled=self.enabled,
            group_regions=[group_region.__json__() for group_region in
                           self.group_regions]
        )

    def get_dict(self):
        return self.__json__()

    def get_domain_name(self):
        domain_name = ""
        if self.group_domain:
            domain_name=self.group_domain.name
        return domain_name

    def get_proxy_dict(self):
        proxy_dict = {
            "uuid": self.uuid,
            "name": self.name,
            "domain_id": self.domain_id,
            "description": self.description,
            "enabled": 1 if self.enabled else 0
        }
        proxy_dict["domain_name"] = self.get_domain_name()
        group_regions = self.get_group_regions()
        proxy_dict["regions"] = [group_region.get_proxy_dict() for group_region in group_regions]

        return proxy_dict

    def get_group_regions(self):
        group_regions = []
        for group_region in self.group_regions:
            if group_region.region_id != -1:
                group_regions.append(group_region)
        return group_regions

    def to_wsme(self):
        uuid = self.uuid
        name = self.name
        domainId = self.domain_id
        description = self.description
        enabled = True if self.enabled else False
        regions = [group_region.to_wsme() for group_region in self.group_regions if
                   group_region.region_id != -1]
        result = GroupWsmeModels.Group(description=description,
                                       name=name,
                                       uuid=uuid,
                                       regions=regions,
                                       enabled=enabled,
                                       domainId=domainId)
        return result

'''
' GroupRegion is a DataObject and contains all the fields defined in GroupRegion table record.
' defined as SqlAlchemy model map to a table
'''


class GroupRegion(Base, CMSBaseModel):
    __tablename__ = "groups_region"

    group_id = Column(String(64), ForeignKey('groups.uuid'), primary_key=True, nullable=False, index=True)
    region_id = Column(Integer, ForeignKey('cms_region.id'), primary_key=True, nullable=False, index=True)

    region = relationship("Region", viewonly=True)

    def __json__(self):
        return dict(
            group_id=self.group_id,
            region_id=self.region_id
        )

    def get_proxy_dict(self):
        proxy_dict = {
            "name": self.region.name,
            "action": "modify"
        }

        return proxy_dict

    def to_wsme(self):
        name = self.region.name
        type = self.region.type
        region = GroupWsmeModels.Region(name=name,
                                        type=type)
        return region

'''
' CmsUser is a DataObject and contains all the fields defined in CmsUser table record.
' defined as SqlAlchemy model map to a table
'''


class CmsRole(Base, CMSBaseModel):
    __tablename__ = 'cms_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            id=self.id,
            name=self.name
        )


'''
' CmsUser is a DataObject and contains all the fields defined in CmsUser table record.
' defined as SqlAlchemy model map to a table
'''


class CmsUser(Base, CMSBaseModel):
    __tablename__ = 'cms_user'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)

    def __json__(self):
        return dict(
            id=self.id,
            name=self.name
        )


'''
' Customer is a DataObject and contains all the fields defined in Customer table record.
' defined as SqlAlchemy model map to a table
'''


class Customer(Base, CMSBaseModel):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    enabled = Column(SmallInteger, nullable=False)
    customer_customer_regions = relationship("CustomerRegion", cascade="all, delete, delete-orphan")
    customer_metadata = relationship("CustomerMetadata", cascade="all, delete, delete-orphan")

    def __json__(self):
        return dict(
            id=self.id,
            uuid=self.uuid,
            name=self.name,
            description=self.description,
            enabled=self.enabled,
            customer_customer_regions=[customer_region.__json__() for customer_region in
                                       self.customer_customer_regions],
            customer_metadata=[customer_metadata.__json__() for customer_metadata in self.customer_metadata]
        )

    def get_dict(self):
        return self.__json__()

    def get_proxy_dict(self):
        proxy_dict = {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "enabled": 1 if self.enabled else 0
        }

        default_customer_region = self.get_default_customer_region()
        if default_customer_region:
            proxy_dict["default_region"] = default_customer_region.get_proxy_dict()

        real_customer_regions = self.get_real_customer_regions()
        proxy_dict["regions"] = [customer_region.get_proxy_dict() for customer_region in real_customer_regions]
        proxy_dict["metadata"] = [customer_metadata.get_proxy_dict() for customer_metadata in self.customer_metadata]

        return proxy_dict

    def get_default_customer_region(self):
        for customer_region in self.customer_customer_regions:
            if customer_region.region_id == -1:
                return customer_region
        return None

    def get_real_customer_regions(self):
        real_customer_regions = []
        for customer_region in self.customer_customer_regions:
            if customer_region.region_id != -1:
                real_customer_regions.append(customer_region)
        return real_customer_regions

    def to_wsme(self):
        name = self.name
        description = self.description
        enabled = True if self.enabled else False
        regions = [customer_region.to_wsme() for customer_region in self.customer_customer_regions if
                   customer_region.region_id != -1]
        defaultRegion = [customer_region.to_wsme() for customer_region in self.customer_customer_regions if
                         customer_region.region_id == -1]
        metadata = {}
        for metadata1 in self.customer_metadata:
            metadata[metadata1.field_key] = metadata1.field_value

        result = WsmeModels.Customer(description=description,
                                     enabled=enabled,
                                     name=name,
                                     regions=regions,
                                     users=defaultRegion[0].users if defaultRegion else [],
                                     metadata=metadata,
                                     defaultQuotas=defaultRegion[0].quotas if defaultRegion else [],
                                     custId=self.uuid,
                                     uuid=self.uuid)
        return result


'''
' CustomerMetadata is a DataObject and contains all the fields defined in customer_metadata table record.
' defined as SqlAlchemy model map to a table
'''


class CustomerMetadata(Base, CMSBaseModel):
    __tablename__ = "customer_metadata"

    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True, nullable=False)
    field_key = Column(String(64), primary_key=True, nullable=False)
    field_value = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            customer_id=self.customer_id,
            field_key=self.field_key,
            field_value=self.field_value
        )

    def get_proxy_dict(self):
        proxy_dict = {
            self.field_key: self.field_value
        }

        return proxy_dict


'''
' CustomerRegion is a DataObject and contains all the fields defined in CustomerRegion table record.
' defined as SqlAlchemy model map to a table
'''


class CustomerRegion(Base, CMSBaseModel):
    __tablename__ = "customer_region"

    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True, nullable=False)
    region_id = Column(Integer, ForeignKey('cms_region.id'), primary_key=True, nullable=False, index=True)

    customer_region_quotas = relationship("Quota",
                                          uselist=True,
                                          primaryjoin="and_(CustomerRegion.customer_id==Quota.customer_id,"
                                                      "CustomerRegion.region_id==Quota.region_id)")

    customer_region_user_roles = relationship("UserRole",
                                              uselist=True,
                                              order_by="UserRole.user_id",
                                              primaryjoin="and_(CustomerRegion.customer_id==UserRole.customer_id,"
                                                          "CustomerRegion.region_id==UserRole.region_id)")

    region = relationship("Region", viewonly=True)

    def __json__(self):
        return dict(
            customer_id=self.customer_id,
            region_id=self.region_id,
            customer_region_quotas=[quota.__json__() for quota in self.customer_region_quotas],
            customer_region_user_roles=[user_role.__json__() for user_role in self.customer_region_user_roles]
        )

    def get_proxy_dict(self):
        proxy_dict = {
            "name": self.region.name,
            "action": "modify"
        }
        proxy_dict["quotas"] = [quota.get_proxy_dict() for quota in self.customer_region_quotas]

        proxy_dict["users"] = []
        user = None

        for user_role in self.customer_region_user_roles:
            if user and user["id"] != user_role.user.name:
                proxy_dict["users"].append(user)
                user = {"id": user_role.user.name, "roles": [user_role.role.name]}
            elif user is None:
                user = {"id": user_role.user.name, "roles": [user_role.role.name]}
            else:
                user["roles"].append(user_role.role.name)
        if user:
            proxy_dict["users"].append(user)

        return proxy_dict

    def to_wsme(self):
        name = self.region.name
        type = self.region.type
        quota = []
        quotas = {}

        # The WSME can't handle existing data and shows empty values for unset new quotas
        for class_name, class_value in WsmeModels.__dict__.iteritems():
            if str(class_name) in "Network, Storage, Compute":
                quotas[str(class_name).lower()] = {}
                for field_key in dir(class_value):
                    if not field_key.startswith('__') and not field_key.startswith('_') \
                            and not callable(getattr(class_value, field_key)):
                        # unset all possible quotas.
                        quotas[str(class_name).lower()][field_key] = wsme.Unset

        for region_quota in self.customer_region_quotas:
            # quotas[region_quota.quota_type] = {}
            for quota_field in region_quota.quota_field_details:
                quotas[region_quota.quota_type][quota_field.field_key] = quota_field.field_value or wsme.Unset

        if self.customer_region_quotas:
            compute = None
            storage = None
            network = None

            if 'compute' in quotas:
                compute = [WsmeModels.Compute(**quotas['compute'])]
            if 'storage' in quotas:
                storage = [WsmeModels.Storage(**quotas['storage'])]
            if 'network' in quotas:
                network = [WsmeModels.Network(**quotas['network'])]

            quota = [WsmeModels.Quota(compute=compute, storage=storage, network=network)]

        users = []
        user = None
        for user_role in self.customer_region_user_roles:
            if user and user.id != user_role.user.name:
                users.append(user)
                user = WsmeModels.User(id=user_role.user.name, role=[user_role.role.name])
            elif user is None:
                user = WsmeModels.User(id=user_role.user.name, role=[user_role.role.name])
            else:
                user.role.append(user_role.role.name)
        if user:
            users.append(user)

        region = WsmeModels.Region(name=name,
                                   type=type,
                                   quotas=quota,
                                   users=users)
        return region


'''
' Quota is a DataObject and contains all the fields defined in Quota table record.
' defined as SqlAlchemy model map to a table
'''


class Quota(Base, CMSBaseModel):
    __tablename__ = "quota"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer_region.customer_id'), nullable=False)
    region_id = Column(Integer, ForeignKey('customer_region.region_id'), nullable=False)
    quota_type = Column(String(64))
    quota_field_details = relationship("QuotaFieldDetail")

    def __json__(self):
        return dict(
            id=self.id,
            customer_id=self.customer_id,
            region_id=self.region_id,
            quota_type=self.quota_type,
            quota_field_details=[quota_field_detail.__json__() for quota_field_detail in self.quota_field_details]
        )

    def get_proxy_dict(self):
        proxy_dict = {}
        field_items = {}
        for quota_field_detail in self.quota_field_details:
            if quota_field_detail.field_value:
                key = quota_field_detail.field_key
                # key.replace("-", "_")
                field_items[key] = quota_field_detail.field_value

        proxy_dict[self.quota_type] = field_items

        return proxy_dict

    def to_wsme(self):
        compute = {}
        storage = {}
        network = {}
        for quota_field in self.quota_field_details:
            if self.quota_type == "compute":
                if not quota_field.field_value:
                    quota_field.field_value = wsme.Unset
                compute[quota_field.field_key] = quota_field.field_value
            elif self.quota_type == "storage":
                if not quota_field.field_value:
                    quota_field.field_value = wsme.Unset
                storage[quota_field.field_key] = quota_field.field_value
            elif self.quota_type == "network":
                if not quota_field.field_value:
                    quota_field.field_value = wsme.Unset
                network[quota_field.field_key] = quota_field.field_value

        quota = WsmeModels.Quota(compute=[WsmeModels.Compute(**compute)],
                                 storage=[WsmeModels.Storage(**storage)],
                                 network=[WsmeModels.Network(**network)])
        return quota


'''
' QuotaFieldDetail is a DataObject and contains all the fields defined in QuotaFieldDetail table record.
' defined as SqlAlchemy model map to a table
'''


class QuotaFieldDetail(Base, CMSBaseModel):
    __tablename__ = "quota_field_detail"

    id = Column(Integer, primary_key=True)
    # quota_id = Column(Integer, ForeignKey('Quota.id'))
    quota_id = Column(Integer, ForeignKey('quota.id'), nullable=False)
    field_key = Column(String(64), nullable=False)
    field_value = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            id=self.id,
            quota_id=self.quota_id,
            field_key=self.field_key,
            field_value=self.field_value
        )


'''
' Region is a DataObject and contains all the fields defined in Region table record.
' defined as SqlAlchemy model map to a table
'''


class Region(Base, CMSBaseModel):
    __tablename__ = "cms_region"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    type = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            id=self.id,
            name=self.name,
            type=self.type
        )


'''
' UserRole is a DataObject and contains all the fields defined in UserRole table record.
' defined as SqlAlchemy model map to a table
'''


class UserRole(Base, CMSBaseModel):
    __tablename__ = "user_role"

    customer_id = Column(Integer, ForeignKey('customer_region.customer_id'), primary_key=True, nullable=False)
    region_id = Column(Integer, ForeignKey('customer_region.region_id'), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('cms_user.id'), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('cms_role.id'), primary_key=True, nullable=False)

    user = relationship("CmsUser", viewonly=True)
    role = relationship("CmsRole", viewonly=True)

    def __json__(self):
        return dict(
            customer_id=self.customer_id,
            region_id=self.region_id,
            user_id=self.user_id,
            role_id=self.role_id
        )

    def to_wsme(self):
        id = ""
        role = []

        user = WsmeModels.User(id=id, role=role)
        return user
