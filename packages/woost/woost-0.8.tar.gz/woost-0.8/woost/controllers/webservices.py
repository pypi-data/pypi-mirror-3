#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from base64 import b64encode
from cocktail.modeling import cached_getter, InstrumentedSet
from cocktail.controllers import context
from cocktail.controllers.webservices import (
    PersistentClassWebService,
    excluded_member
)
from woost.models import (
    changeset_context,
    Item,
    User,
    Site,
    Language,
    get_current_user,
    restricted_modification_context,
    PermissionExpression,
    ReadPermission,
    DeletePermission,
    ReadMemberPermission,
    ReadTranslationPermission
)
from woost.controllers.basecmscontroller import BaseCMSController


class ItemWebService(PersistentClassWebService):
    root_type = Item

    def _init_user_collection(self, user_collection):
        PersistentClassWebService._init_user_collection(self, user_collection)
        user_collection.add_base_filter(
            PermissionExpression(get_current_user(), ReadPermission)
        )

    @cached_getter
    def languages(self):
        return Language.codes

    class JSONEncoder(PersistentClassWebService.JSONEncoder):
                
        def get_member_value(self, obj, member, language = None):

            # Exclude the 'changes' member
            if member is Item.changes:
                value = excluded_member

            # Exclude restricted members
            elif not (
                self.user.has_permission(
                    ReadMemberPermission,
                    member = member
                )
                and self.user.has_permission(
                    ReadTranslationPermission,
                    language = language
                )
            ):
                value = excluded_member
 
            # Special case for user passwords
            elif member is User.password:
                value = obj.password
                if value:
                    value = b64encode(value)            
            else:
                value = PersistentClassWebService.JSONEncoder.get_member_value(
                    self,
                    obj,
                    member,
                    language
                )

            return value

    @cached_getter
    def json_encoder(self):        
        encoder = PersistentClassWebService.json_encoder(self)
        encoder.user = get_current_user()
        return encoder
    
    def _init_new_instance(self, instance):
        with restricted_modification_context(instance):
            PersistentClassWebService._init_new_instance(self, instance)

    def _store_new_instance(self, instance):
        if instance.is_draft:
            instance.insert()
        else:
            with changeset_context(get_current_user()):
                instance.insert()

    def _update_instance(self, instance):
        with restricted_modification_context(instance):
            if instance.is_draft:
                PersistentClassWebService._update_instance(self, instance)
            else:
                with changeset_context(get_current_user()):
                    PersistentClassWebService._update_instance(self, instance)

    def _delete_instances(self, query):

        user = get_current_user()
        
        class ValidatingDeletedSet(InstrumentedSet):
            def item_added(self, item):
                user.require_permission(DeletePermission, target = item)

        deleted_set = ValidatingDeletedSet()

        with changeset_context(user):
            for item in list(query):
                item.delete(deleted_set)


class CMSWebServicesController(BaseCMSController):
    data = ItemWebService    

