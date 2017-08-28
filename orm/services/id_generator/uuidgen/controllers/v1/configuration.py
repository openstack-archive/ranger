"""Configuration rest API input module."""

import logging

from orm.services.id_generator.uuidgen.external_mock.orm_common.utils import utils
from pecan import conf, rest
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class ConfigurationController(rest.RestController):
    """Configuration controller."""

    @wsexpose(str, str, status_code=200)
    def get(self, dump_to_log='false'):
        """get method.

        :param dump_to_log: A boolean string that says whether the
        configuration should be written to log
        :return: A pretty string that contains the service's configuration
        """
        logger.info("Get configuration...")

        dump = dump_to_log.lower() == 'true'
        utils.set_utils_conf(conf)
        result = utils.report_config(conf, dump, logger)
        return result
