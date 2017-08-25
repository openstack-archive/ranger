#!/usr/bin/env python
import os
import argparse
import json
import time
import subprocess
import tempfile
import ast
import re
from os.path import isfile, join

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
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        out = line.rstrip()
        print(">>> " + out)
        output += out
    end = time.time()
    span = end - start
    retcode = p.wait()
    print '>> Ended: %s [%s, %d:%02d]' % (cmd, retcode, span / 60, span % 60)
    return retcode, output


parser = argparse.ArgumentParser(prog='regionator',
                                 description='batch add region to image')
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
parser.add_argument('regions',
                    type=str,
                    default='',
                    help='<comma-separated regions to add, e.g. region1,'
                         'region2>')
args = parser.parse_args()

regions = args.regions.split(',')
if not regions:
    print "Must specify at least one region"
    exit(0)
data = {'regions': [{'name': r} for r in regions]}
fh, file_name = tempfile.mkstemp()
os.write(fh, json.dumps(data))
os.close(fh)

# Prepare images dict with pairs {image_name:image_id}
img_dict = {}
# harg = '--orm-base-url %s' % args.host if args.host else ''
res, output = sh(
    '%s ims %s list_images test ' % (CLI_PATH, ''))
if not res:
    images = ast.literal_eval(output)
    for img in images['images']:
        img_dict[img['name']] = img['id']
    print img_dict

    for file in [f for f in os.listdir(IMAGE_DIR) if
                 isfile(join(IMAGE_DIR, f))]:
        f = read_jsonfile(join(IMAGE_DIR, file))

        print f
        image_name = f['name']
        if image_name in img_dict:
            image_id = img_dict[image_name]
            print 'image_id: ' + image_id
            res, output = sh('%s ims add_regions test %s %s' % (
                CLI_PATH, image_id, file_name))
        else:
            print 'image_name: {} does not exist. ignore.'.format(image_name)

os.unlink(file_name)
