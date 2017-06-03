import subprocess

from pecan import conf


class BaseGit(object):

    def git_init(self):
        raise NotImplementedError("Please Implement this method")

    def git_upload_changes(self):
        raise NotImplementedError("Please Implement this method")

    def git_reset_changes(self):
        raise NotImplementedError("Please Implement this method")

    def validate_git(self):
        raise NotImplementedError("Please Implement this method")


class GitInitError(Exception):
    pass


class GitUploadError(Exception):
    pass


class GitResetError(Exception):
    pass


class GitValidateError(Exception):
    pass

