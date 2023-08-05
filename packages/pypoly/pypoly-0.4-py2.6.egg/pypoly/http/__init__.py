import mimetypes
import threading
import Queue
import copy
from Cookie import BaseCookie
import os
import re
import pkg_resources

import cgi
import types
from cgi import parse_qs, escape
from wsgiref.util import FileWrapper

import pypoly
import pypoly.http.handler
import pypoly.routes
from pypoly.content import BasicContent
from pypoly.http.dispatcher import DefaultRequest, DefaultResponse


# we try to find a session handler on the first request
SessionHandler = None


class ThreadServingProxy(threading.local):
    """
    Handle per session vars.

    :since: 0.2
    """

    #: the request object
    request = None

    #: the response object
    response = None

    #: the session object
    session = None

    def load(self, request, response, session):
        self.request = request
        self.response = response
        self.session = session

    def clear(self):
        """
        Remove all attributes of self.

        :since: 0.2
        """
        self.__dict__.clear()

serving = ThreadServingProxy()


class ThreadLocalProxy(object):
    """
    A Proxy for the per request vars

    :since: 0.2
    """
    __slots__ = ['__attrname__', '__dict__']

    def __init__(self, attrname):
        self.__attrname__ = attrname

    def __getattr__(self, name):
        child = getattr(serving, self.__attrname__)
        return getattr(child, name)

    def __setattr__(self, name, value):
        if name in ("__attrname__", ):
            object.__setattr__(self, name, value)
        else:
            child = getattr(serving, self.__attrname__)
            setattr(child, name, value)

    def __delattr__(self, name):
        child = getattr(serving, self.__attrname__)
        delattr(child, name)

    def _get_dict(self):
        child = getattr(serving, self.__attrname__)
        d = child.__class__.__dict__.copy()
        d.update(child.__dict__)
        return d
    __dict__ = property(_get_dict)

    def __getitem__(self, key):
        child = getattr(serving, self.__attrname__)
        return child[key]

    def __setitem__(self, key, value):
        child = getattr(serving, self.__attrname__)
        child[key] = value

    def __delitem__(self, key):
        child = getattr(serving, self.__attrname__)
        del child[key]

    def __contains__(self, key):
        child = getattr(serving, self.__attrname__)
        return key in child

    def __len__(self):
        child = getattr(serving, self.__attrname__)
        return len(child)

    def __nonzero__(self):
        child = getattr(serving, self.__attrname__)
        return bool(child)

request = ThreadLocalProxy('request')
response = ThreadLocalProxy('response')
session = ThreadLocalProxy('session')


def expose(*args, **kwargs):
    """
    Use this function as decorator to make a function accessible via http

    Example::

        class Main():
            @pypoly.http.expose()
            def index(**args, **kwargs):
                return "xml string"

    :since: 0.2
    """
    def func(f):
        if not hasattr(f, '_pypoly_config'):
            f._pypoly_config = dict()
        f._pypoly_config['exposed'] = True

        # kwargs belongs to the expose() function
        if 'routes' in kwargs:
            f._pypoly_config['routes'] = kwargs['routes']

        if "auth" in kwargs:
            if "auth.require" not in f._pypoly_config:
                f._pypoly_config['auth.require'] = []
            auth = kwargs["auth"]
            if type(auth) != list:
                auth = [auth]
            f._pypoly_config['auth.require'].extend(auth)

        if "session_mode" in kwargs:
            if "session.mode" not in f._pypoly_config:
                f._pypoly_config["session.mode"] = kwargs["session_mode"]

        return f

    if(len(args) == 1 and callable(args[0])):
        return func(args[0])
    else:
        return func


def requesthandler(environment, start_response):
    """
    Handle an incoming http request.

    :since: 0.2
    """

    # TODO: clean this up in PyPoly V0.3
    headers = {}
    headers['Content-Type'] = 'text/html; charset=utf-8'
    # default encoding
    headers['Content-Encoding'] = 'utf-8'

    ret = []
    # remove: old routes
    #from routes import URLGenerator
    #url = URLGenerator(pypoly._dispatcher.mapper, environment)
    #environment['routes.url'] = url

    #print url(controller="module.pp_example.default",  action="index")
    # the session handler isn't set
    if pypoly.http.SessionHandler == None:
        # check if a session handler is defined and we can load it
        session_plugin_name = pypoly.config.get('system.session')
        if session_plugin_name != '':
            session_plugin_pkg = pypoly.plugin.get_package_name(
                session_plugin_name
            )
            if session_plugin_pkg:
                pypoly.log.debug(
                    "Using session plugin: %s" % session_plugin_name
                )
                pypoly.http.SessionHandler = pypoly.plugin.get_plugin(
                    'session',
                    session_plugin_pkg
                )

        # load the default/fallback session handler
        if pypoly.http.SessionHandler == None:
            from pypoly.component.plugin.session_mem import MemSessionHandler
            pypoly.http.SessionHandler = MemSessionHandler

    try:
        # use the dispatcher to get the required handler to handle our request
        path_info = environment.get("PATH_INFO", "/")
        (func, request_object, response_object, result) = pypoly._dispatcher(path_info)

        if func == None:
            raise HTTPError(404, 'Not found')

        # raise HTTP404 Error if function is not exposed
        if not hasattr(func, '_pypoly_config') \
           or not 'exposed' in func._pypoly_config \
           or not func._pypoly_config['exposed'] == True:
            raise HTTPError(404, 'Not found')

        pypoly.http.serving.request = request_object(environment=environment)

        # add url params to the params list
        pypoly.http.request.url_params = result
        for key in result.keys():
            pypoly.http.request.params[key] = result[key]

        # create the response object
        pypoly.http.serving.response = response_object()

        # manage the session
        session_id = None
        if 'session_id' in pypoly.http.serving.request.cookies:
            session_id = pypoly.http.serving.request.cookies['session_id'].value

        pypoly.http.serving.session = pypoly.http.SessionHandler(session_id)

        for hook in pypoly.hook.get_list("http.request.serve.pre"):
            hook()

        pypoly.http.request.config = {}

        if hasattr(func.im_class, "_pypoly_config"):
            # get config from class
            pypoly.http.request.config.update(func.im_class._pypoly_config)

        if hasattr(func, "_pypoly_config"):
            pypoly.http.request.config.update(func._pypoly_config)

        pypoly.http.auth.check_auth()

        # check if the function wants to change the session mode
        session_mode = pypoly.http.request.config.get("session.mode", None)
        if session_mode != None:
            pypoly.http.serving.session.set_mode(session_mode)

        #TODO: raise error if not found or not exposed
        args = []
        kwargs = copy.copy(pypoly.http.request.params)
        content = func(*args, **kwargs)

    except StaticFile, content:
        pypoly.log.debug('static file')
    except HTTPRedirect, content:
        pypoly.log.info('page redirect', traceback=True)
    except HTTPError, content:
        pypoly.log.warning('page error', traceback=True)
    except Exception, inst:
        pypoly.log.warning('page error', traceback=True)
        content = HTTPError(500, 'Error')

    # create request, response and session object if the don't exist
    if pypoly.http.serving.request == None:
        pypoly.http.serving.request = DefaultRequest(environment=environment)
    if pypoly.http.serving.response == None:
        pypoly.http.serving.response = DefaultResponse()

    # don't load session data if we server static files or got an error
    if pypoly.http.serving.session == None and \
       not isinstance(content, StaticFile) and \
       not isinstance(content, HTTPError) and \
       not isinstance(content, HTTPRedirect):
        # manage the session
        session_id = None
        if 'session_id' in pypoly.http.serving.request.cookies:
            session_id = pypoly.http.serving.request.cookies['session_id'].value

        pypoly.http.serving.session = pypoly.http.SessionHandler(session_id)

    try:
        ret = content()
    except HTTPRedirect, content:
        pypoly.log.info('page redirect', traceback=True)
        ret = content()
    except HTTPError, content:
        pypoly.log.warning('page error', traceback=True)
        ret = content()
    except Exception, inst:
        pypoly.log.warning('page error', traceback=True)
        content = HTTPError(500, 'Error')
        ret = content()

    if content._mime_type != None:
        headers['Content-Type'] = content._mime_type

    if content._size != None:
        headers['Content-Length'] = str(content._size)

    headers.update(pypoly.http.response.headers)
    headers = headers.items()

    cookies = str(pypoly.http.response.cookies.output(header=""))
    for item in cookies.split("\r\n"):
        headers.append(('Set-Cookie', item))

    try:
        headers.append(('Server', pypoly.config.get('server.ident')))
    except:
        pass

    try:
        response_code = "%d %s" % content._status
    except:
        pass

    import pprint
    pypoly.log.debug(pprint.pformat(headers))

    start_response(response_code, headers)

    pypoly.http.serving.clear()
    return ret


class Dispatcher(object):
    """
    This is the request dispatcher. It decides witch function to call.

    :since: 0.1
    """

    def __init__(self):
        """
        :since: 0.1
        """
        #import routes
        #self.controllers = {}
        #self.mapper = routes.Mapper()
        #self.mapper.controller_scan = self.controllers.keys
        self._routes = []
        self.regex_static = re.compile("^/_static/(?P<filename>.*)$")
        self.regex_type = re.compile(
            "^(?P<type>(plugin|module|tool))/(?P<name>[^/]+)/(?P<filename>.*)$"
        )

    def connect(self, name, route, controller, **kwargs):
        """
        Connect new controller to the given path.

        :since: 0.1

        :param name: the name of the route
        :type name: String
        :param route: the route
        :type route: String
        :param controller: the controller
        :type controller: Instance
        """
        self._routes.append(
            pypoly.routes.Route(
                name=name,
                route=route,
                controller=controller,
                **kwargs
            )
        )

    def __call__(self, path_info):
        """
        Find the dispatcher and return it.

        :since: 0.1

        :param path_info: the path of the url
        :type path_info: String
        """
        m = self.regex_static.match(path_info)
        if m:
            # looks like a static file
            pypoly.log.info('Static file')
            filename = m.group('filename')

            # check if the file exists in the static path
            filename_static = pypoly.get_path(
                pypoly.config.get('static.path'),
                filename
            )
            if os.path.exists(filename_static):
                raise StaticFile(filename_static)

            # check if the file belongs to a plugin or module
            m = self.regex_type.match(filename)
            filename_egg = None
            if m == None:
                raise HTTPError(404, "Not found")

            pkg_name = None
            if m.group("type") == "module":
                pkg_name = pypoly.module.get_package_name(m.group("name"))
            elif m.group("type") == "plugin":
                pkg_name = pypoly.plugin.get_package_name(m.group("name"))
            elif m.group("type") == "tool":
                pkg_name = pypoly.tool.get_package_name(m.group("name"))

            # no package found
            if pkg_name == None:
                raise HTTPError(404, "Not found")

            # get egg filename
            path = pkg_resources.resource_filename(
                pkg_name,
                "htdocs"
            )
            filename_egg = pypoly.get_path(
                path,
                m.group("filename")
            )
            pypoly.log.debug("Static file path: %s" % filename_egg)

            # check if it exists and deliver it
            if os.path.exists(filename_egg):
                raise StaticFile(filename_egg)

            raise HTTPError(404, "Not found")

        # find a handler
        a = self.find_handler(path_info)
        if a == None:
            pypoly.log.info("No handler found")
            raise HTTPError(404, "Not found")

        (controller, func, results) = a
        if hasattr(controller, "_dispatch"):
            dispatcher = getattr(controller, "_dispatch")
            (request, response) = dispatcher()
        else:
            request = DefaultRequest
            response = DefaultResponse
        return (func, request, response, results)

    def extend(self, name,  controller, routes, path_prefix):
        """
        Connect new controller to the given path.

        :since: 0.1

        :param name: the name of the route
        :type name: String
        :param routes: a list of routes
        :type routes: List
        :param controller: the controller
        :type controller: Instance
        :param path_prefix: the prefix for the path
        :type path_prefix: String
        """
        #self.controllers[name] = controller
        r = []
        #from routes.route import Route
        for route in routes:
            pypoly.log.debug("  extending  route:")
            path = path_prefix + route['path']
            del route['path']
            #route['controller'] = 
            pypoly.log.debug("    path:" + str(path))
            pypoly.log.debug("    kwargs:" + str(route))
            pypoly.log.debug("    name :" + str(name))
            tmp = pypoly.routes.Route(
                name=name,
                route=path,
                controller=controller,
                **route
            )
            self._routes.append(tmp)

        #self.mapper.extend(r,  path_prefix=path_prefix)

    def find_handler(self, path_info):
        #import routes

        #config = routes.request_config()
        #config.mapper = self.mapper
        ##config.host = pypoly.http.request.headers.get('Host', None)
        #config.protocol = 'HTTP/1.1'
        if path_info == '/':
            module_name = pypoly.config.get('start.module')
            package_name = pypoly.module.get_package_name(module_name)
            action = pypoly.config.get('start.action')
            raise HTTPRedirect(
                url=pypoly.url.get_module(
                    package_name,
                    action=action
                )
            )
        else:
            res = None
            for route in self._routes:
                res = route.match(path_info)
                if res != None:
                    break

            # nothing found
            if res == None:
                return None
#            controller_name = result.pop('controller', None)
#           action_name = result.pop('action', None)

            #pypoly.http.request.url_params = result

            # ToDo: add more error checks
            #            controller = self.controllers[controller_name]
            func = getattr(res["controller"], res["action"])

            if callable(func):
                return (res["controller"], func, res["params"])
            else:
                return None

    def get_handler(self, name, action, scheme="default", _scheme=None):
        """
        :param name: the name of the controller
        :type name: String
        :param action: the action
        :type action: String
        :return: a function | None
        """
        if _scheme != None:
            pypoly.log.deprecated("Don't use _scheme!!! Use scheme instead")
            scheme = _scheme
        name = '.'.join([name, scheme])
        for route in self._routes:
            if route.name != name:
                continue

            try:
                func = getattr(route.controller, action)
                return func
            except:
                pypoly.log.warning("Couldn't find handler %s" % name)
                return None

        return None


class HTTPRedirect(BasicContent, BaseException):
    """
    Make a http redirect.

    :since: 0.2
    """
    def __init__(self, url=''):
        """
        :since: 0.2

        :param url: redirect to this url
        """
        self.url = url
        BasicContent.__init__(self, status=(302, 'Found'))

    def __call__(self):
        pypoly.http.response.headers['Location'] = str(self.url)
        return ["error 302"]


class HTTPError(BasicContent, BaseException):
    """
    HTTP-Error exception
    """
    def __init__(self, code, message=''):
        """
        :param code: http error code
        :type code: Integer
        :param message: the error message
        :type message: String
        """
        BasicContent.__init__(self, status=(code, message))

    def __call__(self):
        return ["Error Code: ToDo"]


class StaticFile(BasicContent, BaseException):
    """
    Use this to return a static file.

    :since: 0.2
    """
    #: name of the file
    filename = None

    def __init__(self, filename):
        BasicContent.__init__(self)

        self.filename = filename

    def __call__(self):
        try:
            fp = open(self.filename)

            self._size = os.path.getsize(self.filename)
            #ToDo: do this global, not for every request
            mimetypes.init()
            mime_type = mimetypes.guess_type(self.filename)
            if len(mime_type) == 2:
                self._mime_type = mime_type[0]

            return FileWrapper(fp)
        except BaseException, msg:
            pypoly.log.info("File not found %s" % str(msg))
            raise HTTPError(404, 'Not Found')
