/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

// The client side implementation for the filter box breaks with item
// selectors. This makes the two work together, and uses a modal dialog
// approach which clarifies the selection process a bit.
cocktail.bind(".UserFilterEntry .ItemSelector", function ($itemSelector) {

    var selectorIframe;
    var param;

    this.clear = function () {
        $itemSelector.find(".ItemLabel").html(this.emptyLabel);
        $itemSelector.find("input[type=hidden]").val("");
    }

    this.setItem = function (itemId, label) {
        
        var itemLabel = $itemSelector.find(".ItemLabel").get(0);
        jQuery(itemLabel).empty();

        var icon = document.createElement("img");
        icon.className = "icon";
        icon.src = "/images/" + itemId + "/backoffice_small_thumbnail";
        itemLabel.appendChild(icon);

        itemLabel.appendChild(document.createTextNode(label));

        $itemSelector.find("input[type=hidden]").val(itemId);
    }

    $itemSelector.find(".ItemSelector-button.select").click(function (e) {

        button = this;

        var win = window;
        var depth = 0;
        while (win != window.top) {
            depth++;
            win = win.parent;
        }
        
        selectorIframe = cocktail.createElement("iframe", "ItemSelector-frame" + depth);
        selectorIframe.className = "ItemSelector-frame";
        cocktail.showDialog(selectorIframe);

        function closeDialog() {
            cocktail.closeDialog();
            form.target = prevTarget;
            form.removeChild(param);
        }

        jQuery(selectorIframe).load(function () {
            var iframeJQuery = this.contentWindow.jQuery;
            iframeJQuery(".select_action").click(function () {
                var sel = iframeJQuery(".collection_display").get(0).getSelection();
                if (sel.length) {
                    var id = sel[0].id;
                    var label = iframeJQuery("label", sel[0]).text();
                    $itemSelector.get(0).setItem(id, label);
                }
                else {
                    $itemSelector.get(0).clear();
                }
                closeDialog();
                return false;
            });
            iframeJQuery(".cancel_action").click(function () {
                closeDialog();
                return false;
            });
        });
        
        var form = jQuery(this).parents("form").get(0);
        var prevTarget = form.target;
        param = cocktail.createElement("input", "client_side_scripting", "hidden");
        param.value = "true";
        form.appendChild(param);
        form.target = selectorIframe.name;
    });
});

