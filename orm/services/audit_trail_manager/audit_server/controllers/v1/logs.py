import logging
import wsme

from pecan import rest
from wsmeext.pecan import wsexpose

logger = logging.getLogger(__name__)


class LogChangeResultWSME(wsme.types.DynamicBase):
    """log change result wsme type."""

    result = wsme.wsattr(str, mandatory=True, default=None)

    def __init__(self, **kwargs):
        """"init method."""
        super(LogChangeResult, self).__init__(**kwargs)


class LogChangeResult(object):
    """log change result type."""

    def __init__(self, result):
        """"init method."""
        self.result = result


class LogsController(rest.RestController):
    """Logs Audit controller."""

    @wsexpose(LogChangeResultWSME, str, status_code=201,
              rest_content_types='json')
    def put(self, level):
        """update log level.

        :param level: the log level text name
        :return:
        """

        logger.info("Changing log level to [{}]".format(level))
        try:
            log_level = logging._levelNames.get(level.upper())
            if log_level is not None:
                self._change_log_level(log_level)
                result = "Log level changed to {}.".format(level)
                logger.info(result)
            else:
                raise Exception(
                    "The given log level [{}] doesn't exist.".format(level))
        except Exception as e:
            result = "Fail to change log_level. Reason: {}".format(
                e.message)
            logger.error(result)
        return LogChangeResult(result)

    @staticmethod
    def _change_log_level(log_level):
        path = __name__.split('.')
        if len(path) > 0:
            root = path[0]
            root_logger = logging.getLogger(root)
            root_logger.setLevel(log_level)
        else:
            logger.info("Fail to change log_level to [{}]. "
                        "the given log level doesn't exist.".format(log_level))
