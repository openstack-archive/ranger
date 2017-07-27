"""app module."""
import logging
import os

from pecan import make_app
from pecan.commands import CommandRunner
from audit_server import model
from audit_server.storage import factory

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
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path+'/config.py'])
