import time

from oslo_db.sqlalchemy import session as db_session
from sqlalchemy import Column, Integer, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative.api import declarative_base

from rds.services.model.region_resource_id_status import Model, StatusModel
from rds.storage import region_resource_id_status
import logging
import oslo_db

from pecan import conf

Base = declarative_base()
logger = logging.getLogger(__name__)


class ResourceStatusRecord(Base):
    __tablename__ = 'resource_status'

    id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column(BigInteger, primary_key=False)
    region = Column(Text, primary_key=False)
    status = Column(Text, primary_key=False)
    transaction_id = Column(Text, primary_key=False)
    resource_id = Column(Text, primary_key=False)
    ord_notifier = Column(Text, primary_key=False)
    err_code = Column(Text, primary_key=False)
    err_msg = Column(Text, primary_key=False)
    operation = Column(Text, primary_key=False)
    resource_extra_metadata = relationship("ImageMetadData",
                                           cascade="all, delete, delete-orphan")


class ImageMetadData(Base):
    __tablename__ = 'image_metadata'

    image_meta_data_id = Column(ForeignKey(u'resource_status.id'),
                                primary_key=True)
    checksum = Column(Text, primary_key=False)
    virtual_size = Column(Text, primary_key=False)
    size = Column(Text, primary_key=False)


class Connection(region_resource_id_status.Base):
    """ Implements mysql DB """

    def __init__(self, url):
        self._engine_facade = db_session.EngineFacade(url)

    def add_update_status_record(self,
                                 timestamp,
                                 region,
                                 status,
                                 transaction_id,
                                 resource_id,
                                 ord_notifier,
                                 err_msg,
                                 err_code,
                                 operation,
                                 resource_extra_metadata=None):
        logger.debug("Add/Update status record:\ntimestamp [{}]\nregion [{}]"
                     "\nstatus [{}]\ntransaction_id [{}]\nresource_id [{}]\n"
                     "ord_notifier [{}]\nerr_code [{}]\n"
                     "err_msg [{}] operation [{}] resource_extra_metadata"
                     " [{}]".format(timestamp,
                                    region,
                                    status,
                                    transaction_id,
                                    resource_id,
                                    ord_notifier,
                                    err_code,
                                    err_msg,
                                    operation,
                                    resource_extra_metadata))
        try:
            session = self._engine_facade.get_session()
            with session.begin():
                image_metadata = None
                record = session.query(ResourceStatusRecord).\
                    filter_by(resource_id=resource_id, region=region).first()
                if resource_extra_metadata:
                    image_metadata = ImageMetadData(
                        checksum=resource_extra_metadata['checksum'],
                        virtual_size=resource_extra_metadata['virtual_size'],
                        size=resource_extra_metadata['size'])

                if record is not None:
                    logger.debug("Update record")
                    record.timestamp = timestamp
                    record.region = region
                    record.status = status
                    record.transaction_id = transaction_id
                    record.resource_id = resource_id
                    record.ord_notifier = ord_notifier
                    record.err_msg = err_msg
                    record.err_code = err_code
                    record.operation = operation
                    if record.resource_extra_metadata and image_metadata:
                        record.resource_extra_metadata[0] = image_metadata
                    elif image_metadata:
                        record.resource_extra_metadata.append(image_metadata)
                    else:
                        # remove child if not given
                        session.query(ImageMetadData).filter_by(
                            image_meta_data_id=record.id).delete()
                else:
                    logger.debug("Add record")
                    resource_status = ResourceStatusRecord(timestamp=timestamp,
                                                           region=region,
                                                           status=status,
                                                           transaction_id=transaction_id,
                                                           resource_id=resource_id,
                                                           ord_notifier=ord_notifier,
                                                           err_msg=err_msg,
                                                           err_code=err_code,
                                                           operation=operation)
                    if resource_extra_metadata:
                        resource_status.resource_extra_metadata.append(image_metadata)

                    session.add(resource_status)

        except oslo_db.exception.DBDuplicateEntry as e:
            logger.warning("Duplicate entry: {}".format(str(e)))

    def get_records_by_resource_id(self, resource_id):
        return self.get_records_by_filter_args(resource_id=resource_id)

    def get_records_by_filter_args(self, **filter_args):
        logger.debug("Get records filtered by [{}]".format(filter_args))
        (timestamp, ref_timestamp) = self.get_timstamp_pair()
        logger.debug("timestamp=%s, ref_timestamp=%s" % (timestamp, ref_timestamp))
        records_model = []
        session = self._engine_facade.get_session()
        with session.begin():
            records = session.query(ResourceStatusRecord).filter_by(**filter_args)
            # if found records return these records
            if records is not None:
                for record in records:
                    if record.status == "Submitted" and record.timestamp < ref_timestamp:
                        record.timestamp = timestamp
                        record.status = "Error"
                        record.err_msg = "Status updated to 'Error'. Too long 'Submitted' status"

                    status = Model(record.timestamp,
                                   record.region,
                                   record.status,
                                   record.transaction_id,
                                   record.resource_id,
                                   record.ord_notifier,
                                   record.err_msg,
                                   record.err_code,
                                   record.operation,
                                   record.resource_extra_metadata)
                    records_model.append(status)
                return StatusModel(records_model)
            else:
                logger.debug("No records found")
                return None

    def get_records_by_resource_id_and_status(self,
                                              resource_id,
                                              status):
        """ This method filters all the records where resource_id is the given
        resource_id and status is the given status.
        for the matching records check if a time period elapsed and if so,
        change the status to 'Error' and the timestamp to the given timestamp.
        """
        logger.debug("Get records filtered by resource_id={} "
                     "and status={}".format(resource_id,
                                            status))
        (timestamp, ref_timestamp) = self.get_timstamp_pair()
        logger.debug("timestamp=%s, ref_timestamp=%s" % (timestamp, ref_timestamp))
        session = self._engine_facade.get_session()
        records_model = []
        with session.begin():
            records = session.query(ResourceStatusRecord).\
                filter_by(resource_id=resource_id,
                          status=status)
            if records is not None:
                for record in records:
                    if record.status == "Submitted" and record.timestamp < ref_timestamp:
                        record.timestamp = timestamp
                        record.status = "Error"
                        record.err_msg = "Status updated to 'Error'. Too long 'Submitted' status"
                    else:
                        status = Model(record.timestamp,
                                       record.region,
                                       record.status,
                                       record.transaction_id,
                                       record.resource_id,
                                       record.ord_notifier,
                                       record.err_msg,
                                       record.err_code,
                                       record.operation,
                                       record.resource_extra_metadata)
                        records_model.append(status)
                if len(records_model):
                    return StatusModel(records_model)
            else:
                logger.debug("No records found")
            return None

    def get_timstamp_pair(self):
        timestamp = int(time.time())*1000
        # assume same time period for all resource types
        max_interval_time_in_seconds = conf.region_resource_id_status.max_interval_time.default * 60
        ref_timestamp = (int(time.time()) - max_interval_time_in_seconds) * 1000
        return timestamp, ref_timestamp


