#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import sha
from string import letters, digits
from random import choice
from optparse import OptionParser
from cocktail.translations import translations
from cocktail.persistence import (
    datastore,
    mark_all_migrations_as_executed
)
from woost.models import (
    changeset_context,
    Site,
    HierarchicalPublicationScheme,
    DescriptiveIdPublicationScheme,
    Language,
    Action,
    Publishable,
    Document,
    User,
    Role,
    StandardPage,
    URI,
    Controller,
    Template,
    UserView,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    RenderPermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    CreateTranslationPermission,
    ReadTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ReadHistoryPermission,
    DeleteTrigger,
    CustomTriggerResponse,
    ConfirmDraftPermission,
    EmailTemplate,
    CachingPolicy,
    Extension,
    load_extensions
)

standard_template_identifiers = {
    "cocktail": "woost.views.StandardView",
    "genshi": "woost.views.StandardView"
}

def init_site(
    admin_email = "admin@localhost",
    admin_password = "",
    languages = ("en",),
    uri = "/",
    template_engine = "cocktail",
    extensions = ()):
 
    datastore.root.clear()
    datastore.commit()
    datastore.close()
    
    def set_translations(item, member, key, **kwargs):
        for language in languages:
            value = translations(
                "woost.models.initialization " + key,
                language,
                **kwargs
            )
            if value:
                item.set(member, value, language)

    # Create standard actions
    create = Action()
    create.identifier = "create"
    set_translations(create, "title", "Create action title")
    create.insert()

    read = Action()
    read.identifier = "read"
    set_translations(read, "title", "Read action title")
    read.insert()

    modify = Action()
    modify.identifier = "modify"
    set_translations(modify, "title", "Modify action title")
    modify.insert()

    delete = Action()
    delete.identifier = "delete"
    set_translations(delete, "title", "Delete action title")
    delete.insert()

    confirm_draft = Action()
    confirm_draft.identifier = "confirm_draft"
    set_translations(confirm_draft, "title", "Confirm draft title")
    confirm_draft.insert()

    with changeset_context() as changeset:
        
        # Create the site
        site = Site()
        site.qname = "woost.main_site"
        site.insert()
        site.secret_key = random_string(10)

        # Create the administrator user
        admin = User()
        admin.author = admin
        admin.qname = "woost.administrator"
        admin.owner = admin
        admin.critical = True
        admin.email = admin_email
        admin.password = admin_password
        admin.insert()
        
        changeset.author = admin
        site.author = site.owner = admin
        site.default_language = languages[0]

        if site.default_language in Site.backoffice_language.enumeration:
            site.backoffice_language = site.default_language
            admin.prefered_language = site.default_language
        
        # Create the anonymous user and role
        anonymous_role = Role()
        anonymous_role.implicit = True
        anonymous_role.critical = True
        anonymous_role.qname = "woost.anonymous"
        set_translations(anonymous_role, "title", "Anonymous role title")        
        anonymous_role.insert()

        anonymous_user = User()
        anonymous_user.email = "anonymous@localhost"
        anonymous_user.qname = "woost.anonymous_user"
        anonymous_user.anonymous = True
        anonymous_user.critical = True
        anonymous_user.roles.append(anonymous_role)
        anonymous_user.insert()

        # Create languages
        for code in languages:
            language = Language(iso_code = code)
            language.iso_code = code
            language.insert()
 
        # Create the administrators role        
        administrators = Role()
        administrators.qname = "woost.administrators"
        administrators.critical = True
        set_translations(administrators, "title", "Administrators role title")
        administrators.users.append(admin)
        everything = lambda: {"type": "woost.models.item.Item"}
        administrators.permissions = [
            # Administrators have full control
            ReadPermission(matching_items = everything()),
            CreatePermission(matching_items = everything()),
            ModifyPermission(matching_items = everything()),
            DeletePermission(matching_items = everything()),
            ConfirmDraftPermission(matching_items = everything()),
            ReadMemberPermission(),
            ModifyMemberPermission()
        ]
        administrators.insert()

        # Create the 'everybody' role
        everybody_role = Role()
        everybody_role.implicit = True
        everybody_role.critical = True
        everybody_role.qname = "woost.everybody"
        set_translations(everybody_role, "title", "Everybody role title")
        owned_items = lambda: {
            "type": "woost.models.item.Item",
            "filter": "owned-items"
        }
        everybody_role.permissions = [

            # Everybody can render any item
            RenderPermission(
                matching_items = {
                    "type": "woost.models.item.Item"
                }
            ),

            # Everybody can read published items
            ReadPermission(
                matching_items = {
                    "type": "woost.models.publishable.Publishable",
                    "filter": "published"
                }
            ),
            
            # Content owners have full control
            ModifyPermission(matching_items = owned_items()),
            DeletePermission(matching_items = owned_items()),
            ConfirmDraftPermission(matching_items = owned_items()),
            
            # All members allowed, except for 'local_path', 'controller' and 'qname'
            ReadMemberPermission(
                matching_members = [
                    "woost.models.item.Item.qname",
                    "woost.models.publishable.Publishable.controller",
                    "woost.models.file.File.local_path"
                ],
                authorized = False
            ),

            # Only administrators can see the CachePolicy model
            ReadPermission(
                matching_items = {
                    "type": "woost.models.caching.CachingPolicy"                    
                },
                authorized = False
            ),

            ReadMemberPermission(),
            
            # Only administrators can modify 'owner', 'robots_should_index',
            # 'robots_should_follow' and 'requires_https' members
            ModifyMemberPermission(
                matching_members = ["woost.models.item.Item.owner"],
                authorized = False
            ),
            ModifyMemberPermission(
                matching_members = [
                    "woost.models.publishable.Publishable.requires_https"
                ],
                authorized = False
            ),
            ModifyMemberPermission(
                matching_members = [
                    "woost.models.document.Document.robots_should_index",
                    "woost.models.document.Document.robots_should_follow"
                ],
                authorized = False
            ),
            ModifyMemberPermission(),

            # All languages allowed
            CreateTranslationPermission(),
            ReadTranslationPermission(),
            ModifyTranslationPermission(),
            DeleteTranslationPermission()
        ]
        everybody_role.insert()

        # Create the 'authenticated' role
        authenticated_role = Role()
        authenticated_role.implicit = True
        authenticated_role.critical = True
        authenticated_role.qname = "woost.authenticated"
        set_translations(authenticated_role, "title",
            "Authenticated role title")
        authenticated_role.permissions = [
            ReadHistoryPermission()
        ]
        authenticated_role.insert()

        # Create publication schemes
        for pub_scheme in (
            HierarchicalPublicationScheme(),
            DescriptiveIdPublicationScheme()
        ):
            site.publication_schemes.append(pub_scheme)
            pub_scheme.insert()

        # Create a trigger to purge deleted files from the filesystem
        delete_files_trigger = DeleteTrigger(
            execution_point = "after",
            batch_execution = True,
            matching_items = {"type": "woost.models.file.File"},
            responses = [
                CustomTriggerResponse(
                    code = u"from os import remove\n"
                           u"for item in items:\n"
                           u"    remove(item.file_path)"
                )
            ]
        )
        set_translations(delete_files_trigger, "title",
            "delete_files_trigger"
        )
        site.triggers.append(delete_files_trigger)
        delete_files_trigger.insert()

        # Create standard controllers
        for controller_name in (
            "Document",
            "File",
            "URI",
            "Styles",
            "Feed",
            "WebServices",
            "BackOffice",
            "FirstChildRedirection",
            "Login",
            "PasswordChange",
            "PasswordChangeConfirmation"
        ):
            controller = Controller()
            controller.qname = "woost.%s_controller" % controller_name.lower()          
            set_translations(
                controller,
                "title",
                controller_name + " controller title"
            )
            controller.python_name = \
                "woost.controllers.%scontroller.%sController" % (
                    controller_name.lower(),
                    controller_name
                )
            controller.insert()

        # The backoffice controller is placed at an irregular location
        back_office_controller = \
            Controller.get_instance(qname = "woost.backoffice_controller")
        back_office_controller.python_name = \
            "woost.controllers.backoffice.backofficecontroller." \
            "BackOfficeController"

        # Prevent anonymous access to the backoffice controller
        ReadPermission(
            role = anonymous_role,
            matching_items = {
                "type": "woost.models.publishable.Publishable",
                "filter": "member-controller",
                "filter_operator0": "eq",
                "filter_value0": str(back_office_controller.id)
            },
            authorized = False
        ).insert()

        # Create standard templates
        std_template = Template()
        std_template.identifier = standard_template_identifiers.get(
            template_engine, "StandardView"
        )
        std_template.engine = template_engine
        std_template.qname = "woost.standard_template"
        set_translations(std_template, "title", "Standard template title")
        std_template.insert()

        # Create Login Form view
        login_form_template = Template()
        login_form_template.identifier = u"woost.views.LoginFormView"
        login_form_template.engine = u"cocktail"
        set_translations(
            login_form_template,
            "title", "Login Form template title"
        )
        login_form_template.insert()

        # Create Password Change Request view
        password_change_request_view = Template()
        password_change_request_view.identifier = \
            u"woost.views.PasswordChangeRequestView"
        password_change_request_view.engine = u"cocktail"
        set_translations(
            password_change_request_view,
            "title", "Password Change Request template title"
        )
        password_change_request_view.insert()

        # Create Password Change Email template
        password_change_confirmation_email_template = EmailTemplate()
        password_change_confirmation_email_template.template_engine = u"mako"
        password_change_confirmation_email_template.qname = \
            u"woost.views.password_change_confirmation_email_template"
        set_translations(
            password_change_confirmation_email_template,
            "title", "Password Change Confirmation Email template title"
        )
        set_translations(
            password_change_confirmation_email_template,
            "subject", "Password Change Confirmation Email subject"
        )
        set_translations(
            password_change_confirmation_email_template,
            "body", "Password Change Confirmation Email body"
        )
        password_change_confirmation_email_template.set(
            "sender",
            u'u"'+admin.email+'"'
        )
        password_change_confirmation_email_template.set(
            "receivers",
            u"[user.email]"
        )
        password_change_confirmation_email_template.insert()

        # Create Password Change Confirmation view
        password_change_confirmation_view = Template()
        password_change_confirmation_view.identifier = \
            u"woost.views.PasswordChangeConfirmationView"
        password_change_confirmation_view.engine = u"cocktail"
        set_translations(
            password_change_confirmation_view,
            "title", "Password Change Confirmation view title"
        )
        password_change_confirmation_view.insert()

        # Create standard resources
        site_stylesheet = URI()
        site_stylesheet.uri = uri + "resources/styles/site.css"
        site_stylesheet.mime_type = "text/css"
        site_stylesheet.qname = "woost.site_stylesheet"
        set_translations(site_stylesheet, "title", "Site style sheet title")
        site_stylesheet.insert()

        # Create the temporary home page
        site.home = StandardPage()
        site.home.template = std_template
        site.home.qname = "woost.home"
        set_translations(site.home, "title", "Home page title")
        set_translations(site.home, "inner_title", "Home page inner title")
        set_translations(
            site.home, "body", "Home page body",
            uri = uri + "cms"
        )
        site.home.branch_resources.append(site_stylesheet)
        site.home.insert()
    
        # Create the back office interface
        back_office = Document()
        back_office.controller = back_office_controller
        back_office.critical = True
        back_office.qname = "woost.backoffice"
        back_office.per_language_publication = False
        back_office.parent = site.home
        back_office.hidden = True
        back_office.path = u"cms"
        back_office.inherit_resources = False
        set_translations(back_office, "title", "Back office title")
        back_office.insert()
        
        # Create the user styles dynamic style sheet
        user_styles = Document()
        user_styles.critical = True
        user_styles.qname = "woost.user_styles"
        user_styles.per_language_publication = False
        user_styles.parent = site.home
        user_styles.controller = \
            Controller.get_instance(qname = "woost.styles_controller")
        user_styles.hidden = True
        user_styles.path = u"user_styles"
        user_styles.mime_type = "text/css"
        user_styles.caching_policies.append(
            CachingPolicy(
                server_side_cache = True,
                last_update_expression =
                    "from woost.models import Style\n"
                    "last_update = [publishable, latest(Style)]\n"
            )
        )
        set_translations(user_styles, "title", "User styles title")
        user_styles.insert()

        # Create the web services page
        webservices = Document()
        webservices.critical = True
        webservices.qname = "woost.webservices"
        webservices.parent = site.home
        webservices.controller = \
            Controller.get_instance(qname = "woost.webservices_controller")
        webservices.hidden = True
        webservices.path = u"services"
        webservices.mime_type = "application/json"
        set_translations(webservices, "title", "Web services title")
        webservices.insert()

        # Create the 'content not found' page
        site.not_found_error_page = StandardPage()
        site.not_found_error_page.parent = site.home
        site.not_found_error_page.hidden = True
        site.not_found_error_page.template = std_template
        site.not_found_error_page.qname = "woost.not_found_error_page"
        set_translations(site.not_found_error_page, "title",
            "Not found error page title")
        set_translations(site.not_found_error_page, "body",
            "Not found error page body")            
        site.not_found_error_page.insert()

        # Create forbidden error page
        site.forbidden_error_page = StandardPage()
        site.forbidden_error_page.parent = site.home
        site.forbidden_error_page.hidden = True
        site.forbidden_error_page.template = std_template
        site.forbidden_error_page.qname = "woost.forbidden_error_page"
        set_translations(site.forbidden_error_page, "title",
            "Forbidden error page title")
        set_translations(site.forbidden_error_page, "body",
            "Forbidden error page body")
        site.forbidden_error_page.insert()

        # Create the password change request page
        site.password_change_page = StandardPage()
        site.password_change_page.parent = site.home
        site.password_change_page.hidden = True
        site.password_change_page.template = password_change_request_view
        site.password_change_page.controller = \
            Controller.get_instance(qname='woost.passwordchange_controller')
        site.password_change_page.qname = "woost.password_change_page"
        site.password_change_page.per_language_publication = False
        set_translations(site.password_change_page, "title",
            "Password Change page title")
        set_translations(site.password_change_page, "body",
            "Password Change page body")
        site.password_change_page.insert()

        # Create the password change confirmation page
        site.password_change_confirmation_page = StandardPage()
        site.password_change_confirmation_page.parent = site.home
        site.password_change_confirmation_page.hidden = True
        site.password_change_confirmation_page.per_language_publication = False
        site.password_change_confirmation_page.template = \
            password_change_confirmation_view
        site.password_change_confirmation_page.controller = \
            Controller.get_instance(
                qname='woost.passwordchangeconfirmation_controller'
            )
        site.password_change_confirmation_page.qname = \
            "woost.password_change_confirmation_page"
        set_translations(site.password_change_confirmation_page, "title",
            "Password Change Confirmation page title")
        set_translations(site.password_change_confirmation_page, "body",
            "Password Change Confirmation page body")
        site.password_change_confirmation_page.insert()

        # Create the login page
        site.login_page = StandardPage()
        site.login_page.parent = site.home
        site.login_page.hidden = True
        site.login_page.template = login_form_template 
        site.login_page.controller = \
            Controller.get_instance(qname='woost.login_controller')
        site.login_page.qname = "woost.login_page"
        set_translations(site.login_page, "title", "Login page title")
        site.login_page.insert()

        # Create site-wide user views
        own_items_view = UserView()
        own_items_view.roles.append(everybody_role)
        own_items_view.parameters = {
            "type": "woost.models.item.Item",
            "content_view": "flat",
            "filter": "owned-items",
            "order": "-last_update_time",
            "members": None
        }
        set_translations(
            own_items_view,
            "title",
            "Own items user view"
        )
        own_items_view.insert()
        
        page_tree_view = UserView()
        page_tree_view.roles.append(everybody_role)
        page_tree_view.parameters = {
            "type": "woost.models.publishable.Publishable",
            "content_view": "tree",
            "filter": None,
            "members": None
        }
        set_translations(
            page_tree_view,
            "title",
            "Page tree user view"
        )
        page_tree_view.insert()

        file_gallery_view = UserView()
        file_gallery_view.roles.append(everybody_role)
        file_gallery_view.parameters = {
            "type": "woost.models.file.File",
            "content_view": "thumbnails",
            "filter": None,
            "order": None,
            "members": None
        }
        set_translations(
            file_gallery_view,
            "title",
            "File gallery user view"
        )
        file_gallery_view.insert()
    
    # Enable the selected extensions
    if extensions:
        load_extensions()
        for extension in Extension.select():
            ext_name = extension.__class__.__name__[:-len("Extension")].lower()
            if ext_name in extensions:
                extension.enabled = True

    mark_all_migrations_as_executed()
    datastore.commit()

def random_string(length, source = letters + digits + "!?.-$#&@*"):
    return "".join(choice(source) for i in range(length))

def main():
 
    parser = OptionParser()
    parser.add_option("-u", "--user", help = "Administrator email")
    parser.add_option("-p", "--password", help = "Administrator password")
    parser.add_option("-l", "--languages",
        help = "Comma separated list of languages")
    parser.add_option("-t", "--template-engine",
        default = "cocktail",
        help = "The buffet templating engine to use by default")
    parser.add_option("-e", "--extensions",
        default = "",
        help = "The list of extensions to enable")
    
    options, args = parser.parse_args()

    admin_email = options.user
    admin_password = options.password
    
    if admin_email is None:
        admin_email = raw_input("Administrator email: ") or "admin@localhost"

    if admin_password is None:
        admin_password = raw_input("Administrator password: ") \
            or random_string(8)

    languages = options.languages \
        and options.languages.replace(",", " ") \
        or raw_input("Languages: ") or "en"

    init_site(
        admin_email,
        admin_password,
        languages.split(),
        template_engine = options.template_engine,
        extensions = options.extensions.split(",")
    )
    
    print u"Your site has been successfully created. You can start it by " \
          u"executing the 'run.py' script. An administrator account for the " \
          u"content manager interface has been generated, with the " \
          u"following credentials:\n\n" \
          u"\tEmail:     %s\n" \
          u"\tPassword:  %s\n\n" % (admin_email, admin_password)

if __name__ == "__main__":
    main()

