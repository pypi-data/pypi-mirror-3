/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

cocktail.bind({
    selector: ".BackOfficeLayout",
    behavior: function ($layout) {

        // Disable browser's in-memory caching due to problems going backward 
        // and forward between visited pages
        jQuery(window).unload(function() {});

        // Keep alive the current edit_stack
        if (this.edit_stack)
            setTimeout("keepalive('" + this.edit_stack + "')", 300000);
    },
    parts: {
        ".notification:not(.transient)": function ($notification) {

            var closeButton = document.createElement("img");
            closeButton.className = "close_button";
            closeButton.src = "/resources/images/close_small.png";
            $notification.prepend(closeButton);

            jQuery(closeButton).click(function () {
                $notification.hide("slow");
            });
        }
    }
});

function keepalive(edit_stack) {
    var remoteURL = '/cms/keep_alive?edit_stack=' + edit_stack;
    jQuery.get(remoteURL, function(data) { setTimeout("keepalive('" + edit_stack + "')", 300000); });
}
