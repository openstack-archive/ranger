from rds.storage.mysql.region_resource_id_status import Connection as RegionResourceIdStatusConnection

database = {
    'url' : 'na'
}


def get_region_resource_id_status_connection():
    return RegionResourceIdStatusConnection(database['url'])

