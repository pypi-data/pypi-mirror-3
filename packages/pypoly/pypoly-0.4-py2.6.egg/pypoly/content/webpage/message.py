import pypoly
from pypoly.content.webpage import Content, ContentType

class Message(Content):

    type = ContentType("message")

    def __init__(self, **options):
        self.text = u''
        self.label = u''
        Content.__init__(self, None, **options)

    def generate(self, **values):
        tpl = pypoly.template.load_web('webpage', 'message')

        return tpl.generate(message = self)


class Error(Message):
    type = ContentType("message.error")


class Info(Message):
    type = ContentType("message.info")


class Success(Message):
    type = ContentType("message.success")


class Warning(Message):
    type = ContentType("message.warning")
