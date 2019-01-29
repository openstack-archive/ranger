from __builtin__ import int

from sqlalchemy import func

from orm.services.customer_manager.cms_rest.data.sql_alchemy.models import (CmsDomain, Groups)
from orm.services.customer_manager.cms_rest.logger import get_logger

LOG = get_logger(__name__)


class GroupRecord:
    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__groups = Groups()
        self.__TableName = "groups"

        if session:
            self.setDBSession(session)

    def setDBSession(self, session):
        self.session = session

    @property
    def groups(self):
        return self.__groups

    @groups.setter
    def groups(self, groups):
        self.__groups = groups

    def insert(self, groups):
        try:
            self.session.add(groups)
        except Exception as exception:
            LOG.log_exception("Failed to insert Group" + str(groups), exception)
            raise

    def delete_by_primary_key(self, group_id):
        result = self.session.connection().execute("delete from groups where id = {}".format(group_id))    # nosec
        return result

    def read_by_primary_key(self):
        return self.read_groups(self.__groups.id)

    def read_groups(self, group_id):
        try:
            groups = self.session.query(Groups).filter(Groups.id == group_id)
            return group.first()

        except Exception as exception:
            message = "Failed to read_groups:group_id: %d " % (group_id)
            LOG.log_exception(message, exception)
            raise

    def read_group_by_uuid(self, group_uuid):
        try:
            groups = self.session.query(Groups).filter(Groups.uuid == group_uuid)
            return groups.first()

        except Exception as exception:
            message = "Failed to read_group:group_uuid: %d " % group_uuid
            LOG.log_exception(message, exception)
            raise

    def get_group_id_from_uuid(self, uuid):
        result = self.session.connection().scalar("SELECT id from groups WHERE uuid = \"{}\"".format(uuid))  # nosec

        if result:
            return int(result)
        else:
            return None

    def delete_group_by_uuid(self, uuid):
        try:
            result = self.session.query(Groups).filter(
                Groups.uuid == uuid).delete()
            return result

        except Exception as exception:
            message = "Failed to delete_group_by_uuid: uuid: {0}".format(uuid)
            LOG.log_exception(message, exception)
            raise

    def get_groups_by_criteria(self, **criteria):

        try:
            LOG.info("get_groups_by_criteria: criteria: {0}".format(criteria))
            region = criteria['region'] if 'region' in criteria else None
            user = criteria['user'] if 'user' in criteria else None
            rgroup = criteria['rgroup'] if 'rgroup' in criteria else None
            starts_with = criteria['starts_with'] if 'starts_with' in criteria else None
            contains = criteria['contains'] if 'contains' in criteria else None

            query = self.session.query(Groups)

            if starts_with:
                query = query.filter(
                    Groups.name.ilike("{}%".format(starts_with)))

            if contains:
                query = query.filter(
                    Groups.name.ilike("%{}%".format(contains)))

            query = self.customise_query(query, criteria)
            return query.all()

        except Exception as exception:
            message = "Failed to get_groups_by_criteria: criteria: {0}".format(criteria)
            LOG.log_exception(message, exception)
            raise

    def customise_query(self, query, kw):
        start = int(kw['start']) if 'start' in kw else 0
        limit = int(kw['limit']) if 'limit' in kw else 0

        if start > 0:
            query = query.offset(start)

        if limit > 0:
            query = query.limit(limit)

        return query
