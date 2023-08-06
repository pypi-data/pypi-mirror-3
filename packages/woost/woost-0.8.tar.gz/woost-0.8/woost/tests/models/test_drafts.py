#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from woost.tests.models.basetestcase import BaseTestCase


class DraftTestCase(BaseTestCase):

    def test_indexing_enabled_for_new_drafts(self):

        from cocktail import schema
        from woost.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        foo = Foo()
        foo.is_draft = True
        foo.spam = 4
        foo.insert()
        assert set(Foo.spam.index.items()) == set([(4, foo.id)])

    def test_indexing_disabled_for_draft_copies(self):
        
        from cocktail import schema
        from woost.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        source = Foo()
        source.spam = 4
        source.insert()
        assert set(Foo.spam.index.items()) == set([(4, source.id)])

        foo = Foo()
        foo.draft_source = source
        foo.spam = 3
        foo.insert()

        assert set(Foo.spam.index.items()) == set([(4, source.id)])
        
        foo.spam = 2
        assert set(Foo.spam.index.items()) == set([(4, source.id)])

    def test_versioning_disabled_for_drafts(self):

        from woost.models import Document, changeset_context

        with changeset_context() as insertion_cs:
            doc = Document()
            doc.is_draft = True
            doc.insert()
        
        assert not insertion_cs.changes

        with changeset_context() as modification_cs:
            doc.set("title", "Hello, world!", "en")
        
        assert not modification_cs.changes

        with changeset_context() as deletion_cs:
            doc.delete()
        
        assert not deletion_cs.changes

    def test_copy_draft(self):

        from woost.models import Document

        # Create a source item
        doc = Document()
        doc.set("title", "Test item", "en") 
        doc.insert()

        # Create a draft for the item
        draft = doc.make_draft()
        draft.insert()
        assert draft.is_draft
        assert draft.draft_source is doc
        assert draft in doc.drafts
        assert not doc.id == draft.id
        assert doc.get("title", "en") == draft.get("title", "en")
 
        # Modify the draft
        draft.set("title", "Modified test item", "en")
        assert not doc.get("title", "en") == draft.get("title", "en")
        draft.confirm_draft()
        
        # Confirm it
        assert draft.id not in Document.index
        assert not draft in doc.drafts
        assert doc.get("title", "en") == "Modified test item"

    def test_unique_validation_enabled_for_new_drafts(self):

        from cocktail import schema
        from cocktail.persistence.persistentobject import UniqueValueError
        from woost.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        source = Foo()
        source.spam = 4
        source.insert()

        foo = Foo()
        foo.is_draft = True
        foo.spam = 4

        assert len([error 
            for error in Foo.get_errors(foo) 
            if isinstance(error, UniqueValueError)
            and error.member is Foo.spam
        ]) == 1

    def test_unique_validation_disabled_for_draft_copies(self):
        
        from cocktail import schema
        from cocktail.persistence.persistentobject import UniqueValueError
        from woost.models import Item

        class Foo(Item):
            spam = schema.Integer(indexed = True, unique = True)
 
        source = Foo()
        source.spam = 4
        source.insert()

        foo = source.make_draft()

        assert len([error 
            for error in Foo.get_errors(foo) 
            if isinstance(error, UniqueValueError)
            and error.member is Foo.spam
        ]) == 0

    def test_no_bidirectionality_in_default_references_for_draft_copies(self):

        from cocktail import schema        
        from woost.models import Item

        class Foo(Item):
            pass

        Foo.add_member(
            schema.Reference("parent",
                type = Foo,
                bidirectional = True
            )
        )

        Foo.add_member(
            schema.Collection("children",
                items = schema.Reference(type = Foo),
                bidirectional = True
            )
        )
        
        x = Foo()
        Foo.default_parent = x
        y = Foo()
        y2 = y.make_draft()
        assert y2 not in x.children

