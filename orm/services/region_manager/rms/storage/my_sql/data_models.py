# coding: utf-8
import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from orm.services.region_manager.rms.model.model import Address, EndPoint, RegionData

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    region_id = Column(String(64), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
    address_state = Column(String(64), nullable=False)
    address_country = Column(String(64), nullable=False)
    address_city = Column(String(64), nullable=False)
    address_street = Column(String(64), nullable=False)
    address_zip = Column(String(64), nullable=False)
    region_status = Column(String(64), nullable=False)
    ranger_agent_version = Column(String(64), nullable=False)
    open_stack_version = Column(String(64), nullable=False)
    design_type = Column(String(64), nullable=False)
    location_type = Column(String(64), nullable=False)
    vlcp_name = Column(String(64), nullable=False)
    clli = Column(String(64), nullable=False)
    description = Column(String(255), nullable=False)
    created = Column(DateTime(timezone=False),
                     default=datetime.datetime.now())
    modified = Column(DateTime(timezone=False))
    end_points = relationship(u'RegionEndPoint')
    meta_data = relationship(u'RegionMetaData')

    def __json__(self):
        pass

    def address_to_wsme(self):
        return Address(
            country=self.address_country,
            state=self.address_state,
            city=self.address_city,
            street=self.address_street,
            zip=self.address_zip
        )

    def to_wsme(self):
        wsme_end_points = [end_point.to_wsme() for end_point in self.end_points]

        wsme_meta_data = {}
        for meta_data in self.meta_data:
            # wsme_meta_data[meta_data.meta_data_key] = meta_data.meta_data_value
            if meta_data.meta_data_key not in wsme_meta_data:
                wsme_meta_data[meta_data.meta_data_key] = []
            wsme_meta_data[meta_data.meta_data_key].append(meta_data.meta_data_value)

        id = self.region_id
        name = self.name
        description = self.description
        status = self.region_status
        clli = self.clli
        ranger_agent_version = self.ranger_agent_version
        design_type = self.design_type
        location_type = self.location_type
        vlcp_name = self.vlcp_name
        open_stack_version = self.open_stack_version
        created = self.created
        modified = self.modified
        address = self.address_to_wsme()

        return RegionData(status, id, name, description, clli, ranger_agent_version,
                          design_type, location_type, vlcp_name,
                          open_stack_version, address,
                          metadata=wsme_meta_data,
                          endpoints=wsme_end_points,
                          created=created,
                          modified=modified)


class Group(Base):
    __tablename__ = 'rms_groups'

    id = Column(Integer, primary_key=True)
    group_id = Column(String(64), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    created = Column(DateTime(timezone=False),
                     default=datetime.datetime.now())
    modified = Column(DateTime(timezone=False))

    def __json__(self):
        return dict(
            group_id=self.group_id,
            name=self.name,
            description=self.description,
            created=self.created,
            modified=self.modified
        )

    def to_wsme(self):
        pass


class GroupRegion(Base):
    __tablename__ = 'group_region'

    group_id = Column(ForeignKey(u'rms_groups.group_id'), primary_key=True)
    region_id = Column(ForeignKey(u'region.region_id'), primary_key=True)

    def __json__(self):
        return dict(
            group_id=self.group_id,
            region_id=self.region_id
        )

    def to_wsme(self):
        pass


class RegionEndPoint(Base):
    __tablename__ = 'region_end_point'

    region_id = Column(ForeignKey(u'region.region_id'), primary_key=True)
    end_point_type = Column(String(64), primary_key=True)
    public_url = Column(String(64), nullable=False)

    def __json__(self):
        return dict(
            end_point_type=self.end_point_type,
            public_url=self.public_url
        )

    def to_wsme(self):
        url = self.public_url
        atype = self.end_point_type
        return EndPoint(url, atype)


class RegionMetaData(Base):
    __tablename__ = 'region_meta_data'

    id = Column(Integer, primary_key=True)
    region_id = Column(ForeignKey(u'region.region_id'), nullable=False)
    meta_data_key = Column(String(64), nullable=False)
    meta_data_value = Column(String(255), nullable=False)

    def __json__(self):
        return {self.meta_data_key: self.meta_data_value}

    def to_wsme(self):
        pass
