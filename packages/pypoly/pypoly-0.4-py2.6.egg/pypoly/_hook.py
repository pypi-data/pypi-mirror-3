import pypoly

class HookHandler(dict):
    """
    This is the hook handler.

    There are different hooks in the system.
    Hooks:
        - content.web.webpage.head

    :todo: more description
    """
    _hooks = {}
    def __init__(self):
        """
        Init the Hooksystem
        """
        self._hooks = {
            "content.web.webpage.head" : {},
            "http.request.serve.pre": {}
        }

    def get(self, namespace):
        """
        Return all hooks for the given namespace

        :param namespace: the hook name
        :type namespace: String
        :return: (name, value)
        """
        if namespace in self._hooks:
            return self._hooks[namespace]
        return {}

    def get_hooks(self, namespace):
        """
        Return all hooks for the given namespace

        :param namespace: the hook name
        :type namespace: String
        """
        if namespace in self._hooks:
            return self._hooks[namespace].values()
        return []

    def get_list(self, namespace):
        """
        Return all hooks for the given namespace

        :param namespace: the hook name
        :type namespace: String
        """
        if namespace in self._hooks:
            return self._hooks[namespace].values()
        return []

    def get_wrapped(self, *hooks):
        wrapper = HookWrapper()
        for hook in hooks:
            if hook[0] in self._hooks:
                wrapper.register(
                    hook[0],
                    self.get_list(hook[0]),
                    *hook[1],
                    **hook[2]
                )
        return wrapper

    def register(self, namespace, name, function):
        """
        Append a new hook

        :since: 0.4
        """
        if namespace in self._hooks:
            self._hooks[namespace][name] = function
        else:
            pypoly.log.warning(
                "Unknown namespace: %(namesapce)s" % dict(
                    namesapce = namespace
                )
            )

class HookWrapper(object):
    """
    This is a hook wrapper.

    :since: 0.4
    """
    def __init__(self):
        self._hooks = {}

    def get(self, namespace):
        if not namespace in self._hooks:
            pypoly.log.warning(
                "Unknown namespace: %(namesapce)s" % dict(
                    namesapce = namespace
                )
            )
            return []

        results = []
        for hook in self._hooks[namespace][0]:
            hook_res = hook(
                *self._hooks[namespace][1],
                **self._hooks[namespace][2]
            )

            if type(hook_res) != list:
                hook_res = [hook_res]
            for hook in hook_res:
                results.append(hook)

        return results

    def register(self, namespace, hooks, *args, **kwargs):
        self._hooks[namespace] = (hooks, args, kwargs)
