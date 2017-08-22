from pecan.hooks import PecanHook


class SimpleHookMock(PecanHook):
    def before(self, state):
        setattr(state.request, 'transaction_id', 'some_id')
