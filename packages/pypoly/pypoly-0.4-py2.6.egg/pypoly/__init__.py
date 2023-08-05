#
# PyPoly - Python Web Application Framework
#
# Copyright (c) 2008-2011 Philipp Seidel
#                    2008 Martin Kutz
#
# Dual licensed under the MIT (MIT-LICENSE.txt)
# and GPL (GPL-LICENSE.txt) licenses.
#

import os
import sys
import __builtin__
from optparse import OptionParser

from pypoly._config import Config
from pypoly._locale import Locale
from pypoly._user import User
from pypoly._log    import Log
from pypoly._structure import StructureHandler
from pypoly._hook import HookHandler
from pypoly.component.module import ModuleHandler
from pypoly.component.plugin import AuthPlugin, PluginHandler
from pypoly.component.tool import ToolHandler
from pypoly.content.url import URLHandler

import pypoly.http
import pypoly.http.auth
import pypoly.http.handler

__version__ = "0.4"
__author__ = "PyPoly Team"
__copyright__ = "PyPoly Team"
__license__ = "MIT and GPL"

#: set to dummy auth, is changed by the server
auth = AuthPlugin()

#: config handler
config = Config()

#: hook handler
hook = HookHandler()

#: locale handler
locale = None

#: logging handler
log = None

#: module handler
module = None
#: plugin handler
plugin = None

#: structure handler
structure = None

#: template handler
template = None

#: tool handler
tool = None

#: url handler
url = None

#: user handler
user = None

_dispatcher = pypoly.http.Dispatcher()

def get_path(*path):
    root = os.path.abspath(pypoly.config.get('system.root'))
    return os.path.join(root,*path)

def run():
    parser = OptionParser(version="PyPoly V%s" % (pypoly.__version__))
    parser.add_option("--verbose", "-v",
                      action="count", dest="verbose",
                      default = 0,
                      help="Increase the verbosity."
                     )
    parser.add_option("--traceback", "",
                      action="store", dest="traceback",
                      default = None
                     )
    parser.add_option("--screen", "",
                      action="store_true", dest="screen",
                      default = False,
                      help = 'log to screen'
                     )
    parser.add_option("--config", "-c",
                      action="store", dest="config_file",
                      default = "main.cfg",
                      help = "The config file"
                     )

    (options, args) = parser.parse_args()

    conf_verbose = 50
    if options.verbose != 0:
        conf_verbose = (50 - options.verbose * 10)
        if conf_verbose < 0:
            conf_verbose = 0

    pypoly.log = Log(
        screen = options.screen,
        level = conf_verbose,
        traceback = options.traceback
    )

    config_file = options.config_file

    if os.environ.get("PYPOLY_ROOT", None):
        os.chdir(os.environ.get("PYPOLY_ROOT"))
    # check if we get the config name from the environment
    if os.environ.get("PYPOLY_CONFIG", None):
        config_file = os.environ.get("PYPOLY_CONFIG")

    # is the config a file?
    if not os.path.isfile(config_file):
        pypoly.log.error("Can't find the config file '%s'" % config_file)
        sys.exit(1)

    pypoly.log.info('Parsing main-config ... ')
    #TODO: change this
    pypoly.config.update('global', config_file)
    # start logging
    pypoly.log.start()

    # init main system
    pypoly.log.info('Initializing main system ... ')
    pypoly.locale = Locale()
    __builtin__._ = locale
    pypoly.module = ModuleHandler()
    pypoly.plugin = PluginHandler()
    pypoly.tool = ToolHandler()
    pypoly.user = User()
    pypoly.url = URLHandler()

    pypoly.log.info('Loading modules ... ')
    pypoly.module.load(pypoly.config.get('module.modules'))
    pypoly.log.info('Loading plugins ... ')
    pypoly.plugin.load(pypoly.config.get('plugin.plugins'))
    pypoly.log.info('Loading tools ... ')
    pypoly.tool.load(pypoly.config.get('tool.tools'))

    pypoly.log.info('Initializing tools ... ')
    pypoly.tool.init()
    pypoly.log.info('Initializing plugins ... ')
    pypoly.plugin.init()
    pypoly.log.info('Initializing modules ... ')
    pypoly.module.init()

    pypoly.log.info('Loading structure ... ')
    pypoly.structure = StructureHandler()

    pypoly.log.info('Reading config: Tools')
    pypoly.config.update('tools', config_file)
    pypoly.log.info('Reading config: Plugins')
    pypoly.config.update('plugins', config_file)
    pypoly.log.info('Reading config: Modules')
    pypoly.config.update('modules', config_file)

    pypoly.log.info('Starting tools ... ')
    pypoly.tool.start()
    pypoly.log.info('Starting plugins ... ')
    pypoly.plugin.start()
    pypoly.log.info('Starting modules ... ')
    pypoly.module.start()

    pypoly.log.info('Loading templates ... ')

    #ToDo: if no handler set, use a dummy handler
    template_plugin = pypoly.config.get('template.plugin')
    if template_plugin == "":
        pypoly.log.info("No template plugin specified")
        from pypoly.component.plugin import TemplatePlugin
    else:
        TemplatePlugin = pypoly.plugin.get_plugin_by_name(
            'template',
            pypoly.config.get('template.plugin')
        )
        if TemplatePlugin == None:
            pypoly.log.error("Couldn't find/load the specified template plugin")
            from pypoly.component.plugin import TemplatePlugin

    pypoly.template = TemplatePlugin(pypoly.config.get('template.templates'))

    # remove: old routes
    #pypoly._dispatcher.mapper.create_regs()

    # test for authentication plugin
    auth_plug_name = pypoly.config.get("system.auth")
    pypoly.log.info("Setting Auth-Plugin %s ... " % auth_plug_name)
    auth_plugin_pkg = pypoly.plugin.get_package_name(
        auth_plug_name
    )
    auth_plugin = pypoly.plugin.get_plugin_instance('auth',auth_plugin_pkg)
    if auth_plugin == None:
        pypoly.log.critical('No authentication plugin found, authentication not possible.')
    else:
        pypoly.auth = auth_plugin
        pypoly.log.info('Authentication plugin found and enabled.')

    pypoly.log.info("Loading hooks ...")
    pypoly.hook.register(
        "http.request.serve.pre",
        "pypoly.auth",
        pypoly.http.handler.pypolyauth
    )

    pypoly.hook.register(
        "http.request.serve.pre",
        "pypoly.set_lang",
        pypoly.http.handler.set_lang
    )

    pypoly.hook.register(
        "http.request.serve.pre",
        "pypoly.set_template",
        pypoly.http.handler.set_template
    )

    # the main dispatcher
    pypoly.log.info('Starting server ... ')

    server_type = pypoly.config.get('server.type', None)
    if  server_type == 'standalone' or server_type == None:
        from wsgiref.simple_server import make_server
        httpd = make_server(pypoly.config.get('server.host'),
                            pypoly.config.get('server.port'),
                            pypoly.http.requesthandler
                           )
        httpd.serve_forever()
    elif server_type == 'standalone_threading':
        from wsgiref.simple_server import WSGIRequestHandler
        from pypoly.http.server import ThreadPoolMixIn
        server = ThreadPoolMixIn(
            (
                pypoly.config.get('server.host'),
                pypoly.config.get('server.port')
            ),
            WSGIRequestHandler
        )
        server.set_app(pypoly.http.requesthandler)
        server.serve_forever()
    elif server_type == 'cgi':
        from flup.server.cgi import WSGIServer
        WSGIServer(pypoly.http.requesthandler).run()
    elif server_type == 'fcgi':
        from flup.server.fcgi import WSGIServer
        WSGIServer(pypoly.http.requesthandler).run()
    elif server_type == 'fcgi_standalone':
        pypoly.log.error('Server Type not supported')
        sys.exit(1)
    elif server_type == "wsgi":
        pypoly.log.info("WSGI Mode")
    else:
        pypoly.log.error('Server Type not supported')
        sys.exit(1)

def get_caller():
    """
    Detect who is calling: pypoly, a module, a plugin or a tool.

    :since: 0.1

    :return: a Caller object
    :rtype: instance of Caller object
    :todo: pypoly v0.2 add more information
    """
    try:
        frame = sys._getframe(2)
    except ValueError:
        return 'Error'

    frame_name = frame.f_globals['__name__']
    name = frame_name.split('.')

    # of one handler isn't initialized the caller must be PyPoly itself
    if (pypoly.module == None or \
        pypoly.plugin == None or \
        pypoly.tool == None) and \
       name[0] == 'pypoly':
        return Caller(
            caller_type = 'pypoly',
            frame = frame
        )

    module_pkg_name = pypoly.module.get_root_pkg(frame_name)
    plugin_pkg_name = pypoly.plugin.get_root_pkg(frame_name)
    tool_pkg_name = pypoly.tool.get_root_pkg(frame_name)
    module_pkg_len = len(module_pkg_name)
    plugin_pkg_len = len(plugin_pkg_name)
    tool_pkg_len = len(tool_pkg_name)

    if module_pkg_len > plugin_pkg_len and \
       module_pkg_len > tool_pkg_len:
        return Caller(
            caller_type = "module",
            name = pypoly.module.get_component_name(module_pkg_name),
            pkg_root = module_pkg_name,
            frame = frame
        )

    if plugin_pkg_len > module_pkg_len and \
       plugin_pkg_len > tool_pkg_len:
        return Caller(
            caller_type = "plugin",
            name = pypoly.plugin.get_component_name(plugin_pkg_name),
            pkg_root = plugin_pkg_name,
            frame = frame
        )

    if tool_pkg_len > module_pkg_len and \
       tool_pkg_len > plugin_pkg_len:
        return Caller(
            caller_type = "tool",
            name = pypoly.tool.get_component_name(tool_pkg_name),
            pkg_root = tool_pkg_name,
            frame = frame
        )

    if name[0] == 'pypoly':
        return Caller(
            caller_type = 'pypoly',
            frame = frame
        )

    return Caller(
        caller_type = "component",
        name = "",
        pkg_root = name,
        frame = frame
    )


class Caller(object):
    """
    This is the caller class.

    :since: 0.1

    :param caller_type: the type of the caller
    :param name: the name of the caller
    :param filename: the filename
    :param linenumber: the line number
    :param function: the function name
    :param frame: the frame object
    """
    def __init__(
        self,
        caller_type,
        name = None,
        pkg_root = None,
        filename = '',
        linenumber = 0,
        function = '',
        frame = None):

        self.type = caller_type
        self.name = name
        self.pkg_root = pkg_root
        if frame != None:
            self.filename = frame.f_code.co_filename
            self.linenumber = frame.f_lineno
            self.function = frame.f_code.co_name
        elif frame == None:
            self.filename = filename
            self.linenumber = linenumber
            self.function = function
