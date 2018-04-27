import logging
from pecan import make_app

logger = logging.getLogger(__name__)


def setup_app(config):
    app_conf = dict(config.app)

    app = make_app(app_conf.pop('root'),
                   logging=getattr(config, 'logging', {}),
                   **app_conf)
    logger.info('Starting uuidgen...')
    return app
