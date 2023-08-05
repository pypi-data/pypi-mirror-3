import types

import pypoly
import pypoly.component

class ModuleHandler(object):
    """
    This is the module handler. It handles all the things we want to do with the
    modules
    """

    def set_modules(self,modules):
        #print "set modules"
        if type(modules) == types.StringType:
            modules = modules.split(',')
            pypoly.log.debug(modules)
        # if modules is a list we try to load all the modules in it
        if type(modules) == types.ListType:
            #print "load"
            for module in modules:
                #print module
                ModuleHandler.load(module.strip())

    def get_modules(self):
        modules = []
        for name,value in ModuleHandler.__modules.iteritems():
            modules.append(name)
        return modules


    modules = property(get_modules, set_modules)

    def __init__(self):
        ModuleHandler.__modules = {}
        ModuleHandler.__menu = {}

    def load(self, modules):
        for name in modules:
            try:
                #-print name
                pypoly.log.info('Trying to load module "%s".' % name)
                component = pypoly.component.load(name, 'pypoly.module')
                if component != None:
                    comp = component.entry_point.load()

                    comp = comp()

                    component.comp = comp
                    ModuleHandler.__modules[component.module_name] = component
                    pypoly.log.info('Loading component "%s" successful.' % name)
                else:
                    #-print "not found"
                    pass


            except Exception, inst:
                #-print inst
                pypoly.log.error('Loading module "%s" failed. Error: %s.' % (name, inst), traceback = True)

    def init(self):
        for (tmp,component) in ModuleHandler.__modules.iteritems():
            try:
                component.comp.init()
            except Exception, msg:
                pypoly.log.error('Error while initializing module: %s "%s"' % \
                                 (component.name, str(msg))
                                )

    def start(self):
        for (tmp,component) in ModuleHandler.__modules.iteritems():
            try:
                component.comp.start()
            except Exception, msg:
                pypoly.log.error('Error while starting module: %s "%s"' % \
                                 (component.name, str(msg))
                                )

    def get_package_name(self, name):
        """
        Return the python package name on the pypoly module name

        :param name: PyPoly module name
        :type name: String
        :return: python package name
        :rtype: String
        """
        name = name.lower()
        for (tmp, component) in ModuleHandler.__modules.iteritems():
            if component.name.lower() == name:
                return component.module_name
        return None

    def get_component_name(self, name):
        if name in ModuleHandler.__modules:
            return ModuleHandler.__modules[name].name
        else:
            return None

    def get_menu(self, name):
        if name in ModuleHandler.__menu:
            return ModuleHandler.__menu[name]
        else:
            return None

    def register_menu(self, menu_func):
        caller = pypoly.get_caller()
        if caller.type == 'module':
            ModuleHandler.__menu[caller.pkg_root] = menu_func


    def get_module(self, name):
        if name in ModuleHandler.__modules:
            return ModuleHandler.__modules[name]
        else:
            return None

    def is_module(self, pkg_name):
        """
        Check if the given package name belongs to a module.

        :param pkg_name: package name
        :type pkg_name: String
        :return: True = pkg is a subpackage of the module | False = pkg isn't a\
                sub package
        :rtype: Boolean
        """
        if self.get_root_pkg(pkg_name) == "":
            return False
        return True

    def get_root_pkg(self, pkg_name):
        """
        Get the package name of the root package.

        :sinte: 0.4

        :param pkg_name: package name
        :type pkg_name: String
        :return: "" = Not found | String = package name
        :rtype: String
        """
        for name in ModuleHandler.__modules.keys():
            if len(name) == len(pkg_name) and name == pkg_name or \
               pkg_name[:len(name) + 1] == name + ".":
                return name
        return ""
