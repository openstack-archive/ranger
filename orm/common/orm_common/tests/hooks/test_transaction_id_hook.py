import mock
from orm_common.hooks import transaction_id_hook
from unittest import TestCase
import logging

logger = logging.getLogger(__name__)


class TestTransactionIdHook(TestCase):
    @mock.patch.object(transaction_id_hook.utils, 'make_transid',
                       return_value='test')
    def test_before_sanity(self, mock_make_transid):
        t = transaction_id_hook.TransactionIdHook()
        state = mock.MagicMock()
        t.before(state)
        self.assertEqual(state.request.transaction_id, 'test')
        self.assertEqual(state.request.tracking_id, 'test')
