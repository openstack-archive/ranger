import unittest

import mock
from orm.services.resource_distributor.rds.sot.git_sot.git_sot import GitSoT
from orm.services.resource_distributor.rds.sot import sot_factory


class SoTFactoryTests(unittest.TestCase):
    def setUp(self):
        super(SoTFactoryTests, self).setUp()
        self.addCleanup(mock.patch.stopall)
        git_factory = mock.MagicMock()
        git_factory.get_git_impl = mock.MagicMock()

    def test_get_sot_no_sot_type(self):
        """Check that a runtime error is raised if no git type
        is available from config
        """
        sot_factory.sot_type = ""
        with self.assertRaises(RuntimeError):
            sot_factory.get_sot()

    def test_get_sot_git_type(self):
        """ Check that when 'git' type is provided the returned object
        is instance of  GiTSoT
        """
        sot_factory.sot_type = "git"
        obj = sot_factory.get_sot()
        self.assertIsInstance(obj, GitSoT)

    def test_get_sot_git_sot_params(self):
        sot_factory.sot_type = "git"
        sot_factory.local_repository_path = "2"
        sot_factory.relative_path_format = "3"
        sot_factory.commit_message_format = "4"
        sot_factory.commit_user = "5"
        sot_factory.commit_email = "6"
        sot_factory.git_server_url = "7"
        sot_factory.git_type = "gittle"

        obj = sot_factory.get_sot()
        self.assertEqual(GitSoT.local_repository_path, "2", "local_repository_path not match")
        self.assertEqual(GitSoT.relative_path_format, "3", "relative_path_format not match")
        self.assertEqual(GitSoT.commit_message_format, "4", "commit_message_format not match")
        self.assertEqual(GitSoT.commit_user, "5", "commit_user not match")
        self.assertEqual(GitSoT.commit_email, "6", "commit_email not match")
        self.assertEqual(GitSoT.git_server_url, "7", "git_server_url not match")
        self.assertEqual(GitSoT.git_type, "gittle", "git_type not match")
