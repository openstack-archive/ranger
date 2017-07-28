"""Used for running the pecan application directly from pycharm."""

from pecan.commands import CommandRunner

runner = CommandRunner()
runner.run(['serve', 'config.py'])
