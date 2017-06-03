from pecan import make_app
from pecan import conf
from ims.logger import get_logger
from orm_common.utils.utils import set_utils_conf
from pecan.commands import CommandRunner

from ims.utils import authentication as auth
from orm_common.policy import policy

import os
logger = get_logger(__name__)


def setup_app(config):
    token_conf = auth._get_token_conf(config)
    policy.init(config.authentication.policy_file, token_conf)
    app_conf = dict(config.app)

    app = make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )

    set_utils_conf(conf)

    logger.info('Starting IMS...')
    return app


def main():
    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path+'/config.py'])
