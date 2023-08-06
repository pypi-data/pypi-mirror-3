/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".TwitterPublicationView", function ($view) {

    var $resultsTable = $view.find(".results_table");
    var $form = $view.find(".publication_form")
    var $submitButtons = $form.find(".buttons button:not(:first)");
    var closing = false;

    if (this.action == "publish" && $resultsTable.length) {
        
        var $fields = $view.find(".publication_form .fields");
        $fields.hide();

        $submitButtons.hide();

        var $publishAgainLink = jQuery(cocktail.instantiate(
            "woost.extensions.twitterpublication.TwitterPublicationView.publish_again_link"
        ));
        $publishAgainLink.click(function () {
            $publishAgainLink.remove();
            $submitButtons.show();
            $fields.show();
            return false;
        });
        $form.find(".buttons").append($publishAgainLink);
    }

    $form.find(".buttons button:first").click(function () {
        closing = true;
    });

    $view.find(".publication_form").submit(function () {
        
        if (!closing) {
            var $sign = jQuery(cocktail.instantiate(
                "woost.extensions.twitterpublication.TwitterPublicationView.loading_sign"
            ));
            $form.append(jQuery("<div class='disabling_layer'>"))
            $form.before($sign);

            $resultsTable.hide();
        }

        return true;
    });
});

