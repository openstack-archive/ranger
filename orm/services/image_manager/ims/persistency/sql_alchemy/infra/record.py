from orm.services.image_manager.ims.logger import get_logger

LOG = get_logger(__name__)


class Record(object):

    def __init__(self):
        self.session = None

    def set_db_session(self, session):
        self.session = session

    @staticmethod
    def customise_query(query, kw):
        start = int(kw['start']) if 'start' in kw else 0
        limit = int(kw['limit']) if 'limit' in kw else 0

        if start > 0:
            query = query.offset(start)

        if limit > 0:
            query = query.limit(limit)

        print str(query)
        return query

#   5644 ProCG uses this line - don't edit it
