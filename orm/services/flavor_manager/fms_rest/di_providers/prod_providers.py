import requests

from orm.common.client.audit.audit_client.api import audit
from orm.services.flavor_manager.fms_rest.data.sql_alchemy.data_manager import DataManager
from orm.services.flavor_manager.fms_rest.logic import flavor_logic
from orm.services.flavor_manager.fms_rest.proxies import rds_proxy

providers = [
    ('rds_proxy', rds_proxy),
    ('flavor_logic', flavor_logic),
    ('requests', requests),
    ('data_manager', DataManager),
    ('audit_client', audit)
]
