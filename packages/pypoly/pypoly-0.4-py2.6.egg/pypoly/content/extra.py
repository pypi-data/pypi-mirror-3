import os
import types

import pypoly

from pypoly.content import BasicContent

"""
Handle all the JSON stuff.

For more informations on JSON see http://json.org/

"""


def generate(data):
    def encode_var(value):
        """
        :todo add more types
        """
        if type(value) == types.NoneType:
            return 'null'

        if type(value) == types.BooleanType:
            if value == True:
                return 'true'
            else:
                return 'false'

        if type(value) == types.StringType or \
           type(value) == types.UnicodeType:
            value = value.replace('"', '\\"')
            value = value.replace('\\', '\\\\')
            value = value.replace('/', '\\/')
            value = value.replace('\b', '\\b')
            value = '"%s"' % (value)
            return value

        if type(value) == types.IntType:
            return str(value)



    if type(data) == types.ListType:
        tmp = []
        for item in data:
            if type(item) == types.ListType:
                tmp.append(generate(item))
            elif type(item) == types.DictType:
                tmp.append(generate(item))
            else:
                tmp.append(encode_var(item))
        return '[' + ','.join(tmp) + ']'

    elif type(data) == types.DictType:
        tmp = []
        for key, value in data.items():
            if type(value) == types.ListType or\
               type(value) == types.DictType:
                tmp.append('%s : %s' % (encode_var(key),
                                        generate(value)
                                       )
                          )
            else:
                tmp.append('%s : %s' % (encode_var(key),
                                        encode_var(value)
                                       )
                          )
        return '{' + ','.join(tmp) + '}'

    return "nichts"


class JSON(BasicContent):
    def __init__(self, data="", callback=None):
        BasicContent.__init__(self,
                              status = (200, 'OK'),
                              mime_type = 'application/json; charset=utf-8',
                             )

        self.callback = callback
        self.data = data

    def __call__(self, *args, **kwargs):
        try:
            # Python >= 2.6
            import json
            content = json.dumps(self.data)
        except Exception, msg:
            #-print msg
            # Python < 2.6
            content = generate(self.data)
        # make jsonp
        if self.callback != None:
            content = self.callback + "(" + content + ")"
        content = content.encode('utf-8')
        self._size = len(content)
        return [content]

    def render(self):
        pypoly.log.deprecated('don\'t use the render function')
        return self

class PlainText(BasicContent):
    #: the data of the plain text
    _data = ''

    def __init__(self, status = (200, 'OK'), mime_type = 'text/plain',data = ''):
        BasicContent.__init__(self,
                              status,
                              mime_type = mime_type,
                             )

        self._data = data

    def append(self, data):
        self._data = self._data + data

    def __call__(self, *args, **kwargs):
        content = self._data.encode('utf-8')
        self._size = len(content)
        return [content]
