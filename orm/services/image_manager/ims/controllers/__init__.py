"""Init package."""
import os
from ims.logger import get_logger
from orm_common.injector import injector
import ims.di_providers as di_providers

logger = get_logger(__name__)

_current_dirname = os.path.dirname(os.path.realpath(di_providers.__file__))
injector.register_providers('IMS_ENV', _current_dirname, logger)
