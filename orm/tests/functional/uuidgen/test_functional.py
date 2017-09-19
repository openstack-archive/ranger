import json
import re

import orm.services.id_generator.uuidgen as uuidgen
import orm.services.id_generator.uuidgen.controllers.v1.uuid_controller as uuid_controller
from orm.tests.unit.uuidgen import FunctionalTest

import mock


class MyException(Exception):
    def __init__(self, args=None):
        self.orig = mock.MagicMock()
        if args is not None:
            self.orig.args = args


class TestRootController(FunctionalTest):
    def test_get_not_found(self):
        resp = self.app.get('/a/bogus/url', expect_errors=True)
        self.assertEqual(resp.status_int, 404)

    def test_get(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_int, 200)
        self.assertIn('versions', resp.body)

    def test_bad_request(self):
        resp = self.app.post('/v1/uuids', params={'user_type': 'milkshake'}, expect_errors=True)
        self.assertEqual(resp.status_int, 400)
        self.assertIn('badRequest', resp.body)
        self.assertIn('"code": 400', resp.body)
        self.assertIn('Unknown parameter(s):user_type', resp.body)

    @mock.patch.object(uuidgen.db.db_manager.DBManager, 'create_uuid')
    def test_uuid(self, db_manager_mock):
        resp = self.app.post('/v1/uuids')
        self.assertEqual(resp.status_int, 200)
        body = json.loads(resp.body)
        self.assertTrue(re.search('^[\dTZ.:-]+$', body['issued_at']))
        self.assertEqual('', body['uuid_type'])
        self.assertTrue(re.search('^[0-9a-f]+$', body['uuid']))

    @mock.patch.object(uuidgen.db.db_manager.DBManager, 'create_uuid')
    def test_uuid_with_param(self, db_manager_mock):
        resp = self.app.post('/v1/uuids',
                             params={'uuid_type': 'milkshake'})
        self.assertEqual(resp.status_int, 200)
        body = json.loads(resp.body)
        self.assertTrue(re.search('^[\dTZ.:-]+$', body['issued_at']))
        self.assertEqual('milkshake', body['uuid_type'])
        # Same format as with no parameter
        self.assertTrue(re.search('^[0-9a-f-]+$', body['uuid']))

        resp = self.app.post('/v1/uuids',
                             params={'uuid': 1337, 'uuid_type': 'milkshake'})
        self.assertEqual(resp.status_int, 200)
        body = json.loads(resp.body)
        self.assertTrue(re.search('^[\dTZ.:-]+$', body['issued_at']))
        self.assertEqual('custId', body['uuid_type'])
        # Same format as with no parameter
        self.assertTrue(re.search('^[0-9a-f-]+$', body['uuid']))

    @mock.patch.object(uuidgen.db.db_manager.DBManager, 'create_uuid', side_effect=Exception('boom'))
    def test_uuid_no_connection(self, db_manager_mock):
        resp = self.app.post('/v1/uuids', expect_errors=True)
        self.assertEqual(resp.status_int, 500)
        self.assertIn('badRequest', resp.body)
        self.assertIn('"code": 500', resp.body)

    @mock.patch.object(uuidgen.db.db_manager.DBManager, 'create_uuid',
                       side_effect=MyException())
    def test_uuid_with_param_db_error(self, db_manager_mock):
        resp = self.app.post('/v1/uuids', params={'uuid': '1337'},
                             expect_errors=True)
        self.assertEqual(resp.status_int, 500)
        self.assertIn('badRequest', resp.body)
        self.assertIn('"code": 500', resp.body)

    # @mock.patch.object(uuidgen.db.db_manager.DBManager, 'create_uuid',
    #                    side_effect=MyException([1062]))
    # def test_uuid_with_param_duplicate_key(self, db_manager_mock):
    #     resp = self.app.post('/v1/uuids', params={'uuid': '1337'},
    #                          expect_errors=True)
    #     self.assertEqual(resp.status_int, 400)
    #     self.assertIn('badRequest', resp.body)
    #     self.assertIn('"code": 400', resp.body)

    @mock.patch.object(uuid_controller, 'DBManager')
    def test_uuid_already_exists(self, db_manager_mock):
        my_create_uuid = mock.MagicMock(side_effect=MyException([1062]))
        create_uuid_wrapper = mock.MagicMock()
        create_uuid_wrapper.create_uuid = my_create_uuid
        db_manager_mock.return_value = create_uuid_wrapper

        resp = self.app.post('/v1/uuids',
                             params={'uuid': 1337, 'uuid_type': 'milkshake'},
                             expect_errors=True)
        self.assertEqual(resp.status_int, 200)
        body = json.loads(resp.body)
        self.assertTrue(re.search('^[\dTZ.:-]+$', body['issued_at']))
        self.assertEqual('custId', body['uuid_type'])
        # Same format as with no parameter
        self.assertTrue(re.search('^[0-9a-f-]+$', body['uuid']))

    @mock.patch.object(uuidgen.db.db_manager, 'sessionmaker')
    def test_uuid_commit_error(self, mock_sessionmaker):
        mock_session = mock.MagicMock()
        mock_session.commit = mock.MagicMock(side_effect=SystemError('test'))
        mock_sessionmaker.return_value = mock.MagicMock(
            return_value=mock_session)

        resp = self.app.post('/v1/uuids', params={'uuid': '1337'},
                             expect_errors=True)
        self.assertEqual(resp.status_int, 500)
        self.assertIn('1337', resp.body)

        # TODO: apply the following 2 tests when we understand mocking better: now we don't get the 'inner' exceptions
        # @mock.patch.object('uuidgen.controllers.v1.uuid_controller.Uuid', 'insert', autospec=True)
        # @mock.patch('uuidgen.controllers.v1.uuid_controller.Uuid')
        # def test_uuid_insert_database_error(self, mock_insert, mock_Uuid):
        #     mock_insert.side_effect = sqlalchemy.exc.IntegrityError('boom', 'boom', 'boom')
        #     resp = self.app.post('/v1/uuids', expect_errors=True)
        #     self.assertEqual(resp.status_int, 500)
        #     self.assertIn('badRequest', resp.body)
        #     self.assertIn('"code": 500', resp.body)
        #     self.assertIn('Database error', resp.body)

        # @mock.patch.object('uuidgen.controllers.v1.uuid_controller.Uuid', 'insert', autospec=True)
        # @mock.patch('uuidgen.controllers.v1.uuid_controller.Uuid')
        # def test_uuid_duplicate_uuid(self, mock_insert, mock_Uuid):
        #     mock_insert.side_effect = sqlalchemy.exc.IntegrityError('boom', 'boom', 'boom')
        #     resp = self.app.post('/v1/uuids', expect_errors=True)
        #     self.assertEqual(resp.status_int, 500)
        #     self.assertIn('badRequest', resp.body)
        #     self.assertIn('"code": 500', resp.body)
        #     self.assertIn('Duplicate key error', resp.body)
