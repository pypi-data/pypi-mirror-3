/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".EditPanel", function ($panel) {

    var highlightedBlock = null;

    this.getHighlightedBlock = function () {
        return highlightedBlock;
    }

    this.setHighlightedBlock = function (block) {
        if (block != highlightedBlock) {
            if (highlightedBlock) {
                $panel.find(".block_entry_" + highlightedBlock.blockId).removeClass("highlighted");
                jQuery(highlightedBlock).removeClass("highlighted_block");
            }
            if (block) {
                $panel.find(".block_entry_" + block.blockId).addClass("highlighted");
                jQuery(block).addClass("highlighted_block");
            }
            highlightedBlock = block;
        }
    }

    $panel.find(".block_tree .entry_label") 
        .hover(
            function () {
                var $entry = jQuery(this).closest("li");
                $panel.get(0).setHighlightedBlock(
                    jQuery(".block" + $entry.get(0).blockId).get(0)
                );
            },
            function () {
                $panel.get(0).setHighlightedBlock(null);
            }
        );
});

cocktail.bind(".block", function ($block) {
    $block
        .click(function (e) {
            if (jQuery(this).closest("body.editing").length) {
                location.href = jQuery(".block_entry_" + this.blockId + " a").attr("href");
                return false;
            }
        })
        .mouseenter(function () {
            if (jQuery(this).closest("body.editing").length) {
                jQuery(".EditPanel").get(0).setHighlightedBlock(this);
            }
        })
        .mouseleave(function (e) {
            if (jQuery(this).closest("body.editing").length) {
                var nextBlock = jQuery(e.relatedTarget).closest(".block").get(0);
                jQuery(".EditPanel").get(0).setHighlightedBlock(nextBlock);
            }
        });
});


