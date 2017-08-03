"""Native (bash commands) Git module."""
import logging
import shlex
import subprocess
from threading import Timer
import time

from git_base import (BaseGit, GitInitError, GitResetError, GitUploadError,
                      GitValidateError)
from pecan import conf

logger = logging.getLogger(__name__)


class GitNative(BaseGit):
    """The native Git implementation."""

    def git_init(self):
        """Initialize Git."""
        try:
            logger.info("Local repository path:{}, "
                        "Git server url: {}, "
                        "Git command timeout: "
                        "{} seconds".format(conf.git.local_repository_path,
                                            conf.git.git_server_url,
                                            conf.git.git_cmd_timeout))

            out, error = self._git_pull(conf.git.local_repository_path)
            if self._is_conflict(out) or self._is_error(error):
                logger.error("Git pull result:\nerror:"
                             " {}\nout: {}".format(error, out))
                self.git_reset_changes("Reset all changes due "
                                       "to git pull conflict or error.")

        except GitResetError as exc:
            msg = "Failed to initialize git repository. " \
                  "Reason: {}".format(exc.message)
            logger.error(msg)
            raise GitInitError(msg)

    def git_upload_changes(self):
        """Upload (commit and push) the changes to Git."""
        commit_id = ""
        try:
            logger.info("Upload changes in progress ..")

            self._git_add(conf.git.local_repository_path)

            commit_message = conf.git.commit_message_format.format("")

            logger.info("Committing with the following parameters: "
                        "user: {}, email: {}, message: {}".
                        format(conf.git.commit_user,
                               conf.git.commit_email,
                               commit_message))
            self._git_commit(conf.git.commit_user,
                             conf.git.commit_email,
                             commit_message,
                             conf.git.local_repository_path)

            commit_id, error = self._git_get_commit_id(
                conf.git.local_repository_path)
            logger.info("Commit id : {}".format(commit_id))

            out, error = self._git_pull(conf.git.local_repository_path)
            # This check is needed only for Pull before Push.
            if self._is_error(error):
                raise GitNativeError("Git pull error! [{}]".format(error))

            # Push to repository
            self._git_push(conf.git.local_repository_path)

        except GitNativeError as exc:
            msg = "Failed to upload file to git. " \
                  "Reason: {}".format(exc.message)
            logger.error(msg)
            raise GitUploadError(msg)

        return commit_id

    def validate_git(self):
        logger.info("Git repository validation started...\n"
                    "Git commands timeout: {} "
                    "seconds".format(conf.git.git_cmd_timeout))
        try:
            self._git_config(conf.git.local_repository_path)

            out, error = self._git_pull(conf.git.local_repository_path)
            if self._is_conflict(out) or self._is_error(error):
                logger.info("Git pull error, reset ...")
                self._git_commit(conf.git.commit_user,
                                 conf.git.commit_email,
                                 "Git pull error found !!!",
                                 conf.git.local_repository_path)

                self._git_reset(conf.git.local_repository_path)
                logger.info("Git was reset to server's state.")
            else:
                self._git_add(conf.git.local_repository_path)

                self._git_commit(conf.git.commit_user,
                                 conf.git.commit_email,
                                 "Git validation commit",
                                 conf.git.local_repository_path)

                out, error = self._git_pull(conf.git.local_repository_path)
                # This check is needed only for pull before push.
                if self._is_error(error):
                    raise GitNativeError("Git pull error! [{}]".format(error))

                self._git_push(conf.git.local_repository_path)

            logger.info("Git repository state validation check done !")

        except GitNativeError as exc:
            logger.error("Git state invalid. Reason: [{}]".format(
                exc.message))
            raise GitValidateError("Git state invalid !")

    def git_reset_changes(self, msg):
        logger.info("Reset local repository to Git server started.")
        try:
            self._git_commit(conf.git.commit_user,
                             conf.git.commit_email,
                             msg,
                             conf.git.local_repository_path)

            self._git_reset(conf.git.local_repository_path)
            logger.info("Local repository is now up to date "
                        "with Git server.")

        except GitNativeError as exc:
            msg = "Git reset changes failed. " \
                  "Reason: {}".format(exc.message)
            logger.error(msg)
            raise GitResetError(msg)

    def _git_config(self, repo_dir):
        logger.info("Set git configuration params started.")
        cmds = ['git config --global user.name {}'.format(conf.git.commit_user),
                'git config --global user.email {}'.format(conf.git.commit_email)]

        for cmd in cmds:
            self._execute_git_cmd(cmd, repo_dir)
        logger.info("Set git configuration params done.")

    def _git_add(self, repo_dir):
        logger.info("Git add started.")
        cmd = 'git add --all'
        out, error = self._execute_git_cmd(cmd, repo_dir)
        logger.info("Git add done.")
        return out, error

    def _git_commit(self, user, email, commit_message, repo_dir):
        logger.info("Git commit started.")
        cmd = 'git commit --author="%s <%s>" -am "%s"' % (user,
                                                          email,
                                                          commit_message)
        out, error = self._execute_git_cmd(cmd, repo_dir)
        logger.info("Git commit done.")
        return out, error

    def _git_get_commit_id(self, repo_dir):
        logger.info("Git get commit id started.")
        cmd = 'git rev-parse HEAD'
        out, error = self._execute_git_cmd(cmd, repo_dir)
        # we need to clean \n and whitespaces before returning the commit id
        out = out.strip().split('\n')[0]
        logger.info("Git get commit id done. commit id: {}".format(out))
        return out, error

    def _git_reset(self, repo_dir):
        logger.info("Git reset started.")
        cmd = 'git reset --hard origin/master '
        out, error = self._execute_git_cmd(cmd, repo_dir)
        logger.info("Git reset done.")
        return out, error

    def _git_push(self, repo_dir):
        logger.info("Git push started.")
        cmd = 'git push '
        start_time = time.time()
        out, error = self._execute_git_cmd(cmd, repo_dir)
        logger.info("Git push done "
                    "(%.3f seconds)" % (time.time() - start_time))
        return out, error

    def _execute_git_cmd(self, cmd, repo_dir):
        error = ""
        proc = subprocess.Popen(shlex.split(cmd), cwd=repo_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        timeout = conf.git.git_cmd_timeout
        timer = Timer(timeout, on_subprocess_timeout, [cmd, proc])
        try:
            timer.start()
            (out, error) = proc.communicate()
            logger.debug("Cmd proc id: {}".format(proc.pid))
            proc.wait()
        finally:
            if not timer.is_alive():
                msg = "Git command '{}' timed out !!".format(cmd)
                logger.error(msg)
                # the word error must be in message
                error = "error:" + msg
            timer.cancel()

        if self._is_error(error):
            raise GitNativeError("Git error! [{}]".format(error))
        return out, error

    def _git_pull(self, repo_dir):
        logger.info("Git pull started.")
        cmd = 'git pull '
        error = ""
        start_time = time.time()
        proc = subprocess.Popen(shlex.split(cmd), cwd=repo_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        timeout = conf.git.git_cmd_timeout
        timer = Timer(timeout, on_subprocess_timeout, [cmd, proc])
        try:
            timer.start()
            (out, error) = proc.communicate()
            logger.debug("Cmd proc id: {}".format(proc.pid))
            proc.wait()
        finally:
            if not timer.is_alive():
                msg = "Git command '{}' timed out !!".format(cmd)
                logger.error(msg)
                # the word error must be in message
                error = "error:" + msg
            timer.cancel()

        # Special case for pull caller method will check the output
        if not self._is_error(error):
            logger.info("Git pull done "
                        "(%.3f seconds)" % (time.time() - start_time))

        return out, error

    def _is_error(self, error):
        if error:
            l_error = error.lower()
            if 'error' in l_error or 'fatal' in l_error:
                logger.error("Git operation returned with "
                             "error:\n{}".format(error))
                return True
        return False

    def _is_conflict(self, out):
        if out:
            l_out = out.lower()
            if 'conflict' in l_out:
                logger.info("Git operation returned with "
                            "conflict:\n{}".format(out))
                return True
        return False


def on_subprocess_timeout(cmd, proc):
    logger.error("Subprocess for command : {}, timed out!".format(cmd))
    logger.info("Terminating subprocess id: {}".format(proc.pid))
    proc.kill()


class GitNativeError(Exception):
    """Describes a generic error in a Git operation."""

    pass
