import logging
import os

from oslo_config import cfg

from orm.common.client.audit.audit_client.api import audit
from pecan import conf, make_app
from pecan.commands import CommandRunner
from services import region_resource_id_status
from sot import sot_factory
from storage import factory

logger = logging.getLogger(__name__)


def setup_app(pecan_config):
    """This method is the starting point of the application.
    The application can be started either by running pecan
    and pass it the config.py,
    or by running this file with python,
    then the main method is called and starting pecan.

    The method initializes components and return a WSGI application
    """

    init_sot()
    init_audit()

    factory.database = conf.database
    region_resource_id_status.config = conf.region_resource_id_status

    app = make_app(conf.app.root, logging=conf.logging)
    logger.info('Starting RDS...')

    validate_sot()

    return app


def init_sot():
    """Initialize SoT module
    """
    sot_factory.sot_type = conf.sot.type
    sot_factory.local_repository_path = conf.git.local_repository_path
    sot_factory.relative_path_format = conf.git.relative_path_format
    sot_factory.file_name_format = conf.git.file_name_format
    sot_factory.commit_message_format = conf.git.commit_message_format
    sot_factory.commit_user = conf.git.commit_user
    sot_factory.commit_email = conf.git.commit_email
    sot_factory.git_server_url = conf.git.git_server_url
    sot_factory.git_type = conf.git.type


def init_audit():
    """Initialize audit client module
    """
    audit.init(conf.audit.audit_server_url,
               conf.audit.num_of_send_retries,
               conf.audit.time_wait_between_retries,
               conf.app.service_name)


def validate_sot():
    sot_factory.get_sot().validate_sot_state()


def main():
    config_file = '/etc/ranger/ranger.conf'
    if os.path.isfile(config_file):
        CONF(['--config-file', config_file])

    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])

if __name__ == "__main__":
    main()
