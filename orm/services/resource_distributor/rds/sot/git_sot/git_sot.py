import logging
import os
import threading

from rds.ordupdate.ord_notifier import notify_ord
from rds.sot import base_sot
from rds.sot.base_sot import SoTError

import git_factory
from git_base import GitUploadError, GitInitError, GitResetError
from git_base import GitValidateError

logger = logging.getLogger(__name__)
lock = threading.Lock()


class GitSoT(base_sot.BaseSoT):

    local_repository_path = ""
    relative_path_format = ""
    file_name_format = ""
    commit_message_format = ""
    commit_user = ""
    commit_email = ""
    git_server_url = ""
    git_type = ""

    def __init__(self):
        logger.debug("In Git based SoT")
        self.git_impl = git_factory.get_git_impl(GitSoT.git_type)

    def save_resource_to_sot(self, tracking_id, transaction_id,
                             resource_list, application_id, user_id):
        thread = threading.Thread(target=update_sot,
                                  args=(self.git_impl,
                                        lock,
                                        tracking_id,
                                        transaction_id,
                                        resource_list,
                                        application_id,
                                        user_id))
        thread.start()

    def validate_sot_state(self):
        thread = threading.Thread(target=validate_git,
                                  args=(self.git_impl, lock))

        thread.start()


def update_sot(git_impl, my_lock, tracking_id, transaction_id, resource_list,
               application_id, user_id):
    logger.info("Save resource to SoT. start ...")
    commit_id = ""
    result = False
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.info("Acquire Git lock...")
    # Lock the entire git operations, so that no other threads change local
    # files.
    my_lock.acquire()
    logger.info("Git lock acquired !!!!")
    try:
        init_git(git_impl)

        handle_file_operations(resource_list)

        commit_id = update_git(git_impl)

        logger.info("All files were successfully updated in Git server :-)\n")

        result = True

    except SoTError as exc:
        logger.error("Save resource to SoT Git repository failed. "
                     "Reason: {}.".
                     format(exc.message))
    except GitInitError as init_exc:
        logger.error("Initializing Git repository Failed. Reason: {}.".
                     format(init_exc.message))
    except GitUploadError as upload_exc:
        logger.error("Uploading to Git repository Failed. Reason: {}.".
                     format(upload_exc.message))
        cleanup(git_impl)
    finally:
        logger.info("Release Git lock...")
        my_lock.release()
        logger.info("Git lock released !!!!")
        logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    # This method is called also in case exception raised.
    # Notification to ords will not be sent but status db and audit
    # will be updated.
    for resource in resource_list:
        try:
            notify_ord(transaction_id,
                       tracking_id,
                       resource["resource_type"],
                       commit_id,   # This is the resource-template-version
                       GitSoT.file_name_format.format(
                           resource["resource_name"]),
                       resource["resource_name"],  # This is the resource_id
                       resource["operation"],
                       resource["region_id"],
                       application_id,  # application_id is not available
                       user_id,  # user_id is not available
                       "NA",  # external_id is not available
                       not result)
        except Exception as e:
            logger.error("Error in updating ORD! Error: {}".format(
                e.message
            ))


def handle_file_operations(resource_list):
    for resource in resource_list:
        file_path = get_resource_file_path(resource)
        operation = resource["operation"]
        logger.debug("Operation: {}".format(operation))
        if operation == "delete":
            logger.info("Deleting file: {}".format(file_path))
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info("File successfully deleted!")
                except OSError as ex:
                    msg = "Could not delete file. " \
                          "Reason: {}".format(ex.message)
                    logger.error(msg)
                    raise SoTError(msg)
            else:
                logger.info("File does not exist, nothing to delete..")

        else:  # for all other operations "modify", "create"
            logger.info("Adding file: {}".format(file_path))
            create_file_in_path(file_path, resource["template_data"])
            logger.info("File was successfully added!")


def get_resource_file_path(resource):
    file_name = GitSoT.file_name_format.format(resource["resource_name"])
    relative_path = GitSoT.relative_path_format. \
        format(resource["region_id"],
               resource["resource_type"],
               file_name)
    file_path = GitSoT.local_repository_path + relative_path
    return file_path


def create_file_in_path(file_path, file_data):
    logger.info("Creating file : {}".format(file_path))

    create_dir(file_path)
    logger.debug("Directory path created..")

    write_data_to_file(file_path, file_data)
    logger.info("Data written to file.")


def create_dir(file_path):
    # Create actual directory path if not exist
    f_path = os.path.dirname(file_path)
    if not os.path.exists(f_path):
        try:
            os.makedirs(f_path)
        except OSError as ex:
            msg = "Failed to create directory path. " \
                  "Reason: {}".format(ex.message)
            logger.error(msg)
            raise SoTError(msg)


def write_data_to_file(file_path, file_data):
    # Create and write data to file (If file exists it is overwritten)
    try:
        with open(file_path, 'w') as fo:
            fo.write(file_data)
    except IOError as ex:
        msg = "Could not write data to file. " \
              "Reason: {}".format(ex.message)
        logger.error(msg)
        raise SoTError(msg)
    else:
        fo.close()


def init_git(git_impl):
    try:
        git_impl.git_init()
    except GitInitError as exc:
        logger.error("Failed to initialize Git. "
                     "Reason: {}".format(exc.message))
        raise


def update_git(git_impl):
    commit_id = ""
    try:
        commit_id = git_impl.git_upload_changes()
    except GitUploadError as exc:
        logger.error(exc.message)
        raise
    return commit_id


def validate_git(git_impl, my_lock):
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.info("Acquire Git lock...")
    my_lock.acquire()
    logger.info("Git lock acquired !!!!")
    try:
        git_impl.validate_git()
    except GitValidateError as exc:
        logger.error("Git validation error. Reason: {}.".
                     format(exc.message))
    finally:
        logger.info("Release Git lock...")
        my_lock.release()
        logger.info("Git lock released !!!!")
        logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")


def cleanup(git_impl):
    logger.info("Cleanup started...")
    try:
        git_impl.git_reset_changes("Clean up changes due to upload error.")
    except GitResetError as exc:
        logger.error(exc.message)
        raise SoTError(exc.message)





