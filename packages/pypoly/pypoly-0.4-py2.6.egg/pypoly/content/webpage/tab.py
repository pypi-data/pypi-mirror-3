import os
import types
import sys

import pypoly
import pypoly.http

from pypoly.content.webpage import Content, ContentType, ContentProperties, CSS
from pypoly.content.webpage.form import Form
from pypoly.content.webpage.form.input import HiddenInput

class Tabs(list, Content):
    """
    The main tabs class
    """
    type = ContentType("tab")

    def __init__(self, name, **options):
        """
        see Content.__init__
        """
        Content.__init__(self, name, **options)
        self.id = 'tabs_' + self._name

    def _get_properties(self):
        """
        the get function for the properties options
        """
        props = self._properties
        for item in self:
            props.append(item.properties)
        return props

    properties = property(_get_properties)

    def append(self, item):
        """
        Appends a new tab
        """
        try:
            item.id = self.id + '_' + str(item._name)
        except BaseException, msg:
            pypoly.log.debug(msg)

        list.append(self, item)

    def get_childs(self, level = 1):
        """
        Returns all child items.

        :param level: Get child elements recursively
        :type level: Integer
        :return: List of child elements
        :rtype: List
        """
        if level == 0:
            return []

        if level != None:
            level = level - 1

        items = []
        for item in self:
            func = getattr(item, "get_childs", None)
            if func == None or callable(func) == False:
                continue
            items.append(item)
            items = items + item.get_childs(level = level)

        return items

class DynamicTabs(Tabs):
    """
    DynamicTabs are Tabs managet with javascript

    """
    tab_selected = 0

    type = ContentType("tab.dynamic")

    def __init__(self, name, **options):
        """
        see Tabs.__init__()
        """
        Tabs.__init__(self, name, **options)

    def generate(self, **options):
        """
        generate the dynamic tabs

        uses the tabs_dynamic.xml
        """
        if 'tab' in pypoly.http.request.params:
            self.tab_selected = int(pypoly.http.request.params['tab'])
        else:
            self.tab_selected = 0
        for index, item in enumerate(self):
            if self.tab_selected == index:
                item.selected = True
            else:
                item.selected = False
        for index, tab_item in enumerate(self):
            for item in tab_item:
                if Form == item.__class__:
                    item.append(HiddenInput('tab',
                                            value = index
                                           )
                               )
        tabs = pypoly.template.load_web('webpage', 'tab_dynamic')
        self._properties.append(tabs)
        xml = tabs.generate(tabs = self)
        return xml

class StaticTabs(Tabs):
    """
    StaticTabs are Tabs not managed with javascript

    uses the tabs_static.xml
    """
    #: the content list
    content = []
    type = ContentType("tab.static")

    def __init__(self, name, **options):
        Tabs.__init__(self, name, **options)
        self.content = []

    def generate(self, **options):
        """
        generate the tabs
        """
        if 'tab' in pypoly.http.request.params:
            try:
                tab = int(pypoly.http.request.params['tab'])
            except:
                tab = 0
        else:
            tab = 0
        for index, item in enumerate(self):
            if tab == index:
                item.selected = True
            else:
                item.selected = False
        for index, tab_item in enumerate(self):
            for item in tab_item:
                if Form == item.__class__:
                    item.append(HiddenInput('tab',
                                            value = index
                                           )
                               )
        tabs = pypoly.template.load_web('webpage', 'tab_static')
        self._properties.append(tabs)

        xml = tabs.generate(tabs = self)
        return xml


class TabItem(list, Content):
    """
    this is a TabItem
    """
    #: tab url for StaticTabs
    url = None
    #: True if tab is selected
    selected = False

    type = ContentType("tab.item")

    def __init__(self, name, **options):
        self.url = None
        self.selected = False
        Content.__init__(self, name, **options)

    def _get_properties(self):
        """
        get function for the properties value
        """
        props = self._properties
        for item in self:
            props.append(item.properties)
        return props

    properties = property(_get_properties)

    def get_childs(self, level = 1):
        """
        Returns all child items.

        :param level: Get child elements recursively
        :type level: Integer
        :return: List of child elements
        :rtype: List
        """
        if level == 0:
            return []

        if level != None:
            level = level - 1

        items = []
        for item in self:
            items.append(item)
            items = items + item.get_childs(level=level)

        return items

    def generate(self, **options):
        """
        generete a tab

        B{Info:} only dynamic tabs use this generate function
        """
        tab = pypoly.template.load_web('webpage', 'tab_item')
        self._properties.append(tab)

        xml = tab.generate(tab = self)
        return xml
