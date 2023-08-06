/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
-----------------------------------------------------------------------------*/

cocktail.bind(".ContentTypePicker", function ($picker) {

    function redrawSelection() {
        $picker.find("label.selected").removeClass("selected");
        $picker.find("input:checked").siblings("label").addClass("selected");
    }

    $picker.find("label").attr("tabindex", "0");

    $picker.find("li").each(function () {

        var collapsed = true;

        this.toggle = function (speed /* optional */) {
            this.setCollapsed(!collapsed, speed);
        }
        
        this.getCollapsed = function () {
            return collapsed;
        }

        this.setCollapsed = function (value, speed /* optional */) {
            collapsed = value;
            jQuery(this).children(".toggle_button").attr(
                "src", "/resources/images/" + (collapsed ? "collapsed" : "expanded") + ".png"
            );
            jQuery(this).children("ul")[collapsed ? "hide" : "show"](speed);
        }

        jQuery(this).children("input").change(redrawSelection);           

        if (jQuery(this).children("ul").length) {
            var $img = jQuery("<img>")
                .addClass("toggle_button")
                .attr("src", "/resources/images/collapsed.png")
                .attr("tabindex", "0")
                .click(function (e) {
                    jQuery(this).closest("li").get(0).toggle(300);
                    e.stopPropagation();
                })
                .prependTo(this);

            if (jQuery(this).find("ul input:checked").length) {
                this.setCollapsed(false);
            }
        }
        else {
            jQuery(this).addClass("empty_item");
        }
    });

    redrawSelection();
});

