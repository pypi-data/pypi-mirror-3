import cgi
import types
from Cookie import BaseCookie
import xmlrpclib

from pypoly.content.rpc import XMLResponse as XMLRPCResponse


class ParamWrapper(dict):
    """
    Wrapper for GET and POST params.

    :since: 0.2
    """
    def get_as_list(self, name):
        """
        Return the parameter with the given name as list.

        :since: 0.2

        :param name: name of the parameter
        :type name: String
        :return: value list
        :rtype: List
        """
        if name in dict:
            value = dict[name]
            if type(value) == types.ListType:
                return value
            else:
                return [value]
        else:
            return []

    def get_as_unicode(self, name):
        """
        Return the parameter as unicode.

        :since: 0.2

        :param name: name of the parameter
        :type name: String
        :return: value of the parameter | if it does not exist return ''
        :rtype: Unicode
        """
        if name in dict:
            value = dict[name]
            if type(value) == types.UnicodeType:
                return value
            else:
                return unicode(value)
        else:
            return u''

    def is_file(self, name):
        """
        Check if a submited parameter is a file.

        :since: 0.2

        :param name: name of the file input field
        :type name: String | Unicode
        :return: True = is a file | False = is not a file
        """
        if name in self:
            value = self[name]
            if type(value) == types.ListType:
                value = value[0]
            if value.__class__ == cgi.FieldStorage and \
               value.filename:
                return True
            else:
                return False
        else:
            return None

    def get_as_file(self, name):
        """
        Get a submited file.

        :since: 0.2

        :param name: name of the file input field
        :type name: String | Unicode
        :return: None | File-Object
        """
        if name in self:
            value = self[name]
            if type(value) == types.ListType:
                value = value[0]
            if value.__class__ == cgi.FieldStorage and \
               value.filename:
                return value.file
            else:
                return None
        else:
            return None


class Dispatcher(object):
    """
    :since: 0.3
    """
    def _dispatch(self):
        return (None, None)


class Request(object):
    """
    :since: 0.3
    """
    #: the http headers
    headers = None

    #: request method: post, get
    method = None

    #: post or get params
    params = None

    #: the cookies
    cookies = None

    def __init__(self, environment):
        self.headers = environment

        # get request method
        if 'REQUEST_METHOD' in self.headers:
            self.method = self.headers['REQUEST_METHOD'].lower()
        else:
            self.method = None

        # get parameters
        self.params = ParamWrapper()

        self.cookies = BaseCookie()
        if 'HTTP_COOKIE' in environment:
            self.cookies.load(environment['HTTP_COOKIE'])
            #-print "load", self.cookies

        self.config = {}

        self.url_params = {}


class DefaultDispatcher(object):
    """
    :since: 0.3
    """
    def _dispatch(self):
        return (DefaultRequest, DefaultResponse)


class DefaultRequest(Request):
    """
    Manage all the data for a http request.

    :since: 0.1
    """
    def __init__(self, environment):
        Request.__init__(self, environment)

        if 'wsgi.input' in environment:
            store = cgi.FieldStorage(
                fp=environment['wsgi.input'],
                environ=environment
            )
        else:
            store = cgi.FieldStorage(environ=environment)

        for key in store.keys():
            v = []
            # convert all params to unicode
            values = store[key]
            if type(values) != types.ListType:
                values = [values]

            for value in values:
                if value.filename:
                    v.append(value)
                else:
                    try:
                        v.append(value.value.decode('utf-8'))
                    except Exception:
                    #      # no utf-8? try ISO-8859-1
                        try:
                            v.append(value.value.decode('ISO-8859-1'))
                        except:
                            raise HTTPError(500, 'Wrong URL Encoding')
            if len(v) == 1:
                self.params[key] = v[0]
            else:
                self.params[key] = v


class DefaultResponse(object):
    """

    :since: 0.2
    """

    headers = {}

    _start_reponse = None

    def __init__(self):
        self.headers = {}
        self.cookies = BaseCookie()


def expose(f):
    """
    Use this function as decorator to make a function accessible via http

    Example::

        class Main():
            @pypoly.http.expose()
            def index(**args, **kwargs):
                return "xml string"

    :since: 0.2
    """
    if not hasattr(f, '_pypoly_config'):
        f._pypoly_config = dict()
    f._pypoly_config['exposed'] = True
    return f


class XMLRPCDispatcher(Dispatcher):
    """

    :since: 0.3
    """
    _rpc_functions = None

    def __init__(self):
        Dispatcher.__init__(self)
        self._rpc_functions = dict()

    def _dispatch(self):
        return (XMLRPCRequest, DefaultResponse)

    @expose
    def index(self, *args, **kwargs):
        pypoly.log.debug(
            "rpc-dispatcher: %s %s" % (
                str(args),
                str(kwargs)
            )
        )
        if 'data' in kwargs:
            data = kwargs['data']
            function_name = data[1]
            if function_name in self._rpc_functions:
                args = data[0]
                v = self._rpc_functions[function_name](*args)
                return XMLRPCResponse(v)

    def register_function(self, func, name=None):
        if name == None:
            name = func.__name__
        self._rpc_functions[name] = func


class XMLRPCRequest(Request):
    """

    :since: 0.3
    """
    def __init__(self, environment):
        Request.__init__(self, environment)
        if 'CONTENT_LENGTH' in environment and \
           'wsgi.input' in environment:
            length = int(environment.get('CONTENT_LENGTH', 0))
            data = environment['wsgi.input'].read(length)
            d = xmlrpclib.loads(data)
            self.params['data'] = d
            #print environment['wsgi.input'].read()
            #print environment['wsgi.input'].read(187)
