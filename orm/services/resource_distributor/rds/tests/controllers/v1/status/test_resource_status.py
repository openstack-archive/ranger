"""unittest for post resource."""
from mock import patch

import rds.controllers.v1.status.resource_status as resource
from rds.tests.controllers.v1.functional_test import FunctionalTest


class PostResourceStatus(FunctionalTest):
    """tests for only for api handler."""

    @patch.object(resource.regionResourceIdStatus, 'add_status',
                  return_value=None)
    def test_valid_Post_status(self, input):
        """Post json valid json."""
        response = self.app.post_json('/v1/rds/status/', data)
        assert response.status_int == 201

    @patch.object(resource.regionResourceIdStatus, 'add_status',
                  side_effect=resource.InputError("no input", 'request_id'))
    def test_valid_Post_status_database_error(self, input):
        """Post valid json return database error."""
        response = self.app.post_json('/v1/rds/status/', data,
                                      expect_errors=True)
        assert response.status_int == 400

    @patch.object(resource.regionResourceIdStatus, 'add_status',
                  return_value=None)
    def test_not_valid_json_Post(self, input):
        """Post valid json return database error."""
        response = self.app.post_json('/v1/rds/status/', data_not_valid,
                                      expect_errors=True)
        assert response.status_int == 400


data = {
    "rds-listener": {
        "request-id": "0649c5be323f4792",
        "resource-id": "12fde398643",
        "resource-type": "customer",
        "resource-template-version": "1",
        "resource-template-type": "HOT",
        "resource-operation": "create",
        "ord-notifier-id": "1",
        "region": "dla1",
        "status": "Success",
        "error-code": "200",
        "error-msg": "OK"
    }
}

data_not_valid = {
    "rds_listener": {
        "resource_id": "12fde398643",
        "resource_type": "customer",
        "resource_template_version": "1",
        "resource_template_type": "HOT",
        "resource_operation": "create",
        "ord_notifier_id": "1",
        "region": "dla1",
        "status": "Success",
        "error_code": "200",
        "error_msg": "OK"
    }
}
