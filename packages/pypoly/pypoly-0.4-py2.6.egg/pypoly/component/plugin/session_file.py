"""
Store session data in files.
"""
import os
import time
import pickle
import types

import pypoly
from pypoly.component import Component
from pypoly.component.plugin import SessionPlugin

class Main(Component):
    def init(self):
        pypoly.config.add("session.path", "./session")
        pypoly.config.add("session.ext", ".session")
        pypoly.config.add("lock.path", "./session")
        pypoly.config.add("lock.ext", ".lock")

    def start(self):
        pypoly.plugin.register(FileSessionHandler)

class FileSessionHandler(SessionPlugin):
    """
    Handle the sessions and save the data to a file.
    """

    def __init__(self, session_id):
        SessionPlugin.__init__(self, session_id)
        self.__data = {}
        if self.session_id == None:
            self.create_session()
        else:
            filename = self._get_session_filename()
            if filename == None or \
               not os.path.exists(filename) or \
               not os.path.isfile(filename):
                self.create_session()
        self._lock()
        self._load()

    def __del__(self):
        if self.mode == pypoly.session.MODE_READONLY:
            return

        if self.mode == pypoly.session.MODE_LOADWRITE:
            self._lock()

        self._save()
        self._unlock()

    def _load(self):
        """
        Load the session data.
        """
        filename = self._get_session_filename()

        data = None

        if os.path.exists(filename) and \
           os.path.isfile(filename):
            try:
                fp = open(filename, 'rb')
                data = pickle.load(fp)
                fp.close()
            except:
                pypoly.log.warning("Wrong session data")


        if type(data) == dict:
            self.__data = data
        else:
            self.__data = {}
            pypoly.log.info("No session data")

    def _save(self):
        """
        Save the session data.
        """
        filename = self._get_session_filename()
        try:
            d = pickle.dumps(self.__data)
            fp = open(filename, "wb")
            try:
                # if something went wrong while writing
                fp.write(d)
            except:
                pass
            fp.close()
        except Exception, msg:
            pypoly.log.warning(str(msg))

    def _get_session_filename(self):
        """
        Create filename

        :return: Filename
        :rtype: String
        """
        # we need the / at the end, for security
        session_path = os.path.abspath(pypoly.config.get("session.path")) + "/"

        filename = os.path.abspath(
            os.path.join(
                session_path,
                self.session_id
            )
        )

        if session_path == filename[:len(session_path)]:
            filename = filename + pypoly.config.get("session.ext")
            return filename

        return None

    def _get_lock_filename(self):
        session_path = os.path.abspath(pypoly.config.get("session.path")) + "/"

        filename = os.path.abspath(
            os.path.join(
                session_path,
                self.session_id
            )
        )

        if session_path == filename[:len(session_path)]:
            filename = filename + pypoly.config.get("lock.ext")
            return filename

        return None

    def _lock(self):
        start = time.time()
        while True:
            try:
                fp_lock = os.open(
                    self._get_lock_filename(),
                    os.O_CREAT|os.O_WRONLY|os.O_EXCL
                )
                os.close(fp_lock)
                pypoly.log.debug(
                    "Waited %f seconds to lock session" % (time.time() - start)
                )
                break
            except OSError, msg:
                time.sleep(0.1)
                if time.time() - start > 20:
                    pypoly.log.warning(
                        "Waited over %f seconds to lock session. Stopping!" % \
                        (time.time() - start)
                    )
                    raise HTTP(500, "Timeout")

    def _unlock(self):
        os.unlink(self._get_lock_filename())

    def get(self, name, default = None):
        if name in self.__data:
            return self.__data[name]
        else:
            return default

    def pop(self, name, default = None):
        if name in self.__data:
            value = self.__data[name]
            del self.__data[name]
            return value
        else:
            return default

    def set(self, name, value):
        if self.mode == pypoly.session.MODE_READONLY:
            pypoly.log.warning(
                "Can't set session value. In read only mode."
            )
            return False

        self.__data[name] = value
        return True

    def set_mode(self, mode):
        ret = SessionPlugin.set_mode(self, mode)
        if ret == False:
            # something went wrong
            return ret

        if mode == pypoly.session.MODE_LOADWRITE:
            self._unlock()
            return True

        if mode == pypoly.session.MODE_READONLY:
            self._save()
            self._unlock()
            return True

        return False
