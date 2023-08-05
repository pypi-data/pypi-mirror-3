import types
import logging
import os
import sys
import copy

import pypoly

from pypoly.content.webpage import CSS

class PyPolyHandler(object):
    def __init__(self):
        self.url = pypoly.url
        self.user = pypoly.user

class TemplateOutput(object):
    def __init__(self, **values):
        pass

    def generate(self, *args, **kwargs):
        """
        Generate the output of a sub template to include it into an other one.
        """
        return ""

    def render(self, *args, **kwargs):
        """
        Render the template and return the result as string.
        """
        return ""

    def update(self, **options):
        pass

class WebTemplateOutput(TemplateOutput):
    """

    """
    def __init__(self, **values):
        self.css = CSS()
        self.javascript = []

        self.update(**values)

    def append(self, obj):
        """
        This appends the values of a TemplateOutput object to an other.

        :param obj: this is a TemplateOutput object
        :type obj: TemplateOutput
        """
        self.css.append(obj.css)
        self.javascript.append(obj.javascript)

    def generate(self, *args, **kargs):
        """
        """
        return ""

    def render(self, *args, **kargs):
        """
        """
        return ""

    def update(self, **options):
        """
        This function updates the class params

        :param options:
        :type options: dict
        """
        if type(options) != types.DictType:
            return -1

        for key, value in options.iteritems():
            # only set a value if it exists in the class
            try:
                if not callable(getattr(self, key)):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif type(getattr(self, key)) == types.NoneType:
                        setattr(self, key, value)
            except:
                continue
        return 0

class XMLTemplateOutput(WebTemplateOutput):
    """
    """
    pass

class TemplateConfig(object):
    """
    This class loads
    """
    css = {}

    def __init__(self, name, filename, module = None):
        self.css = {}
        if name:
            self.load(name, filename, module)

    def load(self, name, path, module = None):
        pypoly.log.info('Loading "' + name + '"')
        import ConfigParser
        config = ConfigParser.ConfigParser()
        if module:
            filename = os.path.join(
                pypoly.get_path(
                    pypoly.config.get('template.path')
                ),
                path,
                module,
                'webpage',
                name,
                'config.cfg'
            )
        else:
            filename = os.path.join(
                pypoly.get_path(
                    pypoly.config.get('template.path')
                ),
                path,
                name,
                'pypoly',
                'web',
                'config.cfg'
            )

        pypoly.log.info(
            "Loading template config: %(filename)s" % dict(
                filename = filename
            )
        )

        config.read(filename)
        # TODO:
        for section in config.sections():
            #: create this temporally
            tmp_css = CSS()
            for media_type in tmp_css._media_types:
                option = '.'.join(['css',media_type])
                if config.has_option(section, option):
                    tmp_list = config.get(section, option).split(',')
                    self.css[section] = tmp_css
                    pypoly.log.info("css option found")
                    for item in tmp_list:
                        if module:
                            self.css[section].append(module + '/' + item.strip(),
                                                     media_type = media_type
                                                    )
                        else:
                            self.css[section].append(item.strip(),
                                                     media_type = media_type
                                                    )
