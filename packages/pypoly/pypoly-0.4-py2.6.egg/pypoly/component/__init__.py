import sys

import pkg_resources

import pypoly


class Component(object):
    def init(self):
        pass

    def start(self):
        pass

class ComponentInfo(object):
    """
    A component is a module, a plugin or a tool after it is loaded.

    :since: 0.1
    """
    name = ''
    module_name = ''
    entry_point = None
    def __init__(self):
        self.name = ''
        module_name = ''
        entry_point = None

def load(mod_name, entry_point):
    """
    Load a Component.

    :since: 0.1
    """
    component_path = pypoly.config.get('component.path')
    component_path = pypoly.get_path(component_path)
    component_paths = [component_path] + sys.path

    pkg_env = pkg_resources.Environment(component_paths)
    for name in pkg_env:
        egg = pkg_env[name][0]
        egg.activate()
        for name in egg.get_entry_map(entry_point):
            if name == mod_name:
                entry_point = egg.get_entry_info(entry_point, name)
                component = ComponentInfo()
                component.entry_point = entry_point
                component.module_name = entry_point.module_name
                component.name = entry_point.name
                return component
    return None
