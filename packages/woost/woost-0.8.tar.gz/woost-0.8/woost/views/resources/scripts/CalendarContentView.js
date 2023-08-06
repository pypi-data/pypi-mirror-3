/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".CalendarContentView", function ($contentView) {
        
    var contentView = this;

    $contentView.find("select[name=month]").change(function () {
        jQuery(this).parents("form").submit();
    });
    
    $contentView.find(".month_calendar td").dblclick(function () {
        location.href = cms_uri + "/content/new/fields"
            + "?item_type=" + contentView.contentType
            + "&edited_item_" + contentView.dateMembers[0]
            + "=" + this.date;
    });

    $contentView.find(".year_calendar .month_calendar .has_entries").each(function () {
        var $entries = jQuery(this).find(".entries");
        jQuery(this).find(".day").click(function () {
            $entries.toggle();
            return false;
        });
    });
});

cocktail.bind("body", function () {    
    jQuery(document).click(function () {
        jQuery(".year_calendar .month_calendar .entries").hide();
    });
});

