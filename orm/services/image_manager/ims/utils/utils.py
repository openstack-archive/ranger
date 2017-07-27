from pecan import conf, request
import time


def convert_time_human(time_stamp):
    return time.ctime(int(time_stamp))


def get_server_links(id=None):
    links = {'self': '{}'.format(request.url)}
    self_links = '{}'.format(request.upath_info)
    if id and id not in request.path:
        links['self'] += '{}{}'.format('' if request.path[-1] == '/' else '/',
                                       id)
        self_links += '{}{}'.format('' if request.path[-1] == '/' else '/', id)
    return links, self_links
