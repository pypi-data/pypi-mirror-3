import os
import types
import sys

import pypoly
from pypoly.content.url import URL
from pypoly.content.webpage import Content, ContentType

class MenuObject(list, Content):
    def __init__(self, *args, **options):
        self.title = ''
        Content.__init__(self, *args, **options)

class Menu(MenuObject):
    xml = None
    type = ContentType("menu")
    submenus = []

    def __init__(self, *args, **options):
        MenuObject.__init__(self, *args, **options)
        self.submenus = []

    def append(self, item):
        if isinstance(item, Menu):
            if len(item) > 0 or len(item.submenus) > 0:
                self.submenus.append(item)
        else:
            if isinstance(item.url, URL) and \
               item.url.is_accessible():
                MenuObject.append(self, item)


    def generate(self, *template_file):
        menu = pypoly.template.load_web(*template_file)
        #TODO: add properties support
        xml = menu.generate(menu = self)
        return xml

    def __call__(self, *template_file):
        return self.generate(*template_file)

class MenuItem(MenuObject):
    type = ContentType("menu.item")

    def __init__(self, *args, **options):
        self.title = ""
        self.url = None
        self.description = ""
        MenuObject.__init__(self, *args, **options)

