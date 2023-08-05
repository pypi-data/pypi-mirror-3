import mimetypes
import threading
import Queue
import copy
from Cookie import SimpleCookie

from cgi import parse_qs, escape

import pypoly
import pypoly.session

request = None
response = None
session = None


def pypolyauth():
    action = pypoly.http.request.params.get("_pypoly_action", None)

    if action == None:
        return

    action = action.lower()
    pypoly.log.debug('PyPoly-Action: %s' % action)
    if action == 'login':
        username = pypoly.http.request.params.get("username", None)
        password = pypoly.http.request.params.get("password", None)
        if username == None or password == None:
            return

        pypoly.http.auth.login(
            username,
            password
        )
        del pypoly.http.request.params['username']
        del pypoly.http.request.params['password']

    elif action == 'logout':
        pypoly.http.auth.logout()

    del pypoly.http.request.params['_pypoly_action']


def set_lang():
    """
    Set the language for the system

    :ToDo: check if the language exists
    """
    lang = pypoly.http.request.params.get("_pypoly_lang", None)

    if lang == None:
        return

    pypoly.session.set_pypoly(
        'user.lang',
        lang
    )


def set_template():
    """
    Set the Webpage Template
    """
    tpl = pypoly.http.request.params.get("_pypoly_template", None)

    if tpl == None or not tpl in pypoly.template.templates:
        return

    pypoly.session.set_pypoly(
        'template.name',
        pypoly.http.request.params['_pypoly_template']
    )
    del pypoly.http.request.params['_pypoly_template']
