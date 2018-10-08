import cli_comander as cli
import db_comander as db
import initializer
import logging
import sys
import utils
import yaml_handler as yh


log = logging.getLogger(__name__)


def _validate_service(service):
    allowed_services = ['CMS', 'FMS', 'IMS']
    if service.upper() not in allowed_services:
        raise Exception("service should be one of {}".format(allowed_services))
    return service.upper()


def _init():
    initializer.init_log()
    return


def read_csv_file(file):
    log.debug("reading file {}".format(file))
    return utils.read_csv_file(file)


def resource_db_clean(resource_id, service):
    log.debug("cleaning {} db for resource {}".format(service, resource_id))
    db.remove_resource_db(resource_id, service)
    return


def check_yaml_file(resource_id):
    log.debug('checking yml file if exist for resource {}'.format(resource_id))
    files = yh.check_yaml_exist(resource_id)
    message = 'no yaml files found for this resource'
    if files:
        message = "found files please remove manualy {}".format(files)
    log.debug(message)
    return


def get_resource_regions(resource_id, service_name):

    if service_name.upper() == 'CMS':
        db_regions = db.get_cms_db_resource_regions(resource_id, service_name)
    elif service_name.upper() == 'FMS':
        db_regions = db.get_fms_db_resource_regions(resource_id, service_name)
    elif service_name.upper() == 'IMS':
        db_regions = db.get_ims_db_resource_regions(resource_id, service_name)

#    db_regions = db.get_resource_regions(resource_id, service_name)
    orm_regions = cli.get_resource_regions(resource_id, service_name)
    return orm_regions, db_regions


def clean_rds_resource_status(resource_id):
    log.debug("clean rds status db for resource {}".format(resource_id))
    db.remove_rds_resource_status(resource_id)
    return


def _start_cleaning():
    log.info('start cleaning')
    file_path = sys.argv[1]
    service = _validate_service(sys.argv[2])
    resourses_to_clean = read_csv_file(file_path)
    for resource_id in resourses_to_clean:
        try:
            log.debug(
                'check if resource  {} has any regions before clean'.format(
                    resource_id))
            resource_regions, db_regions = get_resource_regions(resource_id,
                                                                service)
            if resource_regions or db_regions:
                log.error(
                    "got regions {} {} please clean regions from orm before"
                    " removing the resource {}".format(resource_regions,
                                                       db_regions,
                                                       resource_id))
                raise Exception(
                    "got regions {} {} please clean regions from orm before"
                    " removing the resource {}".format(resource_regions,
                                                       db_regions,
                                                       resource_id))

            log.debug('cleaning {}'.format(resource_id))
            resource_db_clean(resource_id, service)
            check_yaml_file(resource_id)
            clean_rds_resource_status(resource_id)
            if service.upper() == "IMS":
                db.remove_rds_image_metadata(resource_id)

        except Exception as exp:
            log.error("---------------{}---------------".format(exp.message))
            if 'not found' not in exp.message:
                log.exception(exp)
            continue
    return


if __name__ == '__main__':
    warning_message = input(
        'IMPORTANT:- please note its your responsibility to backup the db'
        ' before running this script... click enter before continue'
    )
    _init()
    _start_cleaning()
