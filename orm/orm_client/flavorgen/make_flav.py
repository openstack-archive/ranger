#!/usr/bin/env python
import sys
import json


if sys.argv[1].isdigit():
    vcpus = sys.argv[1]
else:
    vcpus = "1"
if sys.argv[1].isdigit():
    ram = sys.argv[1]
else:
    ram = "1"
if sys.argv[1].isdigit():
    disk = sys.argv[1]
else:
    disk = "1"


def calculate_name(flavor):
    return "{0}.c{1}r{2}d{3}".format(flavor['series'], flavor['vcpus'],
                                     flavor['ram'], flavor['disk'])

data = {
    "series": "gv",
    "vcpus": "10",
    "ram": "20",
    "disk": "30",
    "ephemeral": "0",
    "swap": "0",
    "visibility": "public"
  }

flavor_name = calculate_name(data)
series = flavor_name.split('.')[0]

open(flavor_name, "w").write(json.dumps(data, indent=4)+'\n')
