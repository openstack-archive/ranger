import os
from pecan.commands import CommandRunner
from pecan import make_app

from orm.common.orm_common.policy import policy
from orm.common.orm_common.utils import utils
from orm.services.customer_manager.cms_rest.logger import get_logger
from orm.services.customer_manager.cms_rest import model
from orm.services.customer_manager.cms_rest.utils import authentication

from oslo_config import cfg

logger = get_logger(__name__)


def setup_app(config):
    model.init_model()
    token_conf = authentication._get_token_conf(config)
    policy.init(config.authentication.policy_file, token_conf)
    app_conf = dict(config.app)

    # setting configurations for utils to be used from now and on
    utils.set_utils_conf(config)

    app = make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )
    logger.info('Starting CMS...')
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
