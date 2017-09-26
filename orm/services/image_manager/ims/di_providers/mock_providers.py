from orm.common.orm_common.utils import utils
from orm.services.image_manager.ims.ims_mocks import audit_mock, requests_mock
from orm.services.image_manager.ims.logic import image_logic, metadata_logic
from orm.services.image_manager.ims.persistency.sql_alchemy.data_manager import DataManager
from orm.services.image_manager.ims.proxies import rds_proxy

providers = [
    ('rds_proxy', rds_proxy),
    ('image_logic', image_logic),
    ('metadata_logic', metadata_logic),
    ('requests', requests_mock),
    ('data_manager', DataManager),
    ('utils', utils),
    ('audit_client', audit_mock)
]
