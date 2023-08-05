import re
import urllib

import pypoly

class Route(object):
    _regex_parse = re.compile("{([^}]+)}")
    """

    >>> r = Route(route="/{action}")
    >>> res = r.match("/foo")
    >>> res["action"] == "foo" and res["controller"] == None
    True
    >>> r.match("/foo/bar")
    None
    >>> r.generate(action="abc")
    '/abc'
    """
    def __init__(self,
                 name,
                 route,
                 defaults = {},
                 types = {},
                 requirements = {},
                 action = None,
                 controller = None
                ):
        self._action = action
        self.controller = controller
        self._defaults = defaults
        self._types = types
        self._param_names = []
        self._requirements = {}
        self.name = name

        reg = route
        tpl = route
        for a in self._regex_parse.findall(route):
            name, sep, param = a.partition(":")
            if param == "":
                param = "[^/]+"
            reg = reg.replace(
                "{" + a + "}",
                "(?P<%s>%s)" % (name, param)
            )
            tpl = tpl.replace(
                "{" + a + "}",
                "%("+name+")s"
            )
            self._param_names.append(name)

        for n, v in requirements.items():
            t = type(v)
            if t == str or t == unicode:
                self._requirements[n] = re.compile("^" + v + "$")
            else:
                self._requirements[n] = v

        pypoly.log.debug(
            "Creating Route with regex '%s' and template '%s'" % (
                reg,
                tpl
            )
        )
        self._regex_match = re.compile("^" + reg + "$")
        self._tpl = tpl

    def generate(self, action=None, values={}):
        if action != None and \
           self._action != None and \
           self._action != action:
            # we need an URL for a different action
            return None

        for name in self._param_names:
            # skip known values
            if name in ("action", ):
                continue
            if not name in values and not name in self._defaults:
                return None

        # try to set action
        if action == None:
            action = self._action

        values_url = {}
        params = {}
        for name, value in values.items():
            if not name in self._param_names:
                params[name] = value
            else:
                values_url[name] = value

        # if 'action' is in the param_name list, than add it
        if "action" in self._param_names:
            values_url["action"] = action

        ret = self._tpl % values_url

        baseurl = pypoly.config.get("server.baseurl")
        if baseurl[-1] == "/":
            baseurl = baseurl[:-1]
        if ret[0] == "/":
            ret = ret[1:]

        ret = "/".join([baseurl, ret])

        if len(params) == 0:
            return ret

        return ret + "?" + urllib.urlencode(params)

    def match(self, url):
        m = self._regex_match.match(url)
        if not m:
            return None

        res = m.groupdict()
        params = self._defaults.copy()
        for n, v in res.items():
            if n == "controller":
                continue

            if n in self._requirements:
                m = self._requirements[n].match(v)
                if not m:
                    return None

            if n in self._types:
                try:
                    params[n] = self._types[n](v)
                except Exception, inst:
                    pypoly.log.debug(str(inst))
                    return None
            else:
                params[n] = v

        action = params.pop("action", self._action)

        if action == None:
            return None

        return {
            "action": action,
            "controller": self.controller,
            "params": params
        }

if __name__ == "__main__":
    import doctest
    doctest.testmod()
