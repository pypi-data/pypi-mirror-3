"""
Store session data in memory.
"""
import threading

from pypoly.component import Component
from pypoly.component.plugin import SessionPlugin

class MemSession(Component):
    def init(self):
        pass

    def start(self):
        pypoly.plugin.register(MemSessionHandler)

class MemSessionHandler(SessionPlugin):
    """
    """
    __sessions = {}
    __lock = threading.Lock()

    def __init__(self, session_id):
        SessionPlugin.__init__(self, session_id)

        self.__lock.acquire()
        if not self.session_id in MemSessionHandler.__sessions:
            MemSessionHandler.__sessions[self.session_id] = {}
        self.__lock.release()

    def get(self, name, default=None):
        if name in MemSessionHandler.__sessions[self.session_id]:
            return MemSessionHandler.__sessions[self.session_id][name]
        else:
            return default

    def pop(self, name, default=None):
        if not name in MemSessionHandler.__sessions[self.session_id]:
            return default

        self.__lock.acquire()
        value = MemSessionHandler.__sessions[self.session_id][name]
        del MemSessionHandler.__sessions[self.session_id][name]
        self.__lock.release()
        return value

    def set(self, name, value):
        self.__lock.acquire()
        MemSessionHandler.__sessions[self.session_id][name] = value
        self.__lock.release()
