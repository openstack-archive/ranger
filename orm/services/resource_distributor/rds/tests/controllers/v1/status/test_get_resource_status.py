"""unittest get resource status."""
from mock import MagicMock

import rds.controllers.v1.status.get_resource as resource
from rds.services.model.region_resource_id_status import Model
from rds.services.model.region_resource_id_status import StatusModel
from rds.tests.controllers.v1.functional_test import FunctionalTest


class EmptyModel(object):
    """mock class."""

    status = None

    def __init__(self, regions=None):
        """init function.

        :param regions:
        """
        self.regions = regions


class GetResourceStatus(FunctionalTest):
    """tests for get status api."""

    def test_get_not_found_resource(self):
        """get not found."""
        resource.regionResourceIdStatus.get_status_by_resource_id = \
            MagicMock(return_value=EmptyModel())
        response = self.app.get('/v1/rds/status/resource/1',
                                expect_errors=True)
        assert response.status_int == 404

    def test_get_valid_resource(self):
        """get valid resource."""
        result = Model(
            status="200", timestamp="123456789", region="name",
            transaction_id=5, resource_id="1",
            ord_notifier="", err_msg="123", err_code="12", operation="create"
        )
        status_model = StatusModel(status=[result])
        resource.regionResourceIdStatus.get_status_by_resource_id = \
            MagicMock(return_value=status_model)
        response = self.app.get('/v1/rds/status/resource/1')
        assert response.status_int == 200
