import logging

from pecan import conf
from gittle import Gittle

from git_base import BaseGit, GitInitError, GitUploadError

logger = logging.getLogger(__name__)


class GitGittle(BaseGit):

    def __init__(self):
        self.repo = None

    def git_init(self):
        try:
            # Init repository
            logger.debug("Local repository path:{}, Git server url: {}".format(conf.git.local_repository_path,
                                                                               conf.git.git_server_url))
            self.repo = Gittle(conf.git.local_repository_path, origin_uri=conf.git.git_server_url)

            logger.info("Pulling from git..")
            # Update local working copy
            self.repo.pull()

            logger.info("GitGittle - Git is up to date !")

        except Exception as exc:
            logger.error("GitGittle - Failed to initialize Git. Reason: {}".format(exc.message))
            raise GitInitError(exc.message)

    def git_upload_changes(self):
        commit_id = ""
        try:

            logger.info("Commit changes in progress ..")
            # Stage modified files
            self.repo.stage(self.repo.pending_files)

            commit_message = conf.git.commit_message_format.format(self.repo.added_files)
            # Commit the change
            commit_id = self.repo.commit(conf.git.commit_user,
                                         conf.git.commit_email,
                                         commit_message)

            logger.info("Commit details: commit_user:{}, commit_email:{}, "
                        "commit_message:{}, commit_id:{}".format(conf.git.commit_user,
                                                                 conf.git.commit_email,
                                                                 commit_message,
                                                                 commit_id))

            # Push to repository
            self.repo.push()

        except Exception as exc:
            logger.error("GitGittle - Filed to upload file to git.")
            raise GitUploadError("Failed to upload file to Git")

        return commit_id

    def validate_git(self):
        pass
