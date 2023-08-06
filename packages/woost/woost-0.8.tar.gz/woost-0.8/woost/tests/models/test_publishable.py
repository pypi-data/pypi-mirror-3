#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
from __future__ import with_statement
from cocktail.translations import set_language
from woost.tests.models.basetestcase import BaseTestCase


class IsAccessibleExpressionTestCase(BaseTestCase):

    def setUp(self):
        from woost.models import User
        BaseTestCase.setUp(self)
        set_language("en")
        self.user = User()
        self.user.insert()

    def list_accessible_items(self):
        from woost.models import Publishable, IsAccessibleExpression
        return list(Publishable.select(IsAccessibleExpression(self.user)))

    def test_enabled(self):
        
        from woost.models import Publishable, ReadPermission
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                }
            )
        )

        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = False
        b.insert()

        c = Publishable()
        c.enabled = True
        c.insert()

        d = Publishable()
        d.enabled = False
        d.insert()
        
        assert self.list_accessible_items() == [a, c]

    def test_current(self):

        from woost.models import Publishable, ReadPermission
        from datetime import datetime, timedelta
        
        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable"
                }
            )
        )

        now = datetime.now()
        
        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = True
        b.start_date = now
        b.end_date = now + timedelta(days = 1)
        b.insert()

        c = Publishable()
        c.enabled = True
        c.start_date = now + timedelta(days = 1)
        c.insert()

        d = Publishable()
        d.enabled = True
        d.end_date = now - timedelta(days = 1)
        d.insert()

        assert self.list_accessible_items() == [a, b]

    def test_allowed(self):
        
        from woost.models import Publishable, ReadPermission

        a = Publishable()
        a.enabled = True
        a.insert()

        b = Publishable()
        b.enabled = True
        b.insert()

        self.everybody_role.permissions.append(
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable",
                    "filter": "member-id",
                    "filter_operator0": "ne",
                    "filter_value0": str(b.id)
                }
            )
        )
        
        assert self.list_accessible_items() == [a]

