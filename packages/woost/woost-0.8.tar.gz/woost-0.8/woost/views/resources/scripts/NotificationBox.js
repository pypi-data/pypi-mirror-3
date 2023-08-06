/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".NotificationBox", function ($notificationBox) {
    // Hide transient notifications
    setTimeout(
        function () { $notificationBox.find(".notification.transient").hide("slow"); },
        this.notificationTimeout || 2000
    );
});

