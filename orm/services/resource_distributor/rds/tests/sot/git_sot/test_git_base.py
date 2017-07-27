import subprocess
import unittest
import mock
from mock import patch

from rds.sot.git_sot import git_base
from rds.sot.git_sot.git_base import BaseGit, GitResetError


class BaseGitTests(unittest.TestCase):

    def test_git_base_no_method_git_init_implemented(self):
        """ Check if creating an instance and calling git_init method fail"""
        with self.assertRaises(NotImplementedError):
            base_git = BaseGit()
            base_git.git_init()

    def test_git_base_no_method_git_upload_changes_implemented(self):
        """ Check if creating an instance and calling git_upload_changes method fail"""
        with self.assertRaises(NotImplementedError):
            base_git = BaseGit()
            base_git.git_upload_changes()

    # @patch.object(git_base, 'conf')
    # @patch.object(subprocess, 'Popen')
    # def test_git_base_reset_error(self, mock_popen, conf_mock):
    #     """ Test that exception raised when stderr returns error."""
    #     my_pipe = mock.MagicMock()
    #     my_pipe.communicate = mock.MagicMock(return_value=('1', 'error',))
    #     mock_popen.return_value = my_pipe
    #
    #     base_git = BaseGit()
    #     callback = base_git.git_reset_changes
    #     self.assertRaises(GitResetError, callback)

    # @patch.object(git_base, 'conf')
    # @patch.object(subprocess, 'Popen')
    # def test_git_base_reset_no_error(self, mock_popen, conf_mock):
    #     """ Test that no exception raised when no error returned."""
    #     my_pipe = mock.MagicMock()
    #     my_pipe.communicate = mock.MagicMock(return_value=('1', 'bla bla',))
    #     mock_popen.return_value = my_pipe
    #
    #     base_git = BaseGit()
    #     try:
    #         base_git.git_reset_changes()
    #     except GitResetError:
    #         self.fail("No exception should be raised here")

    def test_git_base_no_method_git_reset_changes_implemented(self):
        """ Check if creating an instance and calling
        git_reset_changes method fail
        """
        with self.assertRaises(NotImplementedError):
            base_git = BaseGit()
            base_git.git_reset_changes()

    def test_git_base_no_method_validate_git_implemented(self):
        """ Check if creating an instance and calling validate_git method fail"""
        with self.assertRaises(NotImplementedError):
            base_git = BaseGit()
            base_git.validate_git()

