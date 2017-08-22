import os

from orm.common.orm_common.injector import injector
from orm.services.flavor_manager.fms_rest import di_providers
from orm.services.flavor_manager.fms_rest.logger import get_logger

logger = get_logger(__name__)

_current_dirname = os.path.dirname(os.path.realpath(di_providers.__file__))
injector.register_providers('FMS_ENV', _current_dirname, logger)
