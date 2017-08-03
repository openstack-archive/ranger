from pecan.commands import CommandRunner

runner = CommandRunner()
runner.run(['serve', 'config.py'])
