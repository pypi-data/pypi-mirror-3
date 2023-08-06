/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".BasketIndicator", function ($indicator) {
    
    var blinkInterval = null;

    this.blink = function () {
    
        if (blinkInterval) {
            clearInterval(blinkInterval);
        }

        var blinkStep = 0;
        var LAPSE = 10;
        var STEPS = 60;
        var MIN_OPACITY = 0.25;

        blinkInterval = setInterval(function () {
            blinkStep += 1;
            if (blinkStep >= STEPS) {
                $indicator.css("opacity", "1.0");
                clearInterval(blinkInterval);
            }
            else {
                var x = blinkStep % 20;
                if (x >= 10) x = 10 - (x - 10);
                var o = MIN_OPACITY + (1 - MIN_OPACITY) * x / 10;
                $indicator.css("opacity", o);
            }
        }, LAPSE);
    }

    if (this.blinkOnLoad) {
        this.blink();
    }
});

