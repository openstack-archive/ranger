import os
import sys

from orm.common.orm_common.policy import policy
from orm.common.orm_common.utils.utils import set_utils_conf
from orm.services.image_manager.ims.logger import get_logger
from orm.services.image_manager.ims.utils import authentication as auth

from oslo_config import cfg

from pecan import conf, make_app
from pecan.commands import CommandRunner

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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='ranger', validate_default_values=True)

    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
