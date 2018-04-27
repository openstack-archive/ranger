from orm.common.orm_common.utils import utils
from pecan import abort
from pecan.hooks import PecanHook


class TransactionIdHook(PecanHook):

    def before(self, state):
        try:
            transaction_id = utils.make_transid()
        except Exception as exc:
            abort(500, headers={'faultstring': exc.message})

        tracking_id = state.request.headers['X-AIC-ORM-Tracking-Id'] \
            if 'X-AIC-ORM-Tracking-Id' in state.request.headers else transaction_id
        setattr(state.request, 'transaction_id', transaction_id)
        setattr(state.request, 'tracking_id', tracking_id)
