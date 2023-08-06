# -*- coding:utf-8 -*-


class VideoFormat(object):
    def __init__(self, code, codec, resolution, extension, content_type):
        self.code = code
        self.codec = codec
        self.resolution = resolution
        self.extension = extension
        self.content_type = content_type

    def __eq__(self, other):
        for attr in ('code', 'codec', 'resolution', 'extension', 'content_type'):
            if getattr(self, attr, 'self') != getattr(other, attr, 'other'):
                return False
        return True

    def __repr__(self):
        return "<Format: %s %s %s>" % (self.code, self.codec, self.resolution)


class Mp4Format(VideoFormat):
    def __init__(self, code, resolution):
        super(Mp4Format, self).__init__(code, 'mp4', resolution, '.mp4', 'video/mp4')


class Video(object):
    def __init__(self, platform, vid, url_map, duration):
        self.platform = platform
        self.vid = vid
        self.url_map = url_map
        self.duration = duration

    def get_url(self, format_=None):
        format_ = format_ or self.platform.get_default_format()
        fmt = self.find_best_format(format_)
        return self.url_map[fmt]

    def find_best_format(self, format_):
        for fmt in self.platform.get_lower_formats(format_):
            if fmt in self.url_map:
                return fmt


class BasePlatform(object):

    formats = ()
    default_format = None
    http_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us,en;q=0.5',
    }

    def get_user_feed(self, username, max_results=25):
        return None

    def get_video(self, vid):
        return None

    def list_formats(self):
        return self.formats

    def get_format(self, code, default=True):
        for f in self.list_formats():
            if f.code == code:
                return f
        if default:
            return self.get_default_format()
        else:
            raise KeyError('Unknown code %r' % code)

    def has_format(self, code):
        return code in [f.code for f in self.formats]

    def get_lower_formats(self, format_):
        return self.formats[self.formats.index(format_):]

    def get_default_format(self):
        return self.get_format(self.default_format)

