"""
Warning: Only use the dummy authentication for development purpose.
"""

import pypoly
import pypoly.session
from pypoly.component.plugin import AuthPlugin

class Main(object):
    def init(self):
        pass

    def start(self):
        pypoly.plugin.register(DummyAuth)

class DummyAuth(AuthPlugin):
    """
    This is a dummy authentication.

    :since: 0.4
    """
    def __init__(self):
        AuthPlugin.__init__(self)
        self._passwords = {}

    def login(self, username, password):
        """
        Verifies credentials for username and password.
        """
        tmp = [g.strip() for g in password.split(",")]
        if len(tmp) > 1:
            pypoly.session.set("groups", tmp)
            self._passwords[username] = password
            return True
        return False

    def get_groups(self, username):
        if pypoly.user.get_username() == None:
            return []

        return pypoly.session.get("groups", [])
