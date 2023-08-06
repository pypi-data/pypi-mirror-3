#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translations

translations.define("Woost installation",
    en = u"Woost installation"
)

translations.define("Installer.project",
    en = u"Project"
)

translations.define("Installer.project_name",
    en = u"Project name"
)

translations.define("Installer.project_name-explanation",
    en = u"""Should be in CamelCase form. Will be used as a prefix for Python
    class names, and transformed to lowercase to determine the name of the
    Python package assigned to the project.
    """
)

translations.define("Installer.python_package_repository",
    en = u"Package installation path"
)

translations.define("Installer.python_package_repository-explanation",
    en = u"""Location were the project's Python package and data files will be
    installed."""
)

translations.define("Installer.admin_email",
    en = u"Administrator email"
)

translations.define("Installer.admin_password",
    en = u"Administrator password"
)

translations.define("Installer.languages",
    en = u"Languages"
)

translations.define("Installer.languages-explanation",
    en = u"A list of ISO language codes, separated by whitespace."
)

translations.define("Installer.template_engine",
    en = u"Default template engine"
)

translations.define("Installer.webserver",
    en = u"Web server"
)

translations.define("Installer.webserver_host",
    en = u"Web server host"
)

translations.define("Installer.webserver_port",
    en = u"Web server port number"
)

translations.define("Installer.validate_webserver_address",
    en = u"Test address availability"
)

translations.define("Installer.database",
    en = u"Database"
)

translations.define("Installer.database_host",
    en = u"Database host"
)

translations.define("Installer.database_port",
    en = u"Database port number"
)

translations.define("Installer.validate_database_address",
    en = u"Test address availability"
)

translations.define("Install",
    en = u"Install"
)

translations.define("Installation successful",
    en = u"Your new site has been installed successfully."
)

translations.define(
    "woost.controllers.installer.InstallFolderExists-instance",
    ca = u"El directori d'instal·lació seleccionat ja existeix",
    es = u"El directorio de instalación seleccionado ya existe",
    en = u"The chosen installation directory already exists"
)

translations.define(
    "woost.controllers.installer no installation paths available",
    en = u"""The installer needs to create and import a Python package for the
    project, but currently there's no location available where the package
    could reside. Please, set up a PYTHONPATH environment variable and restart
    the installation process."""
)

translations.define(
    "woost.controllers.installer.WrongAddressError-instance",
    en = lambda instance:
        u"The indicated <em>%s</em> and <em>%s</em> combination is not "
        u"available on this server"
        % (
            translations(instance.host_member, "en"),
            translations(instance.port_member, "en")
        )
)

translations.define(
    "woost.controllers.installer.SubprocessError-instance",
    en = lambda instance:
        u"The installer found an unexpected error and couldn't continue. "
        u"The <em>%s</em> process returned the following error: <pre>%s</pre>"
        % (instance.cmd, instance.error_output)
)

translations.define(
    "Unknown error",
    en = lambda error: u"Unexpected <em>%s</em> exception: %s"
        % (error.__class__.__name__, error)
)

