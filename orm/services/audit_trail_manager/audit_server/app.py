"""app module."""
import logging
import os

from orm.services.audit_trail_manager.audit_server import model
from orm.services.audit_trail_manager.audit_server.storage import factory

from oslo_config import cfg

from pecan.commands import CommandRunner
from pecan import make_app

logger = logging.getLogger(__name__)


def setup_app(config):
    """setup method."""
    model.init_model()
    app_conf = dict(config.app)
    factory.database_url = config.database.url
    factory.echo_statements = config.database.echo_statements

    app = make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )

    logger.info('Starting Audit...')
    return app


def main():
    config_file = '/etc/ranger/ranger.conf'
    if os.path.isfile(config_file):
        CONF(['--config-file', config_file])

    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
