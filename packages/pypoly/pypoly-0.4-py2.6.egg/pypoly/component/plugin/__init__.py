import hashlib
import random
import threading
import types

import pypoly
import pypoly.session

class PluginHandler(object):
    """
    This is the plugin handler. It handles all the things we want to do with
    the plugins.

    :since: 0.1
    """
    def set_plugins(self, plugins):
        if type(plugins) == types.StringType:
            plugins = plugins.split(',')
        # if modules is a list we try to load all the modules in it
        if type(plugins) == types.ListType:
            for plugin in plugins:
                PluginHandler.load(plugin.strip())

    def get_plugins(self):
        plugins = []
        #for name,value in PluginHandler.__plugins.iteritems():
            #    plugins.append(name)
        return plugins

    plugins = property(get_plugins, set_plugins)

    def __init__(self):
        PluginHandler.__plugins = {}
        PluginHandler.__plugins2 = {
            "editor": {},
            "auth": {},
            "session": {},
            "template": {},
            "custom": {}
        }

    def load(self, plugins):
        """
        Load a plugin.

        This function is called by the pypoly!

        :since: 0.1

        :param plugins: a list of plugin names
        :type plugins: List
        :return: True | False
        """
        for name in plugins:
            try:
                pypoly.log.info('Trying to load plugin "%s".' % name)
                component = pypoly.component.load(name, 'pypoly.plugin')
                if component != None:
                    comp = component.entry_point.load()

                    comp = comp()
                    component.comp = comp
                    PluginHandler.__plugins[component.module_name] = component
                    pypoly.log.info('Loading plugin "%s" successful.' % name)
                else:
                    #-print "not found"
                    pass

            except BaseException, inst:
                pypoly.log.error(
                    'Loading plugin "%s" failed. Error: %s.' % (name, inst),
                    traceback=True
                )

    def init(self):
        for (name, plugin) in PluginHandler.__plugins.iteritems():
            try:
                plugin.comp.init()
            except BaseException, msg:
                pypoly.log.error(
                    "Error while initializing plugin: %(name)s " \
                    "'%(message)s'" % {
                        "name": plugin.name,
                        "message": str(msg)
                    },
                    traceback=True
                )

    def start(self):
        for (name, plugin) in PluginHandler.__plugins.iteritems():
            plugin.comp.start()
            try:
                plugin.comp.start()
            except BaseException, msg:
                pypoly.log.error(
                    "Error while starting plugin: %(name)s '%(message)s'" % {
                        "name:": plugin.name,
                        "message": str(msg)
                    }
                )

    def register(self, plugin, name=None):
        """
        Register a plugin.

        :param plugin: a plugin
        :param name: maybe we can remove this parameter in the future
        :return: True or False
        """

        caller = pypoly.get_caller()
        if caller.type == 'plugin':
            if AuthPlugin == plugin.__base__:
                plugin_name = caller.pkg_root
                PluginHandler.__plugins2['auth'][plugin_name] = plugin
            elif EditorPlugin == plugin.__base__:
                plugin_name = caller.pkg_root
                PluginHandler.__plugins2['editor'][plugin_name] = plugin
            elif SessionPlugin == plugin.__base__:
                plugin_name = caller.pkg_root
                PluginHandler.__plugins2['session'][plugin_name] = plugin
            elif TemplatePlugin == plugin.__base__:
                plugin_name = caller.pkg_root
                PluginHandler.__plugins2['template'][plugin_name] = plugin
            elif Plugin == plugin.__base__:
                plugin_name = caller.pkg_root
                PluginHandler.__plugins2['custom'][plugin_name] = plugin

    def get_plugin(self, plugin_type, name):
        """
        Get a plugin

        :param plugin_type: Type of the plugin
        :param name: Name of the plugin
        :return: plugin-class | None
        """
        if name in PluginHandler.__plugins2[plugin_type]:
            return PluginHandler.__plugins2[plugin_type][name]
        else:
            return None

    def get_plugin_by_name(self, plugin_type, name):
        pkg_name = self.get_package_name(name)
        if pkg_name == None:
            return None

        return self.get_plugin(plugin_type, pkg_name)

    def get_plugin_instance(self, plugin_type, name):
        """
        Get the instance of a plugin.

        :param plugin_type: Type of the plugin
        :param name: Name of the plugin
        :return: Instance of the plugin | None
        """
        plugin = self.get_plugin(plugin_type, name)
        if plugin:
            return plugin()
        else:
            return None

    def is_plugin(self, name):
        """
        Check if the given name is the name of a plugin.

        :param name: a name
        :type name: String
        :return: True = a plugin with the given name exists | False = there is
                 no plugin available
        :rtype: Boolean
        """
        if self.get_root_pkg(pkg_name) == "":
            return False
        return True

    def get_component_name(self, name):
        if name in PluginHandler.__plugins:
            return PluginHandler.__plugins[name].name
        else:
            return None

    def get_package_name(self, name):
        """
        Return the python package name of a pypoly plugin

        :param name: PyPoly plugin name
        :type name: String
        :return: python package name or None
        :rtype: String | None
        """
        name = name.lower()
        for component in PluginHandler.__plugins.values():
            if component.name.lower() == name:
                return component.module_name
        return None

    def get_root_pkg(self, pkg_name):
        """
        Get the package name of the root package.

        :sinte: 0.4

        :param pkg_name: package name
        :type pkg_name: String
        :return: "" = Not found | String = package name
        :rtype: String
        """
        for name in PluginHandler.__plugins.keys():
            if pkg_name[:len(name)] == name:
                return name
        return ""


class Plugin(object):
    pass


class EditorPlugin(list, Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self._type = 'editor'

    def get_properties(self):
        """
        Dummy function
        """
        # we need this hier because webpage needs the EditorPlugin class
        from pypoly.content.webpage import ContentProperties
        return ContentProperties()

    def set_properties(self, value):
        """
        Dummy function
        """
        pass

    properties = property(get_properties, set_properties)

    def append(self, value):
        """
        Dummy append function, gets overwriten by the real plugin.
        """
        pass

    def generate(self):
        """
        TODO: remove this function?
        """
        pass


class AuthPlugin(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self._type = 'auth'

    def login(self, username, password):
        pypoly.log.warning(
            "No authentication plugin loaded. Auth not possible."
        )

    def get_group(self, username):
        pypoly.log.warning(
            "No authentication plugin loaded. Auth not possible."
        )


class SessionPlugin(Plugin):
    """
    Use this to create a new Session plugin
    """

    def __init__(self, session_id):
        Plugin.__init__(self)
        self._type = 'session'
        self.mode = pypoly.session.MODE_LOCK
        self.session_id = session_id

    def create_session(self):
        """
        Create a new session.
        """
        self.session_id = hashlib.md5(str(random.random())).hexdigest()

        pypoly.log.debug('New Session-ID %s' % str(self.session_id))

        pypoly.http.response.cookies["session_id"] = self.session_id
        pypoly.http.response.cookies["session_id"]["path"] = "/"
        return self.session_id

    def set_mode(self, mode):
        if self.mode != pypoly.session.MODE_LOCK:
            pypoly.log.warning(
                "It's only possible to change the session mode from LOCK " + \
                "to any other mode."
            )
            return False

        self.mode = mode
        return True

class TemplatePlugin(Plugin):
    #: hold the configs for the PyPoly templates
    _web_config_pypoly = {}

    #: hold the configs for the module templates
    _web_config_modules = {}

    def __init__(self, templates):
        self.templates = []

    def _load_web_config(self, path, templates):
        from pypoly.content.template import TemplateConfig
        if type(templates) == list:
            for name in templates:
                temp = TemplateConfig(
                    name,
                    path
                )
                self._web_config_pypoly[name] = temp

    def load_text(self, *args):
        """
        Load a text template.

        It detects the caller and loads the right template for it.

        :since: 0.4
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            return self.load_text_pypoly(*args)
        else:
            return self.load_text_module(
                caller.name,
                *args
            )

    def load_text_from_string(self, source):
        """
        Load a text template from the given string

        :since: 0.4

        :param source: Use this to load the template
        :type source: String
        :return: The template
        :rtype: TemplateOutput
        """
        from pypoly.content.template import TemplateOutput
        return TemplateOutput()

    def load_text_module(self, module_name, *args):
        """
        Load a text template for a module.

        :since: 0.4

        :return: The template
        :rtype: TemplateOutput
        """
        from pypoly.content.template import TemplateOutput
        return TemplateOutput()

    def load_text_plugin(self, plugin_name, *args):
        """
        Load a text template for a plugin.

        :since: 0.4

        :return: The template
        :rtype: TemplateOutput
        """
        from pypoly.content.template import TemplateOutput
        return TemplateOutput()

    def load_text_pypoly(self, *args):
        """
        Load a text template for PyPoly.

        :since: 0.4

        :return: The template
        :rtype: TemplateOutput
        """
        from pypoly.content.template import TemplateOutput
        return TemplateOutput()

    def load_web(self, *args):
        """
        Load a web template.

        It detects the caller and loads the right template for it.

        :since: 0.4
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            return self.load_web_pypoly(*args)
        else:
            return self.load_web_module(
                caller.name,
                *args
            )

    def load_web_from_string(self, source):
        """
        Load web template from the given string

        :since: 0.4

        :param source: Use this to load the template
        :type source: String
        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()

    def load_web_module(self, module_name, *args):
        """
        Load a web template for a module.

        :since: 0.4

        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()

    def load_web_pypoly(self, *args):
        """
        Load a web template for PyPoly.

        :since: 0.4

        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()

    def load_xml(self, *args):
        """
        Load a xml template.

        It detects the caller and tries to find the right template for it.

        :since: 0.4
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            return self.load_xml_pypoly(*args)
        else:
            return self.load_xml_module(
                caller.name,
                *args
            )

    def load_xml_from_string(self, source):
        """
        Load a xml template from the given string

        :since: 0.4

        :param source: Use this to load the template
        :type source: String
        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()

    def load_xml_module(self, *args):
        """
        Load a xml template for a module.

        :since: 0.4

        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()

    def load_xml_pypoly(self, *args):
        """
        Load a xml template for PyPoly.

        :since: 0.4

        :return: The template
        :rtype: WebTemplateOutput
        """
        from pypoly.content.template import WebTemplateOutput
        return WebTemplateOutput()


class MemSessionHandler(SessionPlugin):
    """
    """
    __sessions = {}
    __lock = threading.Lock()

    def __init__(self, session_id):
        SessionPlugin.__init__(self, session_id)

        if self.session_id == None:
            self.create_session()

        self.__lock.acquire()
        if not self.session_id in MemSessionHandler.__sessions:
            self.create_session()
            MemSessionHandler.__sessions[self.session_id] = {}
        self.__lock.release()

    def get(self, name, default=None):
        if name in MemSessionHandler.__sessions[self.session_id]:
            return MemSessionHandler.__sessions[self.session_id][name]
        else:
            return default

    def pop(self, name, default=None):
        if not name in MemSessionHandler.__sessions[self.session_id]:
            return default

        self.__lock.acquire()
        value = MemSessionHandler.__sessions[self.session_id][name]
        del MemSessionHandler.__sessions[self.session_id][name]
        self.__lock.release()
        return value

    def set(self, name, value):
        self.__lock.acquire()
        MemSessionHandler.__sessions[self.session_id][name] = value
        self.__lock.release()


class CustomPlugin(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self._type = 'custom'
