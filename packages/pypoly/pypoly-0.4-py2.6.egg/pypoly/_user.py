import pypoly
import pypoly.session

class User(object):
    """
    This class provides some functions to get informations on the current user.

    :since: 0.1
    """
    def get_username(self):
        """
        Get the username for the current user.

        :return: Username as String | None = not logged in
        :since: 0.1
        """
        return pypoly.session.get_pypoly('user.username', None)

    def get_groups(self):
        """
        Get all groups the user belongs to

        :return: List with all groupnames
        :since: 0.1
        """
        return pypoly.auth.get_groups(self.get_username())

    def get_languages(self):
        """
        Get the user languages

        :return: list with all languages the user can read and understand
        """
        lang = pypoly.session.get_pypoly('user.lang', '')
        lang = lang.split(',')
        langs = []
        for temp in lang:
            langs.append(temp.strip())
        return langs


