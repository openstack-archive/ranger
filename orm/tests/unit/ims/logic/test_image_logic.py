from orm.services.image_manager.ims.logic import image_logic
from orm.services.image_manager.ims.persistency.sql_alchemy.db_models import Image
from orm.services.image_manager.ims.persistency.wsme import models
from orm.tests.unit.ims import FunctionalTest

import mock


class RDSGetStatus():
    def __init__(self, status_code=200):
        self.status_code = status_code

    def json(self):
        return {'status': 'Success'}


class ImageTest():
    def __init__(self, id=None, status=None, regions=[], min_ram=None,
                 customers=[]):
        self.id = id
        self.status = status
        self.regions = regions
        self.min_ram = min_ram
        self.created_at = "12345678"
        self.updated_at = "12345678"
        self.customers = customers

    def to_db_model(self):
        return ImageTest()

    def validate_model(self, context=None):
        pass

    def validate_update(self, sql_image=None, new_image=None):
        pass


class ImageWrapperTest():
    def __init__(self, image=ImageTest(id=1, status='')):
        self.image = image

    def to_db_model(self):
        return ImageWrapperTest()

    def validate_model(self, context=None):
        pass


class MyError(Exception):
    def __init__(self, message=None):
        self.message = message


class RdsResponse(object):
    """class."""

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {'status': 'Success'}


resolved_regions = [{'type': 'single', 'name': 'rdm1'}]

visibility = "private"
regions = []
image_status_dict = {u'regions': [{u'status': u'Submitted',
                                   u'resource_id':
                                       u'edf1a8152b974eb28a6f4aa3dee3190d',
                                   u'timestamp': 1471954276950,
                                   u'region': u'rdm1',
                                   u'ord_notifier_id': u'',
                                   u'ord_transaction_id':
                                       u'b18836a0-692a-11e6-82f3-005056a5129b',
                                   u'error_code': u'', u'error_msg': u''}],
                     u'status': u'Pending'}


class TestImageLogic(FunctionalTest):
    @mock.patch.object(image_logic, 'di')
    def test_get_image_by_uuid_image_not_found(self, mock_di):
        mock_rds_proxy = mock.MagicMock()
        my_get_image = mock.MagicMock()
        my_get_image.get_image_by_id.return_value = None
        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        try:
            image_logic.get_image_by_uuid('te')
        except image_logic.ErrorStatus as e:
            self.assertEqual(e.status_code, 404)

    @mock.patch.object(image_logic.ImsUtils, 'get_server_links',
                       return_value=["ip", "path"])
    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_get_image_by_uuid_image_no_status(self, mock_image,
                                               mock_di, mock_links):
        mock_rds_proxy = mock.MagicMock()
        mock_rds_proxy.get_status.return_value = RDSGetStatus(status_code=404)
        mock_image.from_db_model.return_value = ImageWrapperTest()
        my_get_image = mock.MagicMock()
        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        result = image_logic.get_image_by_uuid('test')
        self.assertEqual(result.image.status, 'no regions')

    @mock.patch.object(image_logic.ImsUtils, 'get_server_links',
                       return_value=["ip", "path"])
    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_get_image_by_uuid_image_sanity(self, mock_image,
                                            mock_di, mock_links):
        mock_rds_proxy = mock.MagicMock()
        mock_rds_proxy.get_status.return_value = RDSGetStatus()
        my_get_image = mock.MagicMock()
        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        result = image_logic.get_image_by_uuid('test')
        self.assertEqual(result.image.status, 'Success')


class TestDeleteImageLogic(FunctionalTest):
    """test delete image."""

    @mock.patch.object(image_logic, 'update_region_actions', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_image_success(self, mock_di, mock_update_region):
        mock_rds_proxy, mock_data_manager = get_data_manager_mock(
            get_existing_region_names=[])
        mock_rds_proxy.get_status.return_value = RdsResponse()
        mock_di.resolver.unpack.return_value = (mock_rds_proxy,
                                                mock_data_manager)
        global regions
        regions = []
        image_logic.delete_image_by_uuid("image_uuid", "transaction_id")

    @mock.patch.object(image_logic, 'update_region_actions', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_image_success_nords(self, mock_di, mock_update_region):
        mock_rds_proxy, mock_data_manager = \
            get_data_manager_mock(imagejson={"regions": {}},
                                  get_existing_region_names=[])
        mock_rds_proxy.get_status.return_value = RdsResponse()
        mock_di.resolver.unpack.return_value = (mock_rds_proxy,
                                                mock_data_manager)
        image_logic.delete_image_by_uuid("image_uuid", "transaction_id")

    @mock.patch.object(image_logic, 'update_region_actions', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_image_notfound_error(self, mock_di, mock_update_region):
        mock_rds_proxy, mock_data_manager = \
            get_data_manager_mock(mock_sql_image=None)
        mock_di.resolver.unpack.return_value = (mock_rds_proxy,
                                                mock_data_manager)
        try:
            image_logic.delete_image_by_uuid("image_uuid", "transaction_id")
        except Exception as e:
            self.assertEqual(404, e.status_code)

    @mock.patch.object(image_logic, 'update_region_actions',
                       side_effect=ValueError('test'))
    @mock.patch.object(image_logic, 'di')
    def test_delete_image_other_error(self, mock_di, mock_update_region):
        mock_rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = (mock_rds_proxy,
                                                mock_data_manager)
        self.assertRaises(image_logic.ErrorStatus, image_logic.delete_image_by_uuid,
                          "image_uuid", "transaction_id")


class TestUpdateImage(FunctionalTest):
    """tests for update image."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageTest(id="image_id"))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_update_image_success(self, mock_di, mock_send_to_rds_if_needed,
                                  mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        result = image_logic.update_image(ImageTest(), "imgae_id",
                                          "transaction_id")

        self.assertEqual("image_id", result.id)

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageTest(id="image_id"))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_update_image_notfound(self, mock_di, mock_send_to_rds_if_needed,
                                   mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock(
            mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        try:
            result = image_logic.update_image(ImageTest(), "image_id",
                                              "transaction_id")
        except Exception as e:
            self.assertEqual(404, e.status_code)

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageTest(id="image_id"))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed',
                       side_effect=Exception("rds not found"))
    @mock.patch.object(image_logic, 'di')
    def test_update_image_anyerror(self, mock_di, mock_send_to_rds_if_needed,
                                   mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager

        self.assertRaises(Exception, image_logic.update_image, ImageTest(),
                          "imgae_id", "transaction_id")


class TestActivateImageLogic(FunctionalTest):
    """test activate/deactivate image."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageTest(**{'status': 'Success'}))
    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_activate_image_activate_no_activated_image(self,
                                                        mock_image,
                                                        mock_di,
                                                        mock_by_uuid):
        my_enabled = mock.MagicMock()
        my_enabled.enabled = 0

        my_get_image = mock.MagicMock()
        my_get_image.get_image_by_id = mock.MagicMock(return_value=my_enabled)

        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm
        result = image_logic.enable_image("test_id", 1, "transaction_id")
        self.assertEqual(result.status, 'Success')

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageTest(**{'status': 'Success'}))
    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_activate_image_already_activated(self, mock_image,
                                              mock_di,
                                              mock_get_image_by_uuid):
        my_enabled = mock.MagicMock()
        my_enabled.enabled = 1

        my_get_image = mock.MagicMock()
        my_get_image.get_image_by_id = mock.MagicMock(return_value=my_enabled)

        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm
        result = image_logic.enable_image("test_id", 1, "transaction_id")
        self.assertEqual(result.status, 'Success')

    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_activate_image_image_not_found(self, mock_image,
                                            mock_di):
        my_get_image = mock.MagicMock()
        my_get_image.get_image_by_id.return_value = None
        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm
        try:
            image_logic.enable_image("test_id", 1, "transaction_id")
        except image_logic.ErrorStatus as e:
            self.assertEqual(e.status_code, 404)

    @mock.patch.object(image_logic, 'LOG')
    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_activate_image_image_other_exception(self,
                                                  mock_image,
                                                  mock_di,
                                                  log_moc):
        my_get_image = mock.MagicMock()
        my_get_image.get_image_by_id = mock.MagicMock(side_effect=MyError("activate_test"))

        my_get_record = mock.MagicMock()
        my_get_record.get_record.return_value = my_get_image
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm
        try:
            image_logic.enable_image("test_id", 1, "transaction_id")
        except Exception as e:
            self.assertEqual(e.message, 'activate_test')


class TestListImageLogic(FunctionalTest):
    @mock.patch.object(image_logic, 'di')
    def test_list_image_not_found(self, mock_di):
        mock_rds_proxy = mock.MagicMock()
        my_get_image = mock.MagicMock()
        my_get_image.get_image.return_value = None
        my_get_record = mock.MagicMock()
        my_get_record.get_record.side_effect = image_logic.ErrorStatus(404, 'a')
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        try:
            image_logic.get_image_list_by_params('a', 'b', 'c')
        except image_logic.ErrorStatus as e:
            self.assertEqual(e.status_code, 404)

    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_list_image_error(self, mock_image, mock_di):
        mock_rds_proxy = mock.MagicMock()
        my_get_image = mock.MagicMock()
        my_get_record = mock.MagicMock()
        my_get_record.get_record.side_effect = SystemError()
        my_dm = mock.MagicMock(return_value=my_get_record)

        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        try:
            image_logic.get_image_list_by_params('a', 'b', 'c')
        except Exception as e:
            self.assertEqual(e.message, '')

    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_list_image_sanity(self, mock_image, mock_di):
        imagejson = [{"regions": {"name": "mdt1"}}]
        mock_rds_proxy = mock.MagicMock()
        mock_rds_proxy.get_status.return_value = RDSGetStatus()
        mock_data_manager = mock.MagicMock()
        mock_image_rec = mock.MagicMock()
        image_json = mock.MagicMock()
        image_json.return_value = imagejson

        mock_image_rec.get_images_by_criteria.return_value = Image()
        my_dm = mock.MagicMock(mock_data_manager)
        mock_di.resolver.unpack.return_value = my_dm, mock_rds_proxy
        result = image_logic.get_image_list_by_params('a', 'b', 'c')
        self.assertEqual(len(result.images), 0)


class TestCreateImage(FunctionalTest):
    def setUp(self):
        FunctionalTest.setUp(self)

    def tearDown(self):
        FunctionalTest.tearDown(self)

    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    @mock.patch.object(image_logic, 'get_image_by_uuid', return_value='test')
    def test_create_image_sanity(self, mock_di, mock_req, mock_get):
        my_image = mock.MagicMock()
        my_dm = mock.MagicMock()
        my_dm.get_record.return_value = my_image
        my_mock = mock.MagicMock(return_value=my_dm)
        mock_di.resolver.unpack.return_value = my_mock

        result = image_logic.create_image(mock.MagicMock(), 'test1', 'test2')
        self.assertEqual('test', result)

    @mock.patch.object(image_logic, 'di')
    @mock.patch.object(image_logic, 'ImageWrapper')
    def test_create_image_validate_model_failure(self, mock_image, mock_di):
        image = mock.MagicMock()
        image.validate_model.side_effect = ValueError('test')

        self.assertRaises(ValueError, image_logic.create_image, image,
                          'test1', 'test2')


class TestAddRegions(FunctionalTest):
    """tests for add regions."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(regions=[models.Region('region')])))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_regions_success(self, mock_di, mock_send_to_rds_if_needed,
                                 mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        result = image_logic.add_regions('uuid', regions_wrapper,
                                         'transaction')

        self.assertEqual(len(result.regions), 1)
        self.assertEqual('region', result.regions[0].name)

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_regions_image_not_found(self, mock_di, mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock(mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        self.assertRaises(image_logic.ErrorStatus, image_logic.add_regions,
                          'uuid', regions_wrapper, 'transaction')

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       side_effect=ValueError('test'))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_regions_other_error(self, mock_di, mock_send_to_rds_if_needed,
                                     mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        self.assertRaises(ValueError, image_logic.add_regions,
                          'uuid', regions_wrapper, 'transaction')


class TestReplaceRegions(FunctionalTest):
    """tests for replace regions."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(regions=[models.Region('region')])))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_regions_success(self, mock_di, mock_send_to_rds_if_needed,
                                     mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        result = image_logic.replace_regions('uuid', regions_wrapper,
                                             'transaction')

        self.assertEqual(len(result.regions), 1)
        self.assertEqual('region', result.regions[0].name)

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_regions_image_not_found(self, mock_di, mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock(mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        self.assertRaises(image_logic.ErrorStatus, image_logic.replace_regions,
                          'uuid', regions_wrapper, 'transaction')

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       side_effect=ValueError('test'))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_regions_other_error(self, mock_di,
                                         mock_send_to_rds_if_needed,
                                         mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        regions_wrapper = mock.MagicMock()
        regions_wrapper.regions = [mock.MagicMock()]
        self.assertRaises(ValueError, image_logic.replace_regions,
                          'uuid', regions_wrapper, 'transaction')


class TestDeleteRegion(FunctionalTest):
    """tests for delete region."""

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_region_success(self, mock_di, mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        result = image_logic.delete_region('uuid', mock.MagicMock(),
                                           'transaction', True, False)

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_region_rds_err_force_delete(self, mock_di, mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        result = image_logic.delete_region('uuid', mock.MagicMock(),
                                           'transaction', False, True)

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_region_image_not_found(self, mock_di,
                                           mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock(
            mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus, image_logic.delete_region,
                          'uuid', mock.MagicMock(), 'transaction', False, False)

    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_delete_region_protected_image(self, mock_di,
                                           mock_send_to_rds_if_needed):
        rds_proxy, mock_data_manager = get_data_manager_mock(protected=True)
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus, image_logic.delete_region,
                          'uuid', mock.MagicMock(), 'transaction', False, False)

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       side_effect=ValueError('test'))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed',
                       side_effect=ValueError)
    @mock.patch.object(image_logic, 'di')
    def test_delete_region_other_error(self, mock_di,
                                       mock_send_to_rds_if_needed,
                                       mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(ValueError, image_logic.delete_region,
                          'uuid', mock.MagicMock(), 'transaction', False, False)


class TestAddCustomers(FunctionalTest):
    """tests for add customers."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_customers_success(self, mock_di, mock_send_to_rds_if_needed,
                                   mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        customers_wrapper = models.CustomerWrapper(['customer'])
        result = image_logic.add_customers('uuid', customers_wrapper,
                                           'transaction')
        self.assertEqual(result.image.customers.customers, ['customer'])

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_customers_image_not_found(self, mock_di,
                                           mock_send_to_rds_if_needed,
                                           mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock(
            mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus, image_logic.add_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_add_customers_public_image(self, mock_di,
                                        mock_send_to_rds_if_needed,
                                        mock_get_image_by_uuid):
        global visibility
        visibility = 'public'
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus, image_logic.add_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')
        visibility = 'private'

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed',
                       side_effect=ValueError('Duplicate entry'))
    @mock.patch.object(image_logic, 'di')
    def test_add_customers_duplicate_entry(self, mock_di,
                                           mock_send_to_rds_if_needed,
                                           mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus, image_logic.add_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')


class TestReplaceCustomers(FunctionalTest):
    """tests for replace customers."""

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_customers_success(self, mock_di,
                                       mock_send_to_rds_if_needed,
                                       mock_get_image_by_uuid):
        global visibility
        visibility = 'private'
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        customers_wrapper = models.CustomerWrapper(['customer'])
        result = image_logic.replace_customers('uuid', customers_wrapper,
                                               'transaction')
        self.assertEqual(result.image.customers.customers, ['customer'])

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_customers_image_not_found(self, mock_di,
                                               mock_send_to_rds_if_needed,
                                               mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock(
            mock_sql_image=None)
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus,
                          image_logic.replace_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed', return_value=True)
    @mock.patch.object(image_logic, 'di')
    def test_replace_customers_public_image(self, mock_di,
                                            mock_send_to_rds_if_needed,
                                            mock_get_image_by_uuid):
        global visibility
        visibility = 'public'
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(ValueError,
                          image_logic.replace_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')
        visibility = 'private'

    @mock.patch.object(image_logic, 'get_image_by_uuid',
                       return_value=ImageWrapperTest(
                           image=ImageTest(
                               customers=models.CustomerWrapper(['customer']))))
    @mock.patch.object(image_logic, 'send_to_rds_if_needed',
                       side_effect=ValueError('Duplicate entry'))
    @mock.patch.object(image_logic, 'di')
    def test_replace_customers_duplicate_entry(self, mock_di,
                                               mock_send_to_rds_if_needed,
                                               mock_get_image_by_uuid):
        rds_proxy, mock_data_manager = get_data_manager_mock()
        mock_di.resolver.unpack.return_value = mock_data_manager
        self.assertRaises(image_logic.ErrorStatus,
                          image_logic.replace_customers,
                          'uuid', mock.MagicMock(),
                          'transaction')


def get_data_manager_mock(get_existing_region_names={"name": "mdt1"},
                          imagejson={"regions": {"name": "mdt1"}},
                          delete_image_by_id=True,
                          protected=False,
                          begin_transaction=True,
                          flush=True,
                          send_image=True,
                          mock_sql_image=True):
    mock_rds_proxy = mock.MagicMock()
    mock_data_manager = mock.MagicMock()
    mock_data_manager_return_value = mock.MagicMock()
    mock_image_rec = mock.MagicMock()
    image_json = mock.MagicMock()
    image_json.return_value = imagejson
    if mock_sql_image:
        mock_sql_image = mock.MagicMock()
        mock_sql_image.__json__ = image_json
        mock_sql_image.visibility = visibility
        mock_sql_image.protected = protected
        mock_sql_image.get_proxy_dict = mock.MagicMock(return_value={'regions': regions})
        mock_sql_image.get_existing_region_names.return_value = \
            get_existing_region_names
    mock_image_rec.get_image_by_id.return_value = mock_sql_image
    mock_image_rec.delete_image_by_id.return_value = delete_image_by_id
    mock_image_rec.insert.return_value = True
    mock_data_manager_return_value.begin_transaction.return_value = \
        begin_transaction
    mock_data_manager_return_value.flush.return_value = flush
    mock_data_manager_return_value.get_record.return_value = mock_image_rec
    mock_rds_proxy.send_image.return_value = send_image
    mock_data_manager.return_value = mock_data_manager_return_value

    return mock_rds_proxy, mock_data_manager
