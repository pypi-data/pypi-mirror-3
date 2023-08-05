import types

import pypoly
from pypoly.content.webpage import ContentType
from pypoly.content.webpage.form import FormObject

class Button(FormObject):
    type = ContentType("form.button")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)
        self.clicked = False

    def generate(self):
        tpl = pypoly.template.load_web("webpage", "form", "button")
        return tpl.generate(element = self)


class SubmitButton(Button):
    type = ContentType("form.button.submit")

    def __init__(self, name, **options):
        Button.__init__(self, name, **options)


class ResetButton(Button):
    type = ContentType("form.button.reset")

    def __init__(self, name, **options):
        Button.__init__(self, name, **options)

class Radiobutton(FormObject):
    type = ContentType("form.button.radio")

    def __init__(self, name, **options):
        self.checked = False
        FormObject.__init__(self, name, **options)

    def generate(self):
        tpl = pypoly.template.load_web("webpage", "form", "radiobutton")
        return tpl.generate(element = self)

class RadiobuttonGroup(list, FormObject):
    type = ContentType("form.button.radio_group")

    def __init__(self, name, **options):

        FormObject.__init__(self, name, **options)

    def get_value(self):
        return self._value

    def set_value(self, value):
        value = str(value)

        if type(value) == types.StringType:
            for item in self:
                if item.value == value:
                    item.checked = True
                else:
                    item.checked = False

    value = property(get_value, set_value)

    def validate(self):
        errors = []

        self._value = None

        raw = str(self.raw_value)

        if type(raw) == types.StringType:
            for item in self:
                if item.value == raw:
                    item.checked = True
                else:
                    item.checked = False

        for item in self:
            if item.checked == True:
                if self._value != None:
                    errors.append('Internal error')

                self._value = item.value

        if self.required == True and self._value == None:
            errors.append('You have to set an option')

        if len(errors) > 0:
            self._value = None

        return errors

    def generate(self):
        tpl = pypoly.template.load_web("webpage", "form", "radiobutton")
        return tpl.generate(element = self)


class Checkbox(FormObject):
    type = ContentType("form.button.checkbox")

    checked = False

    def __init__(self, name, **options):
        self.checked = False
        FormObject.__init__(self, name, **options)

    def validate(self):
        self._value = self.raw_value

        if self._value == '' or self._value == None:
            self.checked = False
            self._value = None
        else:
            self.checked = True

        return []


    def generate(self):
        tpl = pypoly.template.load_web("webpage", "form", "checkbox")
        return tpl.generate(element = self)

class CheckboxGroup(list, FormObject):
    type = ContentType("form.button.checkbox_group")

    def __init__(self, name, **options):

        FormObject.__init__(self, name, **options)

    def get_value(self):
        return self._value

    def set_value(self, value):
        if type(value) != types.ListType:
            # TODO:
            value = [str(value)]

        if type(value) == types.ListType:
            for item in self:
                if item.value in value:
                    pypoly.log.debug("checked")
                    item.checked = True
                else:
                    pypoly.log.debug("not checked")
                    item.checked = False

    value = property(get_value, set_value)

    def validate(self):
        errors = []

        if type(self.raw_value) != types.ListType:
            self._value = [self.raw_value]
        elif type(self.raw_value) == types.ListType:
            self._value = self.raw_value

        if self.required == True and len(self._value) == 0:
            #TODO: better checks
            errors.append('error')

        if len(errors) > 0:
            self._value = None
        else:
            for item in self:
                if item.value in self._value:
                    pypoly.log.debug("checked")
                    item.checked = True
                else:
                    pypoly.log.debug("not checked")
                    item.checked = False

        return errors

    def generate(self):
        tpl = pypoly.template.load_web("webpage", "form", "checkbox")
        return tpl.generate(element = self)
