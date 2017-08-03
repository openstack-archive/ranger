"""Services module unittests."""
import mock
from mock import patch
from pecan import conf
from rms.controllers.v2.orm.resources import regions
from rms.services import services
from rms.tests.controllers.v1.orm.resources.test_region import full_region
from rms.tests import FunctionalTest

# from rms.model import url_parm as parms


class db(object):
    def __init__(self, name=None, exp=None):
        self.name = name
        self.exp = exp

    def get_group(self, name=None):
        if name:
            return {'regions': [u'lcp_1'],
                    'name': u'ccplz',
                    'description': u'b'}
        else:
            return None

    def get_all_groups(self):
        if self.exp:
            raise Exception("any")
        return [{'regions': [u'lcp_1'], 'name': u'ccplz',
                'description': u'b'}, {'regions': [u'lcp_1'], 'name': u'ccplz',
                                       'description': u'b'}]

    def add_group(self, *items):
        if items[3] and "bad_region" in items[3]:
            raise services.error_base.InputValueError()

    def get_regions(self, region_dict=None, metadata_dict=None,
                    end_point=None):
        if region_dict:
            return {'regions': [u'lcp_1'],
                    'name': u'ccplz',
                    'description': u'b'}
        else:
            return None

    def delete_group(self, id):
        if self.exp:
            raise Exception("any")
        return None

    def get_region_by_id_or_name(self, id_name):
        return id_name

    def add_region(self, **kw):
        if self.exp:
            raise Exception("any")
        return True

    def update_region(self, id=None, **kw):
        if self.exp == "not found":
            raise services.error_base.NotFoundError(message="id not found")
        elif self.exp:
            raise Exception("error")
        return True

    def delete_region(self, id=None, **kw):
        if self.exp:
            raise Exception("not deleted")
        return True


class URlParm(object):

    def __init__(self, metadata=None, clli=None):
        self.metadata = metadata
        self.clli = clli

    def _build_query(self):
        if self.metadata:
            return (self.metadata, self.clli, None)
        return (None, None, None)


class TestServices(FunctionalTest):
    """Main test case for the Services module."""

    def _to_wsme_from_input(self, input):
        full_region = input
        obj = regions.RegionsData()
        obj.clli = full_region["CLLI"]
        obj.name = full_region["name"]
        obj.design_type = full_region["designType"]
        obj.location_type = full_region["locationType"]
        obj.vlcp_name = full_region["vlcpName"]
        obj.id = full_region["id"]
        obj.address.country = full_region["address"]["country"]
        obj.address.city = full_region["address"]["city"]
        obj.address.state = full_region["address"]["state"]
        obj.address.street = full_region["address"]["street"]
        obj.address.zip = full_region["address"]["zip"]
        obj.ranger_agent_version = full_region["rangerAgentVersion"]
        obj.open_stack_version = full_region["OSVersion"]
        obj.metadata = full_region["metadata"]
        obj.status = full_region["status"]
        obj.endpoints = []
        for endpoint in full_region["endpoints"]:
            obj.endpoints.append(regions.EndPoint(type=endpoint["type"],
                                                  publicurl=endpoint[
                                                      "publicURL"]))
        return obj

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_groups_data(self, mock_db_get_group):
        services.get_groups_data('ccplz')

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp=True))
    def test_get_all_groups_data_err(self, mock_db_get_group):
        with self.assertRaises(Exception) as exp:
            services.get_all_groups()

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_all_groups_data(self, mock_db_get_group):
        services.get_all_groups()

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_delete_group(self, mock_db_get_group):
        services.delete_group('id')

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp=True))
    def test_delete_group_err(self, mock_db_get_group):
        with self.assertRaises(Exception) as exp:
            services.delete_group('id')

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_groups_empty_data(self, mock_db_get_group):
        self.assertRaises(services.error_base.NotFoundError,
                          services.get_groups_data, None)

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_regions_empty_data(self, mock_db_get_group):
        url_parm = URlParm()
        self.assertRaises(services.error_base.NotFoundError,
                          services.get_regions_data, url_parm)

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_regions_data(self, mock_db_get_group):
        url_parm = URlParm(metadata="key,value", clli="any")
        services.get_regions_data(url_parm)

    @patch.object(services.data_manager_factory, 'get_data_manager')
    def test_create_group_in_db_success(self, mock_get_data_manager):
        """Make sure that no exception is raised."""
        services.create_group_in_db('d', 'a', 'b', ['c'])

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_create_group_in_db_not_valid_regions(self, mock_get_data_manager):
        """Make sure that no exception is raised."""
        with self.assertRaises(services.error_base.NotFoundError) as exp:
            services.create_group_in_db('d', 'a', 'b', ['bad_region'])

    @patch.object(services.data_manager_factory, 'get_data_manager')
    def test_create_group_in_db_duplicate_entry(self, mock_get_data_manager):
        """Make sure that the expected exception is raised if group exists."""
        my_manager = mock.MagicMock()
        my_manager.add_group = mock.MagicMock(
            side_effect=services.error_base.ConflictError(
                'test'))
        mock_get_data_manager.return_value = my_manager
        self.assertRaises(services.error_base.ConflictError,
                          services.create_group_in_db, 'd', 'a', 'b', ['c'])

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_region_by_id_or_name(self, mock_data_manager_factory):
        result = services.get_region_by_id_or_name({"test1": "test1"})
        self.assertEqual(result, {"test1": "test1"})

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_get_region_by_id_or_name_no_content(self,
                                                 mock_data_manager_factory):
        self.assertRaises(services.error_base.NotFoundError,
                          services.get_region_by_id_or_name, None)

    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=Exception("any"))
    def test_get_region_by_id_or_name_500(self, mock_data_manager_factory):
        self.assertRaises(Exception, services.get_region_by_id_or_name, "id")

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_create_region_success(self, mock_db_get_group,
                                   mock_get_region_id_name):
        result = services.create_full_region(self._to_wsme_from_input(full_region))
        self.assertEqual(result, {"a": "b"})

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_create_region_duplicate(self, mock_db_create_region,
                                     mock_get_region_id_name):
        duplicate = mock.MagicMock()
        duplicate.side_effect = services.base_data_manager.DuplicateEntryError()
        mock_db_create_region.return_value.add_region = duplicate
        with self.assertRaises(services.error_base.ConflictError) as exp:
            result = services.create_full_region(
                self._to_wsme_from_input(full_region))

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_create_region_validate_status_error(self, mock_db_get_group,
                                                 mock_get_region_id_name):
        orig_status = full_region['status']
        full_region['status'] = "123"
        allowed_status = conf.region_options.allowed_status_values[:]
        with self.assertRaises(services.error_base.InputValueError) as exp:
            result = services.create_full_region(self._to_wsme_from_input(full_region))
            test_ok = str(allowed_status) in exp.expected.message
            self.assertEqual(test_ok, True)
        full_region['status'] = orig_status

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_create_region_validate_endpoints_error(self, mock_db_get_group,
                                                    mock_get_region_id_name):
        message = ""
        endpoints_types_must_have = conf.region_options.endpoints_types_must_have[:]
        orig_endpoint = full_region['endpoints']
        full_region['endpoints'] = [
            {
                "type": "dashboards",
                "publicURL": "http://horizon1.com"
            }]
        try:
            result = services.create_full_region(
                self._to_wsme_from_input(full_region))
        except services.error_base.InputValueError as exp:
            message = exp.message
        full_region['endpoints'] = orig_endpoint
        self.assertEqual(str(endpoints_types_must_have) in str(message), True)

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp=True))
    def test_create_region_validate_any_error(self, mock_db_get_group,
                                              mock_get_region_id_name):
        message = None
        try:
            result = services.create_full_region(
                self._to_wsme_from_input(full_region))
        except Exception as exp:
            message = exp.message
        self.assertEqual(message, "any")

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_update_region_success(self, mock_db_get_group,
                                   mock_get_region_id_name):
        result = services.update_region('id',
                                        self._to_wsme_from_input(full_region))
        self.assertEqual(result, {"a": "b"})

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp=True))
    def test_update_region_error(self, mock_db_get_group,
                                 mock_get_region_id_name):
        try:
            result = services.update_region('id',
                                            self._to_wsme_from_input(full_region))
        except Exception as exp:
            message = exp.message
        self.assertEqual(message, "error")

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp="not found"))
    def test_update_region_notfound_error(self, mock_db_get_group,
                                          mock_get_region_id_name):
        try:
            result = services.update_region('id',
                                            self._to_wsme_from_input(full_region))
        except services.error_base.NotFoundError as exp:
            message = exp.message
        self.assertEqual(message, "id not found")

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db(exp=True))
    def test_delete_region_error(self, mock_db_get_group,
                                 mock_get_region_id_name):
        try:
            result = services.delete_region(self._to_wsme_from_input(full_region))
        except Exception as exp:
            message = exp.message
        self.assertEqual(message, "not deleted")

    @patch.object(services, 'get_region_by_id_or_name',
                  return_value={"a": "b"})
    @patch.object(services.data_manager_factory, 'get_data_manager',
                  return_value=db())
    def test_delete_region_success(self, mock_db_get_group,
                                   mock_get_region_id_name):
        result = services.delete_region(self._to_wsme_from_input(full_region))
