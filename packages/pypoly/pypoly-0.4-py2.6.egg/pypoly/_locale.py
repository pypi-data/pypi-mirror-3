import gettext
import os

import pkg_resources

import pypoly

class Locale(object):
    """
    This class handles all our locale support.
    """
    #: use this to cache loaded locales
    _cache = {}

    def __init__(self):
        self._cache = {}


    def get_lang(self, path, language = None, domain = 'main', codeset = 'utf-8'):
        """
        This is the main function to load a language
        :param path: the path to the locale file
        :param domain: the domain
        :param language: the language e.g. de_DE
        :param codeset: the codeset
        :return:
        """
        if language == None:
            language = pypoly.user.get_languages()
            if len(language) == 0:
                language = ['en_US']

        pypoly.log.debug('Languages: %s' % str(language))
        key = str([domain, path, language, codeset])
        pypoly.log.debug('Key: %s' % key)
        if not key in self._cache:
            pypoly.log.debug('Locale not in cache, loading...')
            gettext.bindtextdomain(domain, path)
            gettext.textdomain(domain)
            translator = gettext.translation(domain,
                                             path,
                                             languages=language,
                                             codeset=codeset,
                                             fallback = True
                                            )
            self._cache[key] = translator.ugettext
        else:
            pypoly.log.debug('Locale in cache')

        return self._cache[key]

    def get_template_lang(self, path, language = None, domain = 'main', codeset = 'utf-8'):
        """
        The pypoly uses this function to load the language for the template translation filter

        :todo: check this function
        """
        #os.path.join(pypoly.template.path, path, 'locale')
        tmp_path = pypoly.get_path(pypoly.config.get('template.path'), path, 'locale')
        pypoly.log.debug('Locale Path: %s' % tmp_path)

        return self.get_lang(tmp_path , language, domain, codeset)

    def __call__(self, string):
        """
        Detect who is calling, get the locale path and load the locale.

        :param string: Translate this string
        :type string: String
        :return: translated string
        :rtype: String
        """
        caller = pypoly.get_caller()
        if caller.type == 'pypoly':
            path = pkg_resources.resource_filename(
                "pypoly",
                "locale"
            )
        else:
            path = pkg_resources.resource_filename(
                caller.pkg_root,
                "locale"
            )

        lang = self.get_lang(path)
        return lang(string)

