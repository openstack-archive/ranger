"""ORD trigger main module."""

import json
import time

import logging
import requests

from pecan import conf

from audit_client.api import audit

from rds.services import region_resource_id_status as regionResourceIdStatus

# REST API constants
OK_CODE = 200
ACK_CODE = 200

logger = logging.getLogger(__name__)


class OrdNotFoundError(Exception):
    """Indicates that the correct ORD to notify was not found."""

    pass


class NotifyNotAcknowledgedError(Exception):
    """Indicates that the ORD did not respond correctly to our notification."""

    pass


class ConfigFileError(Exception):
    """Indicates that the configuration file could not be found."""

    pass


def _find_correct_ord(url, lcp_name):
    """Use the Discover API to get the ORD URL.

    :param url: Discovery server URL
    :param lcp_name: The name of the LCP whose ORD is to be found
    :return: The ORD URL, or None if it wasn't found
    """
    logger.info('Getting the ORD URL of LCP %s...' % (lcp_name,))
    # Get the LCP record from RMS
    response = requests.get('%s/v2/orm/regions?regionname=%s' % (url,
                                                                 lcp_name,),
                            verify=conf.verify)
    if response.status_code != OK_CODE:
        return None

    lcp = response.json()
    try:
        for endpoint in lcp['regions'][0]['endpoints']:
            if endpoint['type'] == 'ord':
                return endpoint['publicURL']
    except KeyError:
        return None

    # Invalid LCP record (does not contain an ORD)
    return None


def _notify(ord_url,
            transaction_id,
            resource_id,
            resource_type,
            resource_template_version,
            resource_template_name,
            operation,
            region_id):
    """Send the notification message to the ORD.

    :param ord_url:
    :param transaction_id:
    :param resource_id:
    :param resource_type:
    :param resource_template_version:
    :param resource_template_name:
    :param operation:
    :param region_id:
    :raise: requests.exceptions.ConnectionError when the POST request
    cannot be sent,
    NotifyNotAcknowledgedError when the ORD did not respond to the notification
    as expected
    InvalidJsonError if the payload is missing one of the expected values
    :return:
    """
    # Prepare the request body
    data_to_send = {
        'ord-notifier': {
            'request-id': transaction_id,
            'resource-id': resource_id,
            'resource-type': resource_type,
            'resource-template-version': resource_template_version,
            'resource-template-name': resource_template_name,
            'resource-template-type': conf.ordupdate.template_type,
            'operation': operation,
            'region': region_id
        }
    }

    is_ord_url_https = ord_url.startswith('https')
    https_enabled = conf.ordupdate.https_enabled
    logger.debug('notify: ord_url: %s, https_enabled: %s, JSON: %s' % (
        ord_url, str(https_enabled), data_to_send,))

    logger.info('Notifying ORD...')
    if https_enabled:
        if conf.ordupdate.cert_path == '':
            extra_message = '(not using certificate)'
        else:
            extra_message = ''

        logger.debug('Certificate path: \'%s\' %s' % (
            conf.ordupdate.cert_path, extra_message, ))

        if not is_ord_url_https:
            ord_url = 'https%s' % ord_url[4:]
            logger.debug('switch to https, notifying ord_url: %s' % (
                ord_url))
        try:
            # Added the header to support the older version of requests
            headers = {'Content-Type': 'application/json'}
            response = requests.post('%s/v1/ord/ord_notifier' % (ord_url,),
                                     data=json.dumps(data_to_send),
                                     headers=headers,
                                     cert=conf.ordupdate.cert_path)
        except requests.exceptions.SSLError:
            logger.debug('Received an SSL error (is the certificate valid?)')
            raise
    else:
        if is_ord_url_https:
            ord_url = 'http%s' % ord_url[5:]
            logger.debug('https not supported, notifying ord_url: %s' % (
                ord_url))
        headers = {'Content-Type': 'application/json'}
        response = requests.post('%s/v1/ord/ord_notifier' % (ord_url,),
                                 headers=headers,
                                 data=json.dumps(data_to_send))

    # Make sure the ORD sent an ACK
    if response.status_code != ACK_CODE:
        message = 'Did not receive an ACK from ORD %s, status code: %d' % (
            ord_url, response.status_code, )
        encoded_message = message.replace('\n', '_').replace('\r', '_')
        if encoded_message != message:
            encoded_message = encoded_message + "(encoded)"
        logger.error(encoded_message)
        raise NotifyNotAcknowledgedError(message)


def _update_audit(lcp_name, application_id, tracking_id, transaction_id,
                  transaction_type, resource_id, user_id=None,
                  external_id=None, event_details=None, status=None):
    """Update the Audit repository with the action status."""
    timestamp = int(time.time() * 1000)
    audit.audit(timestamp, application_id, tracking_id, transaction_id,
                transaction_type, resource_id, conf.app.service_name,
                user_id, external_id, event_details)
    logger.info('LCP %s: %s (%s)' % (lcp_name, event_details, status, ))


def _update_resource_status(region, resource_id, status, transaction_id,
                            error_code, error_msg, resource_operation,
                            resource_type):
    """Update the resource status db with the status."""
    if status == 'Success':
        status = 'Submitted'
    else:
        status = 'Error'

    data_to_save = dict(
        timestamp=int(time.time() * 1000),
        region=region,
        resource_id=resource_id,
        status=status,
        transaction_id=transaction_id,
        error_code=error_code,
        error_msg=error_msg,
        resource_operation=resource_operation,
        resource_type=resource_type,
        ord_notifier_id="")

    regionResourceIdStatus.add_status(data_to_save)


def notify_ord(transaction_id,
               tracking_id,
               resource_type,
               resource_template_version,
               resource_name,
               resource_id,
               operation,
               region_id,
               application_id,
               user_id,
               external_id=None,
               error=False):
    """Notify ORD of the changes.

    This function should be called after a resource has changed in SoT
    (created, modified or deleted).

    :param transaction_id: The transaction id under which the resource was
    updated
    :param tracking_id: The tracking ID of the whole operation
    :param resource_type: The resource type ("customer" | "image" | "flavor")
    :param resource_template_version: The version id of the change in git
    :param resource_name: The updated resource name
    :param resource_id: The updated resource ID
    :param operation: Operation made on resource ("create" | "modify" |
    "delete")
    :param region_id: This is the LCP name (not ID!).
    :param application_id: The running application ID (RDS, CMS, etc.)
    :param user_id: The calling user ID
    :param external_id: An external tracking ID (optional)
    :param error: A boolean that says whether an error has occurred during the
    upload operation
    :return:
    :raise: ConfigFileError - when the configuration file was not found,
    OrdNotFoundError - when the ORD was not found,
    requests.exceptions.ConnectionError when the POST request
    cannot be sent,
    NotifyNotAcknowledgedError - when the ORD did not respond to the
    notification as expected
    """
    logger.debug('Entered notify_ord with transaction_id: %s, '
                 'tracking_id: %s, resource_type: %s, '
                 'resource_template_version: %s, resource_name: %s, '
                 'resource_id: %s, operation: %s, region_id: %s, '
                 'application_id: %s, user_id: %s, external_id: %s, '
                 'error: %s' % (transaction_id, tracking_id, resource_type,
                                resource_template_version, resource_name,
                                resource_id, operation, region_id,
                                application_id, user_id, external_id, error,))

    error_msg = ''
    transaction_type = '%s %s' % (operation, resource_type, )
    try:
        if error:
            event_details = 'upload failed'
            status = 'SoT_Error'
            error_msg = 'Upload to SoT Git repository failed'
        else:
            # Discover the correct ORD
            discover_url = '%s:%d' % (conf.ordupdate.discovery_url,
                                      conf.ordupdate.discovery_port,)
            ord_to_update = _find_correct_ord(discover_url, region_id)

            if ord_to_update is None:
                message = 'ORD of LCP %s not found' % (region_id, )
                logger.error(message)
                raise OrdNotFoundError(message)

            _notify(ord_to_update,
                    transaction_id,
                    resource_id,
                    resource_type,
                    resource_template_version,
                    resource_name,
                    operation,
                    region_id)

            # All OK
            event_details = '%s notified' % (region_id, )
            status = 'Success'
    except Exception:
        event_details = '%s notification failed' % (region_id, )
        status = 'ORD_Error'
        error_msg = 'Notification to ORD failed'
        raise
    finally:
        # Update resource_status db with status
        _update_resource_status(region_id, resource_id, status, transaction_id,
                                0, error_msg, operation, resource_type)

        # Write a record to Audit repository. Note that I assigned the
        # appropriate values to event_details and status in every flow, so
        # these variables won't be referenced before assignment
        _update_audit(region_id, application_id, tracking_id, transaction_id,
                      transaction_type, resource_id, user_id, external_id,
                      event_details, status)
        logger.debug(
            "Create Resource Requested to ORD: region=%s resource_id=%s status=%s" % (
                region_id, resource_id, status))
