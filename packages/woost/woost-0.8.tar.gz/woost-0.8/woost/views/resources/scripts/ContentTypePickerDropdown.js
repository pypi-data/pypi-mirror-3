/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".ContentTypePickerDropdown", function ($dropdown) {
    
    var $picker = $dropdown.find(".ContentTypePicker");

    function showSelection() {
        var $selected = $picker.find("input:checked").parent();
        $dropdown.find(".button .label").first().html(
            $selected.find("label").html()
        );
    }

    $picker.find("input").live("click", function () {
        showSelection();
        $dropdown.get(0).setCollapsed(true);
    });

    showSelection();
});

