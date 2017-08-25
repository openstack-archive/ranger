import csv
import logging


log = logging.getLogger(__name__)


def _validate_file(file):
    if str(file).split('.')[-1] != 'csv':
        log.error('please provide csv file')
        raise TypeError('please provide csv file')


def read_csv_file(file):
    _validate_file(file)
    resources = []
    with open(file, 'rb') as csvfile:
        csv_dict = csv.DictReader(csvfile)
        for resource in csv_dict:
            resources.append(resource["uuids"])
        log.debug(
            'list of resources to clean ----{} -------'.format(resources))
    return resources
