#-*- coding: utf-8 -*-
u"""Defines migrations to the database schema for woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

def admin_members_restriction(members):
    
    def add_permission(e):

        from woost.models import Role, ModifyMemberPermission
        
        everybody_role = Role.require_instance(qname = "woost.everybody")
        permission = ModifyMemberPermission(
            matching_members = list(members),
            authorized = False
        )
        permission.insert()
        
        for i, p in enumerate(everybody_role.permissions):
            if isinstance(p, ModifyMemberPermission) and p.authorized:
                everybody_role.permissions.insert(i, permission)
                break
        else:
            everybody_role.permissions.append(permission)

    return add_permission

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Document.robots_*")

step.executing.append(
    admin_members_restriction([
        "woost.models.document.Document.robots_should_index",
        "woost.models.document.Document.robots_should_follow"
    ])
)

@step.processor("woost.models.document.Document")
def set_defaults(document):
    if not hasattr(document, "_robots_should_index"):
        document.robots_should_index = True
        document.robots_should_follow = True

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Publishable.requires_https")

step.executing.append(
    admin_members_restriction([
        "woost.models.publishable.Publishable.requires_https"
    ])
)

@step.processor("woost.models.publishable.Publishable")
def set_defaults(publishable):
    if not hasattr(publishable, "_requires_https"):
        publishable.requires_https = False


#------------------------------------------------------------------------------

step = MigrationStep("make Product extend Publishable")

@when(step.executing)
def update_keys(e):
    from woost.extensions.shop import ShopExtension

    if ShopExtension.enabled:
        from cocktail.translations import translations
        from woost.models import Publishable, Controller, Language
        from woost.extensions.shop import create_product_controller
        from woost.extensions.shop.product import Product

        # Update the publishable keys
        Publishable.keys.update([product.id for product in Product.select()])

        # Create the product controller
        create_product_controller()

#------------------------------------------------------------------------------

step = MigrationStep("use TranslationMapping to translations")

@when(step.executing)
def update_translations(e):
    from cocktail.schema import TranslationMapping
    from cocktail.persistence import PersistentObject

    def translated_items(schema):
        if schema.translated and schema.indexed:
            for item in schema.select():
                yield item
        else:
            for derived_schema in schema.derived_schemas(False):
                for item in translated_items(derived_schema):
                    yield item

    for item in translated_items(PersistentObject):
        translations = TranslationMapping(
            owner = item, 
            items = item.translations._items
        )
        item.translations._items = translations
        item._p_changed = True

    PersistentObject.rebuild_indexes(True)

#------------------------------------------------------------------------------

step = MigrationStep(
    "rename EmailTemplate.embeded_images to EmailTemplate.attachments"
)

step.rename_member(
    "woost.models.EmailTemplate",
    "embeded_images",
    "attachments"
)

#------------------------------------------------------------------------------

step = MigrationStep(
    "Apply full text indexing to elements with no translations"
)

@when(step.executing)
def rebuild_full_text_index(e):
    from woost.models import Item
    Item.rebuild_full_text_indexes(True)

#------------------------------------------------------------------------------

step = MigrationStep(
    "Replace EmailTemplate.attachments with EmailTemplate.initialization_code"
)

@when(step.executing)
def relocate_attachments_code(e):
    from woost.models import EmailTemplate

    for email_template in EmailTemplate.select():
        code = getattr(email_template, "_attachments", None)
        if code:
            del email_template._attachments
            if email_template.initialization_code:
                code = email_template.initialization_code + "\n\n" + code
            email_template.initialization_code = code

#------------------------------------------------------------------------------

step = MigrationStep(
    "Added the Role.implicit member"
)

@when(step.executing)
def flag_implicit_roles(e):
    from woost.models import Role

    implicit_roles_qnames = set((
        "woost.anonymous",
        "woost.everybody",
        "woost.authenticated"
    ))

    for role in Role.select():
        role.implicit = (role.qname in implicit_roles_qnames)

