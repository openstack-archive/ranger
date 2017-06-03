import copy
import uuid
from mock import MagicMock
from fms_rest.data.sql_alchemy.data_manager import DataManager

from fms_rest.logger import get_logger
logger = get_logger(__name__)


def post(url, **kwargs):
    if 'rds/resources' in url:
        logger.debug('MOCK: requests.post called for rds/resources')
        return _build_rds_response()

    elif 'uuids' in url:
        logger.debug('MOCK: requests.post called for uuid')
        return _build_uuid_response()


def delete(url, **kwargs):
    if 'rds/resources' in url:
        logger.debug('MOCK: requests.deletr called for rds/resources')
        return _build_rds_response()

    else:
        raise Exception("No delete action for this url".format(url))


def get(url):
    if 'status/resource' in url:
        logger.debug('MOCK: requests.get called for status/resources')
        return _build_status_response(url)


def _build_uuid_response():
    res = MagicMock()
    res.json.return_value = {
        'uuid': str(uuid.uuid1())
    }

    return res


def _build_rds_response():
    response = MagicMock()
    response.status_code = 201
    response.content = {"flavor": {"profile": "p1",
                                   "status": "Error",
                                   "description": "A standard 2GB Ram 2 vCPUs 50GB Disk, Flavor",
                                   "extra-specs": {"key3": "value3",
                                                   "key2": "value2",
                                                   "key1": "value1"},
                                   "ram": "4096",
                                   "ephemeral": "0",
                                   "visibility": "private",
                                   "regions": [
                                              {
                                                "status": "Error",
                                                "name": "dkk12"
                                              }, {
                                                  "status": "Error",
                                                  "name": "san12"}],
                                   "vcpus": "2",
                                   "swap": "1024",
                                   "disk": "50",
                                   "tenants": ["070be05e-26e2-4519-a46d-224cbf8558f4", "4f7b9561-af8b-4cc0-87e2-319270dad49e"],
                                   "id": "a5310ede-1c15-11e6-86bb-005056a50d38",
                                   "name": "fr4096v2d50"
                                   }
                        }

    response.json.return_value = response.content
    return response


def _build_status_response(url):
    uuid_index = url.find('status/resource/') + 16
    uuid = url[uuid_index:]
    datamanager = DataManager()
    flavor_record = datamanager.get_record('flavor')
    sql_flavor = flavor_record.get_flavor_by_id(uuid)
    _status_response['regions'] = []
    for sql_region in sql_flavor.flavor_regions:
        new_region = copy.copy(_region_mock)
        new_region['region'] = sql_region.region_name
        _status_response['regions'].append(new_region)
    mock = MagicMock()
    mock.json.return_value = _status_response
    return mock


_region_mock = {
    "region": "dla1",
    "timestamp": "1451599200",
    "ord-transaction-id": "0649c5be323f4792afbc1efdd480847d",
    "resource-id": "12fde398643acbed32f8097c98aec20",
    "ord-notifier-id": "",
    "status": "success",
    "error-code": "200",
    "error-msg": "OK"
}

_status_response = {
    "status": "pending",
    "regions": []
}
