/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".ImageEffectsEditor", function ($editor) {

    var dialog = null;
    var $dialog = null;
    var accepted = false;

    jQuery("<button class='edit_button' type='button'>")
        .html(cocktail.translate("woost.views.ImageEffectsEditor.edit_button"))
        .click(function () {
            if (!dialog) {
                createDialog();
            }
            cocktail.showDialog(dialog);

            if (accepted) {
                accepted = false;
            }
            else {
                applyStack($editor.get(0).stack);
            }

            $dialog.find(".image_effect_button").first().focus();
            $editor.get(0).repaint();
        })
        .appendTo($editor);

    var $effectsSummary = jQuery("<div class='effects_summary'>")
        .insertBefore($editor.find(".edit_button"));

    function createDialog() {
        
        dialog = cocktail.instantiate("woost.views.ImageEffectsEditor.imageEffectsDialog");
        dialog.imageEffectsEditor = $editor.get(0);
        $dialog = jQuery(dialog);
        
        $dialog.find(".edited_image").load(function () {
            $dialog.find(".status_bar").empty();
        });

        $dialog.find(".image_effect_button")
            .click(function () {
                createEffectControl(this.imageEffect, function () {
                    jQuery(this).find("input").first().focus();
                });
            });
        
        $dialog.find(".preview_button").click(function () {
            $editor.get(0).repaint();
        });

        $dialog.find(".cancel_button").click(function () {
            cocktail.closeDialog();
        });

        $dialog.find(".accept_button").click(function () {
            accepted = true;
            saveStack();
            cocktail.closeDialog();
        });
        
        return dialog;
    }

    function createEffectControl(imageEffect, callback) {

        var effectControl = cocktail.instantiate(
            "woost.views.ImageEffectsEditor-" + imageEffect + "Control",
            null,
            function () {
                jQuery(this)
                    .hide()
                    .appendTo($dialog.find(".stack_box"));
            }
        );
        effectControl.imageEffect = imageEffect;
        var stackBox = $dialog.find(".stack_box").get(0);
        stackBox.scrollTop = stackBox.scrollHeight;
        jQuery(effectControl)
            .show("fast", function () {
                if (callback) {
                    callback.call(effectControl);
                }
                stackBox.scrollTop = stackBox.scrollHeight;
            });
        
        return effectControl;
    }

    this.repaint = function () {        
        var stack = getStack();
        var imageURI = "/image_effects/" + $editor.get(0).editedItemId + "/" + serializeStack(stack) + "?override=true";
        $dialog.find(".status_bar").html(cocktail.translate("woost.views.ImageEffectsEditor-loading"));
        $dialog.find(".edited_image").attr("src", imageURI);
    }
    
    this.removeEffect = function (index) {
        var $control = jQuery($dialog.find(".stack_box").get(0).childNodes[index]);
        $control.hide("fast", function () {
            $control.remove();
        });
    }

    function getStack() {
        var stack = [];
        $dialog.find(".stack_box").children().each(function () {
            stack.push(this.makeStackNode());
        });
        return stack;
    }

    function saveStack() {
        var stack = getStack();
        $editor.get(0).stack = stack;
        $editor.find("input.input").val(serializeStack(stack));
        updateSummary();
    }

    function updateSummary() {
        $effectsSummary.empty();
        var stack = $editor.get(0).stack;
        for (var i = 0; i < stack.length; i++) {
            var imageEffect = stack[i][0];
            jQuery("<div class='effects_summary_entry'>")
                .append(
                    jQuery("<img>")
                        .attr("src", "/resources/images/image-effect-" + imageEffect + ".png")
                        .attr("alt", "")
                )
                .append(
                    jQuery("<span>")
                        .html(cocktail.translate("woost.views.ImageEffectsEditor-" + imageEffect + "_effect"))
                )
                .appendTo($effectsSummary);
        }
    }

    function applyStack(stack) {

        $dialog.find(".stack_box").empty();

        for (var i = 0; i < stack.length; i++) {
            var node = stack[i];
            var control = createEffectControl(node[0]);
            control.applyStackNode(node);
        }

        $editor.get(0).repaint();
    }

    function serializeStack(stack) {
        
        var str = "";
        
        for (var i = 0; i < stack.length; i++) {
            var effectEntry = stack[i];
            if (i > 0) {
                str += "/";
            }
            str += effectEntry[0];
            if (effectEntry.length > 1) {            
                str += "(";
                for (var j = 1; j < effectEntry.length; j++) {
                    if (j > 1) {
                        str += ",";
                    }
                    str += effectEntry[j];
                }
                str += ")";
            }
        }

        return str;
    }

    updateSummary();
});

cocktail.bind(".image_effects_dialog .image_effect_control", function ($control) {
    
    var editor = $control.closest(".image_effects_dialog").get(0).imageEffectsEditor;
        
    $control.find("input")
        .live("keydown", function (e) {
            if (
                e.keyCode == 13 
                && (this.type == "text" || this.type == "number")
            ) {
                editor.repaint();
                return false;
            }
        });
    
    $control.find(".remove_button").click(function () {
        editor.removeEffect($control.index());
    });
});

cocktail.bind(".image_effects_dialog .brightness_control", function ($control) {

    this.makeStackNode = function () {
        return [this.imageEffect, Number($control.find("input").val()).toFixed(2)];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(Number(node[1]));
    }
});

cocktail.bind(".image_effects_dialog .sharpness_control", function ($control) {

    this.makeStackNode = function () {
        return [this.imageEffect, Number($control.find("input").val()).toFixed(2)];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(Number(node[1]));
    }
});

cocktail.bind(".image_effects_dialog .color_control", function ($control) {

    this.makeStackNode = function () {
        return [this.imageEffect, Number($control.find("input").val()).toFixed(2)];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(Number(node[1]));
    }
});

cocktail.bind(".image_effects_dialog .contrast_control", function ($control) {

    this.makeStackNode = function () {
        return [this.imageEffect, Number($control.find("input").val()).toFixed(2)];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(Number(node[1]));
    }
});

cocktail.bind(".image_effects_dialog .rotate_control", function ($control) {

    this.makeStackNode = function () {
        return [this.imageEffect, Number($control.find("input").val())];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(Number(node[1]));
        repaintAngle();
    }
 
    function repaintAngle() {
        var canvas = $control.find(".angle_selector").get(0);
        var ctx = canvas.getContext('2d');
        var cx = canvas.width / 2;
        var cy = canvas.height / 2;
        var r = canvas.width / 2 - 2;
        var angle = Number($control.find("input").val());
        var rads = (Math.PI / 180) * angle;
        ctx.fillStyle = "#e3dac8";
        ctx.strokeStyle = "#cbbb9c";
        ctx.lineWidth = 2;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2, false);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(cx, cy, 3, 0, Math.PI * 2, false);
        ctx.fillStyle = "#590000";
        ctx.fill();
        ctx.beginPath();
        ctx.strokeStyle = "#590000";
        ctx.moveTo(cx, cx);
        ctx.lineTo(cx + r * Math.cos(rads), cy - r * Math.sin(rads));
        ctx.stroke();
    }
    
    $control.find("input")
        .change(repaintAngle)
        .blur(repaintAngle)
        .keydown(function (e) {
            repaintAngle();
        });

    $control.find("canvas")
        .mousedown(function (e) {
            var cx = this.width / 2;
            var cy = this.height / 2;
            var x = e.layerX - cx;
            var y = e.layerY - cy;
            var angle = (-Math.atan2(y, x) * 180 / Math.PI).toFixed(0); 
            $control.find("input").val(angle);
            repaintAngle();
        });

    repaintAngle();
});

cocktail.bind(".image_effects_dialog .crop_control", function ($control) {

    var $dialog = $control.closest(".image_effects_dialog");

    this.makeStackNode = function () {
        return [
            this.imageEffect,
            $control.find(".x1 input").val(),
            $control.find(".y1 input").val(),
            $control.find(".x2 input").val(),
            $control.find(".y2 input").val()
        ];
    }

    this.applyStackNode = function (node) {
        $control.find(".x1 input").val(node[1]);
        $control.find(".y1 input").val(node[2]);
        $control.find(".x2 input").val(node[3]);
        $control.find(".y2 input").val(node[4]);
    }
    
    var Jcrop = null;

    function showCropCoordinates(c) {
        $control.find(".x1 input").val(c.x);
        $control.find(".y1 input").val(c.y);
        $control.find(".x2 input").val(c.x2);
        $control.find(".y2 input").val(c.y2);
    }

    function clearCropUI() {
        if (Jcrop) {
            Jcrop.destroy();
            Jcrop = null;
        }
    }

    $control.find("input")
        .focus(function () {
            var rect = [
                Number($control.find(".x1 input").val()),
                Number($control.find(".y1 input").val()),
                Number($control.find(".x2 input").val()),
                Number($control.find(".y2 input").val())
            ];
            if (!Jcrop) {
                Jcrop = jQuery.Jcrop($dialog.find(".edited_image"), {
                    onSelect: showCropCoordinates,
                    onChange: showCropCoordinates,
                    setSelect: rect,
                    // Disable keyboard support, it messes with the viewport scroll
                    keySupport: false 
                });
            }
            else {
                Jcrop.setSelect(rect);
            }
        })
        .blur(function (e) {
            if (!insideCropUI(e.target)) {
                clearCropUI();
            }
        });

    function insideCropUI(element) {
        var $element = jQuery(element);
        return $element.closest(".crop_control").length
            || $element.closest(".edited_image_viewport").length;
    }

    $dialog.mousedown(function (e) {
        if (!insideCropUI(e.target)) {
            clearCropUI();
        }
    });
});

cocktail.bind(".image_effects_dialog .thumbnail_control", function ($control) {

    var $dialog = $control.closest(".image_effects_dialog");

    $control.find("input[type=radio]").attr("name", cocktail.requireId());
    $control.find("label").each(function () {
        var input = jQuery(this).siblings("input").get(0);
        if (!input.id) {
            input.id = cocktail.requireId();
        }
        jQuery(this).attr("for", input.id);
    });
    
    var img = $dialog.find(".edited_image").get(0);
    $control.find(".width").val(img.offsetWidth);
    $control.find(".height").val(img.offsetHeight);

    function disableUI(speed, callback) {
        var $options = $control.find("input[type=radio]");
        var $active = $options.filter(":checked").siblings(".option_controls");
        var $inactive= $options.not(":checked").siblings(".option_controls")
        if (speed) {
            $active.slideDown(speed, callback);
            $inactive.slideUp(speed);
        }
        else {
            $active.show();
            $inactive.hide();
        }
    }
    
    $control.find("input[type=radio]")
        .change(function () { disableUI("fast"); })
        .click(function (e) {
            var callback = !(e.clientX || e.clientY) ? null : function () {
                // Focus the first control in the option, only when navigating
                // with the mouse
                jQuery(this).find("input").first().focus();
            };
            disableUI("fast", callback);
        });
    disableUI();

    this.makeStackNode = function () {

        var node = [this.imageEffect];
        var option = $control.find("input[type=radio]:checked").attr("value");

        if (option == "absolute") {
            node.push($control.find("input.width").val());
            node.push($control.find("input.height").val());
        }
        else if (option == "relative") {
            node.push(Number($control.find("input.size").val()).toFixed(2));
        }

        return node;
    }

    this.applyStackNode = function (node) {

        if (node[1].toFixed(0) == node[1]) {
            var option = "absolute";
        }
        else {
            var option = "relative";
        }

        $control.find("input[type=radio]")
            .removeAttr("checked")
            .filter("[value=" + option + "]")
                .attr("checked", true);
        
        if (option == "absolute") {
            $control.find("input.width").val(node[1]);
            $control.find("input.height").val(node[2] || "");
        }
        else if (option == "relative") {
            var size = node[1];
            if (node.length > 2) {
                size = Math.min(size, node[2]);
            }
            $control.find("input.size").val(size);
        }

        disableUI();
    }
});

cocktail.bind(".image_effects_dialog .fill_control", function ($control) {

    var $dialog = $control.closest(".image_effects_dialog");

    $control.find("label").each(function () {
        var input = jQuery(this).siblings("input").get(0);
        if (!input.id) {
            input.id = cocktail.requireId();
        }
        jQuery(this).attr("for", input.id);
    });
    
    var img = $dialog.find(".edited_image").get(0);
    $control.find(".width").val(img.offsetWidth);
    $control.find(".height").val(img.offsetHeight);

    this.makeStackNode = function () {
        return [
            this.imageEffect,
            Number($control.find(".width").val()),
            Number($control.find(".height").val())
        ];
    }

    this.applyStackNode = function (node) {
        $control.find("input.width").val(node[1]);
        $control.find("input.height").val(node[2]);
    }
});

cocktail.bind(".image_effects_dialog .flip_control", function ($control) {

    $control.find("input[type=radio]").attr("name", cocktail.requireId());
    
    $control.find("label").each(function () {
        var input = jQuery(this).siblings("input").get(0);
        if (!input.id) {
            input.id = cocktail.requireId();
        }
        jQuery(this).attr("for", input.id);
    });
        
    this.makeStackNode = function () {
        return [
            this.imageEffect,
            Number($control.find("input[type=radio]:checked").attr("value"))
        ];
    }

    this.applyStackNode = function (node) {
        $control.find("input[type=radio]").val([String(node[1])]);
    }
});

cocktail.bind(".image_effects_dialog .custom_control", function ($control) {

    this.makeStackNode = function () {
        return [$control.find("input").val()];
    }

    this.applyStackNode = function (node) {
        $control.find("input").val(node[0]);
    }
});

