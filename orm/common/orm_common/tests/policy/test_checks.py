import unittest

import mock
from orm_common.policy import _checks
from wsme.exc import ClientSideError


class TestChecks(unittest.TestCase):
    def test_call_simple_checks(self):
        check = _checks.FalseCheck()
        self.assertFalse(check(1, 2, 3))
        check = _checks.TrueCheck()
        self.assertTrue(check(1, 2, 3))

        check = _checks.GenericCheck('a', 'b')
        self.assertFalse(check(1, 2, 3))

    def test_str_simple_checks(self):
        check = _checks.FalseCheck()
        self.assertEqual(str(check), '!')
        check = _checks.TrueCheck()
        self.assertEqual(str(check), '@')

        check = _checks.GenericCheck('a', 'b')
        self.assertEqual(str(check), 'a:b')

    def test_call_complex_checks(self):
        first_rule = _checks.TrueCheck()
        second_rule = _checks.FalseCheck()

        check = _checks.NotCheck(first_rule)
        self.assertFalse(check(1, 2, 3))

        check = _checks.AndCheck([first_rule])
        check.add_check(second_rule)
        self.assertFalse(check(1, 2, 3))
        check = _checks.AndCheck([first_rule, first_rule])
        self.assertTrue(check(1, 2, 3))

        check = _checks.OrCheck([first_rule])
        check.add_check(second_rule)
        self.assertTrue(check(1, 2, 3))
        self.assertEqual(check.pop_check(), (check, second_rule,))
        check = _checks.OrCheck([second_rule, second_rule])
        self.assertFalse(check(1, 2, 3))

    def test_str_complex_checks(self):
        first_rule = _checks.TrueCheck()
        second_rule = _checks.FalseCheck()

        check = _checks.NotCheck(first_rule)
        self.assertEqual(str(check), 'not @')

        check = _checks.AndCheck([first_rule])
        check.add_check(second_rule)
        self.assertEqual(str(check), '(@ and !)')

        check = _checks.OrCheck([first_rule])
        check.add_check(second_rule)
        self.assertEqual(str(check), '(@ or !)')

    def test_call_custom_checks_error(self):
        check = _checks.RoleCheck('a', 'admin')
        try:
            check(1, mock.MagicMock(), 3)
            self.fail('ClientSideError not raised!')
        except ClientSideError as exc:
            self.assertEqual(exc.code, 403)

        for check_type in (_checks.TenantCheck,
                           _checks.DomainCheck):
            check = check_type('a', 'admin')
            # 2 is not a user, so the check will fail
            self.assertFalse(check(1, 2, 3))

    def test_call_custom_checks_success(self):
        user = mock.MagicMock()
        user.user = {'roles': [{'name': 'admin'}]}
        user.tenant = {'name': 'admin'}
        user.domain = {'name': 'admin'}

        for check_type in (_checks.RoleCheck,
                           _checks.TenantCheck,
                           _checks.DomainCheck):
            check = check_type('a', 'admin')
            # 2 is not a user, so the check will fail
            self.assertTrue(check(1, user, 3))

    def test_call_rule_check_error(self):
        enforcer = mock.MagicMock()
        enforcer.rules = {'test': mock.MagicMock(
            side_effect=KeyError('test'))}
        check = _checks.RuleCheck('rule', 'test')
        self.assertFalse(check(1, 2, enforcer))

    def test_call_rule_check_success(self):
        enforcer = mock.MagicMock()
        enforcer.rules = {'test': mock.MagicMock(return_value=True)}
        check = _checks.RuleCheck('rule', 'test')
        self.assertTrue(check(1, 2, enforcer))
