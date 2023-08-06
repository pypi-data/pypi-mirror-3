#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from woost.tests.models.basetestcase import BaseTestCase


class ChangeSetTests(BaseTestCase):

    def test_insert(self):

        from datetime import datetime
        from woost.models import (
            Document, User, ChangeSet, changeset_context
        )

        author = User()
        author.insert()

        with changeset_context(author) as changeset:
            item = Document()
            item.set("title", u"Foo!", "en")
            item.resource_type = u"text/foo"
            item.hidden = True
            assert not changeset.changes
            item.insert()
        
        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)
        
        assert changeset.changes.keys() == [item.id]
        change = changeset.changes[item.id]
        assert change.target is item
        assert change.action is self.create_action
        assert change.changeset is changeset
        assert item.changes == [change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        assert change.item_state["title"] == {"en": u"Foo!"}
        assert change.item_state["resource_type"] == u"text/foo"
        assert change.item_state["hidden"] == True
        assert change.item_state["translation_enabled"] == \
            {"en": item.get("translation_enabled", "en")}

        assert item.author is author
        assert item.owner is author
        assert item.creation_time
        assert item.last_update_time
        assert item.creation_time == item.last_update_time

    def test_delete(self):

        from datetime import datetime
        from woost.models import (
            Item, User, ChangeSet, changeset_context
        )

        author = User()
        author.insert()
        
        item = Item()
        item.insert()

        with changeset_context(author) as changeset:
            item.owner = None
            item.delete()
        
        assert list(ChangeSet.select()) == [changeset]
        assert changeset.author is author
        assert isinstance(changeset.date, datetime)
        
        assert changeset.changes.keys() == [item.id]
        change = changeset.changes[item.id]
        assert change.target is item
        assert change.action is self.delete_action
        assert change.changeset is changeset
        assert item.changes == [change]

        assert not item.id in Item.index

    def test_modify(self):

        from time import sleep
        from datetime import datetime
        from woost.models import (
            Document, User, ChangeSet, changeset_context
        )

        author = User()
        author.insert()

        with changeset_context(author) as creation:
            item = Document()
            item.set("title", u"Foo!", "en")
            item.resource_type = u"text/foo"
            item.hidden = True
            item.insert()
        
        # Make sure creation_time and last_update_time don't match
        sleep(0.1)

        with changeset_context(author) as modification:
            item.set("title", u"Bar!", "en")
            item.resource_type = u"text/bar"
            item.hidden = True

        assert list(ChangeSet.select()) == [creation, modification]
        assert modification.author is author
        assert isinstance(modification.date, datetime)
        
        assert modification.changes.keys() == [item.id]
        change = modification.changes[item.id]
        assert change.target is item
        assert change.action is self.modify_action
        assert change.changeset is modification
        assert change.changed_members == set(["title", "resource_type"])
        assert item.changes == [creation.changes[item.id], change]

        for key in "id", "changes", "creation_time", "last_update_time":
            assert not key in change.item_state

        assert change.item_state["title"] == {"en": u"Bar!"}
        assert change.item_state["resource_type"] == u"text/bar"
        assert change.item_state["hidden"] == True
        assert change.item_state["translation_enabled"] == \
            {"en": item.get("translation_enabled", "en")}

        assert item.author is author
        assert item.owner is author
        assert item.creation_time
        assert item.last_update_time
        assert not item.creation_time == item.last_update_time

