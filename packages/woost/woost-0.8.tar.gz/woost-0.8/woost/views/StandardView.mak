#-*- coding: utf-8 -*-
<%inherit file="BaseView.mak"/>

<%!
from cocktail.translations import translations
from cocktail.html import templates
from woost.models import Site, Publishable, ModifyPermission

container_classes = "BaseView StandardView"
%>

<%def name="container()">
    
    <div class="header">
        ${self.header()}
    </div>

    ${self.menu()}

    <div class="main">
        ${self.main()}
    </div>

    <div class="footer">
        ${self.footer()}
    </div>

</%def>

<%def name="header()">    
    ${self.site_title()}
    ${self.identity()}
    ${self.language_selector()}
</%def>

<%def name="site_title()">
    <h1><a href="/">${Site.main.home.title}</a></h1>
</%def>

<%def name="language_selector()">
    ${self.create_language_selector().render()}
</%def>

<%def name="create_language_selector()">
    <%
    selector = templates.new("woost.views.LanguageSelector")
    selector.add_class("language_selector")
    return selector
    %>
</%def>

<%def name="identity()">
    % if (show_user_controls is UNDEFINED or show_user_controls) and user and not user.anonymous:
        <div class="identity">        
            <strong>${translations(user)}</strong>
            <form method="post">
                <div>
                    <button class="logout_button" name="logout" type="submit">
                        ${translations("Logout")}
                    </button>
                </div>
            </form>
        </div>
    % endif
</%def>

<%def name="create_menu()">
    <%
    menu = templates.new("woost.views.Menu")
    menu.add_class("menu")
    menu.root_visible = False
    menu.collapsible = True
    return menu
    %>
</%def>

<%def name="menu()">
    ${self.create_menu().render()}
</%def>

<%def name="publishable_title()">
    <%
    title = getattr(publishable, "inner_title", None) or translations(publishable)
    %>
    %if title:
        <h2>${title}</h2>
    %endif
</%def>

<%def name="fallback_language_notice()">
    <div class="fallback_language_notice notice">
        ${translations("woost.views.StandardView fallback language notice", fallback = self.content_language)}
    </div>
</%def>

<%def name="toolbar()">
    % if (show_user_controls is UNDEFINED or show_user_controls) and user.has_permission(ModifyPermission, target = publishable):
        <div class="toolbar">
            <% backoffice = Publishable.get_instance(qname = "woost.backoffice") %>
            <a class="edit_link"
               href="${cms.uri(backoffice, 'content', publishable.id, 'fields')}">
                ${translations("Action edit")}
            </a>            
        </div>
    % endif
</%def>

<%def name="main()">
   
    ${self.publishable_title()}
    
    % if not self.fully_translated:
        ${self.fallback_language_notice()}
    % endif
        
    ${self.toolbar()}

    <div class="content">
        ${self.content()}
    </div>

    ${self.attachments()}
</%def>

<%def name="attachments()">
    <%
    attachments = [attachment
                   for attachment in publishable.attachments
                   if attachment.is_published()]
    %>
    % if attachments:
        <ul class="attachments">
            % for attachment in attachments:
                <li>
                    <a href="${cms.uri(attachment)}">
                        <img
                            src="${attachment.get_image_uri('icon16')}"
                            alt="${translations('woost.views.StandardView attachment icon description')}"/>
                        <span>${translations(attachment)}</span>
                    </a>
                </li>
            % endfor
        </ul>
    % endif
</%def>

<%def name="footer()">
</%def>

