"""app module."""
import logging

from orm.services.audit_trail_manager.audit_server import model
from orm.services.audit_trail_manager.audit_server.storage import factory

from pecan import make_app

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
