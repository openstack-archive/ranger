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
        log.debug("DB:--- db address {}".format(db_address))
        db_engines[db_name] = sqlalchemy.create_engine(db_address)
    return db_engines


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
        ''' % (table_name, resource_id)
    return query


def _build_delete_resource_query(resource_id, table_name):
    query = '''
        DELETE from %s
        WHERE %s.uuid = '%s'
        ''' % (table_name, table_name, resource_id)
    return query


def _build_get_resource_regions_query(resource_id, table_name):
    query = '''
        select region_id from %s
        WHERE customer_id = '%s' and region_id != '-1'
        ''' % (table_name, resource_id)
    return query


def _build_get_resource_id_query(resource_id, table_name):
    query = '''
        select * from %s
        WHERE %s.uuid = '%s'
        ''' % (table_name, table_name, resource_id)
    return query


def remove_cms_resource(resource_id):
    query = _build_delete_resource_query(resource_id, conf.customer_table_name)
    log.debug("DB---: deleting customer, query {}".format(query))
    _run_query(query, conf.cms_db_name)
    return


def remove_rds_resource_status(resource_id):
    query = _build_delet_resource_status_query(resource_id,
                                               conf.resource_status_table_name)
    log.debug("DB---: deleting resource status, query {}".format(query))
    _run_query(query, conf.rds_db_name)
    return


def remove_ims_resource(resource_id):
    return


def remove_fms_resource(resource_id):
    return


def get_cms_db_resource_regions(resource_id):
    regions = None
    query = _build_get_resource_id_query(resource_id, conf.customer_table_name)
    result = _run_query(query, conf.cms_db_name)
    if not result.rowcount > 0:
        raise Exception('resource {} not found'.format(resource_id))
    resource_internal_id = result.first().__getitem__('id')
    log.debug("got resource internal id {}".format(resource_internal_id))
    # from resource id get regions
    query = _build_get_resource_regions_query(resource_internal_id,
                                              conf.customer_region_table_name)
    log.debug(query)
    result = _run_query(query, conf.cms_db_name)
    if result.rowcount > 0:
        regions = result.fetchall()
    return regions


def get_ims_db_resource_regions(resource_id):
    return


def get_fms_db_resource_regions(resource_id):
    return


def get_rds_db_resource_status(resource_id):
    return


def remove_resource_db(resource_id, service):
    if service == 'CMS':
        log.debug(
            "cleaning {} db for resource {}".format(service, resource_id))
        remove_cms_resource(resource_id)
    return
