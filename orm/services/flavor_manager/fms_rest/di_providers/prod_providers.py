import requests

from audit_client.api import audit
from fms_rest.data.sql_alchemy.data_manager import DataManager
from fms_rest.logic import flavor_logic
from fms_rest.proxies import rds_proxy
from fms_rest.utils import utils

providers = [
    ('rds_proxy', rds_proxy),
    ('flavor_logic', flavor_logic),
    ('requests', requests),
    ('data_manager', DataManager),
    ('utils', utils),
    ('audit_client', audit)
]
