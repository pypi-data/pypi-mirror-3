#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import re
import buffet
from cocktail.modeling import abstractmethod
from cocktail import schema
from woost.models.item import Item
from woost.models.emailtemplate import EmailTemplate

line_separator_expr = re.compile("[\r\n]+")


class TriggerResponse(Item):
    """A response action, to be executed when invoking the
    L{trigger<woost.models.Trigger>} it is bound to."""
    
    integral = True
    instantiable = False
    visible_from_root = False

    trigger = schema.Reference(   
        type = "woost.models.Trigger",
        visible = False,
        bidirectional = True,
        integral = False
    )

    @abstractmethod
    def execute(self, items, user, batch = False, **context):
        """Executes the response with the supplied context.
        
        This method will be called when the response's trigger conditions are
        met. Subclasses of trigger response are expected to override this
        method in order to implement their particular logic.

        @param items: The list of items that received the condition that
            triggered the response.
        @type items: L{Item<woost.models.item.Item>} list

        @param user: The user that triggered the response.
        @type user: L{User<woost.models.user.User>}

        @param batch: Indicates if the response is being executed by a trigger
            that is set to operate in L{batch mode
            <woost.models.Trigger.batch>}.
        @type batch: bool

        @param context: Additional context. Available keys depend on the kind
            of action that triggered the response.
        """


class CustomTriggerResponse(TriggerResponse):
    """A trigger response that allows the execution of arbitrary python
    code."""
    instantiable = True

    code = schema.CodeBlock(
        language = "python",
        required = True
    )

    def execute(self, items, user, batch = False, **context):
        context.update(
            items = items,
            user = user,
            batch = batch
        )
        code = line_separator_expr.sub("\n", self.code)
        exec code in context


class SendEmailTriggerResponse(TriggerResponse):
    """A trigger response that allows to send an email."""

    instantiable = True

    email_template = schema.Reference(
        type = EmailTemplate,
        related_end = schema.Collection(),
        required = True
    )

    def execute(self, items, user, batch = False, **context):
        context.update(
            items = items,
            user = user,
            batch = batch
        )
        self.email_template.send(context)

# TODO: Implement other response types:
# NotifyUserTriggerResponse
# SendXMPPTriggerResponse (as an extension?)
# SendSMSTriggerResponse (as an extension?)
# WriteLogTriggerResponse (as an extension?)

