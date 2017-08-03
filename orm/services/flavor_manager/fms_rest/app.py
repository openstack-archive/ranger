import os

from fms_rest.data import wsme
from fms_rest.logger import get_logger
from fms_rest.utils import authentication
from orm_common.policy import policy
from pecan.commands import CommandRunner
from pecan import make_app

logger = get_logger(__name__)


def setup_app(config):
    wsme.init_model()
    token_conf = authentication.get_token_conf(config)
    policy.init(config.authentication.policy_file, token_conf)
    app_conf = dict(config.app)

    app = make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )
    logger.info('Starting FMS...')
    return app


def main():
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
