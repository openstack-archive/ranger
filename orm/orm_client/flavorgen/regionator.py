#!/usr/bin/env python
import argparse
import ast
import json
import os
import re
import subprocess
import tempfile
import time


# Default flavor json directory
FLAVOR_DIR = './flavor_dir'
CLI_PATH = '../ormcli/orm'
FID = None
FILE_NAME = None
FLAVOR_NAME = None
REGION_NAME = None


def get_flavor_type(path):
    # The last directory name is the flavor type (e.g., 'medium')
    return path.split('/')[-2]


def get_region_list(regions):
    global REGION_NAME
    result = []
    for region in regions:
        REGION_NAME = region
        res, output = sh('get_region')
        if not res:
            result_region = ast.literal_eval(output)
            result.append({'name': result_region['name'],
                           'designType': result_region['designType']})
        else:
            print 'Failed to get region %s, aborting...' % (region,)
            exit(1)

    return result


def create_command(cli_command):
    if cli_command == 'add_region':
        cmd = 'python %s fms add_region %s %s' % (CLI_PATH, FID, FILE_NAME,)
    elif cli_command == 'get_flavor':
        cmd = '%s fms get_flavor test %s' % (CLI_PATH, FLAVOR_NAME,)
    elif cli_command == 'get_region':
        cmd = '%s rms get_region %s' % (CLI_PATH, REGION_NAME,)
    else:
        raise ValueError('Received an unknown command: %s' % (cli_command,))

    if ';' in cmd or '&&' in cmd:
        raise Exception("Violation of command injection, cmd is " + cmd)
    return cmd


def read_jsonfile(file):
    return json.loads(open(file).read())


def calculate_name(flavor):
    flavor_name = "{0}.c{1}r{2}d{3}".format(flavor['series'], flavor['vcpus'],
                                            int(flavor['ram']) / 1024,
                                            flavor['disk'])
    if 'ephemeral' in flavor and int(flavor['ephemeral']) != 0:
        flavor_name += 'e{0}'.format(flavor['ephemeral'])

    return flavor_name


def sh(cli_command):
    # run a shell command, echoing output, painting error lines red,
    # print runtime and status
    # return status and output

    cmd = create_command(cli_command)
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
                                 description='batch add region to flavor')
parser.add_argument('regions',
                    type=str,
                    default='',
                    help='<comma-separated regions to add, e.g. region1,'
                         'region2>')
parser.add_argument('series',
                    type=str,
                    default='',
                    nargs='?',
                    help='<comma-separated flavor series to add, e.g. nd,gv>')
args = parser.parse_args()

regions = args.regions.split(',')
series_list = args.series.split(',')
if not regions:
    print "Must specify at least one region"
    exit(1)

# Get all regions from RMS
region_list = get_region_list(regions)
any_update = False

for file in [os.path.join(dp, f) for dp, dn, fn in
             os.walk(os.path.expanduser(FLAVOR_DIR)) for f in fn]:
    try:
        f = read_jsonfile(file)
    except ValueError:
        continue

    updated = False
    flavor_type = get_flavor_type(file)
    if not series_list or series_list == [''] or f['series'] in series_list:
        data = {'regions': []}
        for region in region_list:
            # Take only the regions whose design type matches the flavor's
            if flavor_type.lower() == region['designType'].lower():
                data['regions'].append({'name': region['name']})
                updated = True
                any_update = True

        if updated:
            # Create the json file
            fh, file_name = tempfile.mkstemp()
            FILE_NAME = file_name
            os.write(fh, json.dumps(data))
            os.close(fh)

            FLAVOR_NAME = calculate_name(f)
            res, output = sh('get_flavor')
            if not res:
                flavor = ast.literal_eval(output)
                FID = flavor['flavor']['id']
                print 'fid: ' + FID
                res, output = sh('add_region')

            os.unlink(FILE_NAME)

if not any_update:
    if not args.series:
        exp = 'design type of any of the regions:[{}]'.format(args.regions)
    else:
        exp = 'combination of regions:[{}] and series:[{}]'.format(
            args.regions, args.series)

    print('No flavor was updated, please make sure that the {} matches any '
          'flavor under the flavor directory'.format(exp))
