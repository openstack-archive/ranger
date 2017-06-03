from orm_common.hooks.transaction_id_hook import TransactionIdHook
from pecan import abort
from fms_rest.utils import utils


class TransIdHook(TransactionIdHook):

    def before(self, state):
        try:
            transaction_id = utils.make_transid()
        except Exception as exc:
            abort(500, headers={'faultstring': exc.message})

        tracking_id = state.request.headers['X-RANGER-Tracking-Id'] \
            if 'X-RANGER-Tracking-Id' in state.request.headers else transaction_id
        setattr(state.request, 'transaction_id', transaction_id)
        setattr(state.request, 'tracking_id', tracking_id)
