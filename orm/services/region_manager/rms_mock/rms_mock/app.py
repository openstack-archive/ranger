from pecan.commands import CommandRunner
from pecan import make_app
from rms import model
from rms_mock import model


def setup_app(config):

    model.init_model()
    app_conf = dict(config.app)

    return make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )


def main():
    runner = CommandRunner()
    runner.run(['serve', '../config.py'])

if __name__ == "__main__":
    main()
