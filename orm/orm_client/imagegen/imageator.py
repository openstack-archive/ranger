#!/usr/bin/env python
import argparse
import json
import os
from os.path import isfile, join
import re
import subprocess
import tempfile
import time

# from colorama import init, Fore, Back, Style


# Default flavor json directory
IMAGE_DIR = './image_dir'
CLI_PATH = '../ormcli/orm'


def read_jsonfile(file):
    return json.loads(open(file).read())


def sh(cmd):
    # run a shell command, echoing output, painting error lines red,
    # print runtime and status
    # return status and output

    print '>> Starting: ' + cmd
    start = time.time()
    output = ''
    errpat = re.compile('error', re.I)

    cmd = 'python ' + cmd
    p = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b''):
        out = line.rstrip()
        print(">>> " + out)
        output += out
    end = time.time()
    span = end - start
    retcode = p.wait()
    print '>> Ended: %s [%s, %d:%02d]' % (cmd, retcode, span / 60, span % 60)
    return retcode, output


parser = argparse.ArgumentParser(prog='imageator',
                                 description='batch image/region creator')
# parser.add_argument('--image_dir',
#                     type=str,
#                     default='./image_dir',
#                     help='<JSON image directory, default: ./image_dir>')
# parser.add_argument('--host',
#                     type=str,
#                     help='<orm host ip>')
# parser.add_argument('--cli_command',
#                     type=str,
#                     default='/opt/app/orm/ormcli/ormcli/orm',
#                     help='<path to cli command>')
args = parser.parse_args()

summary = []

for file in [f for f in os.listdir(IMAGE_DIR) if
             isfile(join(IMAGE_DIR, f))]:
    f = read_jsonfile(join(IMAGE_DIR, file))

    print f
    image_name = f['name']
    fh, file_name = tempfile.mkstemp()
    os.write(fh, json.dumps({"image": f}))
    os.close(fh)
    # harg = '--orm-base-url %s' % args.host if args.host else ''
    res, output = sh('%s ims create_image test %s' % (
        CLI_PATH, file_name))
    os.unlink(file_name)

    summary.append("File name: {}, Image name: {}, Create image status: {}\n".
                   format(file,
                          image_name,
                          'Success' if res == 0 else 'Failed'))

print "\nImage creation summary:"
print "-----------------------"
for s in summary:
    print s
