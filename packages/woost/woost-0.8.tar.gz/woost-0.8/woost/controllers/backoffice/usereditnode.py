#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from woost.controllers.backoffice.editstack import EditNode


class UserEditNode(EditNode):

    @cached_getter
    def form_adapter(self):

        form_adapter = EditNode.form_adapter(self)
        form_adapter.exclude("password_confirmation")
        
        if self.item.is_inserted:
            form_adapter.exclude("change_password")

            if self.item.encryption_method:
                kwargs = {
                    "export_condition": False,
                    "import_condition": lambda context:
                        context.get("change_password", default = None)
                }
            else:
                kwargs = {}

            form_adapter.copy("password", **kwargs)

        return form_adapter

    @cached_getter
    def form_schema(self):
        
        form_schema = EditNode.form_schema(self)
        password_member = form_schema.get_member("password")
        
        if password_member:
            
            if self.item.encryption_method:

                order = form_schema.members_order = list(form_schema.members_order)
                pos = order.index("password")

                password_conf_member = schema.String(
                    name = "password_confirmation",            
                    edit_control = "cocktail.html.PasswordBox",
                    visible_in_detail_view = False,
                    required = password_member.required
                )
                form_schema.add_member(password_conf_member)
                order.insert(pos + 1, "password_confirmation")

                if self.item.is_inserted:

                    change_password_member = schema.Boolean(
                        name = "change_password",
                        required = True,
                        default = False,
                        visible_in_detail_view = False
                    )
                    form_schema.add_member(change_password_member)
                    order.insert(pos, "change_password")
                    
                    password_member.exclusive = change_password_member
                    password_conf_member.exclusive = change_password_member
            
                @form_schema.add_validation
                def validate_password_confirmation(form_schema, value, ctx):
                    password = ctx.get_value("password")               
                    password_confirmation = ctx.get_value("password_confirmation")

                    if password and password_confirmation \
                    and password != password_confirmation:
                        yield PasswordConfirmationError(
                                form_schema, value, ctx)

            # No encryption: edit passwords in plain sight
            else:
                password_member.edit_control = "cocktail.html.TextBox"

        return form_schema

    def iter_changes(self):
        
        # Discard differences in the password field
        for member, language in EditNode.iter_changes(self):
            if not self.item.encryption_method or member.name not in (
                "change_password", "password", "password_confirmation"
            ):
                yield (member, language)


class PasswordConfirmationError(schema.exceptions.ValidationError):
    """A validation error produced when the password and its confirmation field
    are given different values."""

