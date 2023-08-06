#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os

if hasattr(os, "symlink"):
    from cocktail.styled import styled
    from cocktail.events import when
    from cocktail.persistence import datastore
    from woost import app
    from woost.models.publishable import Publishable
    from woost.models.site import Site
    from woost.models.file import File
    from woost.models.user import User
    from woost.models.rendering.cache import require_rendering

    debug = True
    filesystem_encoding = "utf-8"

    members_affecting_static_publication = set([
        File.title,
        File.file_name,
        File.image_effects,
        Publishable.enabled,
        Publishable.start_date,
        Publishable.end_date
    ])

    @when(File.inserted)
    @when(File.changed)
    @when(File.deleting)
    def _schedule_links_update(e):
     
        file = e.source
        member = getattr(e, "member", None)

        if member is not None:

            if not file.is_inserted:
                return

            if member not in members_affecting_static_publication:
                return  

        # Store the current links, to be removed when the current transaction is
        # committed
        key = "woost.models.File.old_links-%d" % file.id
        old_links = datastore.get_transaction_value(key)

        if old_links is None:
            old_links = set()
            datastore.set_transaction_value(key, old_links)

        old_links.update(get_links(file))
        
        # Add an after commit hook to remove/create the file's links
        datastore.unique_after_commit_hook(
            "woost.models.File.update_static_links-%d" % file.id,
            _update_links_after_commit,
            file,
            old_links
        )

    def _update_links_after_commit(commit_successful, file, old_links):
        if commit_successful:
            remove_links(file, old_links)
            create_links(file)

    def encode_filename(link, encoding = None):
        if encoding is None:
            encoding = filesystem_encoding
        return link.encode(encoding) if isinstance(link, unicode) else link

    def create_links(file, links = None, encoding = None):
        
        if not file.is_inserted:
            return

        anonymous = User.require_instance(qname = "woost.anonymous_user")

        if not file.is_accessible(anonymous):
            return

        if links is None:
            links = get_links(file)

        if file.image_effects:
            linked_file = require_rendering(file)
        else:
            linked_file = file.file_path

        linked_file = encode_filename(linked_file, encoding)

        for link in links:

            link = encode_filename(link, encoding)

            if debug:
                print styled("STATIC PUBLICATION", "white", "green"),
                print "Adding link for #%s (%s -> %s)" % (
                    styled(file.id, style = "bold"),
                    styled(link, "yellow"),
                    styled(linked_file, "brown")
                )

            # Delete the link if it already existed
            try:
                os.remove(link)
            except OSError:
                pass

            # Create the new link
            os.symlink(linked_file, link)

    def remove_links(file, links = None, encoding = None):
        
        if links is None:
            links = get_links(file)

        for link in links:
            link = encode_filename(link, encoding)
            if os.path.lexists(link):
                if debug:
                    print styled("STATIC PUBLICATION", "white", "red"),
                    print "Removing link for #%s (%s)" % (
                        styled(file.id, style = "bold"),
                        styled(link, "yellow")
                    )
                os.remove(link)

    def get_links(file):    
        site = Site.main
        return [
            app.path("static", site.main.get_path(file, language))
            for language in (file.translations or [None])
        ]

