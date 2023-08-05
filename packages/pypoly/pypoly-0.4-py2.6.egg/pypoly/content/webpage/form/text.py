import pypoly

from pypoly.content.webpage import CSS, ContentType
from pypoly.content.webpage.form import FormObject


class Textarea(FormObject):
    """
    """
    type = ContentType("form.text.area")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)
        self._type = 'textarea'

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value
        self.raw_value = str(value)

    value = property(_get_value, _set_value)

    def validate(self):
        errors = []

        self._value = self.raw_value

        errors = errors + FormObject.validate(self)

        # everything ok?
        if len(errors) > 0:
            self._value = None

        return errors

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'textarea')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(element=self)


class WYSIWYG(FormObject):
    """
    """
    type = ContentType("form.text.wysiwyg")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value
        self.raw_value = str(value)

    value = property(_get_value, _set_value)

    def validate(self):
        errors = []

        self._value = self.raw_value

        errors = errors + FormObject.validate(self)

        # everything ok?
        if len(errors) > 0:
            self._value = None

        return errors

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'wysiwyg')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(element=self)
