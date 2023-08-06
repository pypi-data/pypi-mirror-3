# -*- coding: utf-8 -*-
<%!
from cocktail.translations import (
    translations,
    get_language,
    require_language
)
from woost.models import Site, Publishable, Language

output_format = "html4"
container_classes = "BaseView"
site = Site.main
xmlns_definitions = ({
    "xml:lang": get_language(),
    "xmlns":"http://www.w3.org/199/xhtml"
})
translation_members = ("body",)
%>

<%
self.language = get_language()
self.content_language = self.get_content_language(publishable)
self.fully_translated = (self.content_language == self.language)
%>

<%def name="get_content_language(item, language = None)">
    <%
    return item.get_common_language(self.attr.translation_members, language)
    %>
</%def>

<%def name="is_fully_translated(item, language = None)">
    <%
    language = require_language(language)
    return self.get_content_language(item, language) == language
    %>
</%def>

<%def name="member_slot(key, use_fallback_language = True)">
    <%
    member = publishable.__class__[key]
    language = (
        member.translated
        and not self.fully_translated
        and use_fallback_language
        and self.content_language
    )    
    %>
    <div class="${key}_slot"${' lang="%s"' % language if language else ""}>
        ${publishable.get(key, language) or ""}
    </div>
</%def>

<%def name="closure()" filter="trim">
    ${"/" if self.attr.output_format == "xhtml" else ""}
</%def>

${self.dtd()}

<%def name="htmltag(xmlnsdefs)" >
    <% 
    ns_attributes = ''

    if self.attr.output_format == "xhtml":        
        ns_attributes = " ".join('%s="%s"' % item for item in xmlnsdefs.iteritems())
    %>
    <html ${ns_attributes} lang="${self.content_language}">
</%def>
${self.htmltag(self.attr.xmlns_definitions)}
    
    <head>        
        ${self.meta()}
        ${self.resources()}        
    </head>

    <body>
        <div class="${self.attr.container_classes}">
            ${self.container()}
        </div>
        ${body_end_html or ""}
    </body>

</html>

<%def name="getTitle()">
    ${publishable.title}
</%def>

<%def name="get_keywords()">
    <%
        keywords = []
        site_keywords = site.keywords
        if site_keywords:
            keywords.append(site_keywords)
        item_keywords = getattr(publishable, "keywords", None)
        if item_keywords:
            keywords.append(item_keywords)
        return " ".join(keywords) if keywords else None
    %>
</%def>

<%def name="dtd()">
    % if self.attr.output_format == "xhtml":
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    % else:
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> 
    % endif
</%def>

<%def name="meta()">
    
    <meta http-equiv="Content-Type" content="${publishable.mime_type};charset=${publishable.encoding}"${closure()}>
    <meta name="Content-Language" content="${self.language}"${closure()}>
    <title>${self.getTitle()}</title>

    <%
        description = getattr(publishable, "description", None) or site.description
    %>
    % if description:
        <meta name="description" content="${description}"${closure()}>
    % endif
    
    <%            
    keywords = self.get_keywords()
    %>
    % if keywords:
        <meta name="keywords" content="${keywords}"${closure()}>
    % endif

    <%
    robots_should_index = getattr(publishable, "robots_should_index", True)
    robots_should_follow = getattr(publishable, "robots_should_follow", True)
    %>
    % if not robots_should_index or not robots_should_follow:
        <meta name="robots" content="${"%s, %s" % (robots_should_index and "index" or "noindex", robots_should_follow and "follow" or "nofollow")}"${closure()}>
    % endif
    
    <link rel="start" title="${site.home.title}" href="/"${closure()}>
    
    ## Alternate languages
    % if publishable.per_language_publication:
        % for trans_lang in publishable.translations:
            % if trans_lang in Language.codes and trans_lang != language and publishable.get("translation_enabled", trans_lang) and self.is_fully_translated(publishable, trans_lang):
                <link rel="${'canonical' if not self.fully_translated and trans_lang == self.content_language else 'alternate'}"
                      title="${translations('woost.views.BaseView alternate language link', language = trans_lang, lang = trans_lang)}"
                      href="${cms.translate_uri(language = trans_lang)}"
                      lang="${trans_lang}"
                      hreflang="${trans_lang}"${closure()}>
            % endif
        % endfor
    % endif

    ## Shortcut icon
    <%
    icon = site.icon
    %>
    % if icon:                
        <link rel="Shortcut Icon" type="${icon.mime_type}" href="${cms.uri(icon)}"${closure()}>
    % endif

    ## Base tag
    % if base_url:
        <base href="${base_url}"${closure()}>
    % endif
</%def>

<%def name="resource_markup(uri, mime_type = None)">
    % if mime_type == "text/css" or uri.endswith(".css"):
        <link rel="Stylesheet" type="${mime_type or 'text/css'}" href="${uri}"${closure()}>
    % elif mime_type in ("text/javascript", "application/javascript", "text/ecmascript", "application/jscript") or uri.endswith(".js"):
        <script type="${mime_type or 'text/javascript'}" src="${uri}"></script>
    % endif
</%def>

<%def name="resources()">

    ## Resources
    % for resource in publishable.resources:
        ${resource_markup(resource.uri)}
    % endfor
    
    ## User defined styles for user content
    <%
    user_styles = Publishable.get_instance(qname = "woost.user_styles")
    %>
    % if user_styles:
        <link rel="Stylesheet" type="${user_styles.mime_type}" href="${cms.uri(user_styles)}"${closure()}>
    % endif
</%def>

<%def name="container()">
    ${self.content()}
</%def>

<%def name="content()">
    ${member_slot("body")}
</%def>

