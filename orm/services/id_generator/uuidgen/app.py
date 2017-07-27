import os
import logging
from pecan import make_app
from pecan.commands import CommandRunner
from uuidgen import model

logger = logging.getLogger(__name__)


def setup_app(config):
    model.init_model()
    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)
    logger.info('Starting uuidgen...')
    return app


def main():
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path+'/config.py'])
