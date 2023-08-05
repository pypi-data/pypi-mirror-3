import pypoly

from pypoly.content.webpage import ContentType
from pypoly.content.webpage.form import FormObject


class Label(FormObject):
    """
    Use this to create the Label.
    """

    type = ContentType("form.label")

    def __init__(self, name, **options):
        FormObject.__init__(self, name, **options)

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'static')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(element=self)


class LinkLabel(FormObject):
    """
    Use this to create a Link in a form
    """

    #: the url
    url = ''

    type = ContentType("form.label.link")

    def __init__(self, name, **options):
        self.url = ''
        FormObject.__init__(self, name, **options)

    def generate(self):
        tpl = pypoly.template.load_web('webpage', 'form', 'static')
        # do we need this
        #self._properties.append(tpl)
        return tpl.generate(element=self)
