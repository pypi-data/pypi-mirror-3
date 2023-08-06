# -*- coding:utf-8 -*-
import collections
from podcaster.renderers import RssRenderer, ItunesRenderer
from podcaster.dates import rfc2822


VideoFeed = collections.namedtuple('VideoFeed', 'id,guid,title,description,published,updated,duration')
UserFeed = collections.namedtuple('UserFeed', 'username,title,description,videos')


class Feed(object):
    def __init__(self, username, platform, format_):
        self.username = username
        self.format = format_
        self.platform = platform
        self.videos = []
        self.title = self.description = ''
        self._load()

    def _load(self, max_results=25):
        data = self.platform.get_user_feed(self.username, max_results)
        self.title = data.title
        self.description = data.description
        self.videos = data.videos

    def render(self, request):
        r = RssRenderer()
        r.namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        i = ItunesRenderer(r)
        i.default_namespace = 'itunes'
        with r.rss(version='2.0'):
            with r.channel:
                r << r.title(self.title)
                r << i.subtitle('%s (%s)' % (self.description, self.format.resolution))
                for v in self.videos:
                    with r.item:
                        r << r.title(v.title)
                        r << r.guid("%s:%s" % (self.username, v.id), isPermaLink='false')
                        r << r.pubDate(rfc2822(v.published))
                        r << r.enclosure(url='%s/video/%s%s?fmt=%s' % (request.application_url, v.id, self.format.extension, self.format.code),
                                         length=10,
                                         type=self.format.content_type)
                        r << i.duration(v.duration)
                        r << i.subtitle(v.description)
        return r.root.write_xmlstring(pretty_print=True)
