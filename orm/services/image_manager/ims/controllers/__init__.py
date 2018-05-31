import os

from orm.common.orm_common.injector import injector
import orm.services.image_manager.ims.di_providers as di_providers
from orm.services.image_manager.ims.logger import get_logger

logger = get_logger(__name__)

_current_dirname = os.path.dirname(os.path.realpath(di_providers.__file__))
injector.register_providers('IMS_ENV', _current_dirname, logger)
