"""
Handle HTTP-Auth
"""

import pypoly
import pypoly.http
import pypoly.session


def login(username, password):
    """
    Login function for the web auth.

    :param username: the username
    :type username: String
    :param password: the password
    :type password: String
    :return: True = Success | False = Failed
    :rtype: Boolean
    """
    if pypoly.auth.login(username, password) == True:
        pypoly.session.set('user.username', username)
        pypoly.log.info('succesfull login "%s"' % username)
        return True
    else:
        return False


def logout():
    """
    Logout.
    """
    username = pypoly.session.pop('user.username', None)
    if username:
        pypoly.log.info('succesfull logout "%s"' % username)
    else:
        pypoly.log.info('logout called without being logged in')


def check_auth(*args, **kwargs):
    conditions = pypoly.http.request.config.get('auth.require', None)
    if conditions is not None:
        if pypoly.session.get('user.username', None):
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    return False
        else:
            return False
    else:
        return True


def check_auth(*args, **kwargs):
    """
    A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill

    :todo: change this function to use a hook
    """

    conditions = pypoly.http.request.config.get('auth.require', None)
    if conditions is not None:
        if pypoly.session.get('user.username', None):
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise pypoly.http.HTTPRedirect('/auth/login')
        else:
            # set referer (no further checking needed, because this function
            # is always called with an referer through the redirect function)
            ref = pypoly.http.request.headers['PATH_INFO']
            pypoly.session.set('auth.href', ref)
            pypoly.log.info('referer set to: ' + ref)

            raise pypoly.http.HTTPRedirect('/auth/login')


def all(*conditions):
    """
    Returns True if all of the conditions match

    """
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


def any(*conditions):
    """
    Returns True if any of the conditions match
    """
    def check():
        for c in conditions:
            if c():
                return True
        return False

    return check


def group(groupname):
    """
    Returns True if the user is a member of 'groupname'
    """
    def check():
        groups = pypoly.user.get_groups()
        pypoly.log.info("Requiring member of: " + groupname)
        pypoly.log.debug(groups)
        if groupname in groups:
            return True
        else:
            return False
    return check


def require(*conditions):
    """
    A decorator that appends conditions to the auth.require config
    variable.
    """
    def decorate(f):
        if not hasattr(f, '_pypoly_config'):
            f._pypoly_config = dict()
        if 'auth.require' not in f._pypoly_config:
            f._pypoly_config['auth.require'] = []
        f._pypoly_config['auth.require'].extend(conditions)
        return f
    return decorate


def username(reqd_username):
    return lambda: reqd_username == pypoly.session.get_user('username', None)
