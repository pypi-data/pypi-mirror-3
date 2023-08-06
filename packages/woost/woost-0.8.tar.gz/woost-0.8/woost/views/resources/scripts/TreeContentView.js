/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
-----------------------------------------------------------------------------*/

// Submitting the search form in a tree view automatically expands the tree to
// show all results
cocktail.bind(".TreeContentView", function ($contentView) {

    var form = this;

    function expand() {
        $contentView.find("input[name=expanded]").remove();
        form.setParameter("expanded", "all", true);
    }

    var $searchForms = $contentView.find(".filters")
                       .add($contentView.find(".simple_search"));

    $searchForms.find(".search_button").click(expand);
    $searchForms.keypress(function (e) {
        if (e.keyCode == 13) {
            expand();
        }
    });
});

