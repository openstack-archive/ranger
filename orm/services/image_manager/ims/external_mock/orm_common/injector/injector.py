import imp
import os

from orm.common.orm_common.injector import fang

_di = fang.Di()
logger = None


def register_providers(env_variable, providers_dir_path, _logger):
    global logger
    logger = _logger

    # TODO: change all prints to logger
    logger.info('Initializing dependency injector')
    logger.info('Checking {0} variable'.format(env_variable))

    env = None
    if not (env_variable in os.environ):
        logger.warn('No {0} variable found using `prod` injector'.format(env_variable))
        env = 'prod'
    elif os.environ[env_variable] == '__TEST__':
        logger.info('__TEST__ variable found, explicitly skipping provider registration!!!')
        return
    else:
        env = os.environ[env_variable]
        logger.info('{0} found setting injector to {1} environment'.format(env_variable, env))

    logger.info('Setting injector providers')

    module = _import_file_by_name(env, providers_dir_path)

    for provider in module.providers:
        logger.info('Setting provider `{0}` to {1}'.format(provider[0], provider[1]))
        _di.providers.register_instance(provider[0], provider[1])


def get_di():
    return _di


def override_injected_dependency(dep_tuple):
    _di.providers.register_instance(dep_tuple[0], dep_tuple[1], allow_override=True)


def _import_file_by_name(env, providers_dir_path):
    file_path = os.path.join(providers_dir_path, '{0}_providers.py'.format(env))
    try:
        module = imp.load_source('fms_providers', file_path)
    except IOError as ex:
        logger.log_exception(
            'File with providers for the {0} environment, path: {1} wasnt found! Crushing!!!'.format(env, file_path),
            ex)
        raise ex

    return module
