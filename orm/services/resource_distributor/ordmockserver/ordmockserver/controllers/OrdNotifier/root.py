import json
import logging.handlers
from pecan import conf
from pecan import request
import pecan.rest
import requests
import threading
import time
import wsme
from wsme import types as wtypes
from wsmeext.pecan import wsexpose

my_logger = logging.getLogger(__name__)


class Result(wtypes.DynamicBase):
    haha = wsme.wsattr(wtypes.text, mandatory=True)

    def __init__(self, haha):
        self.haha = haha


class OrdNotifierWrapper(wtypes.DynamicBase):
    ord_notifier = wsme.wsattr(
        {str: str, str: str, str: str, str: str, str: str}, mandatory=False,
        name='ord-notifier')

    def __init__(self, ord_notifier=None):
        self.ord_notifier = ord_notifier


def send_status_update(ord_notifier_wrapper):
    # Wait before sending the status update, to make sure RDS updates the
    # status to Submitted
    time.sleep(conf.SECONDS_BEFORE_STATUS_UPDATE)

    json_to_send = {"rds-listener": {}}
    for key in ('ord-notifier-id', 'region', 'status', 'error-code',
                'error-msg',):
        # Take the keys from the configuration
        json_to_send['rds-listener'][key] = conf.status_data[
            key.replace('-', '_')]

    for key in ('request-id', 'resource-id', 'resource-type',
                'resource-template-version', 'resource-template-type',
                'region',):
        # Take the keys from the input json
        json_to_send['rds-listener'][key] = ord_notifier_wrapper.ord_notifier[
            key]

    json_to_send['rds-listener']['resource-operation'] = \
        ord_notifier_wrapper.ord_notifier['operation']

    if ord_notifier_wrapper.ord_notifier['resource-type'] == 'image':
        json_to_send['rds-listener'][
            'resource_extra_metadata'] = dict(conf.image_extra_metadata)

    result = requests.post(conf.RDS_STATUS_URL,
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(json_to_send),
                           verify=conf.verify)
    my_logger.debug(
        'Status update status code: {}, content: {}'.format(result.status_code,
                                                            result.content))
    return result


class OrdNotifier(pecan.rest.RestController):
    def _send_status_update(self, ord_notifier_wrapper):
        thread = threading.Thread(target=send_status_update,
                                  args=(ord_notifier_wrapper,))
        thread.start()

    @wsexpose(Result, body=OrdNotifierWrapper, status_code=200,
              rest_content_types='json')
    def post(self, ord_notifier_wrapper):
        try:
            my_logger.debug('Entered post, ord_notifier: {}'.format(
                ord_notifier_wrapper.ord_notifier))
            mandatory_keys = ['resource-type']
            if not all(
                    [key in ord_notifier_wrapper.ord_notifier for key in
                     mandatory_keys]):
                raise ValueError('A mandatory key is missing')

            self._send_status_update(ord_notifier_wrapper)
        except Exception as exc:
            my_logger.error(str(exc))

        return Result('Success')
