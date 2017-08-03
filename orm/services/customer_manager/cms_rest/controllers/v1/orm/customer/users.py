from cms_rest.logger import get_logger
from cms_rest.logic.customer_logic import CustomerLogic
from cms_rest.logic.error_base import ErrorStatus, NotFound
from cms_rest.model.Models import User, UserResultWrapper
from cms_rest.utils import authentication
from orm_common.utils import api_error_utils as err_utils
from orm_common.utils import utils
from pecan import request, rest
from wsmeext.pecan import wsexpose

LOG = get_logger(__name__)


class DefaultUserController(rest.RestController):

    @wsexpose([str], str, rest_content_types='json')
    def get(self, customer_id):
        return ["This is the users controller ",
                "customer id: " + customer_id,
                "user " + "default user"]

    @wsexpose(UserResultWrapper, str, body=[User], rest_content_types='json', status_code=200)
    def put(self, customer_id, users):  # replace default users to customer
        LOG.info("DefaultUserController - Replace DefaultUsers (put) customer id {0} users: {1}".format(customer_id, str(users)))
        authentication.authorize(request, 'customers:update_default_user')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.replace_default_users(customer_id, users, request.transaction_id)
            LOG.info("DefaultUserController - Replace DefaultUsers (put) Finished well customer id {0} users: {1}".format(customer_id, str(users)))

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to replace default users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except Exception as exception:
            result = UserResultWrapper(transaction_id="Users Not Added", users=[])
            LOG.log_exception("DefaultUserController - Failed to replace default users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(UserResultWrapper, str, body=[User], rest_content_types='json', status_code=200)
    def post(self, customer_id, users):  # add default users to customer
        LOG.info("DefaultUserController - Add DefaultUsers (put) customer id {0} users: {1}".format(customer_id, str(users)))
        authentication.authorize(request, 'customers:add_default_user')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.add_default_users(customer_id, users, request.transaction_id)
            LOG.info("DefaultUserController - Add DefaultUsers (post) Finished well customer id {0} users: {1}".format(
                customer_id, str(users)))

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to add default users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except Exception as exception:
            result = UserResultWrapper(transaction_id="Users Not Added", users=[])
            LOG.log_exception("DefaultUserController - Failed to add default users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, str, status_code=204)
    def delete(self, customer_id, user_id):
        LOG.info("DefaultUserController - Delete DefaultUsers (delete) customer id {0} user_id: {1}".format(customer_id, user_id))
        authentication.authorize(request, 'customers:delete_default_user')
        try:
            customer_logic = CustomerLogic()
            customer_logic.delete_default_users(customer_id, user_id, request.transaction_id)
            LOG.info("DefaultUserController - Delete DefaultUsers (delete) Finished well customer id {0} user_id: {1}".format(customer_id, user_id))
            utils.audit_trail('delete default users', request.transaction_id, request.headers, customer_id)

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to delete default users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except NotFound as e:
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=404)

        except Exception as exception:
            LOG.log_exception("DefaultUserController - Failed in Delete default User", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))


class UserController(rest.RestController):

    @staticmethod
    def _validate(args):
        # validate if user didnt provide input json for users
        # to prevent wsme to take the input from url params
        if 'users' in args and args['users'] and not request.body:
            raise err_utils.get_error(request.transaction_id,
                                      message="bad request, no json body",
                                      status_code=400)

    @wsexpose([str], str, str, rest_content_types='json')
    def get(self, customer_id, region_id):
        return ["This is the users controller ",
                "customer id: " + customer_id,
                "region id: " + region_id]

    @wsexpose(UserResultWrapper, str, str, body=[User], rest_content_types='json', status_code=200)
    def post(self, customer_id, region_id, users):
        self._validate(locals())  # more validations for input
        title = "Add users to Region '{}' for customer: '{}', users: {}".format(region_id, customer_id, str(users))
        LOG.info("UserController - {}".format(title))
        authentication.authorize(request, 'customers:add_region_user')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.add_users(customer_id, region_id, users, request.transaction_id)
            LOG.info("UserController - {} Finished well".format(title))

            event_details = 'Customer {} users: {} added in region {}'.format(
                customer_id, [u.id for u in users], region_id)
            utils.audit_trail('add users', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to {}".format(title), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except Exception as exception:
            result = UserResultWrapper(transaction_id="Users Not Added", users=[])
            LOG.log_exception("UserController - Failed to Add Users (post)", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(UserResultWrapper, str, str, body=[User], rest_content_types='json', status_code=200)
    def put(self, customer_id, region_id, users):
        self._validate(locals())  # more validations for input
        title = "Replace users to Region '{}' for customer: '{}', users: {}".format(region_id, customer_id, str(users))
        LOG.info("UserController - {}".format(title))
        authentication.authorize(request, 'customers:update_region_user')
        try:
            customer_logic = CustomerLogic()
            result = customer_logic.replace_users(customer_id, region_id, users, request.transaction_id)
            LOG.info("UserController - {} Finished well".format(title))

            event_details = 'Customer {} users: {} updated in region {}'.format(
                customer_id, [u.id for u in users], region_id)
            utils.audit_trail('replace users', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to {}".format(title), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except Exception as exception:
            result = UserResultWrapper(transaction_id="Users Not Replaced", users=[])
            LOG.log_exception("UserController - Failed to Replaced Users (put)", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))

        return result

    @wsexpose(None, str, str, str, status_code=204)
    def delete(self, customer_id, region_id, user_id):
        LOG.info("UserController - Delete User (delete) customer id {0} region_id: {1} user_id: {2}".format(customer_id, region_id, user_id))
        authentication.authorize(request, 'customers:delete_region_user')
        try:
            customer_logic = CustomerLogic()
            customer_logic.delete_users(customer_id, region_id, user_id, request.transaction_id)
            LOG.info("UserController - Delete User (delete) Finished well customer id {0} region_id: {1} user_id: {2}".format(customer_id, region_id, user_id))

            event_details = 'Customer {} user: {} deleted in region {}'.format(
                customer_id, user_id, region_id)
            utils.audit_trail('delete users', request.transaction_id,
                              request.headers, customer_id,
                              event_details=event_details)

        except ErrorStatus as exception:
            LOG.log_exception("DefaultUserController - Failed to delete users", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=exception.status_code)

        except LookupError as exception:
            LOG.log_exception("DefaultUserController - {0}".format(exception.message), exception)
            raise err_utils.get_error(request.transaction_id,
                                      message=exception.message,
                                      status_code=404)

        except NotFound as e:
            raise err_utils.get_error(request.transaction_id,
                                      message=e.message,
                                      status_code=404)

        except Exception as exception:
            LOG.log_exception("UserController - Failed to Delete User (delete) ", exception)
            raise err_utils.get_error(request.transaction_id,
                                      status_code=500,
                                      error_details=str(exception))
