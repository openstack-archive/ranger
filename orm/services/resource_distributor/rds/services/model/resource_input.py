
class ResourceData(object):
    def __init__(self, resource_id, resource_type,
                 targets, operation="create",
                 transaction_id="", model="",
                 external_transaction_id=""):
        self.resource_id = resource_id
        self.targets = targets
        self.resource_type = resource_type
        self.operation = operation
        self.transaction_id = transaction_id
        self.model = model
        self.external_transaction_id = external_transaction_id
