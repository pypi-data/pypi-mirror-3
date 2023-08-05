import os
import types

import pypoly

class FeedItem(object):
    title = ''
    link = ''
    description = ''

    author = ''
    uid = ''
    guid = ''
    date = ''
    # pubDate. Publishing date.
    # guid. A string of character that is unique to designate this item.
    # category. The category of the article.


class FeedChannel(list):
    title = ''
    link = ''
    description = ''
    category = ''
    copyright = ''
    image = ''
    language = ''
    docs = ''
    webmaster = ''
    pubdate = ''

    def __init__(self):
        self.title = ''
        self.link = ''
        self.description = ''
        self.image = None

class FeedImage(object):
    url = ''
    title = ''
    link = ''

class Feed(list):
    _template = ''
    _content_type = 'application/rss+xml'
    image = None
    def __init__(self):
        pass

    def render(self):
        pypoly.http.response.headers['Content-Type'] = 'application/rss+xml'
        tpl = pypoly.template.load_xml(os.path.join('newsfeeds',self._template))
        return tpl.generate(channels = self).render()

class RSS_0_9(Feed):
    def __init__(self):
        self._template = 'rss_0_9.xml'

class RSS_1_0(Feed):
    def __init__(self):
        self._template = 'rss_1_0.xml'

class RSS_2_0(Feed):
    def __init__(self):
        self._template = 'rss_2_0.xml'
