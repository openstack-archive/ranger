""" Storage base backend
"""


class Base(object):
    def __init__(self, url):
        pass

    def add_update_status_record(self,
                                 timestamp,
                                 region,
                                 status,
                                 transaction_id,
                                 resource_id,
                                 ord_notifier,
                                 err_msg,
                                 err_code):
        raise NotImplementedError("Please Implement this method")

    def get_records_by_resource_id(self, resource_id):
        raise NotImplementedError("Please Implement this method")

    def get_records_by_filter_args(self, **filter_args):
        raise NotImplementedError("Please Implement this method")