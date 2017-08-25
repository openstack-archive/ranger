import logging


log = logging.getLogger(__name__)


def init_log():
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging.DEBUG)
    logging.info("logger set")
