import logging
import os
from unittest import TestCase

import mock
from orm_common.injector import injector

logger = logging.getLogger(__name__)


class TestInjector(TestCase):
    def setUp(self):
        pass

    @mock.patch.object(injector, '_import_file_by_name')
    def test_register_providers(self, mock_import_file_by_name):
        os.environ['CMS_ENV'] = 'test'
        injector.register_providers('CMS_ENV', 'a/b/c', logger)

    @mock.patch.object(injector, '_import_file_by_name')
    def test_register_providers_env_not_exist(self, mock_import_file_by_name):
        injector.register_providers('CMS_ENV1', 'a/b/c', logger)

    @mock.patch.object(injector, '_import_file_by_name')
    def test_register_providers_env_test(self, mock_import_file_by_name):
        os.environ['CMS_ENV2'] = '__TEST__'
        injector.register_providers('CMS_ENV2', 'a/b/c', logger)

    @mock.patch.object(injector, '_import_file_by_name')
    def test_register_providers_with_existing_provider(self, mock_import_file_by_name):
        mock_import_file_by_name.return_value = type('module', (object,), {'providers': ['a1', 'b2']})()
        os.environ['c3'] = 'test'
        injector.register_providers('c3', 'a/b/c', logger)

    def test_get_di(self):
        injector.get_di()

    @mock.patch.object(injector, 'logger')
    def test_import_file_by_name_ioerror(self, mock_logger):
        injector.logger = mock.MagicMock()
        # Calling it with ('', '.') should raise an IOError
        # (no such file or directory)
        self.assertRaises(IOError, injector._import_file_by_name, '', '.')

    @mock.patch.object(injector.imp, 'load_source', return_value='test')
    def test_import_file_by_name_sanity(self, mock_load_source):
        self.assertEqual(injector._import_file_by_name('', '.'), 'test')

    @mock.patch.object(injector._di.providers, 'register_instance')
    def test_override_injected_dependency(self, mock_di):
        injector.override_injected_dependency((1, 2,))
        self.assertTrue(mock_di.called)

    '''
    @mock.patch.object(ResourceProviderRegister, 'register_instance')
    def test_override_injected_dependency(self, mock_resourceProviderRegister):
        injector.override_injected_dependency(mock.Mock())
    '''
