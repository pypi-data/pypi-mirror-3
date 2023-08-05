import re
from decimal import Decimal
import types

import pypoly
from pypoly.content.webpage import ContentType
from pypoly.content.webpage.form import FormObject


class Input(FormObject):
    """
    Parent for all Input elements.
    """
    #: set this to true if a valuee is readonly(currently not in use)
    readonly = False

    #: set to true if a element is hidden
    hidden = False

    #: autocomplete url
    autocomplete = None

    type = ContentType("form.input")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)
        self.id = "form_input_" + self.name
        self.readonly = False

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
        """
        Validate the values submitted.

        :return: List of error messages
        :rtype: List of Strings
        """
        errors = []
        if self.required == True and (self.raw_value == None or len(self.raw_value) == 0):
                errors.append(self._messages["error_required"] % {"label": self.label})

        return errors

    def generate(self):
        """
        Generate the form. This function is called while PyPoly generates the
        webpage.
        """
        tpl = pypoly.template.load_web("webpage", "form", "input")
        return tpl.generate(element = self)


class TextInput(Input):
    """
    Create a Input field.

    All characters are allowed
    """
    max_length = None
    min_length = None

    type = ContentType("form.input.text")

    def __init__(self, name, **options):
        self.max_length = None
        self.min_length = None
        Input.__init__(self, name, **options)

        # update message list
        msg = {
            "error_maxLength": _("%(label)s: Enter a value less than %(maxLength)i characters long."),
            "error_minLength" : _('%(label)s: Enter a value more than %(minLength)i characters long.')
        }
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = self.raw_value

        if self.raw_value != None:
            if self.max_length != None and len(self.raw_value) > self.max_length:
                errors.append(self._messages['error_maxLength'] % {'max_length' : self.max_length,
                                                                   'label' : self.label
                                                                  }
                             )
            if self.min_length != None and (self.raw_value == None or len(self.raw_value) < self.min_length):
                errors.append(self._messages['error_minLength'] % {'min_length' : self.min_length,
                                                                   'label' : self.label
                                                                  }
                             )
        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            pass
            #self._value = None

        return errors


class AlphaInput(TextInput):
    """
    Create a Input field.

    Only letters are allowed.
    """
    type = ContentType("form.input.alpha")

    def __init__(self, name, **options):
        TextInput.__init__(self, name, **options)
        # update message list
        msg = {'error_onlyLetters' : _('%(label)s Enter only letters.')}
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = self.raw_value
        #print "-----------"
        #print self._value

        if self.raw_value != None:
            check = re.compile('^[a-zA-Z]+$')
            if not check.match(self.raw_value):
                errors.append(self._messages['error_onlyLetters'] % {'label' : self.label})

        errors = errors + TextInput.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class AlphaNumInput(TextInput):
    """
    Create a input field.

    Only alphanumeric value is allowed
    """
    type = ContentType("form.input.alphanum")

    def __init__(self, name, **options):
        TextInput.__init__(self, name, **options)
        # update message list
        msg = {'error_onlyLettersAndNumbers' : _('%(label)s Enter only letters and/or numbers.')}
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = self.raw_value

        if self.raw_value != None:
            check = re.compile('^[a-zA-Z0-9]+$')
            if not check.match(self.raw_value):
                errors.append(self._messages['error_onlyLettersAndNumbers'] % {'label' : self.label})
        errors = errors + TextInput.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class CustomInput(Input):
    """
    Create a custom input field

    Only set regex or characters!!!
    """
    #: check with regex
    regex = None
    #: only this characters are allowed
    characters = None

    type = ContentType("form.input.custom")

    def __init__(self, name, **options):
        Input.__init__(self, name, **options)
        msg = {
            "error_characters":  _("%(label)s: Only characters "\
                                   "'%(characters)s' are allowed"
                                  ),
            "error_regex": _('%(label)s: Wrong Input'),
        }
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = self.raw_value

        if self.regex != None and self._value != None and self._value != '':
            try:
                regex = re.compile(self.regex)
                m = regex.match(self.raw_value)
                if m == None:
                    errors.append(self._messages["error_regex"] % {"label": self.label})
            except BaseException, msg:
                pypoly.log.warning(str(msg))
                errors.append(self._messages["error_regex"] % {"label": self.label})

        if self.characters != None and self._value != None:
            for char in self._value:
                if not char in self.characters:
                    errors.append(
                        self._messages['error_characters'] % {
                            "label": self.label,
                            "characters": self.characters
                        }
                    )
                    break

        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class DateInput(Input):
    """
    Create a date input field
    :todo: add locale support
    """
    type = ContentType("form.input.date")

    def __init__(self, name, **options):
        Input.__init__(self, name, **options)
        msg = {
            "error_wrong_format": _("%(label)s: Wronge Format"),
        }
        self._messages.update(msg)

    def validate(self):
        #TODO: check if we can use babel for validation
        errors = []
        if self.raw_value == None:
            self._value = ''
        else:
            self._value = self.raw_value

        if self.required == False and self._value == '':
            self._value = None
            return Input.validate(self)

        check_de = re.compile('^(?P<day>[0-2]?[0-9]|3[01])\.(?P<month>0?[1-9]|1[0-2])\.(?P<year>[1-9]?[0-9]{3})$')
        match = check_de.match(self._value)
        if match:
            try:
                import datetime
                self._value = datetime.date(int(match.group('year')),
                                            int(match.group('month')),
                                            int(match.group('day'))
                                           )
            except Exception, e:
                errors.append(self._messages["error_wrong_format"] % {"label": self.label})
        else:
            errors.append(self._messages["error_wrong_format"] % {"label": self.label})

        errors = errors + Input.validate(self)
        pypoly.log.todo("Add value")

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class DecimalInput(Input):
    """
    Create a decimalnumber input field.

    Only numbers are allowed.
    """
    #: the minimal value | None = not set
    min_value = None

    #: the maximal value | None = not set
    max_value = None

    #: The minimum number of decimal places allowed.
    min_decimal_places = None

    #: The maximum number of decimal places allowed.
    max_decimal_places = None

    type = ContentType("form.input.decimal")

    def __init__(self, name, **options):
        self.min_value = None
        self.max_value = None
        self.min_decimal_places = None
        self.max_decimal_places = None
        Input.__init__(self, name, **options)

        # update message list
        msg = {
            "error_nonumber": _("%(label)s: Please enter a number"),
            "error_tolarge": _("%(label)s: The value is to large. Please "\
                               "enter a value less then %(maxValue)s"
                              ),
            "error_tosmall": _('%(label)s: The value is to small. Please '\
                                'enter a value larger then %(minValue)s'
                               ),
            "error_mindecimal": _("%(label)s: Please enter more decimale. "\
                                  "Min Decimals %(minDecimal)s"
                                 ),
            "error_maxdecimal": _("%(label)s: Please enter less decimale. "\
                                  "Max Decimals %s(maxDecimal)s"
                                 ),
            "error_decimal": _("%(label)s: Please enter a float number."),
        }
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = None

        if self.raw_value != None and len(self.raw_value) > 0:
            try:
                #try to convert the raw_value
                self._value = Decimal(self.raw_value)

                if self._value.is_nan():
                    errors.append(self._messages["error_nonumber"] % {"label": self.label})

                if self.max_value != None and self._value > self.max_value:
                    errors.append(self._messages["error_tolarge"] % {"label": self.label,
                                                                     "max_value": self.max_value
                                                                    }
                                 )
                if self.min_value != None and self._value < self.min_value:
                    errors.append(self._messages["error_tosmall"] % {"label": self.label,
                                                                     "min_value": self.min_value
                                                                    }
                                 )
                pos = str(self.value).rfind('.')
                if pos < 0:
                    decimal_places = 0
                else:
                    decimal_places = len(str(self.value)) - pos - 1

                if self.min_decimal_places != None and decimal_places < self.min_decimal:
                    errors.append(self._messages["error_mindecimal"] % {"label": self.label,
                                                                        "min_vecimal": self.min_decimal
                                                                       }
                                 )
                if self.max_decimal_places != None and decimal_places > self.max_decimal_places:
                    errors.append(self._messages["error_maxdecimal"] % {"label": self.label,
                                                                        "maxDecimal": self.max_decimal_places
                                                                       }
                                 )

            except Exception, msg:
                errors.append(self._messages["error_nonumber"] % {"label": self.label})
                pypoly.log.debug("Wrong number: %s" % str(msg))
        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class FileInput(Input):
    min_size = None

    max_size = None

    type = ContentType("form.input.file")

    def __init__(self, name, **options):
        self.min_size = None
        self.max_size = None
        self.file = None

        Input.__init__(self, name, **options)

        msg = {
            "error_nofile": _('%(label)s: This is not a file'),
        }
        self._messages.update(msg)

    def validate(self):
        errors = []

        import cgi
        # check if a value is given and if it is a file
        if self.raw_value != None and type(self.raw_value.__class__) != type(cgi.FieldStorage):
            errors.append(
                self._messages["error_nofile"] % {
                    "label": self.label,
                }
            )
        elif type(self.raw_value.__class__) == type(cgi.FieldStorage) and \
           self.raw_value.file != None:
            self.file = self.raw_value.file
            self._value = self.raw_value.filename
            self.raw_value = self.raw_value.filename

        errors = errors + Input.validate(self)

        return errors


class FloatInput(Input):
    """
    Create a floatnumber input field.

    Only numbers are allowed.
    """
    #: the minimal value | None = not set
    min_value = None

    #: the maximal value | None = not set
    max_value = None

    #:
    min_decimal = None

    #:
    max_decimal = None

    type = ContentType("form.input.float")

    def __init__(self, name, **options):
        self.min_value = None
        self.max_value = None
        self.min_decimal = None
        self.max_decimal = None
        Input.__init__(self, name, **options)

        # update message list
        msg = {
            "error_nonumber": _("%(label)s: Please enter a number"),
            "error_tolarge": _("%(label)s: The value is to large. Please "\
                               "enter a value less then %(maxValue)s"
                              ),
            "error_tosmall": _("%(label)s: The value is to small. Please "\
                               "enter a value larger then %(minValue)s"
                              ),
            "error_mindecimal": _("%(label)s: Please enter more decimale. "\
                                  "Min Decimals %(minDecimal)s"
                                 ),
            "error_maxdecimal": _("%(label)s: Please enter less decimale. "\
                                  "Max Decimals %s(maxDecimal)s"
                                 ),
            "error_decimal": _("%(label)s: Please enter a float number."),
        }
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = None

        if self.raw_value != None and len(self.raw_value) > 0:
            try:
                self._value = float(self.raw_value)
                if self.max_value != None and self._value > self.max_value:
                    errors.append(
                        self._messages['error_tolarge'] % {
                            "label": self.label,
                            "maxValue": self.max_value
                        }
                    )
                if self.min_value != None and self._value < self.min_value:
                    errors.append(
                        self._messages["error_tosmall"] % {
                            "label": self.label,
                            "minValue" : self.min_value
                        }
                    )
                if self.min_decimal != None or self.max_decimal != None:
                    tmp = str(self._value).split('.')
                    if len(tmp) == 2:
                        if self.min_decimal != None and len(tmp[1]) >= self.min_decimal:
                            errors.append(self._messages['error_mindecimal'] % {'label' : self.label,
                                                                                'minDecimal' : self.min_decimal
                                                                               }
                                         )
                        if self.max_decimal != None and len(tmp[1]) >= self.max_decimal:
                            errors.append(self._messages['error_maxdecimal'] % {'label' : self.label,
                                                                                'maxDecimal' : self.max_decimal
                                                                               }
                                         )
                    else:
                        errors.append(self._messages['error_decimal'] % {'label' : self.label})

            except:
                errors.append(self._messages['error_nonumber'] % {'label' : self.label})
        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors

class HiddenInput(TextInput):
    """
    Create a hidden input field.
    """
    def __init__(self, name, **options):
        TextInput.__init__(self, name, **options)
        self.hidden = True

class MACInput(Input):
    """
    Create a Input field for a MAC Address.
    """
    type = ContentType("form.input.mac")

    def __init__(self, name, **options):
        Input.__init__(self, name, **options)
        msg = {'error_nomac' : _('%(label)s: Is not a valid MAC Address')}
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = None
        pypoly.log.todo('convert value to mac')

        if self.raw_value != None:
            mac_regex = re.compile('^(?P<num_1>[0-9a-fA-F]{2}):(?P<num_2>[0-9a-fA-F]{2}):(?P<num_3>[0-9a-fA-F]{2}):(?P<num_4>[0-9a-fA-F]{2}):(?P<num_5>[0-9a-fA-F]{2}):(?P<num_6>[0-9a-fA-F]{2})$')
            cmac_regex = re.compile('^(?P<num_1>[0-9a-fA-F]{2})(?P<num_2>[0-9a-fA-F]{2})\.(?P<num_3>[0-9a-fA-F]{2})(?P<num_4>[0-9a-fA-F]{2})\.(?P<num_5>[0-9a-fA-F]{2})(?P<num_6>[0-9a-fA-F]{2})$')
            mac = mac_regex.match(self.raw_value)
            cmac = cmac_regex.match(self.raw_value)
            if not mac and not cmac:
                errors.append(self._messages['error_nomac'] % {'label' : self.label,})
            if mac:
                self._value = (mac.group('num_1'),
                               mac.group('num_2'),
                               mac.group('num_3'),
                               mac.group('num_4'),
                               mac.group('num_5'),
                               mac.group('num_6')
                              )
            if cmac:
                self._value = (cmac.group('num_1'),
                               cmac.group('num_2'),
                               cmac.group('num_3'),
                               cmac.group('num_4'),
                               cmac.group('num_5'),
                               cmac.group('num_6')
                              )
        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors

class NumberInput(Input):
    """
    Create a number input field.

    Only numbers are allowed.
    """
    #: the minimal value | None = not set
    min_value = None

    #: the maximal value | None = not set
    max_value = None

    type = ContentType("form.input.number")

    def __init__(self, name, **options):
        self.max_value = None
        self.min_value = None
        Input.__init__(self, name, **options)

        # update message list
        msg = {'error_nonumber' : _('%(label)s: Please enter a number'),
               'error_tolarge' : _('%(label)s: The value is to large. Please enter a value less then %(maxValue)s'),
               'error_tosmall' : _('%(label)s: The value is to small. Please enter a value larger then %(minValue)s')
              }
        self._messages.update(msg)

    def validate(self):
        errors = []

        self._value = self.raw_value

        if self.required == False and self._value == '':
            self._value = None
            return Input.validate(self)

        if self._value != None and len(self._value) > 0:
            try:
                self._value = int(self._value)
                if self.max_value != None and self._value > self.max_value:
                    errors.append(self._messages['error_tolarge'] % {'label' : self.label,
                                                                      'maxValue' : self.max_value
                                                                    }
                                 )
                if self.min_value != None and self._value < self.min_value:
                    errors.append(self._messages['error_tosmall'] % {'label' : self.label,
                                                                      'minValue' : self.min_value
                                                                    }
                                 )
            except:
                errors.append(self._messages['error_nonumber'] % {'label' : self.label})
        errors = errors + Input.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors


class PasswordInput(TextInput):
    """
    Create a password field.
    """
    type = ContentType("form.input.password")

    def __init__(self, name, **options):
        TextInput.__init__(self, name, **options)

    def validate(self):

        self._value = self.raw_value

        errors = []
        errors = errors + TextInput.validate(self)

        #errors? set value to None
        if len(errors) > 0:
            self._value = None

        return errors
