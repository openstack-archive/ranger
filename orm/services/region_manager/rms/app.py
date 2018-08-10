import logging
import os

from orm.common.orm_common.policy import policy
from orm.common.orm_common.utils import utils
from orm.services.region_manager.rms import model
from orm.services.region_manager.rms.utils import authentication

from oslo_config import cfg

from pecan.commands import CommandRunner
from pecan import make_app

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
    config_file = '/etc/ranger/ranger.conf'
    if os.path.isfile(config_file):
        cfg.CONF(['--config-file', config_file])

    dir_name = os.path.dirname(__file__)
    drive, path_and_file = os.path.splitdrive(dir_name)
    path, filename = os.path.split(path_and_file)
    runner = CommandRunner()
    runner.run(['serve', path + '/config.py'])
