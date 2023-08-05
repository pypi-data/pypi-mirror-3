import os
import types

import pypoly

class Config(object):
    """
    This class handles all the config entries.

    :since: 0.1

    Example(Module,Tool,Plugin):
        1. Add a new entry to the config:
            >>> def init(....):
            >>>    pypoly.config.add('my_option', 'String')

        2. Get a value after the module, tool or plugin is started:
            >>> pypoly.config.get('my_option')

    """
    def __init__(self):
        """
        Initialize the config system and set some default values.
        """
        self.__config = {
            'pypoly.component.components' : [],
            'pypoly.component.path' : 'components',
            'pypoly.log.application.file' : '',
            'pypoly.log.application.severity' : '',
            'pypoly.log.firephp' : False,
            'pypoly.log.web.file_access' : '',
            'pypoly.log.web.file_error' : '',
            'pypoly.menu.file' : '',
            'pypoly.module.modules' : [],
            'pypoly.module.path' : 'modules',
            'pypoly.plugin.plugins' : [],
            'pypoly.server.baseurl' : '/',
            'pypoly.server.host' : '0.0.0.0',
            'pypoly.server.ident' : 'PyPoly V%s' % pypoly.__version__,
            'pypoly.server.port' : 8080,
            'pypoly.server.type' : 'standalone',
            'pypoly.start.module' : '',
            'pypoly.start.action' : '',
            'pypoly.static.path' : 'static',
            'pypoly.static.url' : '/_static',
            'pypoly.static.enable' : True,
            'pypoly.system.root' : '.',
            'pypoly.system.auth' : '',
            'pypoly.system.session' : 'MemSession',
            'pypoly.template.path' : 'template',
            'pypoly.template.plugin' : '',
            'pypoly.template.default': 'default',
            'pypoly.template.style' : 'default',
            'pypoly.template.templates' : [],
            'pypoly.tool.tools' : [],
        }

    def _get(self, key, default = None):
        """

        Don't use this function directly.

        :since: 0.1

        :param key: key of the config entry.
        :type key: String
        :param default: this value is returned if the given config entry doesn't exist
        :type default: any type
        """
        key = key.lower()
        if pypoly.log != None:
            pypoly.log.debug("Get config value with key: %s" % key)

        if key in self.__config:
            return self.__config[key]
        else:
            return default

    def _set(self, key, value):
        """
        Convert the value to the config entry type and set the value of the
        config entry

        Don't use this function directly.

        :since: 0.1

        :param key: key of the config entry
        :type key: String
        :param value: the value of the config entry
        :type value: any type
        """
        key = key.lower()
        if pypoly.log != None:
            pypoly.log.debug("Set config value with key: %s" % key)

        # remove " from the value
        if len(value) > 1 and value[0] == '"':
            value = value[1:]
        if len(value) > 1 and value[-1] == '"':
            value = value[:-1]

        #print("Config setting: %s = %s" % (str(key), str(value)))
        def to_boolean(string):
            string = string.lower().strip()
            if string == "true" or string == "1":
                return True
            elif string == "false" or string == "0":
                return False
            else:
                return None

        if key in self.__config:
            ctype = type(self.__config[key])
            vtype = type(value)
            if ctype == types.StringType:
                if vtype == types.StringType:
                    self.__config[key] = value
                else:
                    self.__config[key] = str(value)
            elif ctype == types.ListType:
                if vtype == types.ListType:
                    self.__config[key] = value
                elif vtype == types.StringType:
                    if len(value) == 0:
                        tmp = []
                    else:
                        tmp = value.split(",")
                        tmp = [i.strip() for i in tmp]
                    # TODO: strip whitespaces
                    self.__config[key] = tmp
            if ctype == types.IntType:
                if vtype == types.IntType:
                    self.__config[key] = value
                elif vtype == types.StringType:
                    self.__config[key] = int(value)
            if ctype == types.BooleanType:
                if vtype == types.BooleanType:
                    self.__config[key] = value
                elif vtype == types.StringType:
                    value = to_boolean(value)
                    vtype = type(value)
                    if vtype == types.BooleanType:
                        self.__config[key] = value

    def get(self, key, default = None):
        """
        Get a value for a given config entry. It detects who is calling.

        :since: 0.1

        :param key: name of the config entry
        :type key: String
        :param default: if the given config entry doesn't exist return this value
        :type default: mixed value
        :return: the value of the config entry or the default value
        :rtype: mixed value
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            return self.get_pypoly(key, default)
        elif caller.type == 'module':
            return self.get_module(caller.name, key, default)
        elif caller.type == 'plugin':
            return self.get_plugin(caller.name, key, default)
        elif caller.type == 'tool':
            return self.get_tool(caller.name, key, default)
        else:
            pypoly.log.warning('Can\'t detect caller')

    def set(self, key, value):
        """
        Set the value of a config entry. It detects who is calling.

        :since: 0.1

        :param key: name of the config entry
        :type key: String
        :param value: the value
        :type value: mixed type
        :return: True = value set | False = error
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            return self.set_pypoly(key, value)
        elif caller.type == 'module':
            return self.set_module(caller.name, key, value)
        elif caller.type == 'plugin':
            return self.set_plugin(caller.name, key, value)
        elif caller.type == 'tool':
            return self.set_tool(caller.name, key, value)
        else:
            pypoly.log.warning('Can\'t detect caller')

    def get_module(self, name, key, default = None):
        """
        Get a value for a given config entry of a module.

        :since: 0.1

        :param name: the module name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param default: if the given config entry doesn't exist return this value
        :type default: mixed value
        :return: the value of the config entry or the default value
        :rtype: mixed value
        """
        return self._get('.'.join(['module', name, key]), default)

    def set_module(self, name, key, value):
        """
        Set the value of a config entry of a module.

        :since: 0.1

        :param name: the tool name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param value: the value
        :type value: mixed type
        :return: True = value set | False = error
        """
        return self._set('.'.join(['module', name, key]), value)

    def get_plugin(self, name, key, default = None):
        """
        Get a value for a given config entry of a plugin.

        :since: 0.1

        :param name: the plugin name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param default: if the given config entry doesn't exist return this value
        :type default: mixed value
        :return: the value of the config entry or the default value
        :rtype: mixed value
        """
        return self._get('.'.join(['plugin', name, key]), default)

    def set_plugin(self, name, key, value):
        """
        Set the value of a config entry of a plugin.

        :since: 0.1

        :param name: the plugin name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param value: the value
        :type value: mixed type
        :return: True = value set | False = error
        """
        return self._set('.'.join(['plugin', name, key]), value)

    def get_pypoly(self, key, default = None):
        """
        Get a value for a given config entry of the pypoly.

        :since: 0.1

        :param key: name of the config entry
        :type key: String
        :param default: if the given config entry doesn't exist return this value
        :type default: mixed value
        :return: the value of the config entry or the default value
        :rtype: mixed value
        """
        return self._get('.'.join(['pypoly',key]), default)

    def set_pypoly(self, key, value):
        """
        Set the value of a config entry of the pypoly.

        :since: 0.1

        :param key: name of the config entry
        :type key: String
        :param value: the value
        :type value: mixed type
        :return: True = value set | False = error
        """
        return self._set('.'.join(['pypoly',key]), value)

    def get_tool(self, name, key, default = None):
        """
        Get a value for a given config entry of a tool.

        :since: 0.1

        :param name: the tool name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param default: if the given config entry doesn't exist return this value
        :type default: mixed value
        :return: the value of the config entry or the default value
        :rtype: mixed value
        """
        return self._get('.'.join(['tool', name, key]), default)

    def set_tool(self, name, key, value):
        """
        Set the value of a config entry of a tool.

        :since: 0.1

        :param name: the tool name
        :type name: String
        :param key: name of the config entry
        :type key: String
        :param value: the value
        :type value: mixed type
        :return: True = value set | False = error
        """

        return self._set('.'.join(['tool', name, key]), value)

    def add(self, key, default):
        """
        Add a new config entry.

        :since: 0.1

        :param key: key of the config entry
        :type key: String
        :param default: the default value
        :type default: any type
        """
        caller = pypoly.get_caller()
        tmp_key = None
        if caller.type == 'pypoly':
            tmp_key = ".".join(['pypoly', key])
        elif caller.type == 'module':
            tmp_key = ".".join(['module', caller.name, key])
        elif caller.type == 'plugin':
            tmp_key = ".".join(['plugin', caller.name, key])
        elif caller.type == 'tool':
            tmp_key = ".".join(['tool', caller.name, key])

        if tmp_key == None:
            pypoly.log.warning("Could not detect the right caller")
            return

        self.__config[tmp_key.lower()] = default

    def update(self, section, config):
        """
        This function updates the configuration
        Config could be a string or a dict:
            - string the filename
            - dict a dictionary with all the options

        :since: 0.1

        :param config: this are all the config options to update
        :type config: dict e.g. {'system.pypoly_path' : '/var/www'}
        """
        if type(config) == types.StringType:
            # if config is a string, try to load the config file and convert it
            # to a dict
            if os.path.exists(config):
                import ConfigParser
                conf = ConfigParser.ConfigParser()
                conf.read(config)
                if section == 'global' and conf.has_section(section):
                    for (key, value) in conf.items(section):
                        self.set_pypoly(key, value)
                elif section == 'modules' and conf.has_section(section):
                    for (key, value) in conf.items(section):
                        keys = key.split('.')
                        pkg_name = pypoly.module.get_package_name(keys[0])
                        if pkg_name == None:
                            continue
                        #keys[0] = pkg_name
                        self._set('.'.join(['module'] + keys), value)
                elif section == 'tools' and conf.has_section(section):
                    for (key, value) in conf.items(section):
                        keys = key.split('.')
                        pkg_name = pypoly.tool.get_package_name(keys[0])
                        if pkg_name == None:
                            continue
                        #keys[0] = pkg_name
                        self._set('.'.join(['tool'] + keys), value)
                elif section == 'plugins' and conf.has_section(section):
                    for (key, value) in conf.items(section):
                        keys = key.split('.')
                        pkg_name = pypoly.plugin.get_package_name(keys[0])
                        if pkg_name == None:
                            continue
                        #keys[0] = pkg_name
                        self._set('.'.join(['plugin'] + keys), value)

