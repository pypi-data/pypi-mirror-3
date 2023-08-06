#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
from warnings import warn
from traceback import print_exc, format_exc
from threading import local
from weakref import WeakKeyDictionary
from cocktail import schema
from cocktail.translations import translations
from cocktail.events import when
from cocktail.persistence import datastore
from cocktail.controllers import UserCollection
from woost.models.action import Action
from woost.models.changesets import ChangeSet
from woost.models.site import Site
from woost.models.item import Item
from woost.models.role import Role
from woost.models.language import Language
from woost.models.usersession import get_current_user
from woost.models.messagestyles import (
    trigger_style,
    trigger_context_style,
    trigger_doesnt_match_style,
    trigger_match_style
)

_thread_data = local()

members_without_triggers = set([
    Item.changes,
    Item.last_update_time
])

verbose = False


def get_triggers_enabled():
    """Indicates if trigger activation is enabled for the current thread.    
    @rtype: bool
    """
    return getattr(_thread_data, "enabled", True)

def set_triggers_enabled(enabled):
    """Enables or disables the activation of triggers for the current thread.
    
    @param enabled: Wether triggers should be enabled.
    @type enabled: bool
    """
    _thread_data.enabled = enabled


class Trigger(Item):
    """Describes an event."""

    instantiable = False
    visible_from_root = False
    members_order = [
        "title",
        "execution_point",
        "batch_execution",
        "matching_roles",
        "condition",
        "custom_context",
        "responses"
    ]
    
    title = schema.String(
        translated = True,
        descriptive = True
    )

    execution_point = schema.String(
        required = True,
        enumeration = ("before", "after"),
        default = "after",
        edit_control = "cocktail.html.RadioSelector",
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(
                "woost.models.Trigger.execution_point " + value,
                language,
                **kwargs
            ),
        text_search = False
    )

    batch_execution = schema.Boolean(
        required = True
    )

    site = schema.Reference(
        type = "woost.models.Site",
        bidirectional = True,
        visible = False
    )

    responses = schema.Collection(
        items = "woost.models.TriggerResponse",
        bidirectional = True,
        related_key = "trigger"
    )

    matching_roles = schema.Collection(
        items = schema.Reference(
            type = Role,
            required = True
        ),
        related_end = schema.Collection(),
        edit_inline = True
    )

    condition = schema.CodeBlock(
        language = "python"
    )
 
    custom_context = schema.CodeBlock(
        language = "python"
    )

    def match(self, user, verbose = False, **context):

        # Check the user
        trigger_roles = self.matching_roles

        if trigger_roles:
            if user is None:
                print trigger_doesnt_match_style("user not specified")
                return False

            for role in user.iter_roles():
                if role in trigger_roles:
                    break
            else:
                print trigger_doesnt_match_style("user doesn't match")
                return False

        # Check the condition
        condition = self.condition

        if condition and not eval(condition, context):
            print trigger_doesnt_match_style("condition doesn't match")
            return False

        return True


class ContentTrigger(Trigger):
    """Base class for triggers based on content type instances."""

    edit_controller = \
        "woost.controllers.backoffice.triggerfieldscontroller." \
        "TriggerFieldsController"

    edit_view = "woost.views.TriggerFields"

    matching_items = schema.Mapping()

    def select_items(self, *args, **kwargs):
        user_collection = UserCollection(Item)
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.allow_language_selection = False
        user_collection.params.source = self.matching_items.get
        user_collection.available_languages = Language.codes
        return user_collection.subset

    def match(self, user, target = None, verbose = False, **context):

        # Check the target
        query = self.select_items()

        if not isinstance(target, query.type):
            if verbose:
                print trigger_doesnt_match_style("type doesn't match")
            return False
        else:
            for filter in query.filters:
                if not filter.eval(target):
                    if verbose:
                        print trigger_doesnt_match_style(
                            "filter doesn't match"
                        )
                    return False

        if not Trigger.match(
            self,
            user,
            target = target,
            verbose = verbose,
            **context
        ):
            return False

        return True


class CreateTrigger(ContentTrigger):
    """A trigger executed when an item is created."""
    instantiable = True


class InsertTrigger(ContentTrigger):
    """A trigger executed when an item is inserted."""
    instantiable = True


class ModifyTrigger(ContentTrigger):
    """A trigger executed when an item is modified."""
    
    instantiable = True
    members_order = ["matching_members", "matching_languages"]

    matching_members = schema.Collection(
        items = schema.String(required = True),
        edit_control = "woost.views.MemberList"
    )

    matching_languages = schema.Collection(
        items = schema.String(
            enumeration = lambda ctx: Language.codes,
            translate_value = lambda value, language = None, **kwargs:
                u"" if not value else translations(value, language, **kwargs)
        )
    )

    def match(self, user,
        target = None,
        member = None,
        language = None,
        verbose = False,
        **context):
        
        if self.matching_members:
            if member is None:
                if verbose:
                    print trigger_doesnt_match_style("member not specified")
                return False

            if (member.schema.full_name + "." + member.name) \
            not in self.matching_members:
                if verbose:
                    print trigger_doesnt_match_style("member doesn't match")
                return False

        if self.matching_languages:
            if language is None:
                if verbose:
                    print trigger_doesnt_match_style("language not specified")
                return False
            if language not in self.matching_languages:
                if verbose:
                    print trigger_doesnt_match_style("language doesn't match")
                return False

        if not ContentTrigger.match(
            self,
            user,
            target = target,
            member = member,
            language = language,
            verbose = verbose,
            **context
        ):
            return False

        return True


class DeleteTrigger(ContentTrigger):
    """A trigger executed when an item is deleted."""
    instantiable = True


class ConfirmDraftTrigger(ContentTrigger):
    """A trigger executed when a draft is confirmed."""
    instantiable = True


def trigger_responses(
    trigger_type,
    user = None,
    verbose = None,
    **context):

    target = context.get("target")

    if user is None:
        user = get_current_user()

    if verbose is None:
        verbose = globals()["verbose"]

    if get_triggers_enabled():

        # Create a structure to hold per-transaction data
        trans_dict = getattr(
            _thread_data,
            "trans_dict",
            None
        )

        if trans_dict is None:
            trans_dict = WeakKeyDictionary()
            _thread_data.trans_dict = trans_dict

        # Get the data for the current transaction
        trans = datastore.connection.transaction_manager.get()
        trans_data = trans_dict.get(trans)
        
        if trans_data is None:
            trans_triggers = {}
            modified_members = {}
            trans_data = {
                "triggers": trans_triggers,
                "modified_members": modified_members
            }
            trans_dict[trans] = trans_data
        else:
            trans_triggers = trans_data["triggers"]
            modified_members = trans_data["modified_members"]

        # Track modified members
        if issubclass(trigger_type, ModifyTrigger):
            target_modified_members = modified_members.get(target)

            if target_modified_members is None:
                target_modified_members = set()
                modified_members[target] = target_modified_members
            
            target_modified_members.add(
                (context["member"], context["language"])
            )

        if not Site.main:
            return None

        # Execute or schedule matching triggers
        for trigger in Site.main.triggers:

            if not isinstance(trigger, trigger_type):
                continue

            if verbose:
                print trigger_style(translations(trigger))
                print trigger_context_style("user", translations(user))
                for k, v in context.iteritems():
                    try:
                        v = translations(v) or unicode(v)
                    except:
                        pass
                    print trigger_context_style(k, v)

            if not trigger.match(
                user = user,
                verbose = verbose,
                **context
            ):
                continue

            print trigger_match_style("match")

            # Track modified / deleted items
            trigger_targets = trans_triggers.get(trigger)

            if trigger_targets is None:
                new_trans_trigger = True
                trigger_targets = set()
                trans_triggers[trigger] = trigger_targets
            else:
                new_trans_trigger = False

            if target is not None:
                trigger_targets.add(target)

            # Apply user defined customizations to the context
            # This can be specially useful to allow after-commit triggers to
            # capture state as it was when they were scheduled for execution
            # (ie. when deleting elements or confirming drafts).
            if trigger.custom_context:
                ctx = {
                    "self": trigger,
                    "context": context,
                    "user": user,
                    "target": target,
                    "trigger_targets": trigger_targets,
                    "modified_members": modified_members
                }
                exec trigger.custom_context in ctx
                context = ctx["context"]

            # Execute after the transaction is committed
            if trigger.execution_point == "after":
                
                if trigger.batch_execution:

                    # Schedule the trigger to be executed when the current
                    # transaction is successfully committed. Each batched
                    # trigger executes only once per transaction.
                    if new_trans_trigger:

                        def batched_response(successful, responses):
                            if successful:
                                try:
                                    for response in responses:
                                        response.execute(
                                            trigger_targets,
                                            user,
                                            batch = True,
                                            modified_members = modified_members,
                                            **context
                                        )

                                    datastore.commit()

                                except Exception, ex:
                                    warn("The following exception was raised "
                                         "by a deferred trigger response:")
                                    print_exc()
                                    datastore.abort()

                        trans.addAfterCommitHook(
                            batched_response,
                            (list(trigger.responses),)
                        )

                # Schedule the trigger to be executed when the current
                # transaction is successfully committed.
                else:
                    def delayed_response(successful, responses):
                        if successful:
                            try:
                                for response in responses:
                                    response.execute([target], user, **context)

                                datastore.commit()

                            except Exception, ex:
                                warn("The following exception was raised "
                                     "by a deferred trigger response:")
                                print_exc()
                                datastore.abort()

                    trans.addAfterCommitHook(
                        delayed_response,
                        (list(trigger.responses),)
                    )

            # Execute immediately, within the transaction
            else:
                for response in trigger.responses:
                    response.execute([target], user, **context)

@when(Item.instantiated)
def _trigger_instantiation_responses(event):
    trigger_responses(
        CreateTrigger,
        target = event.instance,
        values = event.values
    )

@when(Item.inserted)
def _trigger_insertion_responses(event):
    trigger_responses(
        InsertTrigger,
        target = event.source
    )

@when(Item.changed)
def _trigger_modification_responses(event):
    if event.source.is_inserted \
    and event.member not in members_without_triggers \
    and not isinstance(event.member, schema.Collection):
        trigger_responses(
            ModifyTrigger,
            target = event.source,
            member = event.member,
            language = event.language
        )

@when(Item.related)
@when(Item.unrelated)
def _trigger_relation_responses(event):
    if not isinstance(event.member, schema.Reference) \
    and event.member not in members_without_triggers:
        trigger_responses(
            ModifyTrigger,
            target = event.source,
            member = event.member,
            language = None
        )

@when(Item.deleted)
def _trigger_deletion_responses(event):
    trigger_responses(DeleteTrigger, target = event.source)

@when(Item.draft_confirmation)
def _trigger_draft_confirmation_responses(event):
    trigger_responses(ConfirmDraftTrigger, target = event.source)

