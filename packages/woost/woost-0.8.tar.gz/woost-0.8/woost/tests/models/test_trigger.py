#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from woost.tests.models.basetestcase import BaseTestCase


class TriggerMatchTestCase(BaseTestCase):

    def assert_match(self, trigger, *tests):
        test = 1
        for target, user, context, should_match in tests:
            self.assertEqual(
                trigger.match(user, target = target, verbose = True, **context),
                should_match,
                "Trigger %s %s match test %d (target=%s user=%s context=%s)"
                % (
                    trigger,
                    "should" if should_match else "should not",
                    test,
                    target,
                    user,
                    context
                )
            )
            test += 1

    def test_user(self):

        from woost.models import ContentTrigger, Item, Role, User
        
        r1 = Role()
        r2 = Role()
        r3 = Role(base_roles = [r2])

        u1 = User(roles = [r1])
        u2 = User(roles = [r2])
        u3 = User(roles = [r3])
        
        self.assert_match(
            ContentTrigger(matching_roles = [r2]),
            (Item(), u2, {}, True),
            (Item(), u3, {}, True),
            (Item(), None, {}, False),
            (Item(), u1, {}, False)
        )

    def test_target(self):

        from woost.models import (
            ContentTrigger,
            Item,
            Publishable,
            StandardPage,
            User,
            set_current_user
        )
                
        self.assert_match(
            ContentTrigger(matching_items = {
                "type": "woost.models.publishable.Publishable"
            }),
            (Publishable(), None, {}, True),
            (StandardPage(), None, {}, True),
            (Item(), None, {}, False),
            (ContentTrigger(), None, {}, False)
        )

        user = User()
        set_current_user(user)

        self.assert_match(
            ContentTrigger(matching_items = {
                "type": "woost.models.publishable.Publishable",
                "filter": "owned-items"
            }),
            (Publishable(), user, {}, False),
            (Publishable(owner = user), user, {}, True)
        )

    def test_modified_member(self):

        from woost.models import ModifyTrigger, Item, Document

        self.assert_match(
            ModifyTrigger(matching_members = [
                "woost.models.item.Item.owner",
                "woost.models.document.Document.title"
            ]),               
            (Item(), None, {"member": Item.owner}, True),
            (Item(), None, {"member": Item.draft_source}, False),
            (Document(), None, {"member": Document.title}, True),
            (Document(), None, {"member": Document.hidden}, False)
        )

    def test_language(self):

        from woost.models import ModifyTrigger, Item

        self.assert_match(
            ModifyTrigger(matching_languages = ["en", "fr"]),
            (Item(), None, {"language": "en"}, True),
            (Item(), None, {"language": "fr"}, True),
            (Item(), None, {"language": None}, False),
            (Item(), None, {"language": "ru"}, False)
        )


class TriggerInvocationTestCase(BaseTestCase):

    def setUp(self):

        from cocktail.persistence import datastore
        from woost.models import (
            triggerresponse,
            TriggerResponse,
            User,
            set_current_user
        )

        BaseTestCase.setUp(self)
        
        class TestTriggerResponse(TriggerResponse):

            def __init__(self, response_log, *args, **kwargs):
                TriggerResponse.__init__(self, *args, **kwargs)
                self.response_log = response_log

            def execute(self, items, user, batch = False, **context):
                self.response_log.append({
                    "trigger": self.trigger,
                    "items": items,
                    "user": user,
                    "batch": batch,
                    "context": context
                })

        self.TestTriggerResponse = TestTriggerResponse

        # ZODB requires classes to be accessible, so TestTriggerResponse is
        # added to the same module of its base class:
        triggerresponse.TestTriggerResponse = TestTriggerResponse
        TestTriggerResponse.__module__ = TriggerResponse.__module__

        self.user = User()
        set_current_user(self.user)

        datastore.commit()

    def make_trigger(self, trigger_type, response_log = None, **kwargs):
        
        from cocktail.persistence import datastore
        from woost.models.trigger import set_triggers_enabled

        if response_log is None:
            new_response_log = True
            response_log = []
        else:
            new_response_log = False

        set_triggers_enabled(False)

        try:
            trigger = trigger_type(**kwargs)
            trigger.responses = [self.TestTriggerResponse(response_log)]
            trigger.insert()
            self.site.triggers.append(trigger)
            datastore.commit()
            if new_response_log:
                return trigger, response_log
            else:
                return trigger
        finally:
            set_triggers_enabled(True)


class BeforeTestCase(TriggerInvocationTestCase):

    def test_before_create(self):

        from woost.models import CreateTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            CreateTrigger,
            execution_point = "before",
            batch_execution = False
        )

        qname = "item1"
        item1 = Item(qname = qname)
        assert len(response_log) == 1

        id = 234
        item2 = Item(id = id)
        assert len(response_log) == 2

        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item1]
        assert response["user"] is self.user
        assert not response["batch"]
        assert response["context"]["values"]["qname"] == qname

        response = response_log[1]
        assert response["trigger"] is trigger
        assert response["items"] == [item2]
        assert response["user"] is self.user
        assert not response["batch"]
        assert response["context"]["values"]["id"] == id

    def test_before_insert(self):
        
        from woost.models import InsertTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            InsertTrigger,
            execution_point = "before",
            batch_execution = False
        )

        # Create two items. This should trigger the response twice.
        item1 = Item()
        item1.insert()
        assert len(response_log) == 1

        item2 = Item()
        item2.insert()
        assert len(response_log) == 2

        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item1]
        assert response["user"] is self.user
        assert not response["batch"]

        response = response_log[1]
        assert response["trigger"] is trigger
        assert response["items"] == [item2]
        assert response["user"] is self.user
        assert not response["batch"]

    def test_before_modify(self):

        from woost.models import ModifyTrigger, Item, User

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            ModifyTrigger,
            execution_point = "before",
            batch_execution = False
        )

        # Create an item and initialize it. This shouldn't trigger any
        # response, since modifications happen before the item is inserted.
        item = Item()
        item.qname = "foo"
        item.insert()
        assert not response_log
        
        # Modify the inserted item two times. This should trigger the response
        # twice.
        item.qname = "bar"
        assert len(response_log) == 1

        item.owner = User()
        assert len(response_log) == 2

        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item]
        assert response["context"]["member"] is Item.qname
        assert response["user"] is self.user
        assert not response["batch"]

        response = response_log[1]
        assert response["trigger"] is trigger
        assert response["items"] == [item]
        assert response["context"]["member"] is Item.owner
        assert response["user"] is self.user
        assert not response["batch"]

    def test_before_delete(self):
         
        from woost.models import DeleteTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            DeleteTrigger,
            execution_point = "before",
            batch_execution = False
        )

        # Create and insert two items
        item1 = Item()
        item1.insert()
        
        item2 = Item()
        item2.insert()        
        
        # Delete the items. This should trigger the response twice.
        item1.delete()
        assert len(response_log) == 1

        item2.delete()
        assert len(response_log) == 2
         
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item1]
        assert response["user"] is self.user
        assert not response["batch"]

        response = response_log[1]
        assert response["trigger"] is trigger
        assert response["items"] == [item2]
        assert response["user"] is self.user
        assert not response["batch"]

    def test_before_create_insert_modify_delete(self):

        from woost.models import (
            Item,
            CreateTrigger,
            InsertTrigger,
            ModifyTrigger,
            DeleteTrigger
        )

        response_log = []

        create_trigger = self.make_trigger(
            CreateTrigger,
            response_log,            
            execution_point = "before",
            batch_execution = False
        )

        insert_trigger = self.make_trigger(
            InsertTrigger,
            response_log,            
            execution_point = "before",
            batch_execution = False
        )

        modify_trigger = self.make_trigger(
            ModifyTrigger,
            response_log,            
            execution_point = "before",
            batch_execution = False
        )

        delete_trigger = self.make_trigger(
            DeleteTrigger,
            response_log,            
            execution_point = "before",
            batch_execution = False
        )

        # Create and insert an item
        item = Item(qname = "foo")
        item.insert()

        assert len(response_log) == 2
        response = response_log.pop()
        assert response["trigger"] is insert_trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]

        response = response_log.pop()
        assert response["trigger"] is create_trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert response["context"]["values"]["qname"] == "foo"
        assert not response["batch"]

        # Modify the item
        item.qname = "bar"

        assert len(response_log) == 1
        response = response_log.pop()
        assert response["trigger"] is modify_trigger
        assert response["items"] == [item]
        assert response["context"]["member"] is Item.qname
        assert response["user"] is self.user
        assert not response["batch"]

        # Delete the item
        item.delete()

        assert len(response_log) == 1
        response = response_log.pop()
        assert response["trigger"] is delete_trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]


class AfterTestCase(TriggerInvocationTestCase):

    def test_after_insert(self):
        
        from cocktail.persistence import datastore
        from woost.models import InsertTrigger, Item
                
        # Declare the trigger
        trigger, response_log = self.make_trigger(
            InsertTrigger,
            execution_point = "after",
            batch_execution = False
        )

        # Insert a new item, but abort the transaction
        # (the trigger shouldn't be called)
        item = Item()
        item.insert()
        assert not response_log
        datastore.abort()
        assert not response_log

        # Insert a new item, and commit the transaction
        # (the trigger should be executed)
        item = Item()
        item.insert()
        datastore.commit()

        assert len(response_log) == 1
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]

    def test_after_modify(self):
        
        from cocktail.persistence import datastore
        from woost.models import ModifyTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            ModifyTrigger,
            execution_point = "after",
            batch_execution = False
        )

        # Create an item and initialize it. This shouldn't trigger any
        # response, since modifications happen before the item is inserted.
        item = Item()
        item.qname = "foo"
        item.insert()
        datastore.commit()
        assert not response_log
        
        # Modify the inserted item, but abort the transaction. Again, this
        # shouldn't trigger any response.
        item.qname = "bar"
        datastore.abort()
        assert not response_log

        # Modify the inserted item and commit the transaction. This should
        # trigger the response.
        item.qname = "spam"
        datastore.commit()

        assert len(response_log) == 1
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item]
        assert response["context"]["member"] is Item.qname
        assert response["user"] is self.user
        assert not response["batch"]

    def test_after_delete(self):
        
        from cocktail.persistence import datastore
        from woost.models import DeleteTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            DeleteTrigger,
            execution_point = "after",
            batch_execution = False
        )

        # Create and insert an item
        item = Item()
        item.insert()
        datastore.commit()
        
        # Delete the item, but abort the transaction. This shouldn't trigger
        # the response.
        item.delete()
        datastore.abort()
        assert not response_log

        # Delete the inserted item and commit the transaction. This should
        # trigger the response.
        item.delete()
        datastore.commit()

        assert len(response_log) == 1
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]

    def test_after_insert_modify_delete(self):

        from cocktail.persistence import datastore
        from woost.models import (
            Item,
            User,
            InsertTrigger,
            ModifyTrigger,
            DeleteTrigger
        )

        response_log = []

        insert_trigger = self.make_trigger(
            InsertTrigger,
            response_log,            
            execution_point = "after",
            batch_execution = False
        )

        modify_trigger = self.make_trigger(
            ModifyTrigger,
            response_log,            
            execution_point = "after",
            batch_execution = False
        )

        delete_trigger = self.make_trigger(
            DeleteTrigger,
            response_log,            
            execution_point = "after",
            batch_execution = False
        )

        # Create and insert an item
        item = Item()
        item.qname = "foo"
        item.insert()

        # Modify it
        item.qname = "bar"
        item.owner = User()

        # Delete it
        item.delete()

        # Commit the transaction; this should execute all the scheduled
        # responses
        datastore.commit()
        assert len(response_log) == 4

        response = response_log.pop(0)
        assert response["trigger"] is insert_trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]

        for member in (Item.qname, Item.owner):
            response = response_log.pop(0)
            assert response["trigger"] is modify_trigger
            assert response["items"] == [item]
            assert response["context"]["member"] is member
            assert response["user"] is self.user
            assert not response["batch"]

        response = response_log[0]
        assert response["trigger"] is delete_trigger
        assert response["items"] == [item]
        assert response["user"] is self.user
        assert not response["batch"]


class BatchTestCase(TriggerInvocationTestCase):

    def test_after_insert_batched(self):

        from cocktail.persistence import datastore
        from woost.models import InsertTrigger, Item
                
        # Declare the trigger
        trigger, response_log = self.make_trigger(
            InsertTrigger,
            execution_point = "after",
            batch_execution = True
        )

        # Insert new items, but abort the transaction
        # (the trigger shouldn't be called)
        item1 = Item()
        item1.insert()
        assert not response_log
        
        item2 = Item()
        item2.insert()
        assert not response_log

        datastore.abort()
        assert not response_log

        # Create and insert two items, and commit the transaction. The response
        # should be triggered just once.
        item1 = Item()
        item1.insert()        
        item2 = Item()
        item2.insert()
        datastore.commit()

        assert len(response_log) == 1

        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == set([item1, item2])
        assert response["user"] is self.user
        assert response["batch"]

    def test_after_modify_batched(self):

        from cocktail.persistence import datastore
        from woost.models import ModifyTrigger, Item, User

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            ModifyTrigger,
            execution_point = "after",
            batch_execution = True
        )

        # Create two items and initialize them. This shouldn't trigger any
        # response, since modifications happen before items are inserted.
        item1 = Item()
        item1.qname = "foo"
        item1.insert()
        item2 = Item()
        item2.owner = User()
        item2.insert()
        datastore.commit()
        assert not response_log
        
        # Modify the inserted items, but abort the transaction. Again, this
        # shouldn't trigger any response.
        item1.qname = "bar"
        item2.owner = User()
        datastore.abort()
        assert not response_log

        # Modify the inserted items and commit the transaction. This should
        # trigger the response just once.
        item1.qname = "spam"
        item2.owner = User()
        datastore.commit()

        assert len(response_log) == 1
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == set([item1, item2])
        assert response["context"]["modified_members"] == {
            item1: set([(Item.qname, None)]),
            item2: set([(Item.owner, None)])
        }
        assert response["user"] is self.user
        assert response["batch"]

    def test_after_delete_batched(self):

        from cocktail.persistence import datastore
        from woost.models import DeleteTrigger, Item

        # Declare the trigger
        trigger, response_log = self.make_trigger(
            DeleteTrigger,
            execution_point = "after",
            batch_execution = True
        )

        # Create and insert two items
        item1 = Item()
        item1.insert()
        item2 = Item()
        item2.insert()
        datastore.commit()
        
        # Delete the items, but abort the transaction. This shouldn't trigger
        # the response.
        item1.delete()
        item2.delete()
        datastore.abort()
        assert not response_log

        # Delete the inserted items and commit the transaction. This should
        # trigger the response just once.
        item1.delete()
        item2.delete()
        datastore.commit()

        assert len(response_log) == 1
        response = response_log[0]
        assert response["trigger"] is trigger
        assert response["items"] == set([item1, item2])
        assert response["user"] is self.user
        assert response["batch"]

    def test_modify_batched_order(self):

        from cocktail.persistence import datastore
        from woost.models import ModifyTrigger, Item, User

        trigger, response_log = self.make_trigger(
            ModifyTrigger,
            execution_point = "after",
            batch_execution = True,
            matching_members = ["woost.models.item.Item.owner"]
        )

        # Modifying a member that is not covered by the trigger should alter
        # the context passed to responses, even if it is modified before the
        # member that actions the response
        item = Item()
        item.insert()
        item.qname = "foo"
        item.owner = User()
        datastore.commit()

        response = response_log[0]
        assert response["context"]["modified_members"] == {
            item: set([(Item.qname, None), (Item.owner, None)])
        }

