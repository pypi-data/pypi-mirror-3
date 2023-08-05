import pypoly

"""
Structure:
  - PyPoly Data: pypoly.<key> = <value>
  - Module Data: module.<name>.<key> = <value>
  - Plugin Data: plugin.<name>.<key> = <value>
"""

# Lock the session a unlock it at the end
MODE_LOCK = 0

# The session is only locked while loading the data
MODE_READONLY = 1

# Load data and unlock the session
# Write all changes at the end. Changes are NOT merged.
MODE_LOADWRITE = 2

def _get(key, default):
    """
    Get the value with the given key.

    :param key: the key
    :param default: return this if the given key is not found
    :return: the value or the default value
    """
    key = key.lower()
    return pypoly.http.session.get(key, default)

def _pop(key, default):
    """
    Get the value with the given key and delete it

    :param key: the key
    :param default: return this if the given key is not found
    :return: the value or the default value
    """
    key = key.lower()
    return pypoly.http.session.pop(key, default)

def _set(key, value):
    """
    Set the value with the given key

    :param key: the key
    :param value: the value
    """
    key = key.lower()
    pypoly.http.session.set(key, value)

def get(key, default):
    """
    Detect who is calling and get the value with the given key.

    :param key: the key
    :param default: return this if the given key is not found
    :return: the value or the default value
    """
    caller = pypoly.get_caller()
    if caller.type == 'pypoly':
        return get_pypoly(key, default)
    elif caller.type == 'module':
        return get_module(caller.name, key, default)
    elif caller.type == 'plugin':
        return get_plugin(caller.name, key, default)
    else:
        pypoly.log.warning('Can\'t detect caller')

def pop(key, default):
    """
    Detect who is calling and get the value with the given key and delete it.

    :param key: the key
    :param default: return this if the given key is not found
    :return: the value or the default value
    """
    caller = pypoly.get_caller()
    if caller.type == 'pypoly':
        return pop_pypoly(key, default)
    elif caller.type == 'module':
        return pop_module(caller.name, key, default)
    elif caller.type == 'plugin':
        return pop_plugin(caller.name, key, default)
    else:
        pypoly.log.warning('Can\'t detect caller')

def set(key, value):
    """
    Detect who is calling and set the value with the given key.

    :param key: the key
    :param value: the value
    """
    caller = pypoly.get_caller()
    if caller.type == 'pypoly':
        return set_pypoly(key, value)
    elif caller.type == 'module':
        return set_module(caller.name, key, value)
    elif caller.type == 'plugin':
        return set_plugin(caller.name, key, value)
    else:
        pypoly.log.warning('Can\'t detect caller')

def get_pypoly(key, default = None):
    """
    Get the value of a session var for pypoly
    """
    return _get('.'.join(['pypoly',key]), default)

def pop_pypoly(key, default = None):
    """
    Pop the value of a session var for pypoly
    """
    return _pop('.'.join(['pypoly',key]), default)

def set_pypoly(key, value):
    """
    Set the value of a session var for pypoly
    """
    _set('.'.join(['pypoly', key]), value)

def get_module(name, key, default = None):
    """
    Get the value of a session var of the given module

    :since: 0.1

    :param name: name of the module
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _get('.'.join(['module', name, key]), default)

def pop_module(name, key, default = None):
    """
    Pop the value of a session var of the given module

    :since: 0.1

    :param name: name of the module
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _pop('.'.join(['module', name, key]), default)

def set_module(name, key, value):
    """
    Set the value of a session var of the given module

    :since: 0.1

    :param name: name of the module
    :type name: String
    :param key: the name of the value
    :type key: String
    :param value: set this value
    :type value: mixed type
    """
    _set('.'.join(['module', name, key]), value)

def get_plugin(name, key, default = None):
    """
    Get the value of a session var of the given plugin.

    :since: 0.1

    :param name: name of the plugin
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _get('.'.join(['plugin', name, key]), default)

def pop_plugin(name, key, default = None):
    """
    Pop the value of a session var of the given plugin.

    :since: 0.1

    :param name: name of the plugin
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _pop('.'.join(['plugin', name, key]), default)

def set_plugin(name, key, value):
    """
    Set the value of a session var of the given plugin

    :since: 0.1

    :param name: name of the plugin
    :type name: String
    :param key: the name of the value
    :type key: String
    :param value: set this value
    :type value: mixed type
    """
    _set('.'.join(['plugin', name, key]), value)

def get_tool(name, key, default = None):
    """
    Get the value of a session var of the given tool.

    :since: 0.3

    :param name: name of the tool
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _get('.'.join(['tool', name, key]), default)

def pop_tool(name, key, default = None):
    """
    Pop the value of a session var of the given tool.

    :since: 0.3

    :param name: name of the tool
    :type name: String
    :param key: the name of the value
    :type key: String
    :param default: return this value if the value with given key was not found
    :type default: mixed type
    :return: the value or the default value
    :rtype: mixed type
    """
    return _pop('.'.join(['tool', name, key]), default)

def set_tool(name, key, value):
    """
    Set the value of a session var of the given tool.

    :since: 0.3

    :param name: name of the tool
    :type name: String
    :param key: the name of the value
    :type key: String
    :param value: set this value
    :type value: mixed type
    """
    _set('.'.join(['tool', name, key]), value)
