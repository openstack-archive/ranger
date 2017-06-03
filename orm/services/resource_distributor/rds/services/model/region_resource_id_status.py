

class ResourceMetaData(object):
    def __init__(self, checksum, virtual_size, size):
        self.size = size
        self.virtual_size = virtual_size
        self.checksum = checksum

    def as_dict(self):
        return self.__dict__


class Model(object):
    def __init__(self,
                 timestamp,
                 region,
                 status,
                 transaction_id,
                 resource_id,
                 ord_notifier,
                 err_msg,
                 err_code,
                 operation,
                 resource_extra_metadata=None):
        self.timestamp = timestamp
        self.region = region
        self.status = status
        self.ord_transaction_id = transaction_id
        self.resource_id = resource_id
        self.ord_notifier_id = ord_notifier
        self.error_msg = err_msg
        self.error_code = err_code
        self.operation = operation

        if resource_extra_metadata:
            self.resource_extra_metadata = ResourceMetaData(
                checksum=resource_extra_metadata[0].checksum,
                virtual_size=resource_extra_metadata[0].virtual_size,
                size=resource_extra_metadata[0].size
            )
        else:
            self.resource_extra_metadata = None

    def as_dict(self):
        return self.__dict__


class StatusModel(object):
    def __init__(self, status):
        self.regions = status
        self.status = self._get_aggregated_status()

    def _get_aggregated_status(self):
        is_pending = False
        for region in self.regions:
            if region.status == 'Error' and region.operation.strip() != 'delete':
                # If a region had an error, the aggregated status is 'Error'
                return 'Error'
            elif region.status == 'Submitted':
                # Just set the flag but don't return, because there might be
                # an error in any of the next iterations
                is_pending = True

        if is_pending:
            return 'Pending'
        else:
            # If self.regions is empty, the result will still be 'Success' but the
            # server returns 404 Not Found
            return 'Success'
