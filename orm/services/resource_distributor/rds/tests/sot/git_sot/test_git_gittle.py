import mock
from mock import patch

import unittest

from rds.sot.git_sot import git_gittle
from rds.sot.git_sot.git_gittle import GitGittle
from rds.sot.git_sot.git_base import GitInitError, GitUploadError


class GitGittleTests(unittest.TestCase):

    def setUp(self):
        super(GitGittleTests, self).setUp()
        self.addCleanup(mock.patch.stopall)
        self.my_git = GitGittle()

    def tearDown(self):
        # Restore the original config
        self.my_git.repo = None

    ###################
    # git_init        #
    ###################

    @patch.object(git_gittle, 'Gittle', side_effect=Exception("Failed to delete file path"))
    def test_git_gittle_init_git_create_gittle_failed(self, gittle_mock):
        """Test that when Gittle fail to initialize exception is raised."""
        with self.assertRaises(GitInitError):
            self.my_git.git_init()

    @patch.object(git_gittle, 'Gittle')
    @patch.object(git_gittle, 'conf')
    def test_git_gittle_init_git_create_gittle_success(self, gittle_mock, conf_mock):
        """Test that when Gittle initialize success."""
        self.my_git.git_init()

    ######################
    # git_upload_changes #
    ######################

    @patch.object(git_gittle, 'conf')
    def test_git_gittle_git_upload_changes_success(self, conf_mock):
        """Test that when upload success commit id is returned."""
        self.my_git.repo = mock.MagicMock()
        self.my_git.repo.commit = mock.MagicMock(return_value="123")
        commit_id = self.my_git.git_upload_changes()
        self.assertEqual(commit_id, "123")

    @patch.object(git_gittle, 'conf')
    def test_git_gittle_git_upload_changes_commit_failed(self, conf_mock):
        """Test that when upload failed exception raised."""
        self.my_git.repo = mock.MagicMock()
        self.my_git.repo.commit = mock.MagicMock(side_effect=Exception("Failed to commit"))
        self.assertRaises(GitUploadError, self.my_git.git_upload_changes)
