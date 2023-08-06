#-*- coding: utf-8 -*-
u"""
Declaration of back office actions.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import cherrypy
from cocktail.modeling import getter, ListWrapper
from cocktail.translations import translations
from cocktail.controllers import view_state
from cocktail import schema
from woost.models import (
    Item,
    Publishable,
    URI,
    File,
    get_current_user,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    ConfirmDraftPermission,
    ReadHistoryPermission
)
from woost.controllers.backoffice.editstack import (
    SelectionNode,
    RelationNode
)

# User action model declaration
#------------------------------------------------------------------------------

# Class stub (needed by the metaclass)
UserAction = None

_action_list = ListWrapper([])
_action_map = {}

def get_user_action(id):
    """Gets a user action, given its unique identifier.

    @param id: The unique identifier of the action to obtain.
    @type id: str

    @return: The requested user action, or None if not defined.
    @rtype: L{UserAction}
    """
    return _action_map.get(id)

def get_user_actions(**kwargs):
    """Returns a collection of all actions registered with the site.
    
    @return: The list of user actions.
    @rtype: iterable L{UserAction} sequence
    """
    return _action_list  

def get_view_actions(context, target = None):
    """Obtains the list of actions that can be displayed on a given view.

    @param context: A set of string identifiers, such as "context_menu",
        "toolbar", etc. Different views can make use of as many different
        identifiers as they require.
    @type container: str set

    @param target: The item or content type affected by the action.
    @type target: L{Item<woost.models.item.Item>} instance or class

    @return: The list of user actions available under the specified context.
    @rtype: iterable L{UserAction} sequence
    """
    return (
        action
        for action in _action_list
        if action.enabled
            and action.is_available(context, target)
    )

def add_view_action_context(view, clue):
    """Adds contextual information to the given view, to be gathered by
    L{get_view_actions_context} and passed to L{get_view_actions}.
    
    @param view: The view that gains the context clue.
    @type view: L{Element<cocktail.html.element.Element>}

    @param clue: The context identifier added to the view.
    @type clue: str
    """
    view_context = getattr(view, "actions_context", None)
    if view_context is None:
        view_context = set()
        view.actions_context = view_context
    view_context.add(clue)

def get_view_actions_context(view):
    """Extracts clues on the context that applies to a given view and its
    ancestors, to supply to the L{get_view_actions} function.
    
    @param view: The view to inspect.
    @type view: L{Element<cocktail.html.element.Element>}

    @return: The set of context identifiers for the view and its ancestors.
    @rtype: str set
    """
    context = set()

    while view:
        view_context = getattr(view, "actions_context", None)
        if view_context:
            context.update(view_context)
        view = view.parent
     
    return context


class UserAction(object):
    """An action that is made available to users at the backoffice
    interface. The user actions model allows site implementors to extend the
    site with their own actions, or to disable or override standard actions
    with fine grained control of their context.

    @ivar enabled: Controls the site-wide availavility of the action.
    @type enabled: bool

    @ivar included: A set of context identifiers under which the action is
        made available. Entries on the sequence are joined using a logical OR.
        Entries can also consist of a tuple of identifiers, which will be
        joined using a logical AND operation.
    @type included: set(str or tuple(str))

    @ivar excluded: A set of context identifiers under which the action won't
        be made available. Identifiers are specified using the same format used
        by the L{included} parameter. If both X{included} and X{excluded} are
        specified, both conditions will be tested, with X{excluded} carrying
        more weight.
    @type excluded: set(str or tuple(str))

    @ivar content_type: When set, the action will only be made available to the
        indicated content type or its subclasses.
    @type content_type: L{Item<woost.models.Item>} subclass

    @ivar ignores_selection: Set to True for actions that don't operate on a
        selection of content.
    @type ignores_selection: bool

    @ivar min: The minimum number of content items that the action can be
        invoked on. Setting it to 0 or None disables the constraint.
    @type min: int

    @ivar max: The maximum number of content items that the action can be
        invoked on. A value of None disables the constraint.
    @type max: int

    @ivar direct_link: Set to True for actions that can provide a direct URL
        for their execution, without requiring a form submit and redirection.
    @type direct_link: bool

    @ivar parameters: A schema describing user supplied parameters required by
        the action. When set to None, the action requires no additional input
        from the user.
    @type parameters: L{Schema<cocktail.schema.schema.Schema>}
    """
    enabled = True
    included = frozenset(["toolbar_extra", "item_buttons_extra"])
    excluded = frozenset([
        "selector",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])
    content_type = None
    ignores_selection = False
    min = 1
    max = 1
    direct_link = False
    parameters = None

    def __init__(self, id):

        if not id:
            raise ValueError("User actions must have an id")

        if not isinstance(id, basestring):
            raise TypeError("User action identifiers must be strings, not %s"
                            % type(id))
        self._id = id

    def __translate__(self, language, **kwargs):
        return translations("Action " + self.id, **kwargs)

    @getter
    def id(self):
        """The unique identifier for the action.
        @type: str
        """
        return self._id

    def register(self, before = None, after = None):
        """Registers the action with the site, so that it can appear on action
        containers and be handled by controllers.

        Registering an action with an identifier already in use is allowed, and
        will override the previously registered action.

        @param before: Indicates the position for the registered action. Should
            match the identifier of an already registered action. The new
            action will be inserted immediately before the indicated action.
        @type before: str

        @param after: Indicates the position for the registered action. Should
            match the identifier of an already registered action. The new
            action will be inserted immediately after the indicated action.
        @type after: str

        @raise ValueError: Raised if both L{before} and L{after} are set.
        @raise ValueError: Raised if the position indicated by L{after} or
            L{before} can't be found.
        """
        if after and before:
            raise ValueError("Can't combine 'after' and 'before' parameters")

        prev_action = get_user_action(self._id)

        if after or before:
            if prev_action:
                _action_list._items.remove(prev_action)
            
            ref_action = _action_map[after or before]
            pos = _action_list.index(ref_action)
            
            if before:
                _action_list._items.insert(pos, self)
            else:
                _action_list._items.insert(pos + 1, self)

        elif prev_action:
            pos = _action_list.index(prev_action)
            _action_list._items[pos] = self
        else:
            _action_list._items.append(self)

        _action_map[self._id] = self

    def is_available(self, context, target):
        """Indicates if the user action is available under a certain context.
        
        @param context: A set of string identifiers, such as "context_menu",
            "toolbar", etc. Different views can make use of as many different
            identifiers as they require.
        @type container: str set

        @param target: The item or content type affected by the action.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @return: True if the action can be shown in the given context, False
            otherwise.
        @rtype: bool
        """
        
        # Context filters
        def match(tokens):
            for token in tokens:
                if isinstance(token, str):
                    if token in context:
                        return True
                elif context.issuperset(token):
                    return True
            return False

        if self.included and not match(self.included):
            return False

        if self.excluded and match(self.excluded):
            return False
 
        # Content type filter
        if self.content_type is not None:
            if isinstance(target, type):
                if not issubclass(target, self.content_type):
                    return False
            else:
                if not isinstance(target, self.content_type):
                    return False
        
        # Authorization check
        return self.is_permitted(get_current_user(), target)

    def is_permitted(self, user, target):
        """Determines if the given user is allowed to execute the action.

        Subclasses should override this method in order to implement their
        access restrictions.

        @param user: The user to authorize.
        @type user: L{User<woost.models.user.User>}
    
        @param target: The item or content type affected by the action.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @return: True if the user is granted permission, False otherwise.
        @rtype: bool
        """
        return True

    def get_dropdown_panel(self, target):
        """Produces the user interface fragment that should be shown as the
        content for the action's dropdown panel. Returning None indicates the
        action doesn't have a dropdown panel available.

        @param target: The item or content type affected by the action.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @return: The user interface for the action's dropdown panel.
        @rtype: L{Element<cocktail.html.Element>}
        """
        return None

    def get_errors(self, controller, selection):
        """Validates the context of an action before it is invoked.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action will be
            applied to.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: The list of errors for the indicated context.
        @rtype: iterable L{Exception} sequence
        """
        if not self.ignores_selection:

            # Validate selection size
            selection_size = len(selection) if selection is not None else 0

            if (self.min and selection_size < self.min) \
            or (self.max is not None and selection_size > self.max):
                yield SelectionError(self, selection_size)                       

    def invoke(self, controller, selection):
        """Delegates control of the current request to the action. Actions can
        override this method to implement their own response logic; by default,
        users are redirected to an action specific controller.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}
        """
        raise cherrypy.HTTPRedirect(self.get_url(controller, selection))
    
    def get_url(self, controller, selection):
        """Produces the URL of the controller that handles the action
        execution. This is used by the default implementation of the L{invoke}
        method. Actions can override this method to alter this value.

        By default, single selection actions produce an URL of the form
        $cms_base_url/content/$selected_item_id/$action_id. Other actions
        follow the form $cms_base_url/$action_id/?selection=$selection_ids

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action is invoked
            on.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: The URL where the user should be redirected.
        @rtype: str
        """
        params = self.get_url_params(controller, selection)

        if self.ignores_selection:
            return controller.contextual_uri(self.id, **params)

        elif self.min == self.max == 1:
            # Single selection
            return controller.edit_uri(
                    selection[0],
                    self.id,
                    **params)
        else:
            return controller.contextual_uri(
                    self.id,
                    selection = [item.id for item in selection],
                    **params)

    def get_url_params(self, controller, selection):
        """Produces extra URL parameters for the L{get_url} method.
        
        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action is invoked
            on.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: A mapping containing additional parameters to include on the
            URL associated to the action.
        @rtype: dict
        """
        params = {}

        if controller.edit_stack:
            params["edit_stack"] = controller.edit_stack.to_param()
        
        return params

    @getter
    def icon_uri(self):
        return "/resources/images/%s_small.png" % self.id


class SelectionError(Exception):
    """An exception produced by the L{UserAction.get_errors} method when an
    action is attempted against an invalid number of items."""
    
    def __init__(self, action, selection_size):
        Exception.__init__(self, "Can't execute action '%s' on %d item(s)."
            % (action.id, selection_size))
        self.action = action
        self.selection_size = selection_size


# Implementation of concrete actions
#------------------------------------------------------------------------------

class CreateAction(UserAction):
    included = frozenset(["toolbar"])
    excluded = frozenset([
        "collection",
        ("selector", "existing_only"),
        "changelog"
    ])
    ignores_selection = True
    min = None
    max = None
    
    def get_url(self, controller, selection):
        return controller.edit_uri(controller.edited_content_type)


#class CreateBeforeAction(CreateAction):
#   ignores_selection = False


#class CreateInsideAction(CreateAction):
#   ignores_selection = False


#class CreateAfterAction(CreateAction):
#   ignores_selection = False


class MoveAction(UserAction):
    included = frozenset([("toolbar", "tree")])
    max = None


class AddAction(UserAction):
    included = frozenset([("toolbar", "collection")])
    excluded = frozenset(["integral"])
    ignores_selection = True
    min = None
    max = None

    def invoke(self, controller, selection):
        
        # Add a relation node to the edit stack, and redirect the user
        # there
        node = RelationNode()
        node.member = controller.member
        node.action = "add"
        controller.edit_stack.push(node)
        controller.edit_stack.go()


class AddIntegralAction(UserAction):

    included = frozenset([("collection", "toolbar", "integral")])
    ignores_selection = True
    min = None
    max = None
    
    def get_url(self, controller, selection):        
        return controller.edit_uri(controller.root_content_type)


class RemoveAction(UserAction):
    included = frozenset([("toolbar", "collection")])
    excluded = frozenset(["integral"])
    max = None

    def invoke(self, controller, selection):

        stack_node = controller.stack_node

        for item in selection:
            stack_node.unrelate(controller.member, item)

        controller.user_collection.base_collection = \
            schema.get(stack_node.form_data, controller.member)


class OrderAction(UserAction):
    included = frozenset([("order_content_view", "toolbar")])
    max = None

    def invoke(self, controller, selection):
        node = RelationNode()
        node.member = controller.member
        node.action = "order"
        controller.edit_stack.push(node)
        UserAction.invoke(self, controller, selection)

    def get_url_params(self, controller, selection):
        params = UserAction.get_url_params(self, controller, selection)
        params["member"] = controller.section
        return params


class ShowDetailAction(UserAction):
    included = frozenset(["toolbar", "item_buttons"])


class EditAction(UserAction):
    included = frozenset(["toolbar", "item_buttons"])

    def is_permitted(self, user, target):
        return user.has_permission(ModifyPermission, target = target)

    def get_url(self, controller, selection):
        return controller.edit_uri(selection[0])


class DeleteAction(UserAction):
    included = frozenset([
        ("content", "toolbar"),
        ("collection", "toolbar", "integral"),
        "item_buttons"
    ])
    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])
    max = None
    
    def is_permitted(self, user, target):
        return user.has_permission(DeletePermission, target = target)


class ShowChangelogAction(UserAction):
    min = None
    max = 1
    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])

    def get_url(self, controller, selection):

        params = self.get_url_params(controller, selection)

        # Filter by target element
        if selection:
            params["filter"] = "member-changes"
            params["filter_value0"] = str(selection[0].id)

        # Filter by target type
        else:
            user_collection = getattr(controller, "user_collection", None)
            if user_collection and user_collection.type is not Item:
                params["filter"] = "target-type"
                params["filter_value0"] = user_collection.type.full_name

        return controller.contextual_uri(
            "changelog",                
            **params
        )

    def is_permitted(self, user, target):
        return user.has_permission(ReadHistoryPermission)


class DiffAction(UserAction):
    included = frozenset(["item_buttons"])
    
    def is_permitted(self, user, target):
        return user.has_permission(ModifyPermission, target = target)


class RevertAction(UserAction):
    included = frozenset([("diff", "item_body_buttons", "changed")])
    
    def is_permitted(self, user, target):
        return user.has_permission(ModifyPermission, target = target)

    def invoke(self, controller, selection):

        reverted_members = controller.params.read(
            schema.Collection("reverted_members",
                type = set,
                items = schema.String
            )
        )

        stack_node = controller.stack_node

        form_data = stack_node.form_data
        form_schema = stack_node.form_schema
        languages = set(
            list(stack_node.translations)
            + list(stack_node.item.translations.keys())
        )

        source = {}
        stack_node.export_form_data(stack_node.item, source)
        
        for member in form_schema.members().itervalues():
                      
            if member.translated:
                for lang in languages:
                    if (member.name + "-" + lang) in reverted_members:
                        schema.set(
                            form_data,
                            member.name,
                            schema.get(source, member.name, language = lang),
                            language = lang
                        )
            elif member.name in reverted_members:
                schema.set(
                    form_data,
                    member.name,
                    schema.get(source, member.name)
                )


class PreviewAction(UserAction):
    included = frozenset(["toolbar_extra", "item_buttons"])
    content_type = Publishable


class OpenResourceAction(UserAction):
    min = 1
    max = 1
    content_type = Publishable
    included = frozenset(["toolbar", "item_buttons"])
    excluded = frozenset([
        "new",
        "draft",
        "selector",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])

    def get_url(self, controller, selection):
        return controller.context["cms"].uri(selection[0])


class UploadFilesAction(UserAction):
    included = frozenset(["toolbar_extra"])
    content_type = File
    min = None
    max = None
    ignores_selection = True


class ExportAction(UserAction):
    included = frozenset(["toolbar_extra"])
    min = 1
    max = None
    ignores_selection = True
    format = None
    direct_link = True

    def __init__(self, id, format):
        UserAction.__init__(self, id)
        self.format = format

    def get_url(self, controller, selection):
        return "?" + view_state(
            format = self.format
        )


class SelectAction(UserAction):
    included = frozenset([("list_buttons", "selector")])
    excluded = frozenset()
    min = None
    max = None
    
    def invoke(self, controller, selection):

        stack = controller.edit_stack

        if stack:
            
            node = stack[-1]
            params = {}

            if isinstance(node, SelectionNode):
                params[node.selection_parameter] = (
                    selection[0].id
                    if selection
                    else ""
                )

            elif isinstance(node, RelationNode):
                edit_state = node.parent_node
                member = controller.stack_node.member

                if isinstance(member, schema.Reference):
                    edit_state.relate(
                        member,
                        None if not selection else selection[0]
                    )
                else:
                    if controller.stack_node.action == "add":
                        modify_relation = edit_state.relate 
                    else:
                        modify_relation = edit_state.unrelate 

                    for item in selection:
                        modify_relation(member, item)
            
            stack.go_back(**params)


class GoBackAction(UserAction):
    ignores_selection = True
    min = None
    max = None

    def invoke(self, controller, selection):
        controller.go_back()


class CloseAction(GoBackAction):
    included = frozenset(["item_buttons", ("changelog", "bottom_buttons")])
    excluded = frozenset(["changed", "new", "edit"])


class CancelAction(GoBackAction):
    included = frozenset([
        ("list_buttons", "selector"),
        ("item_buttons", "edit"),
        ("item_buttons", "changed"),
        ("item_buttons", "new"),
        ("item_bottom_buttons", "edit"),
        ("item_bottom_buttons", "changed"),
        ("item_bottom_buttons", "new")
    ])
    excluded = frozenset()


class SaveAction(UserAction):
    included = frozenset([
        ("item_buttons", "new"),
        ("item_buttons", "edit"),
        ("item_buttons", "changed"),
        ("item_bottom_buttons", "new"),
        ("item_bottom_buttons", "edit"),
        ("item_bottom_buttons", "changed")
    ])
    ignores_selection = True
    max = None
    min = None
    make_draft = False

    def is_permitted(self, user, target):
        if target.is_inserted:
            return user.has_permission(
                ModifyPermission,
                target = target
            )
        else:
            return user.has_permission(
                CreatePermission,
                target = target.__class__
            )

    def get_errors(self, controller, selection):
        for error in UserAction.get_errors(self, controller, selection):
            yield error

        for error in controller.stack_node.iter_errors():
            yield error

    def invoke(self, controller, selection):
        controller.save_item(make_draft = self.make_draft)


class SaveDraftAction(SaveAction):
    make_draft = True
    included = frozenset(["item_buttons", "item_bottom_buttons"])
    excluded = frozenset(["draft"])

    def is_permitted(self, user, target):
        return True

class ConfirmDraftAction(SaveAction):
    confirm_draft = True
    included = frozenset([
        ("item_buttons", "draft"),
        ("item_bottom_buttons", "draft")
    ])
    excluded = frozenset()
    
    def is_permitted(self, user, target):
        return user.has_permission(ConfirmDraftPermission, target = target)

    def invoke(self, controller, selection):
        controller.confirm_draft()


class PrintAction(UserAction):
    direct_link = True
    ignore_selection = True
    excluded = frozenset(["selector"])

    def get_url(self, controller, selection):
        return "javascript: print();"


# Action registration
#------------------------------------------------------------------------------ 
CreateAction("new").register()
MoveAction("move").register()
AddAction("add").register()
AddIntegralAction("add_integral").register()
RemoveAction("remove").register()
ShowDetailAction("show_detail").register()
PreviewAction("preview").register()
OpenResourceAction("open_resource").register()
UploadFilesAction("upload_files").register()
EditAction("edit").register()
DiffAction("diff").register()
RevertAction("revert").register()
ShowChangelogAction("changelog").register()
DeleteAction("delete").register()
OrderAction("order").register()
ExportAction("export_xls", "msexcel").register()
PrintAction("print").register()
CloseAction("close").register()
CancelAction("cancel").register()
SaveAction("save").register()
SaveDraftAction("save_draft").register()
ConfirmDraftAction("confirm_draft").register()
SelectAction("select").register()

