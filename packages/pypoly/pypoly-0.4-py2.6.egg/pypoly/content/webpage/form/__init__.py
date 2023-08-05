#from pypoly.content.form._form import Form, Label, LinkLabel, ItemGroup
#from pypoly.content.form.button import *
#from pypoly.content.form.input import *
#from pypoly.content.form.list import *

#__all__ = ["buttons", "extras", "inputs", "lists", "static", "texts", "Fieldset", "Form", "TableForm"]

import os
import types
import sys

import pypoly
from pypoly.content.webpage import Content, ContentType

class DictProxy(list):
    """
    """

    #: the elements
    __elements = {}
    def __init__(self):
        self.__elements = {}

    def __setattr__(self, name, value):
        if name not in self.__elements:
            self.__elements[name] = len(self.__elements)
            #list.append(value)


    def __getattr__(self, name):
        for element in self:
            if element.name == name:
                return element
        else:
            return None

    #def append(self, name, value):
    #    if name not in self.__elements:
    #        self.__elements[name] = len(self.__elements)
    #        list.append(value)


class Fieldset(Content, list):
    """
    A Fieldset element for the form
    """
    type = ContentType("form.fieldset")

    def get_childs(self, level = 1):
        """
        Returns all child elements.

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

class Form(Content):
    """
    Use this to create a Form.

    Example:
        - TODO
    """
    #: the form method "post" or "get"
    method = None

    #: the form action e.g. http://example.com/foo/bar
    action = None

    #: a list of errors
    errors = []

    #: this is a list of submit and reset buttons
    buttons = []

    #: elements
    elements = None

    #: the content type, don't set this value manualy
    type = ContentType("form")

    #: the default encoding type of a form
    enctype = None

    def __init__(self, name, method = 'post', template = None, **options):
        self.method = method.lower()
        self.action = None
        self._hidden = []
        Content.__init__(self, name, **options)

        self.__is_submit = False
        self.errors = []

        self.buttons = []
        if template == None:
            self.template = pypoly.template.load_web('webpage', 'form', 'default')
        else:
            self.template = template

        self.elements = DictProxy()

        self.__new_fieldset = True

    def __call__(self, **values):
        """
        it calls the generate function
        """
        return self.generate()

    def _get_hidden(self):
        """
        Get function for the hidden option
        """
        return self._hidden

    #: a list of all hidden elements
    hidden = property(_get_hidden)

    def _get_properties(self):
        """
        Get function for the properties option
        """
        props = self._properties
        for item in self:
            props.append(item.properties)
        return props

    def _set_properties(self, value):
        """
        set function for the properties option
        """
        self._properties = value

    #: the properties
    properties = property(_get_properties, _set_properties)

    def add_button(self, button):
        """
        Add a Button to the form.

        Only add Reset and Submit Buttons
        """
        #: create a button name
        button.name = 'form_' + self._name + '_submit_' + button.name
        self.buttons.append(button)

    def append(self, item):
        """
        Appends a FormObject to the form

        :param item: The item to append
        :type item: Subclass of FormObject
        :return: True = Appended item successfully
        :rtype: Boolean
        """
        if item.type.is_subtype_of("form.input") and \
           item.hidden == True:
            self._hidden.append(item)
            return True

        if item.type.is_subtype_of("form.fieldset", is_type = True):
            self.elements.append(item)
            self.__new_fieldset = True
            return True

        #print "no new fieldset"
        if self.__new_fieldset == True:
            self.__new_fieldset = False
            self.elements.append(Fieldset())

        self.elements[len(self.elements)-1].append(item)
        return True

    def is_submit(self):
        """
        Check if the form was submited

        :return: True if form was submited, False form was NOT submited
        """
        return self.__is_submit

    def is_clicked(self, name):
        """
        check if a the button with the given name was clicked

        :param name: the name of the button
        :type name: String
        :return: True = button was clicked | False = button was not clicked
        :rtype: Boolean
        """
        for button in self.buttons:
            tmp_name = 'form_' + self._name + '_submit_' + name
            if button.name == tmp_name:
                return button.clicked

    def generate(self):
        """
        generate the form and use the template form.xml
        """

        names = self.get_element_names()
        for name in names:
            element = self.get_element_by_name(name)
            if element.type == 'input' and element.subtype == 'file':
                self.enctype = 'multipart/form-data'
                break

        return self.template.generate(form = self)

    def get_childs(self, level = 1):
        """
        Returns all child elements.

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
        for item in self.elements:
            func = getattr(item, "get_childs", None)
            if func == None or callable(func) == False:
                continue
            items.append(item)
            items = items + item.get_childs(level=level)

        return items

    def get_element_names(self, subtype = None):
        """
        Return a list with all element names

        :since: 0.2

        :param element_type: return only elements with the given type
        :type element_type: String
        :param element_subtype: return only elements with the given type and the given subtype
        :type element_subtype: String
        :return: list of element names
        :rtype: List
        """
        names = []
        def get_element_names(item):
            names = []
            if item.type.is_subtype_of("extra.formtable", is_type = True):
                    for col in item.value:
                        for cell in col:
                            if cell.subtype == 'content_cell':
                                if subtype == None:
                                    names.append(cell.value.name)
                                elif cell.value.type.is_subtype_of(subtype, is_type = True):
                                    names.append(cell.value.name)

            else:
                if subtype == None:
                    names.append(item.name)
                elif item.type.is_subtype_of(subtype, is_type = True):
                    names.append(item.name)

            return names

        for item in self.elements:
            # detect if a form item is a fieldset
            if item.type.is_type("form.fieldset"):
                for subitem in item:
                    names = names + get_element_names(subitem)
            else:
                names = names + get_element_names(item)

        for item in self._hidden:
            names.append(item.name)
        return names

    def get_element_by_name(self, name):
        """
        Returns a form element with the given name

        :param name: the name of the element
        :type name: String
        :return: None | the element
        :since: 0.1
        """
        for fieldset in self.elements:
            for item in fieldset:
                if item.type.is_type("extra.formtable"):
                        for col in item.value:
                            for cell in col:
                                if cell.is_subtype_of("table.cell.content", is_type = True):
                                    if name == cell.value.name:
                                        return cell.value
                else:
                    if item.name == name:
                        return item

        for item in self._hidden:
            if item.name == name:
                return item

        # not found
        return None


    def get_raw_value(self, name, default = None):
        """
        Return the value of an formobject

        :since: 0.1
        :param name: the name of the formobject
        :type name: String
        :param default: the default value if the button value is not set
        :type default: any
        """
        element = self.get_element_by_name(name)
        if element != None:
            pypoly.log.debug('element found: %s' % name)
            return element.raw_value

        #not found
        pypoly.log.debug('element not found: %s' % name)
        return default

    def get_value(self, name, default = None):
        """
        return the value of an formobject

        :param name: the name of the formobject
        :type name: String
        :param default: the default value if the button value is not set
        :type default: any
        :since: 0.1
        """
        element = self.get_element_by_name(name)
        if element != None:
            pypoly.log.debug('element found: %s' % name)
            return element.value

        #not found
        pypoly.log.debug('element not found: %s' % name)
        return default

    def set_value(self, name, value):
        """
        set the value of an formobject

        :since: 0.1

        :param name: the name of the formobject
        :type name: String
        :param value: the value to set
        :type value: any
        """
        element = self.get_element_by_name(name)
        if element != None:
            pypoly.log.debug('element found: %s' % name)
            element.value = value
            return True

        #not found
        pypoly.log.debug('element not found: %s' % name)
        return False

    def set_values(self, value_dict):
        """
        set the value of an formobject

        :since: 0.1

        :param value_dict: a dict with all values to set
        :type value_dict: Dict
        """
        for (name, value) in value_dict.items():
            self.set_value(name, value)

    def prepare(self, values):
        """
        prepares the form

        TODO: better text

        :since: 0.1

        :param values: the FormItem values
        :type values: Dict
        """
        self.__is_submit = False

        # first check if this form was submited
        for button in self.buttons:
            if button.name in values:
                self.__is_submit = True
                button.clicked = True

        if self.__is_submit == True:
            names = self.get_element_names()
            for name in names:
                element = self.get_element_by_name(name)
                if element != None:
                    if element.name in values:
                        pypoly.log.debug("set: "+ element.name)
                        element.raw_value = values[name]


    def validate(self):
        """
        validates the form and returns True if everything is ok

        this function also appends generated error messages to self.errors list

        B{Don't call this function more then one time}

        :since: 0.1

        :return: True | False
        """
        self.errors = []
        for item in self.hidden:
            if len(item.validate()) > 0:
                self.errors.append(_("Internel Error: Please try again later" + \
                                     " and contact the System administrator"))
                break

        names = self.get_element_names()
        for name in names:
            element = self.get_element_by_name(name)
            if element != None:
                self.errors = self.errors + element.validate()

        #for fieldset in self.elements:
            #for item in fieldset:
                #errlist = item.validate()
                #if errlist:
                    #for err in errlist:
                        #self.errors.append(err)
        if len(self.errors) > 0:
            return False

        return True

from pypoly.content.webpage.table import Table

class TableForm(Form, Table):
    """


    :since: 0.2
    """
    def __init__(self, name, method = 'post', template = None, **options):
        Table.__init__(self, name, **options)
        Form.__init__(self, name, method, template, **options)

        if template == None:
            self.template = pypoly.template.load_web('webpage', 'form', 'table_form')
        else:
            self.template = template

    def append(self, item):
        """
        Appends a FormObject to the form
        """
        if type(item) == types.ListType:
            Table.append(self, item)
        elif item.type == 'input' and item.hidden == True:
            self._hidden.append(item)

    def get_childs(self, level=1):
        return Table.get_childs(self, level=level)

    def get_element_names(self, subtype = None):
        """
        Return a list with all element names

        :since: 0.2

        :param element_type: return only elements with the given type
        :type element_type: String
        :param element_subtype: return only elements with the given type and the given subtype
        :type element_subtype: String
        :return: list of element names
        :rtype: List
        """
        names = []
        for row in self:
            for cell in row:
                if cell.type.is_subtype_of("table.cell.content", is_type = True):
                    if cell.value != None:
                        item = cell.value

                        if not hasattr(item, "type"):
                            # if the cell is a content_cell, then we need a type
                            # value
                            pypoly.log.error(
                                "Content_cell item has no type attribute"
                            )
                            continue

                        if subtype == None:
                            names.append(item.name)
                        elif subtype != None:
                            if item.type.is_subtype_of(subtype, is_type = True):
                                names.append(item.name)

        for item in self._hidden:
            names.append(item.name)

        return names

    def get_element_by_name(self, name):
        """
        Returns a form element with the given name

        :since: 0.2
        :param name: the name of the element
        :type name: String
        :return: None | the element
        """

        for row in self:
            for cell in row:
                if cell.type.is_subtype_of("table.cell.content", is_type = True):
                    if cell.value != None:
                        item = cell.value
                        if item.name == name:
                            return item

        for item in self._hidden:
            if item.name == name:
                return item

        # not found
        return None





class FormObject(Content):
    """
    This class is the root class for all formitems and formobjects. It's the parent class for e.g. all Input classes

    :since: 0.1

    :param options: the options for the class
    :type options: dict
    """
    label = None
    required = False
    type = ContentType("form")

    def __init__(self, name, **options):
        self.name = name
        self._id = None
        self._value = None
        self.raw_value = u""
        self.label = None
        self.required = False
        self.set_help()
        self._description = None
        Content.__init__(self, name, **options)
        self._messages = {'error_required' : _('%(label)s: This field is required. Please enter a value.')}

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

    value = property(_get_value, _set_value)


    def get_childs(self, level = 1):
        """
        Returns all child items.

        :param level: Get child elements recursively
        :type level: Integer
        :return: List of child elements
        :rtype: List
        """
        return []

    def set_help(self, short_text = None, long_text = None, url = None):
        """
        Not in use, yet!!!
        """
        self.help = {
            'short_text' : short_text,
            'long_text' : long_text,
            'url' : url
        }

    def validate(self):
        """
        Validates the FormItem
        """
        errors = []
        if self.required == True and self.value == None:
            errors.append(self._messages['error_required'] % {'label' : self.label})

        return errors

