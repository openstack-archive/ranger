import unittest

from orm.services.resource_distributor.rds.sot.git_sot import git_factory
from orm.services.resource_distributor.rds.sot.git_sot.git_gittle import GitGittle
from orm.services.resource_distributor.rds.sot.git_sot.git_native import GitNative


class GitFactoryTests(unittest.TestCase):
    def setUp(self):
        super(GitFactoryTests, self).setUp()

    def test_get_git_impl_with_gittle(self):
        """Test that when given gittle the GitGittle instance returned"""
        obj = git_factory.get_git_impl("gittle")
        self.assertIsInstance(obj, GitGittle)

    def test_get_git_impl_with_native(self):
        """Test that when given native the GitNative instance returned"""
        obj = git_factory.get_git_impl("native")
        self.assertIsInstance(obj, GitNative)

    def test_get_sot_no_sot_type(self):
        """Test that when given unknown type, exception raised"""
        with self.assertRaises(RuntimeError):
            git_factory.get_git_impl("unknown")
