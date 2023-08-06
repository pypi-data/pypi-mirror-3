#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import sys
import socket
import re
import os
from shutil import rmtree
from subprocess import Popen, PIPE
from pkg_resources import resource_filename
import buffet
import cherrypy
from beaker.middleware import SessionMiddleware
from cocktail import schema
from cocktail.translations import set_language
from cocktail.html import templates
from cocktail.controllers import get_parameter
from woost.translations import installerstrings
from woost.models.initialization import init_site


class Installer(object):

    base_path = os.path.abspath(resource_filename("woost", ""))
    skeleton_path = os.path.join(base_path, "scripts","project_skeleton")
    views_path = os.path.join(base_path, "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        root = views_path,
        dir = "resources"
    )

    @cherrypy.expose
    def index(self, **params):

        set_language("en")
        submitted = cherrypy.request.method == "POST"
        successful = False
        errors = []
 
        HOST_FORMAT = \
            re.compile(r"^([a-z]+(\.[a-z]+)*)|(\d{1,3}(\.\d{1,3}){3})$")

        paths = sorted([p for p in sys.path if os.access(p, os.W_OK)])

        form_schema = schema.Schema(
            name = "Installer",
            members = [
                schema.String(
                    name = "project_name",
                    required = True,
                    format = r"^[A-Z][A-Za-z_0-9]*$",
                    member_group = "project"
                ),
                schema.String(
                    name = "python_package_repository",
                    required = True,
                    enumeration = paths,
                    default = paths and paths[0] or None,
                    member_group = "project"
                ),
                schema.String(
                    name = "admin_email",
                    required = True,
                    default = "admin@localhost",
                    member_group = "project"
                ),
                schema.String(
                    name = "admin_password",
                    required = True,
                    min = 8,
                    edit_control = "cocktail.html.PasswordBox",
                    member_group = "project"
                ),
                schema.String(
                    name = "languages",
                    required = True,
                    default = "en",
                    format = r"^[a-zA-Z]{2}(\W+[a-zA-Z]{2})*$",
                    member_group = "project"
                ),
                schema.String(
                    name = "template_engine",
                    required = True,
                    default = "cocktail",
                    enumeration = buffet.available_engines.keys(),
                    member_group = "project"
                ),
                schema.String(
                    name = "webserver_host",
                    required = True,
                    format = HOST_FORMAT,
                    default = "127.0.0.1",
                    member_group = "webserver"
                ),
                schema.Integer(
                    name = "webserver_port",
                    required = True,
                    default = 8080,
                    member_group = "webserver"
                ),
                schema.Boolean(
                    name = "validate_webserver_address",
                    default = True,
                    member_group = "webserver"
                ),
                schema.String(
                    name = "database_host",
                    required = True,
                    format = HOST_FORMAT,
                    default = "127.0.0.1",
                    member_group = "database"
                ),
                schema.Integer(
                    name = "database_port",
                    required = True,
                    default = 8081,
                    member_group = "database"
                ),
                schema.Boolean(
                    name = "validate_database_address",
                    default = True,
                    member_group = "database"
                )
            ]
        )

        def make_address_validation(host_field, port_field, check_field):

            def validate_address(schema, validable, context):

                if validable[check_field]:
                    host = validable[host_field]
                    port = validable[port_field]
                    host_member = schema[host_field]
                    port_member = schema[port_field]

                    if host_member.validate(host) \
                    and port_member.validate(port) \
                    and not self._is_valid_local_address(host, port):
                        yield WrongAddressError(
                            schema, validable, context,
                            host_member, port_member
                        )

            return validate_address

        form_schema.add_validation(make_address_validation(
            "webserver_host",
            "webserver_port",
            "validate_webserver_address"
        ))

        form_schema.add_validation(make_address_validation(
            "database_host",
            "database_port",
            "validate_database_address"
        ))

        form_data = {}

        if submitted:
            get_parameter(
                form_schema,
                target = form_data,
                errors = "ignore",
                undefined = "set_none"
            )
            errors = list(form_schema.get_errors(form_data))

            if not errors:

                form_data["project_path"] = os.path.join(
                    form_data["python_package_repository"],
                    form_data["project_name"].lower()
                )

                try:
                    if os.path.exists(form_data["project_path"]):
                        raise InstallFolderExists()

                    self.install(form_data)

                except Exception, ex:                    
                    errors.append(ex)
                    if not isinstance(ex, InstallFolderExists):
                        try:
                            rmtree(form_data["project_path"])
                        except Exception, rmex:
                            errors.append(rmex)
                else:
                    successful = True
        else:
            form_schema.init_instance(form_data)

        view = templates.new("woost.views.Installer")
        view.submitted = submitted
        view.successful = successful
        view.schema = form_schema
        view.data = form_data
        view.errors = errors
        return view.render_page()

    def install(self, params):
        
        params["project_module"] = params["project_name"].lower()

        self._create_project(params)
        self._init_project(params)

    def _create_project(self, params):

        vars = dict(
            ("_%s_" % key.upper(), unicode(value))
            for key, value in params.iteritems()
        )

        keys_expr = re.compile("|".join(vars))

        def expand_vars(text):
            return keys_expr.sub(lambda match: vars[match.group(0)], text)

        def copy(source, target):

            if os.path.isdir(source):
                os.mkdir(target)
                for name in os.listdir(source):
                    copy(
                        os.path.join(source, name),
                        os.path.join(target, expand_vars(name))
                    )

            elif os.path.isfile(source):
                if os.path.splitext(source)[1] != ".pyc":
                    source_file = file(source, "r")
                    try:
                        source_data = source_file.read().decode("utf-8")
                        target_data = expand_vars(source_data).encode("utf-8")
                        target_file = file(target, "w")
                        try:
                            target_file.write(target_data)
                        finally:
                            target_file.close()
                    finally:
                        source_file.close()

        copy(self.skeleton_path, params["project_path"])

        # Create the folder for the database
        os.mkdir(os.path.join(params["project_path"], "data"))

        # Grant execution permission for project scripts
        scripts_path = os.path.join(params["project_path"], "scripts")

        for fname in os.listdir(scripts_path):            
            if fname != "__init__.py":   
                script = os.path.join(scripts_path, fname)
                if os.path.isfile(script):
                    os.chmod(script, 0774)

    def _subprocess(self, cmd):
        # - Not used -
        proc = Popen(cmd, shell = True, stderr = PIPE)
        if proc.wait() != 0:
            raise SubprocessError(cmd, proc.stderr.read())

    def _init_project(self, params):

        # Start the database
        cmd = "runzeo -f %s -a %s:%d" % (
            os.path.join(params["project_path"], "data", "database.fs"),
            params["database_host"],
            params["database_port"]
        )
        Popen(cmd, shell = True)

        __import__(params["project_module"])
        init_site(
            admin_email = params["admin_email"],
            admin_password = params["admin_password"],
            languages = params["languages"].split(),
            template_engine = params["template_engine"]
        )

    def _is_valid_local_address(self, host, port):
        s = socket.socket()
        try:
            s.bind((host, port))
        except socket.error:
            return False
        else:
            s.close()

        return True

    def run(self):
        cherrypy.quickstart(self, "/", config = self.get_configuration())

    def get_configuration(self):
        return {
            "global": {
                "server.socket_port": 10000,
                "tools.encode.on": True,
                "tools.encode.encoding": "utf-8",
                "tools.decode.on": True,
                "tools.decode.encoding": 'utf-8',
                "engine.autoreload_on": False
            },
            "/": {
                "wsgi.pipeline": [("beaker", SessionMiddleware)],
                "wsgi.beaker.config": {"session.type": "memory"}
            }
        }


class InstallFolderExists(Exception):
    pass


class WrongAddressError(schema.exceptions.ValidationError):
 
    def __init__(self, member, value, context, host_member, port_member):
        
        schema.exceptions.ValidationError.__init__(
            self, member, value, context
        )

        self.host_member = host_member
        self.port_member = port_member


class PythonPathError(schema.exceptions.ValidationError):
    """A validation error produced when trying to install a project on a path
    that lies outside the python path."""


class SubprocessError(Exception):

    def __init__(self, cmd, error_output):
        self.cmd = cmd
        self.error_output = error_output

