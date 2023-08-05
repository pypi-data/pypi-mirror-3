
__all__ = ['webpage', 'newsfeed', 'json']

class BasicContent(object):
    """
    Use this if you want to return something to the user.

    :since: 0.3
    """

    #: the mime type
    _mime_type = None

    #: the size, if this is None PyPoly will detect the size
    _size = None

    #: a tuple (Format: (<Integer>, <String>), Example: (200, 'OK')
    _status = None

    def __init__(self,
                 status = (200, 'OK'),
                 mime_type = None,
                 size = None,
                 *kargs,
                 **kwargs
                ):
        """
        :since: 0.3
        """
        self._mime_type = mime_type
        self._size = size
        self._status = status

    def __call__(self, *kargs, **kwargs):
        """

        :return: Always return a iterable object.
        :rtype: iterable object
        """
        pass

from pypoly.content.webpage import Webpage

