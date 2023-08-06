/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".BackOfficeItemView", function ($itemView) {
    
    // Pending changes control
    var itemView = jQuery(".BackOfficeItemView").get(0);
    
    if (itemView.closingItemRequiresConfirmation) {
        var hasPendingChanges = itemView.hasPendingChanges;
        var NAVIGATE_AWAY = 0;
        var SUBMIT_CLOSING = 1;
        var SUBMIT_PRESERVING = 2;
        var departureManner = NAVIGATE_AWAY;

        $itemView.find("form").submit(function () {
            if (departureManner != SUBMIT_CLOSING) {
                departureManner = SUBMIT_PRESERVING;
            }
        });

        $itemView.find(".action_button").click(function () {
            if (this.value == "close") {
                departureManner = SUBMIT_CLOSING;
            }
            else {
                departureManner = SUBMIT_PRESERVING;
            }
        });

        window.onbeforeunload = function () {
            if (hasPendingChanges && departureManner != SUBMIT_PRESERVING) {
                return cocktail.translate("woost.views.BackOfficeItemView pending changes warning");
            }
        }
    }
});

