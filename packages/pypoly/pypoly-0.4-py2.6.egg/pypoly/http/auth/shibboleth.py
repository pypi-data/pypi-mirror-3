"""
"""
import re

import pypoly
import pypoly.session
from pypoly.component import Component
from pypoly.component.plugin import AuthPlugin

class Main(Component):
    def init(self):
        pypoly.config.add("username", "REMOTE_USER")
        pypoly.config.add("groups", [])
        pypoly.config.add("login.auto", False)

        #
        pypoly.config.add("group.parse", False)
        pypoly.config.add("group.header", "")
        pypoly.config.add("group.mapping.file", "")
        pypoly.config.add("group.separator", ";")
        pypoly.config.add("group.regex", "")

    def start(self):
        if pypoly.config.get("login.auto", False):
            pypoly.hook.register(
                "http.request.serve.pre",
                "plugin.auth.shib.autologin",
                autologin
            )
        pypoly.plugin.register(ShibAuth)

class ShibAuth(AuthPlugin):
    """
    :since: 0.4
    """
    def __init__(self):
        pypoly.log.debug("init shib")
        AuthPlugin.__init__(self)
        self._mapping = None
        mapping_file = pypoly.config.get("group.mapping.file", "")
        if mapping_file != None and len(mapping_file) > 0:
            try:
                fp = open(mapping_file)
                self._mapping = []
                while True:
                    line = fp.readline()
                    if line == "":
                        break

                    group, sep, match = line.strip().partition(":")
                    if not sep == ":":
                        continue
                    pypoly.log.debug(
                        "Group mapping: %s to %s" % (
                            match,
                            group
                        )
                    )
                    self._mapping.append(
                        (
                            re.compile("^" + match + "$"),
                            [g.strip() for g in group.split(",")]
                        )
                    )
            except Exception, inst:
                pypoly.log.debug(str(inst))

    def _map_groups(self, groups):
        if self._mapping == None:
            return groups

        res = []
        for group in groups:
            for mapping in self._mapping:
                if mapping[0].match(group):
                    res = res + mapping[1]

        # remove duplicates, this seams to be faster than a loop
        res = dict.fromkeys(res).keys()

        pypoly.log.debug(
            "Mapping groups from %s to %s" % (
                str(groups),
                str(res)
            )
        )
        return res

    def login(self, username, password):
        name = pypoly.http.request.headers.get(
            pypoly.config.get("username"),
            None
        )
        if name == None or name != username:
            return False

        pypoly.log.debug(str(pypoly.config.get("group.parse")))
        if pypoly.config.get("group.parse") == True:
            pypoly.log.info("Parsing groups ...")

            groups = pypoly.http.request.headers.get(
                pypoly.config.get("group.header"),
                None
            )

            pypoly.log.debug(
                "Get from header '%s': %s" % (
                    pypoly.config.get("group.header"),
                    groups
                )
            )
            if groups != None:
                groups = groups.split(
                    pypoly.config.get("group.separator").strip()
                )
                regex = pypoly.config.get("group.regex").strip()
                if len(regex) == 0:
                    pypoly.log.debug(
                        "No RegEx given. Setting groups: %s" % str(tmp_groups)
                    )
                    pypoly.session.set("groups", self._map_groups(groups))
                    return True

                regex = re.compile(regex)
                tmp_groups = []
                for group in groups:
                    m = regex.match(group)
                    if m:
                        tmp_groups.append(m.group("groupname"))

                pypoly.log.debug("Setting groups: %s" % str(tmp_groups))
                pypoly.session.set("groups", self._map_groups(tmp_groups))
                return True


        pypoly.session.set(
            "groups",
            pypoly.config.get("groups")
        )

        return True

    def get_groups(self, username):
         return pypoly.session.get("groups", [])

def autologin(**kwargs):
        name = pypoly.http.request.headers.get(
            pypoly.config.get("username"),
            None
        )
        if name == None or len(name) == 0:
            return

        pypoly.http.auth.login(
            name,
            ""
        )
