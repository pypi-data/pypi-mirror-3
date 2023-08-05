import types
from xml.dom.minidom import parse

import pypoly
from pypoly.content.webpage.menu import MenuItem, Menu

class Item(object):
    """
    This is a structure item.

    :since: 0.1
    """

    title = {}
    name = None
    component = None
    hidden = False

    module = None
    action = None
    link_module = None
    link_action = None

    def __init__(self, module = None,
                 action = None,
                 link_module = None,
                 link_action = None,
                 link_scheme = None,
                 hidden = False
                ):
        self.module = module
        self.action = action
        self.hidden = hidden

        if module == None:
            self.link_module = link_module
            self.link_action = link_action
            if  link_scheme == None:
                link_scheme = 'default'
            self.link_scheme = link_scheme

        self.title = {'default' : u'Not set'}

    def add_title(self, title, language = None):
        """
        Add a item title and use the given language

        :since: 0.1
        """
        if language == None or language == '':
            language = 'default'
        self.title[language] = title

    def get_title(self):
        """
        Get the title of a structure item.

        :since: 0.1

        :return: the title
        :rtype: Unicode
        """
        langs = pypoly.user.get_languages()
        for lang in langs:
            if lang in self.title:
                return self.title[lang]

        return self.title['default']

class StructureHandler(object):
    #: all structure items (Dict)
    _items = None

    #: all list with the keys of all items
    _item_keys = None

    def __init__(self):
        def parse_node(namespace, node):
            """
            Parse a node and process all the child nodes.

            :since: 0.1

            :param namespace: the current namespace
            :type namespace: String
            :param node: the node
            :type node: xml node
            """

            for item in node.childNodes:
                if item.nodeType == item.ELEMENT_NODE and \
                   item.nodeName == 'item':

                    name = item.getAttribute('name')
                    if namespace != None:
                        name = '.'.join([namespace, name])
                    else:
                        name = name
                    #-print name
                    attr_module = item.getAttribute('module')

                    if attr_module != None:
                        attr_module = pypoly.module.get_package_name(attr_module)

                    attr_action = item.getAttribute('action')

                    hidden = False
                    attr_link_hidden = item.getAttribute('hidden')
                    if attr_link_hidden != None:
                        hidden = attr_link_hidden.lower() in ["yes", "true", "t", "1"]

                    if attr_module != None and attr_action != None:
                        tmp_item = Item(attr_module, attr_action, hidden = hidden)
                    else:
                        link_node = node.getElementsByTagName('link')
                        # get the first link node
                        if len(link_node) > 0:
                            link_node = link_node[0]
                            attr_link_module = link_node.getAttribute('module')
                            attr_link_action = link_node.getAttribute('action')
                            attr_link_scheme = link_node.getAttribute('scheme')
                            if attr_link_module != None:
                                attr_link_module = pypoly.module.get_package_name(attr_link_module)
                            tmp_item = Item(link_module = attr_link_module,
                                            link_action = attr_link_action,
                                            link_scheme = attr_link_scheme,
                                            hidden = hidden
                                           )
                        else:
                            tmp_item = Item()

                    for subnode in item.childNodes:
                        if subnode.nodeType == subnode.ELEMENT_NODE:
                            if subnode.nodeName == 'title':
                                attr_lang = subnode.getAttribute('lang')
                                title = subnode.childNodes[0].nodeValue
                                tmp_item.add_title(title, attr_lang)
                            if subnode.nodeName == 'subitems':
                                parse_node(name, subnode)
                    self._items[name] = tmp_item
                    self._item_keys.append(name)

        self._items = {}
        self._item_keys = []


        # read the structure/menu file
        if pypoly.config.get('menu.file'):
            fp = None
            try:
                fp = open(pypoly.config.get('menu.file'))
            except:
                pypoly.log.warning("Can't read the menu file")

            if fp != None:
                # parse the file
                try:
                    dom = parse(fp)
                    menu = dom.getElementsByTagName('menu')
                    parse_node(None, menu[0])
                    fp.close()
                except:
                    pypoly.log.warning("Can't parse the menu file")
        else:
            pypoly.log.info("No menu file given")

        # get modules already in the structure
        struct_modules = []
        for key in self._item_keys:
            if self._items[key].module != None:
                struct_modules.append(self._items[key].module)

        # add missing modules
        for module in pypoly.module.get_modules():
            if not module in struct_modules:
                mod = pypoly.module.get_module(module)
                key = mod.name.lower()
                self._item_keys.append(key)
                self._items[key] = item = Item(module = mod.module_name,
                                               hidden = True
                                              )


    def get_module_path(self, module_name):
        """
        Get the path of a module.

        :since: 0.1

        :param module_name: the name of the module
        :type module_name: String
        :return: the path as list
        :rtype: List
        """
        for (name,item) in self._items.iteritems():
            if item.module == module_name:
                return name.split('.')
        return []

    def get_components(self, *path):
        """
        Get all components by path.

        Example:
            - module A with path foo.bar.a
            - module B with path foo.bar.b
            - path = foo.bar, returns A,B
            - path = foo.bar.a, return A

        :since: 0.1

        :param path: the path
        :return: components
        :rtype: List
        """
        path = '.'.join(path)
        components = []
        for (name, item) in self._items.iteritems():
            if name[0:len(path)] == path:
                if item.module != None:
                    components.append(item.module)
        return components

    def get_menu(self):
        """
        Create and return the Menu

        :since: 0.1

        :return: the menu
        :rtype: Menu
        """
        menu = Menu()
        for name in self._item_keys:
            item = self._items[name]
            #-print len(name.split('.'))
            if len(name.split('.')) == 1 and item.hidden == False:
                tmp = MenuItem()
                tmp.title = item.get_title()
                if item.module != None:
                    tmp.url = pypoly.url.get_module(
                        item.module,
                        action="index",
                        scheme='default'
                    )
                elif item.link_module != None:
                    tmp.url = pypoly.url.get_module(item.link_module,
                                                   action = item.link_action,
                                                   scheme = item.link_scheme
                                                  )
                menu.append(tmp)
        m = Menu()
        m.append(menu)
        return menu

