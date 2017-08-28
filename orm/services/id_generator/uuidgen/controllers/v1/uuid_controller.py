import datetime
import logging
import uuid

from orm.services.id_generator.uuidgen.db.db_manager import DBManager
from pecan import expose, response
from pecan.rest import RestController

LOG = logging.getLogger(__name__)


def respond(reason, code, message):
    """A helper function to create a response dict with the given values"""
    return {
        reason: {
            "code": code,
            "message": message
        }
    }


class UUIDController(RestController):
    @expose(template='json')
    def post(self, **kw):
        """Method to handle POST /v1/uuids
        create and return a new uuid
            prameters:
                uuid_type (optional)
            return: dict describing success or failure of post command
        """
        messageToReturn = None
        uuid_type = ''
        customer_id = None
        if 'uuid_type' in kw:
            uuid_type = kw['uuid_type']
            del kw['uuid_type']
        if 'uuid' in kw:
            customer_id = kw['uuid']
            del kw['uuid']
        LOG.info("UUIDController.post (url: /v1/uuids) uuid_type=" + uuid_type)

        if len(kw):
            response.status = 400
            messageToReturn = respond("badRequest", 400, 'Unknown parameter(s):' + ', '.join(kw.keys()))
            LOG.info("UUIDController.post - " + str(messageToReturn))
            return messageToReturn

        if not customer_id:
            return self.create_new_uuid(uuid_type)

        return self.validate_and_add_uuid(customer_id)

    def validate_and_add_uuid(self, customer_id):
        try:
            uuid_type = "custId"
            db_manager = DBManager()
            db_manager.create_uuid(customer_id, uuid_type)
            return {
                "uuid": customer_id,
                "issued_at": datetime.datetime.utcnow().isoformat() + 'Z',
                "uuid_type": uuid_type
            }
        except Exception as e:
            # ignore case of uuid already exist, this can append when creating customer with specific uuid,
            # we just need to save it in the database that we will not give this value in the future requests
            # but we don't need to throw exception if already exist, this is not our responsible
            # if it is duplicate uuid it will fail in the service which uses this uuid (cms, fms)
            if e.orig.args[0] != 1062:
                response.status = 500
                messageToReturn = respond("badRequest", 500, 'Database error')
                LOG.error(str(messageToReturn) + "Exception: " + str(e))
                return messageToReturn
        return {
            "uuid": customer_id,
            "issued_at": datetime.datetime.utcnow().isoformat() + 'Z',
            "uuid_type": uuid_type
        }

    def create_new_uuid(self, uuid_type):
        uu = uuid.uuid4().hex

        try:
            db_manager = DBManager()
            db_manager.create_uuid(uu, uuid_type)
            return {
                "uuid": uu,
                "issued_at": datetime.datetime.utcnow().isoformat() + 'Z',
                "uuid_type": uuid_type
            }
        except Exception as e:
            response.status = 500
            messageToReturn = respond("badRequest", 500, 'Database error')
            LOG.error(str(messageToReturn) + "Exception: " + str(e))
            return messageToReturn
