
#from pypoly import http
from pypoly.content import BasicContent
import xmlrpclib

class XMLResponse(BasicContent):
    #: return value
    _params = None

    def __init__(self, params):
        BasicContent.__init__(self)
        self._params = params
        self._mime_type = 'text/xml'

    def __call__(self):
        content = xmlrpclib.dumps(params = (self._params,),
                                  methodresponse=True
                                 )
        _size = len(content)
        return [content]

