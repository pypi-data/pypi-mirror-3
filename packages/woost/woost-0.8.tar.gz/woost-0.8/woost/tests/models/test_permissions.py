#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from woost.tests.models.basetestcase import BaseTestCase
from nose.tools import assert_raises


class PermissionTestCase(BaseTestCase):

    def assert_authorized(self, user, permission_type, **context):
        assert user.has_permission(permission_type, **context)
        user.require_permission(permission_type, **context)

    def assert_not_authorized(self, user, permission_type, **context):
        from woost.models import AuthorizationError
        assert not user.has_permission(permission_type, **context)
        assert_raises(
            AuthorizationError,
            user.require_permission,
            permission_type,
            **context
        )

    def test_permission_acquisition(self):

        from woost.models import (
            User,
            Role,
            ReadPermission
        )
        
        R = lambda **kwargs: Role(permissions = [ReadPermission()], **kwargs)        
        r1 = R()
        r2 = R()
        r3 = R()
        r4 = R(base_roles = [r3])
        r5 = R(base_roles = [r2, r4])

        self.everybody_role.permissions.append(ReadPermission())
        self.authenticated_role.permissions.append(ReadPermission())

        user = User()
        user.roles = [r1, r5]

        print list(user.iter_permissions())

        assert list(user.iter_permissions()) == [
            r1.permissions[0],
            r5.permissions[0],
            r2.permissions[0],
            r4.permissions[0],
            r3.permissions[0],
            self.authenticated_role.permissions[0],
            self.everybody_role.permissions[0]
        ]

    def test_content_permissions(self):

        from woost.models import (
            Item,
            Publishable,
            User,
            Role,
            Permission,
            CreatePermission,
            ReadPermission,
            ModifyPermission,
            DeletePermission
        )

        class TestPermission(Permission):
            pass

        item = Item()
        doc = Publishable()

        for permission_type in [
            CreatePermission,
            ReadPermission,
            ModifyPermission,
            DeletePermission
        ]:            
            role = Role()
            user = User(roles = [role])

            # Permission denied (no permissions defined)
            self.assert_not_authorized(user, permission_type, target = doc)

            # Permission granted
            role.permissions.append(
                permission_type(
                    matching_items = {
                        "type": "woost.models.publishable.Publishable"
                    },
                    authorized = True
                )
            )
            
            self.assert_authorized(user, permission_type, target = doc)

            # Permission denied (wrong target)
            self.assert_not_authorized(user, permission_type, target = item)

            # Permission denied (wrong permission type)
            self.assert_not_authorized(user, TestPermission)
            
            # Permission denied (prevailing negative permission)
            role.permissions.insert(
                0,
                permission_type(
                    matching_items = {
                        "type": "woost.models.item.Item"
                    },
                    authorized = False
                )
            )

            self.assert_not_authorized(user, permission_type, target = doc)

    def test_member_permissions(self):

        from woost.models import (
            Item,
            Publishable,
            User,
            Role,
            Permission,
            ReadMemberPermission,
            ModifyMemberPermission
        )

        class TestPermission(Permission):
            pass

        prefix = "woost.models.publishable.Publishable."
        m1 = Publishable.resource_type
        m2 = Publishable.parent
        m3 = Publishable.controller

        for permission_type in [ReadMemberPermission, ModifyMemberPermission]:
            
            role = Role()
            user = User(roles = [role])

            # No permissions by default
            self.assert_not_authorized(user, permission_type, member = m1)
            self.assert_not_authorized(user, permission_type, member = m2)
            self.assert_not_authorized(user, permission_type, member = m3)

            # Positive permission
            role.permissions.append(
                permission_type(
                    matching_members = [
                        prefix + m1.name,
                        prefix + m2.name
                    ],
                    authorized = True
                )
            )
            
            self.assert_authorized(user, permission_type, member = m1)
            self.assert_authorized(user, permission_type, member = m2)
            self.assert_not_authorized(user, permission_type, member = m3)

            # Permission denied (wrong permission type)
            self.assert_not_authorized(user, TestPermission)
            
            # Negative permission
            role.permissions.insert(
                0,
                permission_type(
                    matching_members = [prefix + m1.name],
                    authorized = False
                )
            )

            self.assert_not_authorized(user, permission_type, member = m1)
            self.assert_authorized(user, permission_type, member = m2)
            self.assert_not_authorized(user, permission_type, member = m3)

    def test_translation_permissions(self):

        from woost.models import (
            Item,
            Publishable,
            User,
            Role,
            Permission,
            CreateTranslationPermission,
            ReadTranslationPermission,
            ModifyTranslationPermission,
            DeleteTranslationPermission
        )

        class TestPermission(Permission):
            pass

        l1 = "en"
        l2 = "fr"
        l3 = "ru"

        for permission_type in [
            CreateTranslationPermission,
            ReadTranslationPermission,
            ModifyTranslationPermission,
            DeleteTranslationPermission
        ]:            
            role = Role()
            user = User(roles = [role])

            # No permissions by default
            self.assert_not_authorized(user, permission_type, language = l1)
            self.assert_not_authorized(user, permission_type, language = l2)
            self.assert_not_authorized(user, permission_type, language = l3)

            # Permission granted
            role.permissions.append(
                permission_type(
                    matching_languages = [l1, l2],
                    authorized = True
                )
            )
            
            self.assert_authorized(user, permission_type, language = l1)
            self.assert_authorized(user, permission_type, language = l2)
            self.assert_not_authorized(user, permission_type, language = l3)

            # Permission denied (wrong permission type)
            self.assert_not_authorized(user, TestPermission)
            
            # Negative permission
            role.permissions.insert(
                0,
                permission_type(
                    matching_languages = [l1],
                    authorized = False
                )
            )

            self.assert_not_authorized(user, permission_type, language = l1)
            self.assert_authorized(user, permission_type, language = l2)
            self.assert_not_authorized(user, permission_type, language = l3)

    def test_permission_expression(self):

        from woost.models import (
            Item,
            Publishable,
            User,
            ReadPermission,
            PermissionExpression
        )
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                },
                authorized = True
            )
        )

        i1 = Item()
        i2 = Item()
        d1 = Publishable()
        d2 = Publishable()
        
        i1.insert()
        i2.insert()
        d1.insert()
        d2.insert()

        results = set(Item.select(filters = [
            PermissionExpression(User(), ReadPermission)
        ]))

        assert results == set([d1, d2])

