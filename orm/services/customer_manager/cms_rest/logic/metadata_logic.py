import json
from pecan import request

from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.data.data_manager import DataManager
from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import CustomerMetadata
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest.model.Models import CustomerResultWrapper
from orm.services.customer_manager.cms_rest.rds_proxy import RdsProxy

logger = get_logger(__name__)


def add_customer_metadata(customer_uuid, metadata_wrapper, transaction_id):
    sql_metadata_collection = map_metadata(customer_uuid, metadata_wrapper)

    datamanager = DataManager()

    try:
        customer_record = datamanager.get_record('customer')
        sql_customer = customer_record.read_customer_by_uuid(customer_uuid)
        if not sql_customer:
            logger.error('customer not found, customer uuid: {0}'.format(customer_uuid))
            raise ValueError('customer not found, customer uuid: {0}'.format(customer_uuid))

        for metadata in sql_metadata_collection:
            metadata_match = [m for m in sql_customer.customer_metadata if m.field_key == metadata.field_key]
            if len(metadata_match) > 0:
                logger.error('Duplicate metadata key, key already exits: {0}'.format(metadata.field_key))
                raise AttributeError('Duplicate metadata key, key already exits: {0}'.format(metadata.field_key))

        for metadata in sql_metadata_collection:
            sql_customer.customer_metadata.append(metadata)
            logger.debug('updating metadata {0}'.format(json.dumps(metadata.get_proxy_dict())))

        logger.debug('finished appending metadata to customer')
        if len(sql_customer.customer_customer_regions) > 1:
            RdsProxy.send_customer(sql_customer, transaction_id, "PUT")
        datamanager.commit()

        customer_result_wrapper = build_response(customer_uuid, transaction_id)

        return customer_result_wrapper

    except Exception as exp:
        datamanager.rollback()
        raise exp


def update_customer_metadata(customer_uuid, metadata_wrapper, transaction_id):
    sql_metadata_collection = map_metadata(customer_uuid, metadata_wrapper)

    datamanager = DataManager()

    try:
        customer_record = datamanager.get_record('customer')
        sql_customer = customer_record.read_customer_by_uuid(customer_uuid)

        if not sql_customer:
            logger.error('customer not found, customer uuid: {0}'.format(customer_uuid))
            raise ValueError('customer not found, customer uuid: {0}'.format(customer_uuid))

        while len(sql_customer.customer_metadata) > 0:
            sql_customer.customer_metadata.remove(sql_customer.customer_metadata[0])

        for metadata in sql_metadata_collection:
            sql_customer.customer_metadata.append(metadata)
            logger.debug('updating metadata {0}'.format(json.dumps(metadata.get_proxy_dict())))

        if len(sql_customer.customer_customer_regions) > 1:
            RdsProxy.send_customer(sql_customer, transaction_id, "PUT")
        datamanager.commit()

        customer_result_wrapper = build_response(customer_uuid, transaction_id)

        return customer_result_wrapper

    except Exception as exp:
        datamanager.rollback()
        raise exp


def map_metadata(customer_id, metadata_wrapper):
    sql_metadata_collection = []
    for key, value in metadata_wrapper.metadata.iteritems():
        sql_metadata = CustomerMetadata()
        sql_metadata.customer_id = customer_id
        sql_metadata.field_key = key
        sql_metadata.field_value = value

        sql_metadata_collection.append(sql_metadata)
    return sql_metadata_collection


def build_response(customer_uuid, transaction_id):
    # The link should point to the customer itself (/v1/orm/customers/{id}),
    # so the 'metadata' element should be removed.
    link_elements = request.url.split('/')
    link_elements.remove('metadata')
    base_link = '/'.join(link_elements)

    timestamp = utils.get_time_human()
    customer_result_wrapper = CustomerResultWrapper(
        transaction_id=transaction_id,
        id=customer_uuid,
        updated=None,
        created=timestamp,
        links={'self': base_link})
    return customer_result_wrapper
