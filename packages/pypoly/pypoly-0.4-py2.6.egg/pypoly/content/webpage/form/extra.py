import re
import types

import pypoly

from pypoly.content.webpage import ContentType
from pypoly.content.webpage.table import ContentCell
from pypoly.content.webpage.form import FormObject

class FormTable(FormObject):
    """
    Test
    """
    type = ContentType("extra.formtable")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

        #TODO: add locale support
        if type(value) == types.StringType or type(value) == types.UnicodeType:
            self.raw_value = value
        else:
            self.raw_value = str(value)

    value = property(_get_value, _set_value)


    def validate(self):
        errors = []
        for row in self.value:
            for cell in row:
                if type(cell) == ContentCell:
                    #-print type(cell.value)
                    errors = errors + cell.value.validate()
        return errors

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'extras')

        return tpl.generate(element = self)

class CustomField(FormObject):
    """
    """

    type = ContentType("extra.custom")
    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)

    def validate(self):
        return []

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'extras')

        return tpl.generate(element = self)

