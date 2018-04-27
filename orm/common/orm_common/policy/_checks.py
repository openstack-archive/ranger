# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import logging

import six

from orm.common.orm_common.utils import api_error_utils as err_utils
from orm.common.orm_common.utils import dictator


logger = logging.getLogger(__name__)

registered_checks = {}


@six.add_metaclass(abc.ABCMeta)
class BaseCheck(object):
    """Abstract base class for Check classes."""

    @abc.abstractmethod
    def __str__(self):
        """String representation of the Check tree rooted at this node."""

        pass

    @abc.abstractmethod
    def __call__(self, target, cred, enforcer):
        """Triggers if instance of the class is called.

        Performs the check. Returns False to reject the access or a
        true value (not necessary True) to accept the access.
        """

        pass


class FalseCheck(BaseCheck):
    """A policy check that always returns ``False`` (disallow)."""

    def __str__(self):
        """Return a string representation of this check."""

        return '!'

    def __call__(self, target, cred, enforcer):
        """Check the policy."""

        logger.debug('False check, never passing')
        return False


class TrueCheck(BaseCheck):
    """A policy check that always returns ``True`` (allow)."""

    def __str__(self):
        """Return a string representation of this check."""

        return '@'

    def __call__(self, target, cred, enforcer):
        """Check the policy."""

        logger.debug('True check, always passing')
        return True


class Check(BaseCheck):
    def __init__(self, kind, match):
        self.kind = kind
        self.match = match

    def __str__(self):
        """Return a string representation of this check."""

        return '%s:%s' % (self.kind, self.match)


class NotCheck(BaseCheck):
    def __init__(self, rule):
        self.rule = rule

    def __str__(self):
        """Return a string representation of this check."""

        return 'not %s' % self.rule

    def __call__(self, target, cred, enforcer):
        """Check the policy.

        Returns the logical inverse of the wrapped check.
        """

        return not self.rule(target, cred, enforcer)


class AndCheck(BaseCheck):
    def __init__(self, rules):
        self.rules = rules

    def __str__(self):
        """Return a string representation of this check."""

        return '(%s)' % ' and '.join(str(r) for r in self.rules)

    def __call__(self, target, cred, enforcer):
        """Check the policy.

        Requires that all rules accept in order to return True.
        """

        for rule in self.rules:
            if not rule(target, cred, enforcer):
                return False

        return True

    def add_check(self, rule):
        """Adds rule to be tested.

        Allows addition of another rule to the list of rules that will
        be tested.

        :returns: self
        :rtype: :class:`.AndCheck`
        """

        self.rules.append(rule)
        return self


class OrCheck(BaseCheck):
    def __init__(self, rules):
        self.rules = rules

    def __str__(self):
        """Return a string representation of this check."""

        return '(%s)' % ' or '.join(str(r) for r in self.rules)

    def __call__(self, target, cred, enforcer):
        """Check the policy.

        Requires that at least one rule accept in order to return True.
        """

        for rule in self.rules:
            if rule(target, cred, enforcer):
                return True
        return False

    def add_check(self, rule):
        """Adds rule to be tested.

        Allows addition of another rule to the list of rules that will
        be tested.  Returns the OrCheck object for convenience.
        """

        self.rules.append(rule)
        return self

    def pop_check(self):
        """Pops the last check from the list and returns them

        :returns: self, the popped check
        :rtype: :class:`.OrCheck`, class:`.Check`
        """

        check = self.rules.pop()
        return self, check


def register(name, func=None):
    # Perform the actual decoration by registering the function or
    # class.  Returns the function or class for compliance with the
    # decorator interface.
    def decorator(func):
        registered_checks[name] = func
        return func

    # If the function or class is given, do the registration
    if func:
        return decorator(func)

    return decorator


@register('rule')
class RuleCheck(Check):
    def __call__(self, target, creds, enforcer):
        try:
            return enforcer.rules[self.match](target, creds, enforcer)
        except KeyError:
            # We don't have any matching rule; fail closed
            return False


@register('role')
class RoleCheck(Check):
    """Check that there is a matching role in the ``user`` object."""

    def __call__(self, target, user, enforcer):
        logger.debug('Checking against policy role:{}'.format(self.match))

        result = any(
            [role['name'] == self.match for role in user.user['roles']])
        logger.debug('Role check result: {}'.format(result))
        if not result:
            logger.info(
                'INFO|CON{}AUTH001|Not allowed to perform this operation,'
                ' user:{} does not have role:{}'.format(
                    dictator.get('service_name', 'ORM'),
                    user.user['name'], self.match))

        return result


@register('user')
class UserCheck(Check):
    """Check that the user matches."""

    def __call__(self, target, user, enforcer):
        try:
            logger.debug('Checking user:{}'.format(self.match))
            result = user.user['name'] == self.match
            logger.debug('User check result: {}'.format(result))
            if not result:
                logger.info(
                    'INFO|CON{}AUTH002|Not allowed to perform this operation,'
                    ' user:{} is not the user:{}'.format(
                        dictator.get('service_name', 'ORM'),
                        user.user['name'], self.match))
                raise err_utils.get_error('N/A', status_code=403)
            return result
        except Exception:
            logger.debug('Invalid user, failing user check')
            raise


@register('tenant')
class TenantCheck(Check):
    """Check that the user's tenant matches."""

    def __call__(self, target, user, enforcer):
        try:
            logger.debug('Checking tenant:{}'.format(self.match))
            result = user.tenant['name'] == self.match
            logger.debug('Tenant check result: {}'.format(result))
            if not result:
                logger.info(
                    'INFO|CON{}AUTH003|Not allowed to perform this operation,'
                    ' user:{} is not in tenant:{}'.format(
                        dictator.get('service_name', 'ORM'),
                        user.user['name'], self.match))
            return result
        except Exception:
            logger.debug('Invalid user, failing tenant check')
            return False


@register('domain')
class DomainCheck(Check):
    """Check that the user's domain matches."""

    def __call__(self, target, user, enforcer):
        try:
            logger.debug('Checking domain:{}'.format(self.match))
            result = user.domain['name'] == self.match
            logger.debug('Domain check result: {}'.format(result))
            return result
        except Exception:
            logger.debug('Invalid user, failing domain check')
            return False


@register(None)
class GenericCheck(Check):
    """Check an individual match.

    Matches look like:

        - tenant:%(tenant_id)s
        - role:compute:admin
        - True:%(user.enabled)s
        - 'Member':%(role.name)s
    """

    def __call__(self, target, creds, enforcer):
        # We do not want anything besides role, tenant and domain
        logger.debug('Received an unknown check!')
        return False
