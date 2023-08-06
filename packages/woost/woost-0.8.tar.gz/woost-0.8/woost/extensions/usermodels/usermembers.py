#-*- coding: utf-8 -*-
u"""Provides persistent models that describe schema types.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from weakref import WeakKeyDictionary
from warnings import warn
from cocktail.events import event_handler
from cocktail.pkgutils import import_module, import_object
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import Item


class UserMember(Item):

    class __metaclass__(Item.__metaclass__):
        def __init__(cls, name, bases, members):
            Item.__metaclass__.__init__(cls, name, bases, members)
            
            # Automatically create polymorphic members
            if cls.member_class is not schema.Member \
            and not issubclass(
                cls.member_class,
                (schema.RelationMember, schema.Schema)
            ):
                # Make sure the strings for the extension have been loaded
                from woost.extensions.usermodels import strings

                # Default
                if not cls.get_member("member_default"):
                    cls.add_member(cls.create_member_default_member())
                    translations.copy_key(
                        "UserMember.member_default",
                        name + ".member_default",
                        overwrite = False
                    )
                    
                # Enumeration
                if not cls.get_member("member_enumeration"):
                    cls.add_member(cls.create_member_enumeration_member())
                    translations.copy_key(
                        "UserMember.member_enumeration",
                        name + ".member_enumeration",
                        overwrite = False
                    )

    instantiable = False
    visible_from_root = False
    member_class = schema.Member
    member_property_prefix = "member_"
    edit_controls = None
    search_controls = None
    edit_node_class = \
        "woost.extensions.usermodels.usermembereditnode.UserMemberEditNode"
    edit_form = "woost.extensions.usermodels.UserMemberForm"

    groups_order = [
        "description",
        "definition",
        "constraints",
        "behavior"
    ] + (Item.groups_order or [])

    members_order = [
        "label",
        "explanation",
        "member_name",
        "member_translated",
        "member_versioned",
        "member_descriptive",
        "member_indexed",
        "member_unique",
        "member_required",
        "member_member_group",
        "member_listed_by_default",
        "member_editable",
        "member_edit_control",
        "member_searchable",
        "member_search_control",
        "initialization"
    ]

    label = schema.String(
        required = True,
        translated = True,
        descriptive = True,
        member_group = "description"
    )

    explanation = schema.String(
        translated = True,
        edit_control = "woost.views.RichTextEditor",
        listed_by_default = False,
        member_group = "description"
    )

    parent_schema = schema.Reference(
        type = "woost.extensions.usermodels.usermembers.UserModel",
        bidirectional = True,
        visible = False
    )

    parent_collection = schema.Reference(
        type = "woost.extensions.usermodels.usermembers.UserCollection",
        bidirectional = True,
        visible = False
    )

    member_name = schema.String(
        required = True,
        format = r"^[a-zA-Z][a-zA-Z0-9_]*$",
        listed_by_default = False,
        text_search = False,
        member_group = "definition"
    )

    member_translated = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )

    member_versioned = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "definition"
    )
    
    member_descriptive = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )

    member_indexed = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )

    initialization = schema.CodeBlock(
        language = "python",
        member_group = "code"
    )

    member_unique = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "constraints"
    )

    member_required = schema.Boolean(
        default = False,
        required = True,
        listed_by_default = False,
        member_group = "constraints"
    )

    member_member_group = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "behavior"
    )

    member_listed_by_default = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )

    member_editable = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )

    member_edit_control = schema.String(
        listed_by_default = False,
        member_group = "behavior",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            translations(
                "woost.extensions.usermodels.auto-control",
                language
            )
            if not value else translations(value)
    )

    member_searchable = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )

    member_search_control = schema.String(
        listed_by_default = False,
        member_group = "behavior",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            translations(
                "woost.extensions.usermodels.auto-control",
                language
            )
            if not value else translations(value)
    )
    
    @classmethod
    def create_member_default_member(cls):
        return cls.member_class("member_default",
            member_group = "definition",
        )
    
    @classmethod
    def create_member_enumeration_member(cls):
        return schema.Collection("member_enumeration",
            required = False,
            items = cls.member_class(required = True),
            member_group = "constraints",
            edit_control = "cocktail.html.TextArea"
        )

    def update_member_definition(self):
        """Creates or updates the schema member described by the item."""
        return self.produce_member(self.get_produced_member())

    def produce_member(self, member = None):
        
        # Instantiate a new member
        if member is None:
            member = self.member_class()

        # Define translations
        if self.parent_schema:
            trans_key = self.parent_schema.member_name + "." + self.member_name
            translations.clear_key(trans_key)
            for lang in self.translations:
                translations[lang][trans_key] = self.get("label", lang)
                explanation = self.get("explanation", lang)
                if explanation:
                    translations[lang][trans_key + "-explanation"] = \
                        explanation

        # Copy meta-properties, but remove the element from its schema first,
        # to allow it to be renamed
        try:
            parent_schema = member.schema
            if parent_schema:
                prev_schema_order = parent_schema.members_order
                parent_schema.remove_member(member)
            for key in self.__class__.members():
                if key.startswith(self.member_property_prefix):
                    property_name = key[len(self.member_property_prefix):]
                    property_value = self.get(key)
                    setattr(member, property_name, property_value)
        finally:
            if parent_schema:
                parent_schema.add_member(member)
                parent_schema.members_order = prev_schema_order 

        # Apply user defined logic to the member
        if self.initialization:
            exec self.initialization in {
                "member": member,
                "user_member": self
            }

        return member

    def get_produced_member(self):
        """Returns a reference to the member produced and registered into the
        application by an earlier call to `produce_member`.
        """
        if self.parent_schema is not None:
            parent_member = self.parent_schema.get_produced_member()
            if parent_member:
                return parent_member.get_member(self.member_name)

        elif self.parent_collection is not None:
            parent_member = self.parent_collection.get_produced_member()
            if parent_member:
                return parent_member.items

    def remove_produced_member(self):
        """Removes the member produced and registered by an earlier call to
        `produce_member`.
        """
        member = self.get_produced_member()
        
        if member is None:
            return

        if self.parent_schema:
            parent_schema = self.parent_schema.get_produced_member()
            if parent_schema is not None:
                parent_schema.remove_member(self)
        elif self.parent_collection:
            parent_collection = self.parent_collection.get_produced_member()
            if parent_collection:
                parent_collection.items = None
       
    _v_after_commit_actions = None

    def _after_commit(self, action, *args):

        if self._v_after_commit_actions is None:
            self._v_after_commit_actions = WeakKeyDictionary()

        trans = datastore.connection.transaction_manager.get()
        transaction_actions = self._v_after_commit_actions.get(trans)

        if transaction_actions is None:
            self._v_after_commit_actions[trans] = transaction_actions = set()

        if action not in transaction_actions:
            transaction_actions.add(action)
            def commit_hook(successful, *args):
                if successful:
                    try:
                        action(*args)
                    except Exception, ex:
                        warn(str(ex))
            trans.addAfterCommitHook(commit_hook, args)

    @event_handler
    def handle_changed(cls, e):
        user_member = e.source
        if user_member.is_inserted and user_member.parent_schema:
            user_member._after_commit(user_member.update_member_definition)

    @event_handler
    def handle_deleting(cls, e):
        user_member = e.source
        user_member._after_commit(user_member.remove_produced_member)


class UserBoolean(UserMember):

    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Boolean
    edit_controls = [
        "cocktail.html.CheckBox",
        "cocktail.html.RadioSelector"
    ]
    search_controls = [
        "cocktail.html.CheckBox",
        "cocktail.html.RadioSelector"
    ]
    default_member_required = True
    default_member_default = False


class UserInteger(UserMember):
     
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Integer

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )
    
    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserDecimal(UserMember):

    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Decimal

    member_min = schema.Decimal(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Decimal(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserFloat(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Float

    member_min = schema.Float(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Float(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserFraction(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Fraction

    member_min = schema.Fraction(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Fraction(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserString(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.String
    edit_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.PasswordBox",
        "cocktail.html.TextArea",
        "woost.views.RichTextEditor"
    ]
    search_controls = [
        "cocktail.html.TextBox"
    ]

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )

    member_format = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "constraints"
    )

    member_text_search = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )
    
    member_normalized_index = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "definition"
    )


class UserDate(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Date
    edit_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]
    search_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserTime(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Time
    edit_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]
    search_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserDateTime(UserMember):
    
    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.DateTime
    edit_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]
    search_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.DatePicker"
    ]

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserRelation(UserMember):

    instantiable = False
    groups_order = UserMember.groups_order
    member_class = schema.RelationMember

    member_related_key = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "definition"        
    )

    member_bidirectional = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )
    
    member_integral = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )

    member_cascade_delete = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "definition"
    )

    member_text_search = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )


class UserReference(UserRelation):

    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Reference
    edit_controls = [
        "cocktail.html.DropdownSelector",
        "cocktail.html.RadioSelector",
        "woost.views.ItemSelector"
    ]
    search_controls = [
        "cocktail.html.DropdownSelector",
        "cocktail.html.RadioSelector",
        "woost.views.ItemSelector"
    ]

    member_type = schema.Reference(
        class_family = Item,
        member_group = "definition"
    )

    member_class_family = schema.Reference(
        class_family = Item,
        member_group = "definition"
    )

    member_type.exclusive = member_class_family.not_()
    member_class_family = member_type.not_()
    
    member_cycles_allowed = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "definition"
    )


class UserCollection(UserRelation):

    instantiable = True
    groups_order = UserMember.groups_order
    member_class = schema.Collection
    edit_controls = [
        "cocktail.html.TextArea",
        "cocktail.html.CheckList",
        "cocktail.html.MultipleChoiceSelector"
    ]
    search_controls = [
        "cocktail.html.DropdownSelector",
        "cocktail.html.RadioSelector",
        "woost.views.ItemSelector",
        "cocktail.html.CheckList",
        "cocktail.html.MultipleChoiceSelector"
    ]

    member_items = schema.Reference(
        type = UserMember,
        required = True,
        bidirectional = True,
        related_key = "parent_collection",
        integral = True,
        member_group = "constraints"
    )

    member_min = schema.Integer(
        listed_by_default = False,
        member_group = "constraints"
    )

    member_max = schema.Integer(
        min = member_min,
        listed_by_default = False,
        member_group = "constraints"
    )


class UserModel(UserMember):

    def __init__(self, *args, **kwargs):
        UserMember.__init__(self, *args, **kwargs)

    instantiable = True
    groups_order = UserMember.groups_order
    visible_from_root = True
    member_class = schema.Schema
    
    edit_node_class = \
        "woost.extensions.usermodels.usermodeleditnode.UserModelEditNode"

    default_member_indexed = True

    plural_label = schema.String(
        required = True,
        translated = True,
        listed_by_default = False,
        member_group = "description"
    )

    package_name = schema.String(
        required = True,
        default = "woost.models",
        format = r"[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*",
        listed_by_default = False,
        text_search = False,
        member_group = "definition"
    )

    base_model = schema.Reference(
        required = True,
        class_family = Item,
        default = Item,
        member_group = "definition"
    )

    child_members = schema.Collection(
        items = schema.Reference(
            type = UserMember,
            related_end = schema.Reference(),
            bidirectional = True,
            integral = True
        ),
        bidirectional = True,
        related_key = "parent_schema",
        integral = True,
        listed_by_default = False,
        member_group = "definition"
    )

    member_instantiable = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )

    member_visible_from_root = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "behavior"
    )

    def produce_member(self, member = None):
 
        # Models aren't created like other regular members
        if member is None:
            member = self.base_model.__metaclass__(
                str(self.member_name),
                (self.base_model,),
                {"full_name": self.package_name + "." + self.member_name}
            )

        # Make the model available at the module level, so that its
        # instances can be pickled
        module = import_module(self.package_name)
        setattr(
            module,
            self.member_name,
            member
        )
        member.__module__ = self.package_name

        # Define translations
        translations.clear_key(self.member_name)

        for lang in self.translations:
            translations[lang][self.member_name] = self.get("label", lang)
            translations[lang][self.member_name + "-plural"] = \
                self.get("plural_label", lang)

            explanation = self.get("explanation", lang)
            if explanation:
                translations[lang][self.member_name + "-explanation"] = \
                    explanation

        member.members_order = []

        # Add or update child members
        for child_user_member in self.child_members:
            member.members_order.append(child_user_member.member_name)
            
            # Look for an existing version of the child member
            child_member = member.get_member(child_user_member.member_name)

            if child_member:
                
                # Temporarily remove the child from the schema, in case it
                # needs to be renamed (a member name can't be changed while the
                # member is bound to a schema)
                member.remove_member(child_member)

                # Also, if the member's type has changed, discard it
                if not isinstance(
                    child_member,
                    child_user_member.member_class
                ):
                    child_member = None

            child_member = child_user_member.produce_member(child_member)
            member.add_member(child_member)

        return UserMember.produce_member(self, member)

    def get_produced_member(self):
        
        full_name = self.package_name + "." + self.member_name

        for cls in Item.schema_tree():
            if cls.full_name == full_name:
                return cls

    def remove_produced_member(self):
        model = self.get_produced_member()
        if model is not None:
            model.select().delete_items()
            datastore.commit()
            self.base_model.remove_derived_schema(model)

    @event_handler
    def handle_changed(cls, e):
        user_member = e.source
        user_member._after_commit(user_member.update_member_definition)

