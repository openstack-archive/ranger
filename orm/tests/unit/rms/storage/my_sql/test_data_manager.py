import unittest

import mock

from orm.services.region_manager.rms.services import error_base
from orm.services.region_manager.rms.storage.my_sql import data_manager, data_models
from orm.services.region_manager.rms.storage.base_data_manager import DuplicateEntryError

end_point_list = [{"type": "ord",
                   "url": "http://ord.com"}]

meta_data_dict = {"key_1": ["value_1"]}


return_region = data_models.Region(region_id='SNA1')


class QueryObject():

    def __init__(self, ret=None):
        self.ret = ret

    def filter(self, query=None):
        ret = mock.MagicMock()
        if self.ret:
            ret.first.return_value = return_region
            return ret
        else:
            ret.first.return_value = None
            return ret

    def filter_by(self, *args, **kwargs):
        ret = mock.MagicMock()
        if self.ret:
            ret.first.return_value = return_region
            return ret
        else:
            ret.first.return_value = None
            return ret


class MyFacade(object):
    """Mock EngineFacade class."""

    def __init__(self, filter_by=None, query=None, is_ref_err=False):
        """Initialize the object."""
        self._filter_by = filter_by
        self._query = query
        self._is_ref_err = is_ref_err

    def get_session(self):
        """Make add() Raise a duplicate entry exception."""
        session = mock.MagicMock()
        dup_ent = data_manager.oslo_db.exception.DBDuplicateEntry
        session.add = mock.MagicMock(side_effect=dup_ent('test'))
        if self._is_ref_err:
            dup_ent = data_manager.oslo_db.exception.DBReferenceError
            session.add = mock.MagicMock(side_effect=dup_ent('test', "", "", ""))
        my_filter = mock.MagicMock()
        my_filter.filter_by = mock.MagicMock(return_value=self._filter_by)
        if self._query is not None:
            ret = self._query
        else:
            ret = my_filter
        session.query = mock.MagicMock(return_value=ret)

        return session


class TestDataManager(unittest.TestCase):

    @mock.patch.object(data_manager, 'db_session')
    def test_add_region_sanity(self, mock_db_session):
        """Test that no exception is raised when calling add_status_record."""
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.add_region("reg1", "region1", "a_state", "a_country",
                                   "a_city", "a_street", "a_zip", "a_status", "aic_ver",
                                   "os_ver", "design_type", "loc_type", "vlcp", "clli",
                                   end_point_list, meta_data_dict, "a_desc")

    @mock.patch.object(data_manager.db_session, 'EngineFacade', return_value=MyFacade())
    def test_add_region_duplicate_error(self, mock_db_session):
        """Test that duplicate exception is raised when calling add_status_record."""
        my_data_manager = data_manager.DataManager("url", "", "")
        with self.assertRaises(DuplicateEntryError):
            my_data_manager.add_region("reg1", "region1", "a_state", "a_country",
                                       "a_city", "a_street", "a_zip", "a_status", "aic_ver",
                                       "os_ver", "design_type", "loc_type", "vlcp", "clli",
                                       [], {}, "a_desc")

    @mock.patch.object(data_manager, 'db_session')
    def test_add_group_sanity(self, mock_db_session):
        """Test that no exception is raised when calling add_group."""
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.add_group("group1", "group 1", "bla bla", ["region1"])

    @mock.patch.object(data_manager.db_session, 'EngineFacade', return_value=MyFacade())
    def test_add_group_duplicate_error(self, mock_db_session):
        """Test that ConflictError is raised when calling add_group."""
        my_data_manager = data_manager.DataManager("url", "", "")
        with self.assertRaises(error_base.ConflictError):
            my_data_manager.add_group("group1", "group 1", "bla bla", ["region1"])

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(is_ref_err=True))
    def test_add_group_reference_error(self, mock_db_session):
        """Test that reference exception is raised when calling add_group."""
        my_data_manager = data_manager.DataManager("url", "", "")
        with self.assertRaises(error_base.InputValueError):
            my_data_manager.add_group("group1", "group 1", "bla bla", ["region1"])

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(query=QueryObject(ret=return_region)))
    def test_get_region_id_or_name_success(self, mock_db_session):
        my_data_manager = data_manager.DataManager('url', "", "")
        result = my_data_manager.get_region_by_id_or_name("id")
        self.assertEqual(result.id, 'SNA1')

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_get_region_id_or_name_None(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        result = my_data_manager.get_region_by_id_or_name("id")
        self.assertEqual(result, None)

    @mock.patch.object(data_manager.db_session, 'EngineFacade')
    def test_get_region_id_or_name_error(self, mock_db_session):
        mock_get_session = mock.MagicMock()
        mock_get_session.get_session.side_effect = ValueError('test')
        mock_db_session.return_value = mock_get_session

        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(ValueError, my_data_manager.get_region_by_id_or_name,
                          "id")

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           filter_by=[return_region]))
    def test_get_regions(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        result = my_data_manager.get_regions(
            region_filters_dict={"meta_data_key": "1"},
            meta_data_dict=None, end_point_dict=None)
        self.assertEqual(result[0].id, return_region.region_id)

        # Test that no exception is raised on the other successful flow
        mock_db_session.return_value = mock.MagicMock()
        my_data_manager.get_regions(
            region_filters_dict=None,
            meta_data_dict={"meta_data_keys": ["1"], "meta_data_pairs": []},
            end_point_dict=end_point_list[0])

    @mock.patch.object(data_manager.db_session, 'EngineFacade')
    def test_get_all_regions(self, mock_db_session):
        all_regions = [return_region]
        mock_db_session.return_value = MyFacade(query=all_regions)
        my_data_manager = data_manager.DataManager("url", "", "")

        result = my_data_manager.get_all_regions()
        self.assertEqual(len(result), len(all_regions))
        self.assertEqual(result[0].id, all_regions[0].region_id)

    @mock.patch.object(data_manager, 'db_session')
    def test_update_region_sanity(self, mock_db_session):
        """Test that no exception is raised when calling update_region."""
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.update_region("reg1", "region1", "region_name",
                                      "a_state", "a_country",
                                      "a_city", "a_street", "a_zip", "a_status",
                                      "aic_ver",
                                      "os_ver", "design_type", "loc_type",
                                      "vlcp", "clli",
                                      end_point_list, meta_data_dict, "a_desc")

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_update_region_region_not_found(self, mock_engine_facade):
        """Test that NotFoundError is raised when calling update_region."""
        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(data_manager.error_base.NotFoundError,
                          my_data_manager.update_region, "reg1", "region1",
                          "region_name",
                          "a_state", "a_country",
                          "a_city", "a_street", "a_zip", "a_status",
                          "aic_ver",
                          "os_ver", "design_type", "loc_type",
                          "vlcp", "clli",
                          end_point_list, meta_data_dict, "a_desc")

    @mock.patch.object(data_manager.db_session, 'EngineFacade')
    def test_update_region_other_error(self, mock_engine_facade):
        """Test that ValueError is raised when calling update_region."""
        mock_session = mock.MagicMock()
        mock_session.get_session.side_effect = ValueError('test')
        mock_engine_facade.return_value = mock_session
        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(ValueError,
                          my_data_manager.update_region, "reg1", "region1",
                          "region_name",
                          "a_state", "a_country",
                          "a_city", "a_street", "a_zip", "a_status",
                          "aic_ver",
                          "os_ver", "design_type", "loc_type",
                          "vlcp", "clli",
                          end_point_list, meta_data_dict, "a_desc")

    @mock.patch.object(data_manager, 'db_session')
    def test_delete_region_sanity(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.delete_region("region")

    @mock.patch.object(data_manager, 'db_session')
    def test_add_meta_data_to_region_sanity(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.add_meta_data_to_region('region', {'meta': 'data'})

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_add_meta_data_to_region_region_not_found(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        result = my_data_manager.add_meta_data_to_region('region',
                                                         {'meta': 'data'})
        self.assertIsNone(result)

    @mock.patch.object(data_manager.db_session, 'EngineFacade')
    def test_add_meta_data_to_region_error(self, mock_db_session):
        mock_begin = mock.MagicMock()
        mock_begin.begin.side_effect = data_manager.oslo_db.exception.DBDuplicateEntry(
            'test')
        mock_get_session = mock.MagicMock()
        mock_get_session.get_session.return_value = mock_begin
        mock_db_session.return_value = mock_get_session

        my_data_manager = data_manager.DataManager("url", "", "")

        self.assertRaises(data_manager.error_base.ConflictError,
                          my_data_manager.add_meta_data_to_region,
                          'region', {'meta': 'data'})

    @mock.patch.object(data_manager, 'db_session')
    def test_update_region_meta_data_sanity(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.update_region_meta_data('region', {'meta': 'data'})

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_update_region_meta_data_region_not_found(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(data_manager.error_base.NotFoundError,
                          my_data_manager.update_region_meta_data,
                          'region', {'meta': 'data'})

    @mock.patch.object(data_manager, 'db_session')
    def test_delete_region_metadata_sanity(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.delete_region_metadata('region', {'meta': 'data'})

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_delete_region_metadata_region_not_found(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(data_manager.error_base.NotFoundError,
                          my_data_manager.delete_region_metadata,
                          'region', {'meta': 'data'})

    @mock.patch.object(data_manager, 'db_session')
    def test_update_region_status_sanity(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        my_data_manager.update_region_status('region', 'status')

    @mock.patch.object(data_manager.db_session, 'EngineFacade',
                       return_value=MyFacade(
                           query=QueryObject(ret=None)))
    def test_update_region_status_region_not_found(self, mock_db_session):
        my_data_manager = data_manager.DataManager("url", "", "")
        self.assertRaises(data_manager.error_base.NotFoundError,
                          my_data_manager.update_region_status,
                          'region', 'status')

    @mock.patch.object(data_manager, 'db_session')
    def test_group_functions_sanity(self, mock_db_session):
        """Test that no exception is raised when calling group functions."""
        my_data_manager = data_manager.DataManager("url", "", "")

        my_data_manager.delete_group('group')
        my_data_manager.get_group('group')
        my_data_manager.update_group('id', 'name', 'description', ['region'])
        my_data_manager.get_all_groups()
