import os
import mock
import unittest
import threading
from mock import patch

from rds.sot.git_sot import git_sot as sot
from rds.sot.base_sot import SoTError
from rds.sot.git_sot.git_base import GitUploadError, GitInitError, GitResetError
from rds.sot.git_sot.git_base import GitValidateError
from rds.sot import sot_factory

from rds.tests import config as conf

lock = mock.MagicMock()

resource = {
        "operation": "create",
        "region_id": '1',
        "resource_type": '2',
        "resource_name": '3',
        "template_data": '4'
}

resource_delete = {
        "operation": "delete",
        "region_id": '1',
        "resource_type": '2',
        "resource_name": '3',
        "template_data": '4'
}


def dummy_thread_method():
    pass


class GitSoTTest(unittest.TestCase):

    def setUp(self):
        super(GitSoTTest, self).setUp()
        self.addCleanup(mock.patch.stopall)
        git_factory = mock.MagicMock()
        git_factory.get_git_impl = mock.MagicMock()

    ##################
    ### update_sot ###
    ##################

    @patch.object(sot, 'init_git', side_effect=GitInitError("Failed to initialize Git"))
    def test_git_sot_update_sot_init_git_fail(self, result):
        """" init_git fails and raise exception"""
        try:
            sot.update_sot("", lock, '1', '2', ['3','5'], '4', '6')
        except SoTError:
            self.fail("Exception should have been handled inside method")

    @patch.object(sot, 'handle_file_operations', side_effect=SoTError("Failed to create file path"))
    @patch.object(sot, 'init_git')
    def test_git_sot_update_sot_create_files_fail(self, git_repo, result):
        """" create_files fails and raise exception"""
        try:
            sot.update_sot("", lock, "a", "b", ['c', 'd'], 'e', 'f')
        except SoTError:
            self.fail("Exception should have been handled inside method")

    @patch.object(sot, 'update_git', side_effect=GitUploadError("Failed to upload file to Git"))
    @patch.object(sot, 'init_git')
    @patch.object(sot, 'handle_file_operations')
    @patch.object(sot, 'cleanup')
    def test_git_sot_update_sot_update_git_fail(self, git_repo, files_created, result, clean_result):
        """" update git fails and raise exception"""
        try:
            sot.update_sot("",lock, 'a', 'b', ['c', 'd'], 'e', 'f')
        except GitUploadError:
            self.fail("Exception should have been handled inside method")

    @patch.object(sot, 'update_git')
    @patch.object(sot, 'init_git')
    @patch.object(sot, 'handle_file_operations')
    @patch.object(sot, 'cleanup')
    def test_git_sot_update_sot_success(self, git_repo, files_created, result, cleanup_result):
        """"no exceptions raised"""
        try:
            sot.update_sot("", lock, "a", "b", ['c', 'd'], 'e', 'f')
        except SoTError:
            self.fail("Exception should have been handled inside method")

    #######################
    #   create_dir        #
    #######################

    @patch.object(os.path, 'dirname', return_value="File path")
    @patch.object(os.path, 'exists', return_value=False)
    @patch.object(os, 'makedirs')
    def test_git_sot_create_dir_path_not_exist_success(self, dir_name, exists, makedirs):
        """create directory path when path not exist and makedir success"""
        sot.create_dir("my_file")

    @patch.object(os.path, 'dirname', return_value="File path")
    @patch.object(os.path, 'exists', return_value=True)
    def test_git_sot_create_dir_path_exists_success(self, dir_name, exists):
        """create directory path when path not exist and makedir success"""
        sot.create_dir("my_file")

    @patch.object(os.path, 'dirname', return_value="File path")
    @patch.object(os.path, 'exists', return_value=False)
    @patch.object(os, 'makedirs', side_effect=OSError("Could not make dir"))
    def test_git_sot_create_dir_makedir_fails(self, dir_name, exists, makedirs):
        """create direcory path makedir throws exception and the methos throws SoTError"""
        with self.assertRaises(SoTError):
            sot.create_dir("my_file")

    ############################
    # save_resource_to_sot     #
    ############################

    @patch.object(threading, 'Thread', return_value=threading.Thread(target=dummy_thread_method))
    def test_git_sot_save_resource_to_sot(self, thread):
        """Check the save runs in a new thread"""
        sot_factory.sot_type = "git"
        sot_factory.git_type = "gittle"
        git_impl = mock.MagicMock()
        sot = sot_factory.get_sot()
        sot.save_resource_to_sot("t_id", "tk_id", [], "a_id", "u_id")
        self.assertNotEqual(thread, threading.Thread.getName("main_thread"))

    ################################
    # create_file_in_path          #
    ################################

    @patch.object(sot, 'create_dir', return_value="File path")
    @patch.object(sot, 'write_data_to_file', return_value=True)
    def test_git_sot_create_file_in_path_success(self, aDir, aFile):
        """create file in path success scenario no exception raised"""
        try:
            sot.create_file_in_path("path", "data")
        except SoTError:
            self.fail("No exceptions should be thrown in this case")

    @patch.object(sot, 'create_dir', side_effect=SoTError("Failed to create file path"))
    def test_git_sot_create_file_in_path_create_dir_failed(self, aDir):
        """create file in path fail, create file raise exception """
        with self.assertRaises(SoTError):
            sot.create_file_in_path("path", "data")

    @patch.object(sot, 'create_dir', return_value="File path")
    @patch.object(sot, 'write_data_to_file', side_effect=SoTError("Could not write to file"))
    def test_git_sot_create_file_in_path_create_file_failed(self, aDir, aFile):
        """create file in path fail,create dir success, writing data to file failed """
        with self.assertRaises(SoTError):
            sot.create_file_in_path("path", "data")

    #############################
    #  get_resource_file_path   #
    #############################

    def test_git_sot_get_resource_file_path_failed(self):
        """get_resource_file_path """
        sot_factory.sot_type = "git"
        sot_factory.git_type = "native"
        sot_factory.local_repository_path = conf.git["local_repository_path"]
        sot_factory.relative_path_format = conf.git["relative_path_format"]
        sot_factory.file_name_format = conf.git["file_name_format"]
        sot_factory.get_sot()

        name = conf.git["file_name_format"].format(resource["resource_name"])
        path = conf.git["local_repository_path"] + \
            conf.git["relative_path_format"].format(resource["region_id"],
                                                    resource["resource_type"],
                                                    name)

        result_path = sot.get_resource_file_path(resource)
        self.assertEqual(path, result_path)

    #############################
    #  handle_file_operations   #
    #############################

    # @patch.object(sot, 'create_file_in_path', return_value=True)
    # def test_git_sot_handle_file_operations_success(self, result):
    #     """create files """
    #     roll_list = []
    #     sot.handle_file_operations([resource, ])
    #     self.assertEqual(len(roll_list), 1)
    #
    #
    # @patch.object(os, 'remove')
    # @patch.object(os.path, 'exists', return_value=True)
    # def test_git_sot_handle_file_operations_delete_success(self,
    #                                                        result,
    #                                                        result2):
    #     """delete files """
    #     roll_list = []
    #     sot.handle_file_operations([resource_delete, ], roll_list)
    #     self.assertEqual(len(roll_list), 1)

    #############################
    #  write_data_to_file       #
    #############################

    @patch('__builtin__.open')
    @patch.object(os, 'close')
    @patch.object(os, 'write', return_value=True)
    def test_git_sot_write_data_to_file_success(self, result1, result2, result3):
        """Check create_file success """
        try:
            sot.write_data_to_file("file_path", "data11")
        except SoTError:
            self.fail("No exceptions should be thrown in this case")

    @patch('__builtin__.open', side_effect=IOError("Failed writing data to file"))
    def test_git_sot_write_data_to_file_failed(self, result1):
        """Check create file failed , could not write to file """
        with self.assertRaises(SoTError):
            sot.write_data_to_file("file_path", "data")

    #############################
    #  cleanup                  #
    #############################

    def test_git_sot_cleanup_files_success(self):
        """Check cleanup success """
        git_impl = mock.MagicMock()
        git_impl.git_reset_changes = mock.MagicMock()
        try:
            sot.cleanup(git_impl)
        except SoTError:
            self.fail("No exceptions should be thrown in this case")

    def test_git_sot_cleanup_files_remove_failed(self):
        """Check cleanup fail because reset git failed """
        git_impl = mock.MagicMock()
        git_impl.git_reset_changes = mock.MagicMock(side_effect=GitResetError("failed to reset"))
        with self.assertRaises(SoTError):
            sot.cleanup(git_impl)

    #############################
    #  init_git                 #
    #############################

    def test_git_sot_init_git_success(self):
        """Check init_git success """
        git_impl = mock.MagicMock()
        git_impl.git_init = mock.MagicMock()
        try:
            sot.init_git(git_impl)
        except GitInitError:
            self.fail("No exceptions should be thrown in this case")

    def test_git_sot_init_git_gittle_failed(self):
        """Check init_git failed """
        git_impl = mock.MagicMock()
        git_impl.git_init = mock.MagicMock(side_effect=GitInitError("failed to init"))
        with self.assertRaises(GitInitError):
            sot.init_git(git_impl)

    #############################
    #  update_git               #
    #############################

    def test_git_sot_update_git_success(self):
        """Check update_git success"""
        git_impl = mock.MagicMock()
        git_impl.git_upload_changes = mock.MagicMock(return_value="123")

        commit_id = sot.update_git(git_impl)
        self.assertEqual(commit_id, "123")

    def test_git_sot_update_git_commit_faild(self):
        """Check update_git commit failed"""
        git_impl = mock.MagicMock()
        git_impl.git_upload_changes = mock.MagicMock(
            side_effect=GitUploadError("Failed in upload"))
        with self.assertRaises(GitUploadError):
            sot.update_git(git_impl)

    #############################
    #  validate_git             #
    #############################

    def test_git_sot_validate_git_faild(self):
        """Check validate_git failed"""
        git_impl = mock.MagicMock()
        git_impl.validate_git = mock.MagicMock(
            side_effect=GitValidateError("Failed in upload"))
        try:
            sot.validate_git(git_impl, lock)
        except GitInitError:
            self.fail("No exceptions should be thrown in this case")


