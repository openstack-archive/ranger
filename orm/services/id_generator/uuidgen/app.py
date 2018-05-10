import os

from oslo_log import log as logging

from pecan.commands import CommandRunner
from pecan import make_app

LOG = logging.getLogger(__name__)


def setup_app(config):
    app_conf = dict(config.app)
    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)
    LOG.info('Starting uuidgen...')

    return app


def main():
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
