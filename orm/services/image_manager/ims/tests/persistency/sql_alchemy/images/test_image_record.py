from ims.persistency.sql_alchemy import data_manager
from ims.persistency.sql_alchemy.db_models import Image
from ims.tests import FunctionalTest
import mock


class MyError(Exception):
    def __init__(self, message=None):
        self.message = message


class TestImageRecord(FunctionalTest):
    def test_insert_sanity(self):
        session = mock.MagicMock()
        session.add = mock.MagicMock()

        dm = data_manager.ImageRecord(session)

        dm.insert(Image())

        assert session.add.called

    def test_insert_error(self):
        add = mock.MagicMock(return_value=SystemError())
        session = mock.MagicMock(return_value=add)

        dm = data_manager.ImageRecord(session)

        self.assertRaises(Exception, dm.insert)

    def test_get_images_by_name_sanity(self):
        session = mock.MagicMock()
        all = mock.MagicMock()
        query = mock.MagicMock(return_value=all)

        dm = data_manager.ImageRecord(session)

        dm.create_images_by_name_query = mock.MagicMock()
        dm.customise_query = mock.MagicMock(return_value=query)

        dm.get_images_by_name('a')

        assert query.all.called

    def test_get_images_by_name_error(self):
        session = mock.MagicMock()
        all = mock.MagicMock()
        query = mock.MagicMock(return_value=SystemError())

        dm = data_manager.ImageRecord(session)

        dm.create_images_by_name_query = mock.MagicMock(query)
        dm.customise_query = mock.MagicMock(return_value=SystemError())

        self.assertRaises(Exception, dm.get_images_by_name)

        self.assertRaises(Exception, dm.insert)

    def test_get_images_by_criteria_sanity(self):
        join = mock.MagicMock()
        filter = mock.MagicMock(return_value=[Image()])
        query = mock.MagicMock()
        query.join = mock.MagicMock(return_value=join)
        query.filter = mock.MagicMock(return_value=filter)
        query.all = mock.MagicMock(return_value=[Image()])
        join.filter = mock.MagicMock(return_value=filter)

        session = mock.MagicMock()
        session.query = mock.MagicMock(return_value=query)

        dm = data_manager.ImageRecord(session)
        dm.customise_query = mock.MagicMock()

        r = dm.get_images_by_criteria(visibility='a', region='b', Customer='c')

        self.assertEqual(len(r), 0)

    def test_get_images_by_criteria_error(self):
        join = mock.MagicMock()
        filter = mock.MagicMock(return_value=[Image()])
        query = mock.MagicMock()
        query.join = mock.MagicMock(return_value=join)
        query.filter = mock.MagicMock(return_value=filter)
        query.all = mock.MagicMock(return_value=SystemError())
        join.filter = mock.MagicMock(return_value=filter)

        session = mock.MagicMock()
        session.query = mock.MagicMock(return_value=query)

        dm = data_manager.ImageRecord(session)
        dm.customise_query = mock.MagicMock(return_value=SystemError())

        self.assertRaises(Exception, dm.get_images_by_criteria)

    def test_create_images_by_name_query_sanity(self):
        filter = mock.MagicMock(return_value=[Image()])
        query = mock.MagicMock()
        query.filter = mock.MagicMock(filter)

        session = mock.MagicMock()
        session.query = mock.MagicMock(query)

        dm = data_manager.ImageRecord(session)

        r = dm.create_images_by_name_query('a')

        self.assertEqual(len(r), 0)

    def test_create_images_by_name_query_error(self):
        query = mock.MagicMock()
        query.filter = mock.MagicMock(return_value=SystemError())

        session = mock.MagicMock()
        session.query = mock.MagicMock(return_value=SystemError())

        dm = data_manager.ImageRecord(session)

        self.assertRaises(Exception, dm.create_images_by_name_query, 'a')

    def test_get_image_sanity(self):
        query = mock.MagicMock()
        query.first = mock.MagicMock(Image())

        session = mock.MagicMock()
        session.query = mock.MagicMock(query)

        dm = data_manager.ImageRecord(session)

        r = dm.get_image('a')

        self.assertEqual(len(r), 0)

    def test_get_image_query_error(self):
        query = mock.MagicMock()
        query.first = mock.MagicMock(return_value=SystemError())

        session = mock.MagicMock()
        session.query = mock.MagicMock(return_value=SystemError())

        dm = data_manager.ImageRecord(session)

        self.assertRaises(Exception, dm.get_image, 'a')

    def test_delete_image_by_id_sanity(self):
        format = mock.MagicMock()
        execute = mock.MagicMock(return_value=format)

        session = mock.MagicMock()
        session.connection = mock.MagicMock(return_value=execute)

        dm = data_manager.ImageRecord(session)
        dm.customise_query = mock.MagicMock()

        dm.delete_image_by_id('a')

        assert session.connection.called

    def test_delete_image_by_id_error(self):
        session = mock.MagicMock()
        session.connection = mock.MagicMock(return_value=SystemError())

        dm = data_manager.ImageRecord(session)
        dm.customise_query = mock.MagicMock()

        self.assertRaises(Exception, dm.delete_image_by_id, 'a')
