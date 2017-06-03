from mock import MagicMock
from fms_rest.logger import get_logger

logger = get_logger(__name__)


def init(audit_server_url, num_of_send_retries, time_wait_between_retries):
    logger.debug('MOCK: audit.init called')
    pass


def audit(timestamp, application_id, tracking_id, transaction_id, transaction_type, resource_id, service_name,
          user_id=None, external_id=None, event_details=None, status=None):
    logger.debug('MOCK: audit.audit called')
    return 200
