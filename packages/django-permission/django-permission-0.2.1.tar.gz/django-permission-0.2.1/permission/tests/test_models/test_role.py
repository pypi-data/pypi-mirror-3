# vim: set fileencoding=utf-8 :
"""
Unittest module of ...


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
License:
    The MIT License (MIT)

    Copyright (c) 2012 Alisue allright reserved.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.

"""
from __future__ import with_statement
from django.test import TestCase

from permission.models import Role
from permission.tests.utils import create_user
from permission.tests.utils import create_role
from permission.tests.utils import create_permission


class PermissionRoleManagerTestCase(TestCase):

    def test_filter_by_user(self):
        # role1           -- user1, user2
        #   +- role2      -- user3
        #   +- role3      -- user4, user5
        #   |    +- role4 -- user6
        #   |    +- role5 -- user7
        #   +- role6      -- user8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)

        self.assertItemsEqual(Role.objects.filter_by_user(user1), [
                role1, role2, role3, role4, role5, role6
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user2), [
                role1, role2, role3, role4, role5, role6
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user3), [
                role2,
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user4), [
                role3, role4, role5,
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user5), [
                role3, role4, role5,
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user6), [
                role4,
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user7), [
                role5,
            ])
        self.assertItemsEqual(Role.objects.filter_by_user(user8), [
                role6,
            ])

    def test_get_all_permissions_of_user(self):
        # role1           -- user1, user2 -- perm1, perm2
        #   +- role2      -- user3        -- perm3
        #   +- role3      -- user4, user5 -- perm4, perm5
        #   |    +- role4 -- user6        -- perm6
        #   |    +- role5 -- user7        -- perm7
        #   +- role6      -- user8        -- perm8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        perm1 = create_permission('permission_test_perm1')
        perm2 = create_permission('permission_test_perm2')
        perm3 = create_permission('permission_test_perm3')
        perm4 = create_permission('permission_test_perm4')
        perm5 = create_permission('permission_test_perm5')
        perm6 = create_permission('permission_test_perm6')
        perm7 = create_permission('permission_test_perm7')
        perm8 = create_permission('permission_test_perm8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)
        role1._permissions.add(perm1, perm2)
        role2._permissions.add(perm3)
        role3._permissions.add(perm4, perm5)
        role4._permissions.add(perm6)
        role5._permissions.add(perm7)
        role6._permissions.add(perm8)

        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user1), [
                perm1, perm2, perm3, perm4,
                perm5, perm6, perm7, perm8,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user2), [
                perm1, perm2, perm3, perm4,
                perm5, perm6, perm7, perm8,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user3), [
                perm3,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user4), [
                perm4, perm5, perm6, perm7,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user5), [
                perm4, perm5, perm6, perm7,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user6), [
                perm6,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user7), [
                perm7,
            ])
        self.assertItemsEqual(Role.objects.get_all_permissions_of_user(user8), [
                perm8,
            ])



class PermissionRoleModelTestCase(TestCase):

    def testcreate(self):
        role = create_role('permission_test_role1')
        self.assertItemsEqual(role.name, 'permission_test_role1')
        self.assertItemsEqual(role.codename, 'permission_test_role1')
        self.assertItemsEqual(role.description, 'permission_test_role1')

        return role

    def test__get_all_users(self):
        # role1           -- user1, user2
        #   +- role2      -- user3
        #   +- role3      -- user4, user5
        #   |    +- role4 -- user6
        #   |    +- role5 -- user7
        #   +- role6      -- user8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)

        self.assertItemsEqual(role1.users, [
                user1, user2, user3, user4,
                user5, user6, user7, user8,
            ])
        self.assertItemsEqual(role2.users, [
                user3,
            ])
        self.assertItemsEqual(role3.users, [
                user4, user5, user6, user7,
            ])
        self.assertItemsEqual(role4.users, [
                user6,
            ])
        self.assertItemsEqual(role5.users, [
                user7,
            ])
        self.assertItemsEqual(role6.users, [
                user8,
            ])

    def test__get_all_permissions(self):
        # role1           -- perm1, perm2
        #   +- role2      -- perm3
        #   +- role3      -- perm4, perm5
        #   |    +- role4 -- perm6
        #   |    +- role5 -- perm7
        #   +- role6      -- perm8
        perm1 = create_permission('permission_test_perm1')
        perm2 = create_permission('permission_test_perm2')
        perm3 = create_permission('permission_test_perm3')
        perm4 = create_permission('permission_test_perm4')
        perm5 = create_permission('permission_test_perm5')
        perm6 = create_permission('permission_test_perm6')
        perm7 = create_permission('permission_test_perm7')
        perm8 = create_permission('permission_test_perm8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._permissions.add(perm1, perm2)
        role2._permissions.add(perm3)
        role3._permissions.add(perm4, perm5)
        role4._permissions.add(perm6)
        role5._permissions.add(perm7)
        role6._permissions.add(perm8)

        self.assertItemsEqual(role1.permissions, [
                perm1, perm2, perm3, perm4,
                perm5, perm6, perm7, perm8
            ])
        self.assertItemsEqual(role2.permissions, [
                perm3,
            ])
        self.assertItemsEqual(role3.permissions, [
                perm4, perm5, perm6, perm7
            ])
        self.assertItemsEqual(role4.permissions, [
                perm6,
            ])
        self.assertItemsEqual(role5.permissions, [
                perm7,
            ])
        self.assertItemsEqual(role6.permissions, [
                perm8,
            ])

    def test_is_belong(self):
        # role1           -- user1, user2
        #   +- role2      -- user3
        #   +- role3      -- user4, user5
        #   |    +- role4 -- user6
        #   |    +- role5 -- user7
        #   +- role6      -- user8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)

        self.assertTrue(role1.is_belong(user1))
        self.assertTrue(role1.is_belong(user2))
        self.assertTrue(role1.is_belong(user3))
        self.assertTrue(role1.is_belong(user4))
        self.assertTrue(role1.is_belong(user5))
        self.assertTrue(role1.is_belong(user6))
        self.assertTrue(role1.is_belong(user7))
        self.assertTrue(role1.is_belong(user8))

        self.assertFalse(role2.is_belong(user1))
        self.assertFalse(role2.is_belong(user2))
        self.assertTrue(role2.is_belong(user3))
        self.assertFalse(role2.is_belong(user4))
        self.assertFalse(role2.is_belong(user5))
        self.assertFalse(role2.is_belong(user6))
        self.assertFalse(role2.is_belong(user7))
        self.assertFalse(role2.is_belong(user8))

        self.assertFalse(role3.is_belong(user1))
        self.assertFalse(role3.is_belong(user2))
        self.assertFalse(role3.is_belong(user3))
        self.assertTrue(role3.is_belong(user4))
        self.assertTrue(role3.is_belong(user5))
        self.assertTrue(role3.is_belong(user6))
        self.assertTrue(role3.is_belong(user7))
        self.assertFalse(role3.is_belong(user8))

    def test_add_users(self):
        # role1           -- user1, user2
        #   +- role2      -- user3
        #   +- role3      -- user4, user5
        #   |    +- role4 -- user6
        #   |    +- role5 -- user7
        #   +- role6      -- user8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)

        # actually role1 doesn't have user3
        self.assertFalse(role1._users.filter(pk=user3.pk).exists())
        # but user3 is in the subroles of role1 thus add_users doesn't add
        role1.add_users(user3)
        self.assertFalse(role1._users.filter(pk=user3.pk).exists())

        # role2 doesn't have user2
        self.assertFalse(role2._users.filter(pk=user2.pk).exists())
        # and no subroles have user2 thus add_users add user2 to role2
        role2.add_users(user2)
        self.assertTrue(role2._users.filter(pk=user2.pk).exists())

    def test_remove_users(self):
        # role1           -- user1, user2
        #   +- role2      -- user3
        #   +- role3      -- user4, user5
        #   |    +- role4 -- user6
        #   |    +- role5 -- user7
        #   +- role6      -- user8
        user1 = create_user('permission_test_user1')
        user2 = create_user('permission_test_user2')
        user3 = create_user('permission_test_user3')
        user4 = create_user('permission_test_user4')
        user5 = create_user('permission_test_user5')
        user6 = create_user('permission_test_user6')
        user7 = create_user('permission_test_user7')
        user8 = create_user('permission_test_user8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._users.add(user1, user2)
        role2._users.add(user3)
        role3._users.add(user4, user5)
        role4._users.add(user6)
        role5._users.add(user7)
        role6._users.add(user8)

        # actually role1 doesn't have user3
        self.assertFalse(role1._users.filter(pk=user3.pk).exists())
        # thus remove_user doesn't remove even user3 is in subroles
        role1.remove_users(user3)
        self.assertFalse(role1._users.filter(pk=user3.pk).exists())
        self.assertTrue(role1.users.filter(pk=user3.pk).exists())

        # role2 have user3
        self.assertTrue(role2._users.filter(pk=user3.pk).exists())
        # thus remove_user remove user3
        role2.remove_users(user3)
        self.assertFalse(role2._users.filter(pk=user3.pk).exists())
        self.assertFalse(role2.users.filter(pk=user3.pk).exists())
        self.assertFalse(role1.users.filter(pk=user3.pk).exists())

    def test_add_permissions(self):
        # role1           -- perm1, perm2
        #   +- role2      -- perm3
        #   +- role3      -- perm4, perm5
        #   |    +- role4 -- perm6
        #   |    +- role5 -- perm7
        #   +- role6      -- perm8
        perm1 = create_permission('permission_test_perm1')
        perm2 = create_permission('permission_test_perm2')
        perm3 = create_permission('permission_test_perm3')
        perm4 = create_permission('permission_test_perm4')
        perm5 = create_permission('permission_test_perm5')
        perm6 = create_permission('permission_test_perm6')
        perm7 = create_permission('permission_test_perm7')
        perm8 = create_permission('permission_test_perm8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._permissions.add(perm1, perm2)
        role2._permissions.add(perm3)
        role3._permissions.add(perm4, perm5)
        role4._permissions.add(perm6)
        role5._permissions.add(perm7)
        role6._permissions.add(perm8)

        # actually role1 doesn't have perm3
        self.assertFalse(role1._permissions.filter(pk=perm3.pk).exists())
        # but perm3 is in the subroles of role1 thus add_permissions doesn't add
        role1.add_permissions(perm3)
        self.assertFalse(role1._permissions.filter(pk=perm3.pk).exists())

        # role2 doesn't have perm2
        self.assertFalse(role2._permissions.filter(pk=perm2.pk).exists())
        # and no subroles have perm2 thus add_perms add perm2 to role2
        role2.add_permissions(perm2)
        self.assertTrue(role2._permissions.filter(pk=perm2.pk).exists())

    def test_remove_permissions(self):
        # role1           -- perm1, perm2
        #   +- role2      -- perm3
        #   +- role3      -- perm4, perm5
        #   |    +- role4 -- perm6
        #   |    +- role5 -- perm7
        #   +- role6      -- perm8
        perm1 = create_permission('permission_test_perm1')
        perm2 = create_permission('permission_test_perm2')
        perm3 = create_permission('permission_test_perm3')
        perm4 = create_permission('permission_test_perm4')
        perm5 = create_permission('permission_test_perm5')
        perm6 = create_permission('permission_test_perm6')
        perm7 = create_permission('permission_test_perm7')
        perm8 = create_permission('permission_test_perm8')
        role1 = create_role('permission_test_role1')
        role2 = create_role('permission_test_role2', role1)
        role3 = create_role('permission_test_role3', role1)
        role4 = create_role('permission_test_role4', role3)
        role5 = create_role('permission_test_role5', role3)
        role6 = create_role('permission_test_role6', role1)
        role1._permissions.add(perm1, perm2)
        role2._permissions.add(perm3)
        role3._permissions.add(perm4, perm5)
        role4._permissions.add(perm6)
        role5._permissions.add(perm7)
        role6._permissions.add(perm8)

        # actually role1 doesn't have perm3
        self.assertFalse(role1._permissions.filter(pk=perm3.pk).exists())
        # thus remove_perm doesn't remove even perm3 is in subroles
        role1.remove_permissions(perm3)
        self.assertFalse(role1._permissions.filter(pk=perm3.pk).exists())
        self.assertTrue(role1.permissions.filter(pk=perm3.pk).exists())

        # role2 have perm3
        self.assertTrue(role2._permissions.filter(pk=perm3.pk).exists())
        # thus remove_perm remove perm3
        role2.remove_permissions(perm3)
        self.assertFalse(role2._permissions.filter(pk=perm3.pk).exists())
        self.assertFalse(role2.permissions.filter(pk=perm3.pk).exists())
        self.assertFalse(role1.permissions.filter(pk=perm3.pk).exists())

