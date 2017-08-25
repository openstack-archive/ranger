#!/usr/bin/env python
import argparse
import json
import os
import subprocess
import tempfile
import time

# Default flavor json directory
FLAVOR_DIR = './flavor_dir'


def read_jsonfile(file):
    return json.loads(open(file).read())


def calculate_name(flavor):
    return "{0}.c{1}r{2}d{3}".format(flavor['series'], flavor['vcpus'],
                                     int(flavor['ram']) / 1024, flavor['disk'])


def sh(harg, file_name):
    # run a shell command, echoing output, painting error lines red,
    # print runtime and status
    # return status and output

    cmd = create_command(harg, file_name)

    print '>> Starting: ' + cmd
    start = time.time()
    output = ''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
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


def create_command(harg, file_name):
    cmd = 'python ../ormcli/orm fms %s create_flavor %s' % \
          (harg, file_name)
    if ';' in cmd or '&&' in cmd:
        raise Exception("Violation of command injection, cmd is " + cmd)
    return cmd


parser = argparse.ArgumentParser(prog='flavorator',
                                 description='batch flavor creator')
args = parser.parse_args()

for file in [os.path.join(dp, f) for dp, dn, fn in
             os.walk(os.path.expanduser(FLAVOR_DIR)) for f in fn]:
    try:
        f = read_jsonfile(file)
    except ValueError:
        continue

    print f
    flavor_name = calculate_name(f)
    fh, file_name = tempfile.mkstemp()
    os.write(fh, json.dumps({"flavor": f}))
    os.close(fh)
    res, output = sh('', file_name)
    os.unlink(file_name)
