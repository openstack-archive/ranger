""" SoT interface definition
"""


class BaseSoT(object):

    def save_resource_to_sot(self,
                             tracking_id,
                             transaction_id,
                             resource_list):
        raise NotImplementedError("Please Implement this method")

    def validate_sot_state(self):
        raise NotImplementedError("Please Implement this method")


class SoTError(Exception):
    pass
