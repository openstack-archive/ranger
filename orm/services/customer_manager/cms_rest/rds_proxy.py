import pprint
import requests
import json
from pecan import conf
from pecan import request
from cms_rest.logic.error_base import ErrorStatus
from cms_rest.logger import get_logger

LOG = get_logger(__name__)
headers = {'content-type': 'application/json'}


class RdsProxy(object):

    @staticmethod
    def get_status(resource_id):
        try:
            LOG.debug(
                "Sending to RDS Server to get status: " + conf.api.rds_server.base + conf.api.rds_server.status + resource_id)
            resp = requests.get(
                conf.api.rds_server.base + conf.api.rds_server.status + resource_id,
                verify=conf.verify)
            LOG.debug(
                "Sending to RDS Server to get status: " + conf.api.rds_server.base + conf.api.rds_server.status + resource_id)
            pp = pprint.PrettyPrinter(width=30)
            pretty_text = pp.pformat(resp.json())
            LOG.debug("Response from RDS Server:\n" + pretty_text)
            return resp
        except Exception as exp:
            LOG.log_exception(
                "CustomerLogic - Failed to Get status for customer : " + resource_id,
                exp)
            raise

    @staticmethod
    def send_customer(customer, transaction_id, method):  # method is "POST" or "PUT"
        return RdsProxy.send_customer_dict(customer.get_proxy_dict(), transaction_id, method)

    @staticmethod
    def send_customer_dict(customer_dict, transaction_id, method):  # method is "POST" or "PUT"
        data = {
            "service_template":
                {
                    "resource": {
                        "resource_type": "customer"
                    },
                    "model": str(json.dumps(customer_dict)),
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
                        "resource_type": "customer"
                    },
                    "model": customer_dict,
                    "tracking": {
                        "external_id": "",
                        "tracking_id": transaction_id
                    }
                }
        }

        pp = pprint.PrettyPrinter(width=30)
        pretty_text = pp.pformat(data_to_display)
        wrapper_json = json.dumps(data)

        headers['X-RANGER-Client'] = request.headers[
            'X-RANGER-Client'] if 'X-RANGER-Client' in request.headers else \
            'NA'
        headers['X-RANGER-Requester'] = request.headers[
            'X-RANGER-Requester'] if 'X-RANGER-Requester' in request.headers else \
            ''

        LOG.debug("Wrapper JSON before sending action: {0} to Rds Proxy\n{1}".format(method, pretty_text))
        LOG.info("Sending to RDS Server: " + conf.api.rds_server.base + conf.api.rds_server.resources)

        wrapper_json = json.dumps(data)

        if method == "POST":
            resp = requests.post(conf.api.rds_server.base + conf.api.rds_server.resources,
                                 data=wrapper_json,
                                 headers=headers,
                                 verify=conf.verify)
        else:
            resp = requests.put(conf.api.rds_server.base + conf.api.rds_server.resources,
                                data=wrapper_json,
                                headers=headers,
                                verify=conf.verify)
        if resp.content:
            LOG.debug("Response Content from rds server: {0}".format(resp.content))

        content = resp.content
        if resp.content:
            content = resp.json()

        if resp.content and 200 <= resp.status_code < 300:
            content = resp.json()
            return content

        raise ErrorStatus(resp.status_code, content)
