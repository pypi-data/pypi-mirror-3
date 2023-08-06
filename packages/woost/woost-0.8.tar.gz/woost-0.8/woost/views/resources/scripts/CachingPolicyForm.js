/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".CachingPolicyForm", function ($form) {

    $form.find(".cache_enabled_field").each(function () {

        function setExpanded(expanded, speed) {
            $form
                .find(".server_side_cache_field")
                .add($form.find(".cache_expiration_field"))
                .add($form.find(".last_update_expression_field"))
                .add($form.find(".cache_key_expression_field"))
                [expanded ? "show" : "hide"](speed);
        }

        jQuery(this).find("input.control")
            .click(function () { setExpanded(this.checked, "slow"); })
            .each(function () { setExpanded(this.checked); });
    });
});

