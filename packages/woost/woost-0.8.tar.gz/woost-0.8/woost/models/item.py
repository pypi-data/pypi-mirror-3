#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from datetime import datetime
from cocktail.modeling import getter, ListWrapper, SetWrapper
from cocktail.events import event_handler, Event
from cocktail import schema
from cocktail.translations import translations
from cocktail.persistence import (
    datastore, 
    PersistentObject, 
    PersistentClass, 
    PersistentMapping,
    MaxValue
)
from woost.models.changesets import ChangeSet, Change
from woost.models.action import Action

# Extension property that allows changing the controller that handles a
# collection in the backoffice
schema.Collection.edit_controller = \
    "woost.controllers.backoffice.collectioncontroller." \
    "CollectionController"

# Extension property that makes it easier to customize the edit view for a
# collection in the backoffice
schema.Collection.edit_view = None

# Extension property that sets the default type that should be shown by default
# when opening an item selector for the indicated property
schema.RelationMember.selector_default_type = None

# Extension property that allows to indicate that specific members don't modify
# the 'last_update_time' member of items when changed
schema.Member.affects_last_update_time = True


class Item(PersistentObject):
    """Base class for all CMS items. Provides basic functionality such as
    authorship, group membership, draft copies and versioning.
    """
    members_order = [
        "id",
        "qname",
        "author",
        "owner"
    ]

    # Enable full text indexing for all items (although the Item class itself
    # doesn't provide any searchable text field by default, its subclasses may,
    # or it may be extended; by enabling full text indexing at the root class,
    # heterogeneous queries on the whole Item class will use available 
    # indexes).
    full_text_indexed = True

    # Extension property that indicates if content types should be visible from
    # the backoffice root view
    visible_from_root = True

    # Extension property that indicates if the backoffice should show child
    # entries for this content type in the type selector
    collapsed_backoffice_menu = False

    def __translate__(self, language, **kwargs):
        if self.draft_source is not None:
            return translations(
                "woost.models.Item draft copy",
                language,
                item = self.draft_source,
                draft_id = self._draft_id,
                **kwargs
            )
        else:
            return PersistentObject.__translate__(self, language, **kwargs)

    # Unique qualified name
    #--------------------------------------------------------------------------
    qname = schema.String(
        unique = True,
        indexed = True,
        text_search = False,
        listed_by_default = False,
        member_group = "administration"
    )

    # Backoffice customization
    #--------------------------------------------------------------------------
    show_detail_view = "woost.views.BackOfficeShowDetailView"
    show_detail_controller = \
        "woost.controllers.backoffice.showdetailcontroller." \
        "ShowDetailController"
    collection_view = "woost.views.BackOfficeCollectionView"
    edit_node_class = "woost.controllers.backoffice.editstack.EditNode"
    edit_view = "woost.views.BackOfficeFieldsView"
    edit_form = "woost.views.ContentForm"
    edit_controller = \
        "woost.controllers.backoffice.itemfieldscontroller." \
        "ItemFieldsController"

    __deleted = False

    @getter
    def is_deleted(self):
        return self.__deleted

    # Indexing
    #--------------------------------------------------------------------------
 
    # Make sure draft copies' members don't get indexed
    def _should_index_member(self, member):
        return PersistentObject._should_index_member(self, member) and (
            member.primary or self.draft_source is None
        )

    def _should_index_member_full_text(self, member):
        return PersistentObject._should_index_member_full_text(self, member) \
            and self.draft_source is None

     # When validating unique members, ignore conflicts with the draft source
    def _counts_as_duplicate(self, other):
        return PersistentObject._counts_as_duplicate(self, other) \
            and other is not self.draft_source \
            and self is not other.draft_source

    # Last change timestamp
    #--------------------------------------------------------------------------
    @classmethod
    def get_last_instance_change(cls):
        max_value = datastore.root.get(cls.full_name + ".last_instance_change")
        return None if max_value is None else max_value.value

    @classmethod
    def set_last_instance_change(cls, last_change):
        for cls in cls.__mro__:
            if hasattr(cls, "set_last_instance_change"):
                key = cls.full_name + ".last_instance_change"
                max_value = datastore.root.get(key)
                if max_value is None:
                    datastore.root[key] = max_value = MaxValue(last_change)
                else:
                    max_value.value = last_change

    # Versioning
    #--------------------------------------------------------------------------
    versioned = True

    changes = schema.Collection(
        required = True,
        versioned = False,
        editable = False,
        items = "woost.models.Change",
        bidirectional = True,
        visible = False
    )

    creation_time = schema.DateTime(
        versioned = False,
        editable = False,
        member_group = "administration",
        indexed = True
    )

    last_update_time = schema.DateTime(
        indexed = True,
        versioned = False,
        editable = False,
        member_group = "administration"
    )

    is_draft = schema.Boolean(
        required = True,
        default = False,
        indexed = True,
        listed_by_default = False,
        editable = False,
        versioned = False,
        member_group = "administration"
    )

    draft_source = schema.Reference(
        type = "woost.models.Item",
        related_key = "drafts",
        bidirectional = True,
        editable = False,
        listed_by_default = False,
        indexed = True,
        versioned = False,
        member_group = "administration"
    )

    drafts = schema.Collection(
        items = "woost.models.Item",
        related_key = "draft_source",
        bidirectional = True,
        cascade_delete = True,
        editable = False,
        versioned = False,
        searchable = False,
        member_group = "administration"
    )

    _draft_count = 0
    _draft_id = None

    @getter
    def draft_id(self):
        """A numerical identifier for draft copies, guaranteed to be unique
        among their source item.
        @type: int
        """
        return self._draft_id

    def make_draft(self):
        """Creates a new draft copy of the item. Subclasses can tweak the copy
        process by overriding either this method or L{get_draft_adapter} (for
        example, to exclude one or more members).

        @return: The draft copy of the item.
        @rtype: L{Item}
        """
        draft = self.__class__(bidirectional = False)
        draft.bidirectional = True
        draft.draft_source = self
        draft.is_draft = True
        draft.bidirectional = False
        
        self._draft_count += 1
        draft._draft_id = self._draft_count

        adapter = self.get_draft_adapter()
        adapter.export_object(
            self,
            draft,
            source_schema = self.__class__,
            source_accessor = schema.SchemaObjectAccessor,
            target_accessor = schema.SchemaObjectAccessor
        )
        
        return draft

    draft_confirmation = Event(doc = """
        An event triggered just before a draft is confirmed.
        """)

    def confirm_draft(self):
        """Confirms a draft. On draft copies, this applies all the changes made
        by the draft to its source element, and deletes the draft. On brand new
        drafts, the item itself simply drops its draft status, and otherwise
        remains the same.
        
        @raise ValueError: Raised if the item is not a draft.
        """            
        if not self.is_draft:
            raise ValueError("confirm_draft() must be called on a draft")

        self.draft_confirmation()

        if self.draft_source is None:
            self.bidirectional = True
            self.is_draft = False
        else:
            adapter = self.get_draft_adapter()
            adapter.source_accessor = schema.SchemaObjectAccessor
            adapter.target_accessor = schema.SchemaObjectAccessor
            adapter.import_object(
                self,
                self.draft_source,
                source_schema = self.__class__
            )
            self.delete()

    @classmethod
    def get_draft_adapter(cls):
        """Produces an adapter that defines the copy process used by the
        L{make_draft} method in order to produce draft copies of the item.

        @return: An adapter with all the rules required to obtain a draft copy
            of the item.
        @rtype: L{Adapter<cocktail.schema.adapter.Adapter>}
        """
        adapter = schema.Adapter()
        adapter.collection_copy_mode = schema.shallow
        adapter.exclude([
            member.name
            for member in cls.members().itervalues()
            if cls._should_exclude_in_draft(member)
        ] + ["owner"])
        return adapter

    @classmethod
    def _should_exclude_in_draft(cls, member):
        return not member.editable or not member.visible

    @classmethod
    def _create_translation_schema(cls, members):
        members["versioned"] = False
        PersistentObject._create_translation_schema.im_func(cls, members)
        
    @classmethod
    def _add_member(cls, member):
        if member.name == "translations":
            member.editable = False
            member.searchable = False
        PersistentClass._add_member(cls, member)

    def _get_revision_state(self):
        """Produces a dictionary with the values for the item's versioned
        members. The value of translated members is represented using a
        (language, translated value) mapping.

        @return: The item's current state.
        @rtype: dict
        """

        # Store the item state for the revision
        state = PersistentMapping()

        for key, member in self.__class__.members().iteritems():
           
            if not member.versioned:
                continue

            if member.translated:
                value = dict(
                    (language, translation.get(key))
                    for language, translation in self.translations.iteritems()
                )
            else:
                value = self.get(key)
                
                # Make a copy of mutable objects
                if isinstance(
                    value, (list, set, ListWrapper, SetWrapper)
                ):
                    value = list(value)

            state[key] = value

        return state

    # Item insertion overriden to make it versioning aware
    @event_handler
    def handle_inserting(cls, event):

        item = event.source
        now = datetime.now()
        item.creation_time = now
        item.last_update_time = now
        item.set_last_instance_change(now)
        item.__deleted = False

        if not item.is_draft and item.__class__.versioned:
            changeset = ChangeSet.current

            if changeset:
                change = Change()
                change.action = Action.get_instance(identifier = "create")
                change.target = item
                change.changed_members = set(
                    member.name
                    for member in item.__class__.members().itervalues()
                    if member.versioned
                )
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                changeset.changes[item.id] = change
                
                if item.author is None:
                    item.author = changeset.author

                if item.owner is None:
                    item.owner = changeset.author
                
                change.insert(event.inserted_objects)
        
    # Extend item modification to make it versioning aware
    @event_handler
    def handle_changed(cls, event):

        item = event.source
        now = None

        if item.is_inserted:
            now = datetime.now()
            item.set_last_instance_change(now)

        if getattr(item, "_v_initializing", False) \
        or not event.member.versioned \
        or not item.is_inserted \
        or item.is_draft \
        or not item.__class__.versioned:
            return
        
        changeset = ChangeSet.current

        if changeset:

            member_name = event.member.name
            language = event.language
            change = changeset.changes.get(item.id)

            if change is None:
                action_type = "modify"
                change = Change()
                change.action = Action.get_instance(identifier = action_type)
                change.target = item
                change.changed_members = set()
                change.item_state = item._get_revision_state()
                change.changeset = changeset
                changeset.changes[item.id] = change
                if event.member.affects_last_update_time:
                    item.last_update_time = now or datetime.now()
                change.insert()
            else:
                action_type = change.action.identifier

            if action_type == "modify":
                change.changed_members.add(member_name)
                
            if action_type in ("create", "modify"):
                value = event.value

                # Make a copy of mutable objects
                if isinstance(
                    value, (list, set, ListWrapper, SetWrapper)
                ):
                    value = list(value)

                if language:
                    change.item_state[member_name][language] = value
                else:
                    change.item_state[member_name] = value
        elif event.member.affects_last_update_time:
            item.last_update_time = datetime.now()

    @event_handler
    def handle_deleting(cls, event):
        
        item = event.source

        # Update the last time of modification for the item
        now = datetime.now()
        item.set_last_instance_change(now)
        item.last_update_time = now

        if not item.is_draft and item.__class__.versioned:
            changeset = ChangeSet.current

            # Add a revision for the delete operation
            if changeset:
                change = changeset.changes.get(item.id)

                if change and change.action.identifier != "delete":
                    del changeset.changes[item.id]

                if change is None \
                or change.action.identifier not in ("create", "delete"):
                    change = Change()
                    change.action = Action.get_instance(identifier = "delete")
                    change.target = item
                    change.changeset = changeset
                    changeset.changes[item.id] = change
                    change.insert()

        item.__deleted = True
    
    @event_handler
    def handle_deleted(cls, event):
        
        item = event.source

        # Break the relation to the draft's source. This needs to be done
        # explicitly, because drafts are flagged as non bidirectional (to keep
        # their changes in isolation), which prevents automatic management of
        # referential integrity
        if item.draft_source is not None:
            item.draft_source.drafts.remove(item)

    _preserved_members = frozenset([changes])

    def _should_cascade_delete(self, member):
        return member.cascade_delete and not self.is_draft

    def _should_erase_member(self, member):
        return PersistentObject._should_erase_member(self, member) \
            and member not in self._preserved_members \
            and member is not self.__class__.draft_source

    # Ownership and authorship
    #--------------------------------------------------------------------------
    author = schema.Reference(
        indexed = True,
        editable = False,
        type = "woost.models.User",
        listed_by_default = False,
        member_group = "administration"
    )
    
    owner = schema.Reference(
        indexed = True,
        type = "woost.models.User",
        listed_by_default = False,
        member_group = "administration"
    )


Item.id.versioned = False
Item.id.editable = False
Item.id.listed_by_default = False
Item.id.member_group = "administration"
Item.changes.visible = False

