/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".EditPanel", function ($panel) {
    
    this.getExpanded = function () {
        return $panel.hasClass("expanded");
    }

    this.setExpanded = function (expanded) {
        if (expanded) {    
            $panel.addClass("expanded");
            jQuery(document.body).addClass("editing");
        }
        else {
            $panel.removeClass("expanded");
            jQuery(document.body).removeClass("editing");
        }
    }

    this.toggleExpanded = function () {
        this.setExpanded(!this.getExpanded());
    }

    // Create a button to show the panel
    jQuery(cocktail.instantiate("woost.views.EditPanel.show_panel_button"))
        .mouseover(function () { $panel.get(0).setExpanded(true); })
        .click(function () { $panel.get(0).setExpanded(true); })
        .appendTo($panel);

    // Create a button to close the panel
    jQuery(cocktail.instantiate("woost.views.EditPanel.close_panel_button"))
        .click(function () { $panel.get(0).setExpanded(false); })
        .appendTo($panel);
});

jQuery(function () {
    
    // Toggle the visibility of edit panels with a keyboard shortcut
    jQuery(document).keydown(function (e) {
        if (e.keyCode == 69 && e.shiftKey && e.altKey) {
            jQuery(document).find(".EditPanel").each(function () {
                this.toggleExpanded();
            });
            return false;
        }
    });

    // Collapse all edit panels when the document is clicked
    jQuery(document).click(function (e) {
        if (!jQuery(e.target).closest(".EditPanel").length) {
            jQuery(document).find(".EditPanel.expanded").each(function () {
                this.setExpanded(false);
            });
        }
    });
});

