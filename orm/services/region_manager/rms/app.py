import logging
import os

from orm_common.policy import policy
from orm_common.utils import utils
from pecan.commands import CommandRunner
from pecan import make_app
from rms import model
from rms.utils import authentication

logger = logging.getLogger(__name__)


def setup_app(config):
    model.init_model()
    token_conf = authentication.get_token_conf(config)
    policy.init(config.authentication.policy_file, token_conf)
    app_conf = dict(config.app)

    utils.set_utils_conf(config)

    app = make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )

    logger.info('Starting RMS...')
    return app


def main():
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
