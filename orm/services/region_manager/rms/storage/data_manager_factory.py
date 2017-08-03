import logging

from pecan import conf
from rms.storage.my_sql.data_manager import DataManager

LOG = logging.getLogger(__name__)


def get_data_manager():
    try:
        dm = DataManager(url=conf.database.url,
                         max_retries=conf.database.max_retries,
                         retries_interval=conf.database.retries_interval)
        return dm
    except Exception:
        nagios_message = "CRITICAL|CONDB001 - Could not establish " \
                         "database connection"
        LOG.error(nagios_message)
        raise Exception("Could not establish database connection")
