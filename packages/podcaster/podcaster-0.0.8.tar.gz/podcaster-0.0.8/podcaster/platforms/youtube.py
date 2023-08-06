# -*- coding:utf-8 -*-
import requests
import cgi
from nagare import log
from nagare.namespaces import xml
from podcaster.feed import VideoFeed, UserFeed
from podcaster.dates import parse_date
from podcaster.platforms.base import BasePlatform, Mp4Format, Video


class YoutubePlatform(BasePlatform):

    formats = (Mp4Format('38', '4096x3072'),
               Mp4Format('37', '1080x1920'),
               Mp4Format('22', '720x1280'),
               Mp4Format('18', '360x640'),
               Mp4Format('17', '144x176'))
    default_format = '17'

    def get_user_feed(self, username, max_results=25):
        xs = requests.get('http://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&max-results=%d' % (username, max_results),
                          headers=self.http_headers)
        root = xml.XmlRenderer().parse_xmlstring(xs.text)
        nsmap = root.nsmap
        if 'yt' not in nsmap or 'media' not in nsmap:
            log.warning("Could not load chain %s" % self.username)
            return None

        ns = nsmap[None] #Default namespace is Atom
        nsyt = nsmap['yt'] #YouTube namespace
        nsmedia = nsmap['media'] #Media namespace

        videos = []
        feed_title = username
        feed_description = '%s on YouTube' % username
        for vtag in root.findall('{%s}entry' % ns):
            guid = vtag.find('{%s}id' % ns).text
            published = parse_date(vtag.find('{%s}published' % ns).text)
            updated = parse_date(vtag.find('{%s}updated' % ns).text)
            title = vtag.find('{%s}title' % ns).text
            vid = vtag.find('{%s}group/{%s}videoid' % (nsmedia, nsyt)).text
            duration = int(vtag.find('{%s}group/{%s}duration' % (nsmedia, nsyt)).get('seconds'))
            description = ''
            videos.append(VideoFeed(vid, guid, title, description, published, updated, duration))
        return UserFeed(username.lower(), feed_title, feed_description, videos)

    def get_video(self, vid):
        for type_ in ['embedded', 'detailpage', 'vevo', '']:
            params = dict(video_id=vid, el=type_, ps='default', eurl='', gl='US', hl='en')
            resp = requests.get('http://www.youtube.com/get_video_info',
                                params=params,
                                headers=self.http_headers)
            video_info = cgi.parse_qs(resp.text)
            if 'token' in video_info:
                break

        # URLs
        url_map = {}
        for e in video_info['url_encoded_fmt_stream_map'][0].split(','):
            url_fmt = cgi.parse_qs(e)
            url_fmt_code = url_fmt['itag'][0]
            if self.has_format(url_fmt_code):
                fmt = self.get_format(url_fmt_code)
                url_map[fmt] = url_fmt['url'][0]

        # Duration
        duration = int(video_info['length_seconds'][0])

        return Video(self, vid, url_map, duration)
