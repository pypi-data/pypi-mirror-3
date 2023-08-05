import os
import types
import sys
import copy

import pypoly

from pypoly.content.webpage import Content, ContentType, ContentProperties

class Header(list, Content):
    """
    Handle all header data for the table.

    :since: 0.1
    """
    def append(self, cells):
        """
        Append the cells as a new row to the table header

        :since: 0.1

        :param cells: list of cells or strings to append
        :type cells: List
        """
        tmp_cells = []

        for cell in cells:
            if Cell in type(cell).__bases__:
                tmp_cells.append(cell)
            else:
                tmp_cell = LabelCell()
                tmp_cell.value = cell
                tmp_cells.append(tmp_cell)

        list.append(self,tmp_cells)

class Footer(list, Content):
    """
    Handle all footer data for the table.
    """
    def append(self, cells):
        """
        Append the cells as a new row to the table footer

        :since: 0.1
        :param cells: list of cells or strings to append
        :type cells: List
        """
        tmp_cells = []

        for cell in cells:
            if Cell in type(cell).__bases__:
                tmp_cells.append(cell)
            else:
                tmp_cell = LabelCell()
                tmp_cell.value = cell
                tmp_cells.append(tmp_cell)

        list.append(self,tmp_cells)

class Table(list, Content):
    """
    Create a table.

    Example::

        page = Webpage()

        # create table
        table = Table()
        table.cols.append(TextCell())
        table.cols.append(TextCell())

        # add two rows to the header
        table.header.append(['Test Label11', 'Test Label12'])
        table.header.append(['Test Label21', TextCell(value = 'Test Label22')])

        # add two rows to the footer
        table.footer.append(['Test Label11', 'Test Label12'])
        table.footer.append(['Test Label21', TextCell(value = 'Test Label22')])

        # add two data rows
        table.append(['Cell11', 'Cell12'])
        table.append([LabelCell(value = 'Cell21'), 'Cell22'])

        page.append(table)

    :since: 0.1

    :todo: add checks for header and footer
    """

    type = ContentType("table")

    def __init__(self, *args, **options):
        self.title = u''
        self._caption = None
        Content.__init__(self, *args, **options)
        self.cols = []
        self.header = Header()
        self.footer = Footer()
        self.id = 'table_' + self._name

        self.template = pypoly.template.load_web('webpage', 'table', 'table')

    def get_caption(self):
        if self._caption == None or self._caption == '':
            return self.title
        else:
            return self._caption

    def set_caption(self, value):
        self._caption = value

    caption = property(get_caption, set_caption)

    def append(self, cells):
        #TODO: this check dosn't work with colspan and rowspan
        #if len(item) != len(self.cols):
        #    pypoly.log.debug('Can not append item with %d cols to table with %d cols' % (len(item), len(self.cols)))
        #    return 0
        #:a temp list of items to append
        tmp_cells = []
        index = 0
        for cell in cells:
            if Cell in type(cell).__bases__:
                tmp_cell = cell
            else:
                tmp_cell = copy.copy(self.cols[index])
                tmp_cell.value = cell
            if tmp_cell.colspan != None and tmp_cell.colspan > 1:
                index = index + tmp_cell.colspan
            else:
                index = index + 1
            tmp_cells.append(tmp_cell)

        list.append(self,tmp_cells)

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
        for row in self:
            for item in row:
                func = getattr(item, "get_childs", None)
                if func == None or callable(func) == False:
                    continue
                items.append(item)
                items = items + item.get_childs(level=level)

        return items

    def generate(self, **options):
        return self.template.generate(table = self)

class Cell(Content):
    """
    This is the parent Column class

    :since: 0.1
    """
    colspan = None
    rowspan = None
    type = ContentType("table.cell")

    def __init__(self, *args, **options):
        """
        Set all defaults
        """
        if 'value' in options:
            self._value = options['value']
        else:
            self._value = None
        self.colspan = None
        self.rowspan = None

        Content.__init__(self, *args, **options)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

    value = property(_get_value,_set_value)

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

        func = getattr(self._value, "get_childs", None)
        if func == None or callable(func) == False:
            return []

        return [self._value] + self._value.get_childs(level=level)

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'table', 'cell')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(cell = self)

class ContentCell(Cell):
    """
    Use this column if you want to display a Label

    :since: 0.1
    """
    type = ContentType("table.cell.content")

    def __init__(self, *args, **options):
        Cell.__init__(self, *args, **options)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

    value = property(_get_value,_set_value)

class LabelCell(Cell):
    """
    Use this column if you want to display a Label

    :since: 0.1
    """
    type = ContentType("table.cell.label")

    def __init__(self, *args, **options):
        Cell.__init__(self, *args, **options)


class LinkCell(Cell):
    """
    Use this cell if you want to display a Link

    :since: 0.1
    """
    #: the url
    url = None

    type = ContentType("table.cell.link")

    def __init__(self, *args, **options):
        self.url = None
        Cell.__init__(self, *args, **options)


class TextCell(Cell):
    """
    Use this column if you want to display text

    :since: 0.1
    """
    type = ContentType("table.cell.text")

    def __init__(self, *args, **options):
        Cell.__init__(self, *args, **options)

class DateCell(Cell):
    """
    Use this column if you want to display a date

    :since: 0.1
    """
    type = ContentType("table.cell.date")

    def __init__(self, *args, **options):
        Cell.__init__(self, *args, **options)

class MoneyCell(Cell):
    """
    Use this Column for money values

    :since: 0.1
    """
    currency = ''

    #: highlight all positiv and negativ values
    highlight_both = False
    #: highlight all negativ values
    highlight_neg = False
    #: highlight all positiv values
    highlight_pos = False

    type = ContentType("table.cell.money")

    def __init__(self, *args, **options):
        """
        Set all defaults
        """
        self.currency = ''
        self.highlight_both = False
        self.highlight_neg = False
        self.highlight_pos = False
        Cell.__init__(self, *args, **options)

    #def format(self, value):
        #tmp = '%.2f %s' % (value, self.currency)
        #col = Col(value = tmp,
                  #type = 'money'
                 #)
        #if (self.highlight_both or self.highlight_neg) and value < 0:
            #col.css_class = 'table_highlight_neg'
        #elif (self.highlight_both or self.highlight_pos) and value >= 0:
            #col.css_class = 'table_highlight_pos'
        #return col
