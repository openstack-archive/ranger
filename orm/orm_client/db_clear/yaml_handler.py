import config as conf
import fnmatch
import os


def _get_resource_file_path():
    file_path = conf.local_repository_path
    return file_path


def _find_file(resource_id):
    file_name = conf.file_name_format.format(resource_id)
    folder_to_search = _get_resource_file_path()
    matches = []
    for root, dirnames, filenames in os.walk(folder_to_search):
        for filename in fnmatch.filter(filenames, file_name):
            matches.append(os.path.join(root, filename))
    return matches


def check_yaml_exist(resource_id):
    files = _find_file(resource_id)
    if files:
        return files
    return None
