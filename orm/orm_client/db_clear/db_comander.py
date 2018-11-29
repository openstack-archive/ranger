import config as conf
import logging
import sqlalchemy

log = logging.getLogger(__name__)

db_engines = {}


def _db_create_engine(db_name):
    global db_engines
    if db_name not in db_engines:
        db_address = 'mysql://{}:{}@{}:{}/{}'.format(conf.sql_user,
                                                     conf.sql_password,
                                                     conf.sql_server,
                                                     conf.sql_port,
                                                     db_name)
        db_engines[db_name] = sqlalchemy.create_engine(db_address)
    return db_engines


def _get_db_info(service):
    if service.upper() == 'CMS':
        db_name = conf.cms_db_name
        table_col = conf.customer_tbl_column
        table_name = conf.customer_table_name
        region_table_name = conf.customer_region_table_name

    elif service.upper() == 'FMS':
        db_name = conf.fms_db_name
        table_col = conf.flavor_tbl_column
        table_name = conf.flavor_table_name
        region_table_name = conf.flavor_region_table_name

    elif service.upper() == 'IMS':
        db_name = conf.ims_db_name
        table_col = conf.image_tbl_column
        table_name = conf.image_table_name
        region_table_name = conf.image_region_table_name

    return db_name, table_name, table_col, region_table_name


def _run_query(query, db_name):
    db_engines = _db_create_engine(db_name)
    connection = db_engines[db_name].connect()
    try:
        sqlres = connection.execute(query)
    except Exception as exp:
        sqlres = None
        log.error("fail to delete resource {}".format(exp))
    finally:
        # close the connection
        connection.close()
        # db_engines[db_name].dispose()
    return sqlres


def _build_delet_resource_status_query(resource_id, table_name):
    query = '''
        DELETE from %s
        WHERE resource_id = '%s'
        ''' % (table_name, resource_id)  # nosec
    return query


def _build_delete_image_metadata(resource_id, image_metadata_table,
                                 resource_table):
    query = '''
        DELETE from %s
        WHERE  image_meta_data_id in
            (SELECT id from %s where resource_id = '%s')
        ''' % (image_metadata_table, resource_table, resource_id)  # nosec
    return query


def _build_delete_resource_query(resource_id, table_col, table_name):
    query = '''
        DELETE from %s
        WHERE %s.%s = '%s'
        ''' % (table_name, table_name, table_col, resource_id)  # nosec
    return query


def _build_get_cms_regions_query(resource_id, table_name):
    query = '''
        select region_id from %s
        WHERE customer_id = '%s' and region_id != '-1'
        ''' % (table_name, resource_id)    # nosec
    return query


def _build_get_fms_regions_query(resource_id, table_name):
    query = '''
        select region_name from %s
        WHERE flavor_internal_id = '%s'
        ''' % (table_name, resource_id)    # nosec
    return query


def _build_get_ims_regions_query(resource_id, table_name):
    query = '''
        select region_name from %s
        WHERE image_id = '%s'
        ''' % (table_name, resource_id)    # nosec
    return query


def _build_get_resource_id_query(resource_id, table_col, table_name):
    query = '''
        select * from %s
        WHERE %s.%s = '%s'
        ''' % (table_name, table_name, table_col, resource_id)    # nosec
    return query


def remove_resource_id(resource_id, service):
    db_name, table_name, table_col, region_table_name = _get_db_info(service)
    resource_type = table_name
    query = _build_delete_resource_query(resource_id, table_col, table_name)
    log.debug("DB---: deleting {}, query {}".format(resource_type, query))
    _run_query(query, db_name)
    return


def remove_rds_resource_status(resource_id):
    query = _build_delet_resource_status_query(resource_id,
                                               conf.resource_status_table_name)
    log.debug("DB---: deleting resource status, query {}".format(query))
    _run_query(query, conf.rds_db_name)
    return


def remove_rds_image_metadata(resource_id):
    query = _build_delete_image_metadata(resource_id,
                                         conf.image_metadata_table_name,
                                         conf.resource_status_table_name)
    log.debug("DB---: deleting image_metadata, query {}".format(query))
    _run_query(query, conf.rds_db_name)
    return


def get_cms_db_resource_regions(resource_id, service):
    regions = None
    db_name, table_name, table_col, region_table_name = _get_db_info(service)

    query = _build_get_resource_id_query(resource_id, table_col, table_name)
    result = _run_query(query, db_name)
    if not result.rowcount > 0:
        raise Exception('resource {} not found'.format(resource_id))
    resource_internal_id = result.first().__getitem__('id')
    log.debug("got resource internal id {}".format(resource_internal_id))
    # from resource id get regions
    query = _build_get_cms_regions_query(resource_internal_id,
                                         region_table_name)

    log.debug(query)
    result = _run_query(query, db_name)
    if result.rowcount > 0:
        regions = result.fetchall()
    return regions


def get_fms_db_resource_regions(resource_id, service):
    regions = None
    db_name, table_name, table_col, region_table_name = _get_db_info(service)

    query = _build_get_resource_id_query(resource_id, table_col,
                                         conf.flavor_table_name)
    result = _run_query(query, db_name)
    if not result.rowcount > 0:
        raise Exception('resource {} not found'.format(resource_id))
    resource_internal_id = result.first().__getitem__('internal_id')
    log.debug("got resource internal id {}".format(resource_internal_id))
    # from resource id get regions
    query = _build_get_fms_regions_query(resource_internal_id,
                                         region_table_name)
    log.debug(query)
    result = _run_query(query, db_name)
    if result.rowcount > 0:
        regions = result.fetchall()
    return regions


def get_ims_db_resource_regions(resource_id, service):
    regions = None
    db_name, table_name, table_col, region_table_name = _get_db_info(service)

    query = _build_get_resource_id_query(resource_id, table_col, table_name)
    result = _run_query(query, db_name)
    if not result.rowcount > 0:
        raise Exception('resource {} not found'.format(resource_id))
    resource_internal_id = result.first().__getitem__('id')
    log.debug("got resource internal id {}".format(resource_internal_id))
    # from resource id get regions
    query = _build_get_ims_regions_query(resource_internal_id,
                                         region_table_name)

    log.debug(query)
    result = _run_query(query, db_name)
    if result.rowcount > 0:
        regions = result.fetchall()
    return regions


def get_rds_db_resource_status(resource_id):
    return


def remove_resource_db(resource_id, service):
    log.debug(
        "cleaning {} db for resource {}".format(service, resource_id))
    remove_resource_id(resource_id, service)

    return
