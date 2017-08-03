import json
import pprint

from ims.logger import get_logger
from ims.logic.error_base import ErrorStatus
from orm_common.injector import injector
from pecan import conf, request

di = injector.get_di()

LOG = get_logger(__name__)

headers = {'content-type': 'application/json'}


@di.dependsOn('requests')
def send_image(image_dict, transaction_id, action="put"):
        # action can be "post" for creating image or "delete" for deleting image
        requests = di.resolver.unpack(send_image)

        data = {
            "service_template":
                {
                    "resource": {
                        "resource_type": "image"
                    },
                    "model": str(json.dumps(image_dict)),
                    "tracking": {
                        "external_id": "",
                        "tracking_id": transaction_id
                    }
                }
        }

        data_to_display = {
            "service_template":
                {
                    "resource": {
                        "resource_type": "image"
                    },
                    "model": image_dict,
                    "tracking": {
                        "external_id": "",
                        "tracking_id": transaction_id
                    }
                }
        }
        try:
            pp = pprint.PrettyPrinter(width=30)
            pretty_text = pp.pformat(data_to_display)
            wrapper_json = json.dumps(data)

            headers['X-RANGER-Client'] = request.headers[
                'X-RANGER-Client'] if 'X-RANGER-Client' in request.headers else \
                'NA'
            headers['X-RANGER-Requester'] = request.headers[
                'X-RANGER-Requester'] if 'X-RANGER-Requester' in request.headers else \
                ''

            LOG.debug("Wrapper JSON before sending action: {0} to Rds Proxy {1}".format(action, pretty_text))
            LOG.info("Sending to RDS Server: " + conf.api.rds_server.base + conf.api.rds_server.resources)
            if action == "post":
                resp = requests.post(conf.api.rds_server.base + conf.api.rds_server.resources,
                                     data=wrapper_json,
                                     headers=headers, verify=conf.verify)
            elif action == "put":
                resp = requests.put(conf.api.rds_server.base + conf.api.rds_server.resources,
                                    data=wrapper_json,
                                    headers=headers, verify=conf.verify)
            elif action == "delete":
                resp = requests.delete(conf.api.rds_server.base + conf.api.rds_server.resources,
                                       data=wrapper_json,
                                       headers=headers, verify=conf.verify)
            else:
                raise Exception("Invalid action in RdxProxy.send_image("
                                "image_dict, transaction_id, action) "
                                "action can be post or delete, "
                                "got {0}".format(action))

            content = resp.content
            LOG.debug("return from rds server status code: {0} "
                      "content: {1}".format(resp.status_code, resp.content))
            if resp.content and 200 <= resp.status_code < 300:
                content = resp.json()
            else:
                # In case of error from rds, the response is WSME format response.
                # the error message is within the 'faultstring'
                raise ErrorStatus(resp.status_code,
                                  json.loads(content)["faultstring"])

        except Exception as exp:
            LOG.log_exception("ImageLogic - Failed to update image", exp)
            raise exp

        return content


@di.dependsOn('requests')
def get_status(resource_id, json_convert=True):
    requests = di.resolver.unpack(send_image)

    resp = requests.get(conf.api.rds_server.base + conf.api.rds_server.status + resource_id, verify=conf.verify)
    if json_convert:
        resp = resp.json()
    return resp
