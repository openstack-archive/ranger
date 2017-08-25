#!/usr/bin/env python
import json
import re
import sys


data = {
    "swap": "0",
    "visibility": "public"
}

flavor_name = sys.argv[1]
series, geometry = flavor_name.split('.')
try:
    # Try with ephemeral
    match = re.search('c(.+?)r(.+?)d(.+?)e(.*)', geometry)
    vcpus = match.group(1)
    ram = match.group(2)
    disk = match.group(3)
    ephemeral = match.group(4)
except AttributeError:
    # Try without ephemeral. If this doesn't work, the input is invalid
    match = re.search('c(.+?)r(.+?)d(.*)', geometry)
    vcpus = match.group(1)
    ram = match.group(2)
    disk = match.group(3)
    ephemeral = 0

# Fill the Flavor data
data['series'] = series
data['vcpus'] = vcpus
data['ram'] = str(int(ram) * 1024)
data['disk'] = disk
data['ephemeral'] = str(ephemeral)

# Write the Flavor JSON to the file
open(flavor_name, "w").write(json.dumps(data, indent=4) + '\n')
