import requests

from orm.common.client.audit.audit_client.api import audit
from orm.services.flavor_manager.fms_rest.data.sql_alchemy.data_manager import DataManager
from orm.services.flavor_manager.fms_rest.logic import flavor_logic
from orm.services.flavor_manager.fms_rest.proxies import rds_proxy
from orm.services.flavor_manager.fms_rest.utils import utils

providers = [
    ('rds_proxy', rds_proxy),
    ('flavor_logic', flavor_logic),
    ('requests', requests),
    ('data_manager', DataManager),
    ('utils', utils),
    ('audit_client', audit)
]
