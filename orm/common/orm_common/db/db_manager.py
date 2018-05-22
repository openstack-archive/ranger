import logging

from orm import base_config
from orm.common.orm_common.db.uuid_db import UUID
from oslo_db.sqlalchemy import session as db_session

logger = logging.getLogger(__name__)


class DBManager(object):

    def __init__(self, connection_string=None):
        if not connection_string:
            connection_string = base_config.db_url + 'orm'

        self._engine_facade = db_session.EngineFacade(connection_string, autocommit=False)
        self._session = None

    def get_session(self):
        if not self._session:
            self._session = self._engine_facade.get_session()
        return self._session

    @property
    def session(self):
        return self.get_session()

    def begin_transaction(self):
        # self.session.begin()
        # no need to begin transaction - the transaction is open automatically
        pass

    def get_engine(self):
        return self._engine_facade.get_engine()

    @property
    def engine(self):
        return self.get_engine()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def create_uuid(self, _uuid, _uuid_type):
        uuid = UUID()
        uuid.uuid = _uuid
        uuid.uuid_type = _uuid_type

        try:
            self.begin_transaction()
            self.session.add(uuid)
            self.session.commit()
            self.session.close()
            self.engine.dispose()
        except SystemError as ex:
            logger.exception(ex)
            raise ex
