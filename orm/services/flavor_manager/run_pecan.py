'''
' this script is running the pecan web server inside ide so we can set break points in the code and debug our code
'''
from pecan.commands import CommandRunner

runner = CommandRunner()
runner.run(['serve', 'config.py'])
