import json
import logging
from pecan.hooks import PecanHook

from orm_common.utils import api_error_utils as err_utils

logger = logging.getLogger(__name__)


class APIErrorHook(PecanHook):

    def after(self, state):
        # Handle http errors. reformat returned body and header.
        status_code = state.response.status_code

        transaction_id = str(getattr(state.request,
                                     'transaction_id',
                                     'N/A'))
        tracking_id = str(getattr(state.request,
                                  'tracking_id',
                                  'N/A'))

        result_json = {}
        if 400 <= status_code <= 500:

            if status_code == 401:
                result_json = err_utils.get_error_dict(401,
                                                       transaction_id,
                                                       None)

            else:
                dict_body = None
                try:
                    logger.debug('error: {}'.format(state.response))
                    dict_body = json.loads(state.response.body)
                    if 'line' in str(state.response.body) and 'column' in str(
                            state.response.body):
                        result_json = dict_body
                        status_code = 400
                        if 'faultstring' in dict_body:
                            result_json = err_utils.get_error_dict(status_code,
                                                                   transaction_id,
                                                                   dict_body['faultstring'],
                                                                   "")
                    else:
                        result_json = json.loads(dict_body['faultstring'])
                        logger.debug('Received faultstring: {}'.format(result_json))
                    # make sure status code in header and in body are the same
                    if 'code' in result_json:
                        status_code = result_json['code']

                    logger.info('Received status code: {}, transaction_id: {}, tracking_id: {}'.
                                format(status_code, transaction_id, tracking_id))

                except ValueError:
                    msg = 'Could not read faultstring from response body!'
                    logger.error('{} {}'.format(msg, state.response.body))
                    if 'faultstring' in state.response.headers:
                        msg = state.response.headers['faultstring']
                    elif dict_body and 'faultstring' in dict_body:
                        msg = dict_body['faultstring']

                    result_json = err_utils.get_error_dict(status_code,
                                                           transaction_id,
                                                           msg,
                                                           "")

            setattr(state.response, 'body', json.dumps(result_json))
            state.response.status_code = status_code
            state.response.headers.add('X-RANGER-Request-Id', tracking_id)
