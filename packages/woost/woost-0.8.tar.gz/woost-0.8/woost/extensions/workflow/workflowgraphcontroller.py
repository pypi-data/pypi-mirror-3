#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cStringIO import StringIO
import cherrypy
from cocktail import schema
from cocktail.controllers import get_parameter
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.workflow.state import State
from woost.extensions.workflow.graph import workflow_graph, render_graph

title_expr = re.compile("<title>.*</title>")


class WorkflowGraphController(BaseBackOfficeController):

    def __call__(self, **kwargs):
        
        cherrypy.response.headers["Content-Type"] = "image/svg+xml"

        states = get_parameter(
            schema.Collection("states",
                items = schema.Reference(type = State),
                default = schema.DynamicDefault(
                    lambda: list(State.select())
                )
            )
        )

        canvas = StringIO()
        graph = workflow_graph(states)
        render_graph(graph, canvas, "svg")
        svg = canvas.getvalue()
        
        # Add a stylesheet
        pos = svg.find("<svg")
        if pos != -1:
            svg = (
                svg[:pos]
                + "<?xml-stylesheet href='/resources/styles/workflow-graph.css' type='text/css'?>"
                + svg[pos:]
            )

        # Add a script
        pos = svg.rfind("</svg>")
        if pos != -1:
            svg = (
                svg[:pos]
                + "<script type='application/ecmascript' xlink:href='/resources/scripts/workflow-graph.js'/>"
                + svg[pos:]
            )

        # Remove pointless title attributes
        svg = title_expr.sub("", svg)

        return svg

