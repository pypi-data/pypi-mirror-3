import os
import types
import logging
import sys
from datetime import datetime
import time as pytime

import pypoly
from pypoly._hook import HookWrapper
from pypoly.content import BasicContent

class CSS(dict):

    _media_types = ['all', 'aural', 'braille', 'embossed', 'handheld', 'print', 'projection', 'screen', 'tty', 'tv']

    def __init__(self, css = None, css_media_type = 'all'):
        for media_type in self._media_types:
            dict.__setitem__(self, media_type, [])
        if css != None:
            self.append(css, css_media_type)

    def __setitem__(self, key, value):
        pass

    def append(self, css, media_type = None):
        """
        appends a css object to an other
        """
        if type(css) == type(self) and media_type == None:
            for media, css_list in css.iteritems():
                if (type(css_list) == types.ListType) and (media in self._media_types):
                    tmp = dict.__getitem__(self, media)
                    for css in css_list:
                        if not css in tmp:
                            tmp.append(css)
                    dict.__setitem__(self, media, tmp)
        elif type(css) == types.ListType and media_type in self._media_types:
            tmp = dict.__getitem__(self, media_type)
            for css in css_list:
                if not css in tmp:
                    tmp.append(css)
            dict.__setitem__(self, media_type, tmp)
        elif type(css) == types.StringType and media_type in self._media_types:
            tmp = dict.__getitem__(self, media_type)
            if not css in tmp:
                tmp.append(css)
            dict.__setitem__(self, media_type, tmp)

class ContentType(object):
    """
    Handle the content type.

    Example:
        a = ContentType("foo")
        b = ContentType("foo.bar")
        print b.is_subtype(a)
        print b.is_subtype("foo")


    >>> a = ContentType("foo")
    >>> a.is_subtype("foo.bar"), a.is_subtype_of("foo.bar")
    False, True

    :since: 0.4
    """
    def __init__(self, content_type):
        """
        :param content_type: The name of the content.
        :type content_type: String
        """
        self._type = content_type

    def __eq__(self, content_type):
        if isinstance(content_type, ContentType):
            content_type = content_type._type

        return self._type == content_type

    def __ne__(self, content_type):
        return not self.__eq__(content_type)

    def __repr__(self):
        return self._type

    def __str__(self):
        return self._type

    def is_subtype(self, content_type, is_type = False):
        """
        Checks if the given content type is a subtype of the object.

        :since: 0.4

        :param content_type: The content type to compare with
        :type content_type: String | ContentType
        :param is_type: Perform also an is_type() check
        :type is_type: Boolean (Default: False)
        :return: True = is subtype | False = is not subtype
        :rtype: Boolean
        """
        if is_type == True and self.is_type(content_type):
            return True

        if isinstance(content_type, ContentType):
            content_type = content_type._type

        _type = self._type

        if _type[-1] != ".":
            _type = _type + "."

        if len(content_type) < len(_type):
            return False

        return content_type[:len(_type)] == _type

    def is_subtype_of(self, content_type, is_type = False):
        """
        Checks if the content type is a subtype of 'content_type'.

        :since: 0.4

        :param content_type: The content type to compare with
        :type content_type: String | ContentType
        :param is_type: Perform also an is_type() check
        :type is_type: Boolean (Default: False)
        :return: True = is subtype | False = is not subtype
        :rtype: Boolean
        """
        if is_type == True and self.is_type(content_type):
            return True

        if isinstance(content_type, ContentType):
            content_type = content_type._type

        if content_type[-1] != ".":
            content_type = content_type + "."

        if len(content_type) > len(self._type):
            return False

        return self._type[:len(content_type)] == content_type

    def is_type(self, content_type):
        """
        Compare the given types and return True if they match.

        :since: 0.4

        :param content_type: The content type to compare with
        :type content_type: String | ContentType
        :return: True = types match | False = types don't match
        :rtype: Boolean
        """
        if isinstance(content_type, ContentType):
            content_type = content_type._type

        return self._type == content_type


class Content(object):
    """
    This is the root class for all content objects (e.g. Form, Table, ...)
    """

    title = u''
    _properties = None
    _name = ''
    type = ContentType("default")

    def __init__(self, *args, **options):
        self.title = u''

        self.update(**options)

        if self.type == None:
            self.type = ContentType("default")

        if len(args) == 0:
            # create a hash if name not set
            import random
            try:
                # python 2.5+
                import hashlib
                name = hashlib.md5(str(random.random())).hexdigest()[:10]
            except:
                #python 2.4
                import md5
                name = md5.new(str(random.random())).hexdigest()
        else:
            name = args[0]

        self._name = name

        self._properties = ContentProperties()

    def __call__(self, **options):
        return self.generate(**options)


    def _get_id(self):
        """
        This function will create an ID if it is not set.

        :return: the item id
        """
        if self._id == None or self._id == '':
            # create a hash if name not set
            import random
            try:
                # python 2.5+
                import hashlib
                tmp_id = hashlib.md5(str(random.random())).hexdigest()[:10]
            except:
                #python 2.4
                import md5
                tmp_id = md5.new(str(random.random())).hexdigest()
            # remove leading numbers
            while(ord(tmp_id[0]) > 47 and ord(tmp_id[0]) < 58):
                tmp_id = tmp_id[1:]
                if len(tmp_id) < 20:
                    tmp_id = hashlib.md5(str(random.random())).hexdigest()
            self._id = tmp_id[:10]

        return self._id

    def _set_id(self, value):
        """
        Set the Item ID

        :param value: this is the id
        :type value: String
        """
        self._id = value

    id = property(_get_id, _set_id)

    def _get_name(self):
        return self._name

    def _set_name(self, value):
        self._name = value

    name = property(_get_name, _set_name)

    def _get_properties(self):
        return self._properties

    def _set_properties(self, value):
        self._properties = value

    properties = property(_get_properties, _set_properties)

    def generate(self):
        """
        This is just a dummy function. It gets overwriten by the "real" content
        class
        """
        pass

    def get_childs(self, level = 1):
        """
        Returns all child items.
        """
        return []

    def get_forms(self):
        return []

    def update(self, **options):
        """
        This function updates the options for the formitem

        :param options: the options to set
        :type options: dict
        """
        if type(options) != types.DictType:
            return -1

        for key, value in options.iteritems():
            # only set a value if it exists in the class
            try:
                if __debug__:
                    if type(value) == types.UnicodeType or type(value) == types.StringType:
                        tmp_debug_value = value
                    else:
                        # if value not String or Unicode try to convert for
                        # debug output
                        tmp_debug_value = str(value)
                    pypoly.log.info('Setting Content Option %s = %s' % (str(key), tmp_debug_value))
                if not callable(getattr(self, key)):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                        pypoly.log.debug("Types match: setting value")
                    elif type(getattr(self, key)) == types.NoneType:
                        #
                        setattr(self, key, value)
                        pypoly.log.debug("Target Type is None: setting the value")
                    elif type(getattr(self, key)) == types.UnicodeType and type(value) == types.StringType:
                        # try to convert a string to unicode
                        try:
                            value = unicode(value, 'utf-8')
                            setattr(self, key, value)
                            pypoly.log.debug("Target Type is Unicode and Source Type is String: converting and setting the value")
                        except:
                            pass
                    else:
                        pypoly.log.info('Failed: Types doesn\'t match')
            except BaseException, inst:
                pypoly.log.info('Failed: %s ' % str(inst))
                continue
        return 0

class JavaScript(Content):
    """
    This class is for the javascript support.
    There are two different method you can use this:

        1. add an url to a javascript file
        2. add the javascript sourcecode

    Example:
    script = JavaScript(url = 'foo.js')
    or
    script = JavaScript(source = 'a = 1; a++;')
    """
    type = ContentType("javascript")
    def __init__(self, url = None, source = None, **options):
        self.url = url
        self.source = source

        self.update(**options)

    def generate(self):
        if self.url != None:
            s = """<script src="%(url)s" type="text/javascript"></script>"""
            return pypoly.template.load_web_from_string(
                s % dict(url = self.url)
            ).generate()
        if self.source != None:
            s = """
            <script type="text/javascript">
            /*<![CDATA[*/
            %(source)s
            /*]]>*/
            </script>
            """
            return pypoly.template.load_web_from_string(
                s % dict(source = self.source)
            ).generate()

class TextContent(Content):
    value = u''
    def __init__(self, *args, **options):
        self.value = u''
        Content.__init__(self, *args, **options)

    def generate(self):
        return self.value


class XMLContent(list, Content):
    def __init__(self, *args, **options):
        Content.__init__(self, *args, **options)

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'xml_content')
        self._properties.append(tpl)
        return tpl.generate(content = self)

class GenericContent(Content):
    def __init__(self, *args, **options):
        Content.__init__(self, *args, **options)

class TemplateContent(Content):
    def __init__(self, *args, **options):
        self.template = None
        Content.__init__(self, *args, **options)

        #: the content handler
        self._content_handler = ContentHandler()
        #: the var handler
        self._var_handler = VarHandler()
        #: the handler for the template plugins
        self._template_plugin_handler = PluginHandler()

    def append(self, *valueList, **valueDict):
        pypoly.log.debug('trying to append content')
        for item in valueList:
            try:
                name = getattr(item, 'name')
                #TODO: add an isContent function
                if isinstance(item, Content):
                    self._content_handler.append(item)
                    pypoly.log.debug('successfull as content')
                else:
                    self._var_handler.append(item)
                    pypoly.log.debug('successfull as var')
            except BaseException, inst:
                pypoly.log.debug("Webpage: no name for item given" + str(inst))

        for key, item in valueDict.iteritems():
            # TODO: do we need this test?
            try:
                name = getattr(item, 'name')
            except:
                name = key
                pypoly.log.debug('Type: ' + str(type(item)))

            if name == key:
                if isinstance(item, Content):
                    self._content_handler.append(**{key : item})
                    pypoly.log.debug('successfull as content')
                else:
                    self._var_handler.append(**{key : item})
                    pypoly.log.debug('successfull as var')
            else:
                pypoly.log.debug("Webpage: itemname is '" + str(name) + "' but '" +
                            str(key) + "' expected" )

    def generate(self, **options):
        self._properties.append(self.template)
        xml = self.template.generate(content = self._content_handler,
                                     plugin = self._template_plugin_handler,
                                     var = self._var_handler
                                    )
        self._properties.append(self.template)
        return xml

    def get_forms(self):
        forms = []
        for item in self._content_handler:
            try:
                #print "item ", item._type
                if item._type == 'form':
                    forms.append(item)
            except BaseException, msg:
                pypoly.log.warning(str(msg))
        return forms

class ContentProperties(object):
    """
    This are the content properties
    """

    def __init__(self, **values):
        self.css = CSS()
        #: this should always be None or a generated xml object produced with the genshi generate() function
        self.xml = None

        self.update(**values)

    def append(self, obj):
        """
        This appends the values of a ContentProperties object to an other.

        :param obj: this is a ContentProperties object
        :type obj: ContentProperties
        """
        pypoly.log.debug('append Properties')
        #print type(obj)
        if ContentProperties == obj.__class__ or ContentProperties in obj.__class__.__bases__:
            self.css.append(obj.css)
        elif CSS == obj.__class__:
            self.css.append(obj)
        else:
            pypoly.log.debug('Can\'t detect contentproperties type')


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
            if key == 'css':
                self.css.append(value)
            else:
                try:
                    if not callable(getattr(self, key)):
                        if type(getattr(self, key)) == type(value):
                            setattr(self, key, value)
                        elif type(getattr(self, key)) == types.NoneType:
                            setattr(self, key, value)
                except:
                    continue
        return 0



class Handler(dict):
    def append(self, *valueList, **value_dict):
        for item in valueList:
            try:
                name = getattr(item, 'name')
                self.update({name : item})
            except BaseException, inst:
                continue
        self.update(value_dict)

# NEW Handler Root Class
# slow change
class HandlerL(list):
    """
    This is the parent handler class for all list style handlers
    """
    def append(self, *valueList, **value_dict):
        """
        append content to the handler
        """
        for item in valueList:
            try:
                name = getattr(item, 'name')
                if len(name) > 0:
                    list.append(self,item)
            except BaseException, inst:
                pypoly.log.debug('can not append: %s' % str(inst))
                continue
        for item in value_dict.values():
            list.append(self, item)

class ContentHandler(HandlerL):
    """
    This class handles the content management in the xml templates.

    A content object can be called with ${content('name_of_the_object')}
    """

    def __init__(self):
        HandlerL.__init__(self)

    def __getattr__(self, name):
        pypoly.log.debug('ContentHandler:' + name)
        content = None
        for item in self:
            if item.name == name:
                content = item
                break

        if content == None:
            pypoly.log.debug('GenericContent')
            return GenericContent(name)
        try:
            if not callable(content):
                content = GenericContent(name,
                                         title = name,
                                         value = self[name]
                                        )
        except BaseException, inst:
            pypoly.log.debug('Error' + str(inst))
            content = GenericContent(name)
        return content

    def __call__(self, name):
        return self.__getattr__(name)

    def get_properties(self):
        properties = ContentProperties()
        for item in self:
            try:
                props = getattr(item, 'properties')
                if not callable(props):
                    properties.append(props)
            except:
                continue

        return properties

    def set_properties(self, value):
        self.__properties = value

    properties = property(get_properties, set_properties)


class MenuHandler(Handler):
    """
    This is the menu handler
    """
    def __getattr__(self, name):
        #print "-----------------"
        #print name
        try:
            if name in self:
                menu = self[name]
                if type(menu) != types.ListType:
                    #print "list"
                    menu = [menu]

                #strip empty menus
                pos = 0
                while pos < len(menu):
                    if len(menu[pos]) == 0 and len(menu[pos].submenus) == 0 and menu[pos].xml == None:
                        del menu[pos]
                    else:
                        pos = pos + 1

                return menu

            else:
                return []
        except BaseException, inst:
            pypoly.log.debug('Error' + str(inst))
        return []

class MessageHandler(object):
    """
    This is the message handler.
    """
    def __init__(self):
        #: internal message lists
        self.__messages = {'success' : [],
                           'error' : [],
                           'info' : [],
                           'warning' : [],
                          }
        #: if all messages are requestet return them in this order
        self.__order = ['error', 'warning', 'info', 'success']

    def __getattr__(self, name):
        """
        Return the message lists.

          - all = return all messages ordered by order
          - error = all error messages
          - warning = all warning messages
          - info = all info messages
          - success = all success messages

        :param name: the name of the error list to return
        :type name: String
        :return: message list or empty list
        """
        if name == 'all':
            messages = []
            for key in self.__order:
                messages = messages + self.__messages[key]
            return messages

        if name in self.__messages:
            return self.__messages[name]
        return []

    def append(self, message):
        """
        Detect message type and append the message to the right message list

        :param message: instance of a Message object
        :type message: instance of a Message object
        :return: True | False
        """
        for (name, value) in self.__messages.items():
            if message.type.is_subtype_of("message." + name, is_type = True):
                self.__messages[name].append(message)
                return True

        return False


class ModuleHandler(Handler):
    name = None
    def __init__(self, name):
        self._name = name

    def url(self, name, *args, **kwargs):
        output = pypoly.url.get_module(self._name, name, *args, **kwargs)
        return output

class PluginHandler(Handler):
    """
    This class handles the template plugins.
    """
    def __init__(self):
        Handler.__init__(self)

    def __getattr__(self, name):
        pypoly.log.debug('PluginHandler:' + name)
        try:
            plugin = pypoly.module.get_template_plugin(name)
            if not plugin == None:
                return plugin
        except BaseException, inst:
            pypoly.log.debug('Error' + str(inst))
        # TODO:
        return None

class VarHandler(Handler):
    """
    Handle all vars of a webpage.

    Example:
        1. Python::

            page = Webpage()
            page.append(test_var = 5)
            page.render()

        2. Template::

            var.test_var
    """
    def __init__(self):
        Handler.__init__(self)

    def __getattr__(self, name):
        """
        Return the value of variable.

        :param name: the name of the variable
        :type name: String
        :return: the value of the variable | None
        :rtype: any type
        """
        return self.__call__(name)

    def __call__(self, name, default = None):
        """
        Return the value of a variable.

        :param name: the name of the variable
        :type name: String
        :param default: the default value, return this if the variable is not set
        :type default: any type
        :return: the value of the variable
        :rtype: any type
        """
        pypoly.log.debug('VarHandler:' + name)

        if name in self:
            return self[name]
        else:
            return default

class Webpage(BasicContent):
    def __init__(self):
        #ToDo: set charset on Accept-Charset HTTP Header
        BasicContent.__init__(self,
                              status = (200, 'OK'),
                              mime_type = 'text/html; charset=utf-8',
                             )
        if __debug__:
            self.__time = {}
            self.__time['init.start'] = datetime.now()

        #: the template to use for the webpage, if None, then use the default template
        self.template = None
        #: the content handler
        self._content_handler = ContentHandler()
        #: the var handler
        self._var_handler = VarHandler()
        #: the handler for the template plugins
        self._template_plugin_handler = PluginHandler()

        # try to get the module name
        try:
            frame = sys._getframe(1)
        except ValueError, msg:
            pypoly.log.error('Error: %s' % str(msg))
        tmp = frame.f_globals['__name__'].split('.')
        self.module_name = tmp[1]

        #: the module handler
        self._module_handler = ModuleHandler(self.module_name)

        #: the menu handler
        self._menu_handler = MenuHandler()

        self._message_handler = MessageHandler()

        menu_content = []

        #print module_list
        caller = pypoly.get_caller()
        path = pypoly.structure.get_module_path(caller.pkg_root)
        #-print "-----------path", path
        if len(path) > 0:
            module_list = pypoly.structure.get_components(path[0])
        else:
            module_list = []
        #-print module_list
        for module_name in module_list:
            menu_func = pypoly.module.get_menu(module_name)
            if menu_func != None:
                menu = menu_func()
                if type(menu) == types.ListType:
                    menu_content = menu_content + menu
                elif menu != None:
                    menu_content.append(menu)
        # add menus to the MenuHandler
        self._menu_handler['content'] =  menu_content
        self._menu_handler['main'] = pypoly.structure.get_menu()

        if __debug__:
            self.__time['init.stop'] = datetime.now()

    def __call__(self, *args, **kwargs):
        content = self.generate()
        self._size = len(content)
        return [content]

    def append(self, *valueList, **valueDict):
        if __debug__:
            _time_start = datetime.now()

        pypoly.log.debug("Trying to append")
        for item in valueList:
            try:
                if isinstance(item, Content):
                    if item.type.is_subtype_of("message"):
                        self._message_handler.append(item)
                        pypoly.log.debug("Successful as message")
                    else:
                        self._content_handler.append(item)
                        pypoly.log.debug("Successful as content")
                else:
                    self._var_handler.append(item)
                    pypoly.log.debug("Successful as var")

            except Exception, inst:
                pypoly.log.warning("Couldn't appending content" + str(inst))

        for key, item in valueDict.iteritems():
            try:
                name = getattr(item, '_name')
                if name != key:
                    pypoly.log.debug(
                        "Webpage: item name is '%(name)s' but '%(key)s' " + \
                        "expected" % dict(
                            name = str(name),
                            key = str(key)
                        )
                    )
                    continue
            except:
                name = key

            try:
                if isinstance(item, Content):
                    if item.type.is_subtype_of("message"):
                        self._message_handler.append(item)
                        pypoly.log.debug("Successful as message")
                    else:
                        self._content_handler.append(**{key : item})
                        pypoly.log.debug("Successful as content")
                else:
                    self._var_handler.append(**{key : item})
                    pypoly.log.debug("Successful as var")

            except Exception, inst:
                pypoly.log.warning("Couldn't appending content" + str(inst))

        if __debug__:
            _time_stop = datetime.now()
            if 'append.time' in self.__time:
                self.__time['append.time'] = self.__time['append.time'] + \
                        (_time_stop - _time_start)
            else:
                self.__time['append.time'] = _time_stop - _time_start

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
        for item in self._content_handler:
            func = getattr(item, "get_childs", None)
            if func == None or callable(func) == False:
                continue
            items.append(item)
            items = items + item.get_childs(level = level)

        return items

    def render(self):
        pypoly.log.deprecated("Don't use the render()-function in the future:"+\
                              "old: page = Webpage(); return page.render()"+\
                              "new: page = Webpage(); return page"
                             )
        return self

    def generate(self, strip_whitespaces = True):
        if __debug__:
            self.__time['render.start'] = datetime.now()

        pypoly.log.debug("render")

        #: the properties for the whole webpage
        page_props = ContentProperties()

        # if no template is set then load the content.xml
        if self.template == None:
            self.template = pypoly.template.load_web('webpage', 'content')

        page_props.update(css = self.template.css)
        # debug
        #pypoly.log.debug('----------')
        #for item in self._content_handler:
            #    pypoly.log.debug(str(item.title))

        #: render the modul content
        content = self.template.generate(module = self._module_handler,
                                         content = self._content_handler,
                                         plugin = self._template_plugin_handler,
                                         var = self._var_handler,
                                         message = self._message_handler,
                                        )

        #: load the body template
        body_tpl = pypoly.template.load_web('webpage', 'body')

        page_props.update(css = body_tpl.css)

        body_content = body_tpl.generate(content = content,
                                         menu = self._menu_handler,
                                         plugin = self._template_plugin_handler,
                                         message = self._message_handler,
                                        )

        #: generate the page
        main_tpl = pypoly.template.load_web('webpage', 'main')
        page_props.update(css = main_tpl.css)

        page_props.append(self._content_handler.properties)

        if __debug__:
            self.__time['render.xml.start'] = datetime.now()

        #: render the page
        content = main_tpl.render(
            body = body_content,
            css = page_props.css,
            hook = pypoly.hook.get_wrapped(
                (
                    "content.web.webpage.head",
                    [],
                    dict(webpage = self)
                )
            )
        )

        if __debug__:
            self.__time['render.xml.stop'] = datetime.now()

        if __debug__:
            self.__time['render.clean.start'] = datetime.now()

        tmp_content = content.split("\n")
        content = []
        for a in tmp_content:
            content.append(a.strip())

        content = "\n".join(content)

        if __debug__:
            self.__time['render.clean.stop'] = datetime.now()

        if __debug__:
            try:
                self.__time['render.stop'] = datetime.now()
                time = self.__time['render.stop'] - self.__time['init.start']
                time_init = self.__time['init.stop'] - self.__time['init.start']
                if not 'append.time' in self.__time:
                    self.__time['append.time'] = datetime.now() - datetime.now()
                time_append = self.__time['append.time']
                time_render = self.__time['render.stop'] - self.__time['render.start']
                time_render_xml = self.__time['render.xml.stop'] - self.__time['render.xml.start']
                time_render_clean = self.__time['render.clean.stop'] - self.__time['render.clean.start']
                pypoly.log.info('Time (Webpage): %s' % str(time))
                pypoly.log.info('  Init: %s' % str(time_init))
                pypoly.log.info('  Append: %s' % str(self.__time['append.time']))
                pypoly.log.info('  Render: %s' % str(time_render))
                pypoly.log.info('    XML:   %s' % str(time_render_xml))
                pypoly.log.info('    Clean: %s' % str(time_render_clean))
            except BaseException, msg:
                pass
                #-print msg
            # This is for the webpage benchmark
            #-print 'Time: %.6f %.6f %.6f %.6f %.6f %.6f' % ((float(time.seconds)+float(time.microseconds)/1000000),
            #                                               (float(time_init.seconds) + float(time_init.microseconds)/1000000),
            #                                               (float(time_append.seconds) + float(time_append.microseconds)/1000000),
            #                                               (float(time_render.seconds) + float(time_render.microseconds)/1000000),
            #                                               (float(time_render_xml.seconds)+float(time_render_xml.microseconds)/1000000),
            #                                               (float(time_render_clean.seconds)+float(time_render_clean.microseconds)/1000000)
            #                                             )
        return content
