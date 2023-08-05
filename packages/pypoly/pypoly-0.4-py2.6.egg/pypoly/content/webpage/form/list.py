import types

import pypoly

from pypoly.content.webpage import ContentType
from pypoly.content.webpage.form import FormObject


class List(list, FormObject):

    multiple = False

    type = ContentType("form.list")

    def __init__(self, name, **options):

        FormObject.__init__(self, name, **options)

        self.multiple = False

        # update message list
        msg = {
            'error_internal': _('%(label)s: There was an internal error.'),
        }
        self._messages.update(msg)

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'list')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(element=self)

    def validate(self):

        errors = []

        self._value = self.raw_value

        def set_item_selected(item, value):
            if item.value != None and item.value == value:
                item.selected = True
                return True
            elif item.label != None and item.label == value:
                item.selected = True
                return True
            item.selected = False
            return False

        def set_item_multi_selected(item, value):
            is_selected = False
            if item.value != None and item.value in value:
                item.selected = True
                is_selected = True
            elif item.label != None and item.label in value:
                item.selected = True
                is_selected = True
            return is_selected

        if self.raw_value == '__pypoly_none__':
            self._value = None

        if (self.multiple == True) and \
           (
               type(self._value) == types.StringType or \
               type(self._value) == types.UnicodeType
           ):
            self._value = [self.raw_value]

        if type(self._value) == types.StringType or \
           type(self._value) == types.UnicodeType:
            for item in self:
                if type(item) == ListGroup:
                    for subitem in item:
                        set_item_selected(subitem, self._value)
                else:
                    pass
                    #-print setItemSelected(item, self._value)
        elif type(self._value) == types.ListType:
            for item in self:
                if type(item) == ListGroup:
                    for subitem in item:
                        set_item_multi_selected(subitem, self._value)
                else:
                    set_item_multi_selected(item, self._value)
        else:
            #TODO: internal error
            pass

        #errors? set value to None
        if len(errors) > 0:
            pass
            #self._value = None

        return errors


class EmptyItem(FormObject):
    """
    This is an empty list item. It won't return any value if it was selected.
    """
    selected = False

    type = ContentType("form.list.item.empty")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)
        self._value = '__pypoly_none__'
        self.selected = False


class ListItem(FormObject):
    """
    The list item.
    """
    selected = False

    type = ContentType("form.list.item")

    def __init__(self, name, **options):
        self.selected = False

        FormObject.__init__(self, name, **options)


class ListGroup(list, FormObject):
    """
    Group list items.
    """
    type = ContentType("form.list.item_group")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)


class SelectList(List):
    """
    Create a select list.
    """
    type = ContentType("form.list.select")

    def __init__(self, name, **options):
        List.__init__(self, name, **options)


class DropdownList(List):
    """
    Create a dropdown list.
    """
    type = ContentType("form.list.dropdown")

    def __init__(self, name, **options):

        List.__init__(self, name, **options)
