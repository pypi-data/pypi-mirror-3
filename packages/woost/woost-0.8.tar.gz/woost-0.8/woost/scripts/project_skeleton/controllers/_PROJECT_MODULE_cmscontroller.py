#-*- coding: utf-8 -*-
u"""
Provides the CMS subclass used to customize the behavior of the site.
"""
from pkg_resources import resource_filename
from cocktail.controllers import folder_publisher
from cocktail.controllers import renderingengines
from woost.controllers.cmscontroller import CMSController

renderingengines.rendering_options.update({
    "mako.directories": [
        resource_filename("_PROJECT_MODULE_", "views"),
        resource_filename("woost", "views")
    ],
    "mako.output_encoding": "utf-8"
})


class _PROJECT_NAME_CMSController(CMSController):

    _cp_config = CMSController.copy_config()
    _cp_config["rendering.engine"] = "_TEMPLATE_ENGINE_"

    class ApplicationContainer(CMSController.ApplicationContainer):
        _PROJECT_MODULE__resources = folder_publisher(
            resource_filename("_PROJECT_MODULE_.views", "resources")
        )

