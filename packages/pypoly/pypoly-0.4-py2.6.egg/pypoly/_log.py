import os
import sys
import types
import traceback
import datetime
import time
import logging
import logging.handlers

import pypoly

# don't display the no handler warning
logging.Logger.manager.emittedNoHandlerWarning = 1

class Log(object):
    """
    This class uses python logging and sets some default values.
    """

    # FIXME: search some way to get pypoly.system.root_path and LOGTYPE
    #        from config space (which seems to be not initialized
    #        before the first event is logged)

    # define look of logentry
    #  0 - standard
    #  1 - minimalized
    format = 0

    # abort level
    # set the severity at which you want the program to instantly stop
    # Example: ABORT = ERROR (halts on error)
    #          ABORT = None  (halts never)
    abort = None

    traceback = None

    #: export log messages to firephp
    firephp = 0

    #: this are the log levels
    _log_levels = {'CRITICAL' : 50,
                   'ERROR' : 40,
                   'DEPRECATED' : 35,
                   'TODO' : 34,
                   'WARNING' : 30,
                   'INFO' : 20,
                   'DEBUG' : 10,
                   'NOTSET' : 0
                  }
    #: this are the log formats
    _log_formats = {'FORMAT_SIMPLE' : 0,
                    'FORMAT_NORMAL' : 1,
                    'FORMAT_EXTENDED' : 2
                   }

    def __init__(self, screen = False, traceback = None, level = 50):
        # set levels and formats as class vars
        for (key, value) in self._log_levels.iteritems():
            setattr(self, key, value)

        for (key, value) in self._log_formats.iteritems():
            setattr(self, key, value)

        #: currently not used
        self.format = self.FORMAT_NORMAL

        if traceback:
            self.traceback = traceback

        #self.abort = self.CRITICAL
        #TODO: change this
        self.abort = None

        logger = logging.getLogger('pypoly')
        logger.setLevel(logging.DEBUG)

        # set the screen logger
        if screen == True:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            handler.setLevel(level)
            logger.addHandler(handler)

        logger = logging.getLogger('access')
        logger = logging.getLogger('error')

    def _log(self, level, msg, msg_list = [], traceback = False, caller = None):
        """
        This is the "real" logging function. Never call this function
        directly!!! Use functions like error, info, ... insted.

        :param level: the log level
        :param msg: the msg
        :type msg: str or list
        :param msg_list: a list of messages
        :type msg_list: list
        :param traceback: display traceback
        :type traceback: Boolean
        :param caller: the caller object
        :type caller: Caller object
        """
        if caller == None:
            caller = pypoly.get_caller()

        if traceback == True or self.traceback == 'all':
            import traceback
            tmp_list = traceback.format_exc().split('\n')
            if tmp_list[0] != 'None':
                # add traceback messages to msg_list and remove emtpy line
                msg_list = msg_list + tmp_list[:-1]

        level_name = self.get_level_name(level)
        context = ''
        # get context from frame

        logstr = '[%(filename)s:%(line)s:%(function)s] %(message)s'

        info = {'filename' : caller.filename,
                'line' : caller.linenumber,
                'function' : caller.function,
                'message' : ''
        }

        logger = logging.getLogger('pypoly')
        info['message'] = msg
        logger.log(level,
                   logstr % info
                   )
        for m in msg_list:
            logstr = "%s" % (str(m))

            self._log_fire_php(level, logstr)

            logger.log(level,
                       logstr
                       )

        # check abort severity
        if self.abort != None and self.abort <= level:
            logger.log(level,
                       ">>> Severity of logmessage forced program halt. <<<"
                      )
            sys.exit(0)

    def _log_fire_php(self, level, msg):
        if self.firephp != 1:
            return False

        firephp_levelname = "LOG"
        if level >= 40:
            firephp_levelname = 'ERROR'
        elif level >= 30:
            firephp_levelname = 'WARN'
        elif level >= 20:
            firephp_levelname = 'INFO'
        else:
            # don't log messages with level lower then 20
            return False

        if not 'X-FirePHP-Data-100000000001' in pypoly.http.response.headers:
            # add FirePHP headers
            pypoly.http.response.headers['X-FirePHP-Data-100000000001'] = '{'
            pypoly.http.response.headers['X-FirePHP-Data-200000000001'] = \
                    '"FirePHP.Dump":{'
            pypoly.http.response.headers['X-FirePHP-Data-299999999999'] = \
                    '"__SKIP__":"__SKIP__"},'
            pypoly.http.response.headers['X-FirePHP-Data-300000000001'] = \
                    '"FirePHP.Firebug.Console":['
            pypoly.http.response.headers['X-FirePHP-Data-399999999999'] = \
                    '["__SKIP__"]],'
            pypoly.http.response.headers['X-FirePHP-Data-999999999999'] = \
                    '"__SKIP__":"__SKIP__"}'


        current_time = datetime.datetime.today()
        microseconds = '%06d' % current_time.microsecond
        while(len(microseconds) < 8):
            microseconds = microseconds + '0'
        # X  YYY ZZZZZZZZ
        # |   |    |
        # |   |    - Microseconds
        # |   - Seconds based on last 3 digits of a unix timestamp
        # - Section prefix
        msgid = '3%s%s' % (str(int(time.time()))[-3:],
                             microseconds
                            )
        msg = msg.replace('"', '\\"')
        msg = msg.replace("\n", '')
        pypoly.http.response.headers['X-FirePHP-Data-%s' % msgid] = \
                '["%s", "%s"],' % (firephp_levelname,
                                   msg
                                  )

    def __call__(self, level, msg, traceback = False):
        self._log(level, msg, traceback = traceback)

    def get_level_name(self, level):
        for (key, value) in self._log_levels.iteritems():
            if value == level:
                return str(key)

        return ''

    def critical(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = CRITICAL
        """
        self._log(self.CRITICAL,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                  )

    def debug(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = DEBUG
        """
        self._log(self.DEBUG,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                  )

    def deprecated(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = DEBRECATED
        """
        try:
            frame = sys._getframe(2)
        except ValueError:
            #-print('No callstack available. This should never happen.');
            #-print('Last log message: "%s"' % str(msg))
            sys.exit(1)
        tmp_msg_list = []
        tmp_msg_list.append('  Function called from:')
        tmp_msg_list.append('    Filename: %s' % (frame.f_code.co_filename))
        tmp_msg_list.append('    Line:     %s' % (frame.f_lineno))
        if 'self' in frame.f_locals:
            module_name = frame.f_globals['__name__']
            tmp_msg_list.append('    Module:   %s' % (module_name))
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
                tmp_msg_list.append('    Class:    %s' % (class_name))

        tmp_msg_list.append('    Function: %s' % (frame.f_code.co_name))
        msg_list = tmp_msg_list + msg_list
        self._log(self.DEPRECATED,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )

    def error(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = ERROR
        """
        self._log(self.ERROR,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )

    def info(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = INFO
        """
        self._log(self.INFO,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )

    def log(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = NOTSET
        """
        self._log(self.NOTSET,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )

    def start(self):
        """
        Setup the logging by using the values from the config file.
        """
        logger = logging.getLogger('pypoly')

        log_app_file = pypoly.config.get("log.application.file")
        log_app_lvl = pypoly.config.get("log.application.severity")
        if log_app_file != "":
            handler = logging.handlers.RotatingFileHandler(log_app_file)
            for lvl_name, lvl_value in self._log_levels.items():
                if lvl_name.lower() == log_app_lvl.lower():
                    handler.setLevel(lvl_value)
            handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            )
            logger.addHandler(handler)

    def todo(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = TODO
        """
        self._log(self.TODO,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )

    def warning(self, msg, msg_list = [], traceback = False):
        """
        Wrapper for the _log() function with loglevel = WARNING
        """
        self._log(self.WARNING,
                  msg,
                  msg_list = msg_list,
                  traceback = traceback,
                  caller = pypoly.get_caller()
                 )
