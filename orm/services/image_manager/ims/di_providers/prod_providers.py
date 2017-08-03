import requests

from audit_client.api import audit
from ims.logic import image_logic, metadata_logic
from ims.persistency.sql_alchemy.data_manager import DataManager
from ims.proxies import rds_proxy
from orm_common.utils import utils

providers = [
    ('rds_proxy', rds_proxy),
    ('image_logic', image_logic),
    ('metadata_logic', metadata_logic),
    ('requests', requests),
    ('data_manager', DataManager),
    ('utils', utils),
    ('audit_client', audit)
]
