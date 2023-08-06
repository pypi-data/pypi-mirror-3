#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.translations import translations
from woost.models import Extension

translations.define("WorkflowExtension",
    ca = u"Circuïts de treball",
    es = u"Circuitos de trabajo",
    en = u"Workflow"
)

translations.define("WorkflowExtension-plural",
    ca = u"Circuïts de treball",
    es = u"Circuitos de trabajo",
    en = u"Workflow"
)


class WorkflowExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet construïr circuïts de treball, mitjançant la definició
            d'estats i transicions pels elements.""",
            "ca"
        )
        self.set("description",
            u"""Permite construir circuitos de trabajo, mediante la definición
            de estados y transiciones para los elementos.""",
            "es",
        )
        self.set("description",
            u"""Allows the set up of workflows, based on a system of item
            states and transitions..""",
            "en"
        )

    def _load(self):

        from woost.extensions.workflow import (
            strings,
            state,
            transition,
            transitionpermission,
            transitiontrigger,
            setstatetriggerresponse,
            useractions
        )

        # Add a controller to handle transition schemas
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.workflow.transitioncontroller \
            import TransitionController

        BackOfficeController.workflow_transition = TransitionController

        # Add a content view for workflow graphs (if GraphViz is installed)
        from woost.extensions.workflow.graph import graphviz_command

        if graphviz_command:

            from woost.controllers.backoffice.contentviews \
                import global_content_views

            global_content_views.add(
                state.State,
                "woost.extensions.workflow.WorkflowGraphContentView",
                is_default = True
            )

            # Add a controller to render the SVG graphs for the graphs content view
            from woost.controllers.backoffice.backofficecontroller \
                import BackOfficeController
            from woost.extensions.workflow.workflowgraphcontroller \
                import WorkflowGraphController

            BackOfficeController.workflow_graph = WorkflowGraphController

