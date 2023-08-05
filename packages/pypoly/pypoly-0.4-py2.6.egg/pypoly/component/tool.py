import types

import pypoly

class ToolHandler(object):

    #: tools
    __tools = {}
    #: registered tools
    __tools_reg = {}
    def __init__(self):
        #: tools
        self.__tools = {}
        #: registered tools
        self.__tools_reg = {}

    def __setattr__(self, name, value):
        if name == 'tools' and not type(value) == types.StringType:
            pypoly.log.debug('error')
        elif name != 'tools':
            pypoly.log.info('Adding tool "%s"' % (name))
            object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name in ToolHandler.__tools_reg:
            return ToolHandler.__tools_reg[name]
        else:
            return object.__getattribute__(self, name)
            return None
        #return object.__getattribute__(self, name)

    def load(self, tools):
        for name in tools:
            try:
                pypoly.log.info('Trying to load tool: "%s".' % name)
                component = pypoly.component.load(name, 'pypoly.tool')
                if component != None:
                    comp = component.entry_point.load()

                    comp = comp()

                    component.comp = comp
                    ToolHandler.__tools[component.module_name] = component
                    pypoly.log.info('Loading tool "%s" successful.' % name)
                else:
                    #-print "not found"
                    pass

            except Exception, inst:
                #-print inst
                pypoly.log.error('Loading tool "%s" failed. Error: %s.' % (name, inst), traceback = True)


    def register(self, name, tool):
        """
        Register a new tool with the given name.

        Example::

            pypoly.tool.register('foo', Example())

        :since: 0.1

        :param name: name of the tool
        :type name: String
        :param tool: tool instance
        :type tool: Instance
        """
        ToolHandler.__tools_reg[name] = tool

    def init(self):
        """
        Initialize all tools by calling the init()-function of the tool.

        :since: 0.1
        """
        for (name, tool) in ToolHandler.__tools.iteritems():
            try:
                tool.comp.init()
            except Exception, msg:
                pypoly.log.error('Error while initializing tool: %s "%s"' % \
                                 (tool.name, str(msg))
                                )

    def start(self):
        """
        Start all tools by calling the start()-function of the tool.

        :since: 0.1
        """
        for (name, tool) in ToolHandler.__tools.iteritems():
            try:
                tool.comp.start()
            except Exception, msg:
                pypoly.log.error('Error while starting tool: %s "%s"' % \
                                 (tool.name, str(msg))
                                )

    def is_tool(self, name):
        """
        Check if a tool with the given name exists.

        :since: 0.1

        :param name: the tool name
        :type name: String
        :return: True = tool exists | False = tool doesn't exist
        :rtype: Boolean
        """
        if self.get_root_pkg(pkg_name) == "":
            return False
        return True

    def get_component_name(self, name):
        if name in ToolHandler.__tools:
            return ToolHandler.__tools[name].name
        else:
            return None

    def get_package_name(self, name):
        """
        Get the package name by the name of the tool

        :since: 0.1

        :param name: the name of the tool
        :type name: String
        :return: the package name
        :rtype: String
        """
        for component in ToolHandler.__tools.itervalues():
            if component.name.lower() == name.lower():
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
        for name in ToolHandler.__tools.keys():
            if pkg_name[:len(name)] == name:
                return name
        return ""
