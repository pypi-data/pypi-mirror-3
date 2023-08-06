/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
-----------------------------------------------------------------------------*/

cocktail.declare("woost");

woost.initRichTextEditor = function (instance) {

    // Paste as plain text by default
    instance.pasteAsPlainText = true;

    var doc = instance.contentDocument;

    var evento = tinymce.dom.Event;

	evento.remove(instance.id + '_resize', 'mousedown');

	evento.add(instance.id + '_resize', 'mousedown', function(e) {

        var ed = instance;
        var extend = tinymce.extend;

        ed.settings = s = extend({
            theme_advanced_resizing_use_cookie : 1,
            theme_advanced_resizing : true
        }, ed.settings);

        var DOM = tinymce.DOM;
        var c, p, w, h, n, pa;

        // Measure container
        c = DOM.get(ed.id + '_tbl');
        w = c.clientWidth;
        h = c.clientHeight;

        miw = s.theme_advanced_resizing_min_width || 100;
        mih = s.theme_advanced_resizing_min_height || 100;
        maw = s.theme_advanced_resizing_max_width || 0xFFFF;
        mah = s.theme_advanced_resizing_max_height || 0xFFFF;

        // Setup placeholder
        p = DOM.add(DOM.get(ed.id + '_parent'), 'div', {'class' : 'mcePlaceHolder'});
        DOM.setStyles(p, {width : w, height : h});

        // Replace with placeholder
        DOM.hide(c);
        DOM.show(p);

        // Create internal resize obj
        r = {
            x : e.screenX,
            y : e.screenY,
            w : w,
            h : h,
            dx : null,
            dy : null
        };

        // Start listening
        mf = evento.add(document, 'mousemove', function(e) {
            var w, h;

            // Calc delta values
            r.dx = e.screenX - r.x;
            r.dy = e.screenY - r.y;

            // Boundery fix box
            w = Math.max(miw, r.w + r.dx);
            h = Math.max(mih, r.h + r.dy);
            w = Math.min(maw, w);
            h = Math.min(mah, h);

            // Resize placeholder
            if (s.theme_advanced_resize_horizontal)
                p.style.width = w + 'px';

            p.style.height = h + 'px';

            return evento.cancel(e);
        });

        me = evento.add(document, 'mouseup', function(e) {

            // Stop listening
            evento.remove(document, 'mousemove', mf);
            evento.remove(document, 'mouseup', me);

            var c = DOM.get(ed.id + '_tbl');

            c.style.display = '';
            DOM.remove(p);

            if (r.dx === null) {
                return;
            }
            
            var Cookie = tinymce.util.Cookie;

            jQuery(".field_instance-RichTextEditor:visible textarea").each(function () {

                var areaid = jQuery(this).attr('id');

                var c = DOM.get(areaid + '_tbl');

                var ifr = DOM.get(areaid + '_ifr');

                if (s.theme_advanced_resize_horizontal)
                    c.style.width = (r.w + r.dx) + 'px';

                c.style.height = (r.h + r.dy) + 'px';
                var hc = ifr.clientHeight + r.dy
                ifr.style.height = (ifr.clientHeight + r.dy) + 'px';

                if (s.theme_advanced_resizing_use_cookie) {
                    Cookie.setHash("TinyMCE_" + areaid + "_size", {
                        cw : r.w + r.dx,
                        ch : r.h + r.dy,
                        ci : hc
                    });
                }
            });
        });

        return evento.cancel(e);
	});

}

