/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2010
-----------------------------------------------------------------------------*/

(function () {

     var SVGNS = "http://www.w3.org/2000/svg";

    // CMS path
    var url = top.location.href;
    var pos = url.lastIndexOf("?");
    if (pos != -1) {
       url = url.substr(0, pos);
    }
    if (url.charAt(url.length - 1) != "/") {
       url += "/";
    }

    // Get SVG coordinates of the mouse position
    function getMousePosition(element, e) {
        var point = document.documentElement.createSVGPoint();
        point.x = e.clientX;
        point.y = e.clientY;
        var m = element.getScreenCTM();
        return point.matrixTransform(m.inverse());
    }

    // Click to edit
    function editClickedItem() {
        top.location.href = url + this.parentNode.id + "/fields/";
    }

    var clickable = document.querySelectorAll("g.node > *, g.edge > *");
    
    for (var i = 0; i < clickable.length; i++) {
        var node = clickable[i];
        node.onclick = editClickedItem;
    }

    // Drag a line between states to create a new transition
    var sourceState = null;
    var connector = null;

    function beginNewTransition(e) {
        sourceState = this.id;
        connector = document.createElementNS(SVGNS, "line");        
        var state = this.getElementsByTagName("ellipse")[0];
        var cx = state.cx.baseVal.value;
        var cy = state.cy.baseVal.value;
        connector.setAttribute("class", "connector");
        connector.setAttribute("x1", cx);
        connector.setAttribute("y1", cy);
        connector.setAttribute("x2", cx);
        connector.setAttribute("y2", cy);        
        this.parentNode.insertBefore(connector, this);
        e.preventDefault();
    }

    function connectNewTransition(e) {
        if (sourceState) {
            var targetState = this.id;
            console.log(targetState);
            if (targetState != sourceState) {
                top.location.href = url 
                    + "new/fields/?item_type=woost.extensions.workflow.transition.Transition"
                    + "&edited_item_source_state=" + sourceState
                    + "&edited_item_target_state=" + targetState;
            }
            discardConnector();
        }
    }

    function discardConnector() {
        if (connector) {
            connector.parentNode.removeChild(connector);
            sourceState = null;
            connector = null;
        }
    }

    document.onmousemove = function (e) {
        if (connector) {
            var mouse = getMousePosition(connector, e);
            connector.setAttribute("x2", mouse.x);
            connector.setAttribute("y2", mouse.y);
        }
    }

    document.addEventListener("mouseup", discardConnector, false);

    var states = document.querySelectorAll("g.node");

    for (var i = 0; i < states.length; i++) {
        states[i].onmousedown = beginNewTransition;
        states[i].addEventListener("mouseup", connectNewTransition, true);
    }
})();

