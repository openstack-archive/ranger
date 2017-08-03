from ims.logger import get_logger
from ims.persistency.sql_alchemy.image.image_record import ImageRecord
from oslo_db.sqlalchemy import session as db_session
from pecan import conf
from sqlalchemy.event import listen

LOG = get_logger(__name__)


# event handling
def on_before_flush(session, flush_context, instances):
    print("on_before_flush:", str(flush_context))
    for model in session.new:
        if hasattr(model, "validate"):
            model.validate("new")

    for model in session.dirty:
        if hasattr(model, "validate"):
            model.validate("dirty")


class DataManager(object):

    def __init__(self, connection_string=None):

        if not connection_string:
            connection_string = conf.database.connection_string

        self._engine_facade = db_session.EngineFacade(connection_string, autocommit=False)
        self._session = None
        listen(self.session, 'before_flush', on_before_flush)
        self.image_record = None

    def get_engine(self):
        return self._engine_facade.get_engine()

    @property
    def engine(self):
        return self.get_engine()

    def get_session(self):
        if not self._session:
            self._session = self._engine_facade.get_session()
        return self._session

    @property
    def session(self):
        return self.get_session()

    def flush(self):
        try:
            self.session.flush()
        except Exception as exp:
            raise

    def commit(self):
        self.session.commit()

    def expire_all(self):
        self.session.expire_all()

    def close(self):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def begin_transaction(self):
        pass
        # no need to begin transaction - the transaction is open automatically

    def get_record(self, record_name):
        if record_name == "Image" or record_name == "image":
            if not self.image_record:
                self.image_record = ImageRecord(self.session)
            return self.image_record
        return None

#      7540 ProCG uses this line - don't edit it
