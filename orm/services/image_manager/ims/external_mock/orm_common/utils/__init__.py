import cross_api_utils
import utils


def set_utils_conf(conf):
    cross_api_utils.set_utils_conf(conf)
    utils.set_utils_conf(conf)


__all__ = ['cross_api_utils', 'utils']
