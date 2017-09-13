"""Unittest module for git_native."""
import unittest

import mock
from mock import patch
from orm.services.resource_distributor.rds.sot.git_sot import git_native
from orm.services.resource_distributor.rds.sot.git_sot.git_native import GitNativeError, GitValidateError


class GitNativeTest(unittest.TestCase):
    """The test case of GitNative."""

    # @patch.object(git_native.subprocess, 'Popen')
    # def test_git_operations_sanity(self, mock_popen):
    #     """Test that no exception is raised when performing git operations."""
    #     my_pipe = mock.MagicMock()
    #     my_pipe.communicate = mock.MagicMock(return_value=('1', '2',))
    #     mock_popen.return_value = my_pipe
    #     test_git = git_native.GitNative()
    #     for callback in [test_git._git_pull, test_git._git_add,
    #                      test_git._git_push, test_git._git_get_commit_id]:
    #         callback('test')
    #
    #     test_git._git_commit('test', 'test', 'test', 'test')

    # @patch.object(git_native.subprocess, 'Popen')
    # def test_git_operations_error(self, mock_popen):
    #     """Test that an exception is raised when stderror returns error."""
    #     my_pipe = mock.MagicMock()
    #     my_pipe.communicate = mock.MagicMock(return_value=('1', 'error',))
    #     mock_popen.return_value = my_pipe
    #     test_git = git_native.GitNative()
    #     for callback in [test_git._git_pull, test_git._git_add,
    #                      test_git._git_push, test_git._git_get_commit_id]:
    #         self.assertRaises(git_native.GitNativeError, callback, 'test')
    #
    #     self.assertRaises(git_native.GitNativeError,
    #                       test_git._git_commit, 'test', 'test', 'test', 'test')

    @patch.object(git_native, 'conf')
    @patch.object(git_native.subprocess, 'Popen')
    def test_git_init_sanity(self, mock_popen, mock_conf):
        """Test that no exception is raised when calling git_init."""
        my_pipe = mock.MagicMock()
        my_pipe.communicate = mock.MagicMock(return_value=('1', '2',))
        mock_popen.return_value = my_pipe
        test_git = git_native.GitNative()
        test_git.git_init()

    @patch.object(git_native, 'conf')
    @patch.object(git_native.subprocess, 'Popen')
    def test_git_upload_changes_sanity(self, mock_popen, mock_conf):
        """Test that no exception is raised when calling git_upload_changes."""
        my_pipe = mock.MagicMock()
        my_pipe.communicate = mock.MagicMock(return_value=('1', '2',))
        mock_popen.return_value = my_pipe
        test_git = git_native.GitNative()
        test_git.git_upload_changes()

    @patch.object(git_native, 'conf')
    @patch.object(git_native.subprocess, 'Popen')
    def test_git_upload_changes_error(self, mock_popen, mock_conf):
        """Test that an exception is raised when stderror returns error."""
        my_pipe = mock.MagicMock()
        my_pipe.communicate = mock.MagicMock(return_value=('1', 'error',))
        mock_popen.return_value = my_pipe
        test_git = git_native.GitNative()
        self.assertRaises(git_native.GitUploadError,
                          test_git.git_upload_changes)

    @patch.object(git_native, 'conf')
    @patch.object(git_native.subprocess, 'Popen')
    def test_git_validate_git_sanity(self, mock_popen, mock_conf):
        """Test that no exception is raised when calling validate_git."""
        my_pipe = mock.MagicMock()
        my_pipe.communicate = mock.MagicMock(return_value=('1', '2',))
        mock_popen.return_value = my_pipe
        test_git = git_native.GitNative()
        test_git.validate_git()

    @patch.object(git_native, 'conf')
    @patch.object(git_native.subprocess, 'Popen')
    @patch.object(git_native.GitNative, '_git_config',
                  side_effect=GitNativeError("Could not write to file"))
    def test_git_native_validate_git_config_fail(self, conf, mock_popen, result):
        """Test that no exception is raised when calling git_init.aein"""
        my_pipe = mock.MagicMock()
        my_pipe.communicate = mock.MagicMock(return_value=('1', '2',))
        mock_popen.return_value = my_pipe
        test_git = git_native.GitNative()
        with self.assertRaises(GitValidateError):
            test_git.validate_git()
