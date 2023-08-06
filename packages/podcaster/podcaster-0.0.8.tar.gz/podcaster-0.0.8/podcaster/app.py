# -*- coding:utf-8 -*-
from nagare import presentation, editor, validator, log, wsgi, component
from nagare.namespaces import xhtml5
from podcaster.platforms.youtube import YoutubePlatform
from podcaster.feed import Feed
import webob


class Podcaster(object):
    def __init__(self):
        self.platform = YoutubePlatform()
        self.author = editor.Property('').validate(lambda v: validator.StringValidator(v, strip=True).not_empty().to_string())
        self.format_code = editor.Property(self.platform.get_default_format().code)
        self.reset()

    def reset(self):
        self.link = ''

    def make_link(self):
        if not self.author.error:
            self.link = '/feed/%s/%s' % (self.author.value, self.format_code.value)


@presentation.render_for(Podcaster)
def render(self, h, *args):
    h.head.css_url('css/bootstrap.min.css')
    h.head.css_url('css/bootstrap-responsive.min.css')
    with h.div(class_='navbar'):
        with h.div(class_='navbar-inner'):
            with h.div(class_='container'):
                h << h.a('Podcaster', class_="brand", href=h.request.application_url)

    with h.div(class_='container'):
        with h.section(id='form'):
            h << h.h2('Step 1 : Generate your podcast link')
            with h.form(class_='form-horizontal').pre_action(self.reset):
                with h.fieldset:
                    with h.div(class_='control-group %s' % ('error' if self.author.error else '')):
                        h << h.label('Youtube user name', class_='control-label')
                        with h.div(class_='controls'):
                            h << h.input(type='text', value=self.author()).action(self.author)
                            h << (h.span(self.author.error, class_='help-inline') if self.author.error else '')
                    with h.div(class_='control-group'):
                        h << h.label('Desired video resolution', class_='control-label')
                        with h.div(class_='controls'):
                            with h.select.action(self.format_code):
                                for fmt in self.platform.list_formats():
                                    h << h.option(fmt.resolution, value=fmt.code).selected(self.format_code())
                            h << h.span('If the resolution is not available for a video, Podcaster will try lower resolutions', class_='help-inline')
                    with h.div(class_='form-actions'):
                        h << h.input(type='submit', class_='btn btn-primary', value='Create my link !').action(self.make_link)

        if self.link:
            with h.section(id='link'):
                h << h.h2('Step 2 : Add this link to iTunes')
                url = h.request.application_url + self.link
                h << h.p(h.a(url, href=url))

                h << h.p('Enjoy watching your videos !')
        with h.footer:
            pass
    return h.root


@presentation.init_for(Podcaster, 'len(url) >= 1 and url[0]=="feed"')
def init_feed(self, url, comp, http_method, request):
    log.info('init_feed %s %s' % (url, request.params))
    cid = url[1]
    format_ = self.platform.get_format(url[2]) if len(url) >= 3 else self.platform.get_default_format()
    log.info('Using format %s' % format_)
    f = Feed(cid, YoutubePlatform(), format_)
    raise webob.exc.HTTPOk(content_type='text/xml', body=f.render(request))


@presentation.init_for(Podcaster, 'len(url) >= 1 and url[0]=="video"')
def init_video(self, url, comp, http_method, request):
    log.info('init_video %s %s' % (url, request.params))
    vid = url[1].replace('.mp4', '')
    video = self.platform.get_video(vid)
    format_ = self.platform.get_format(request.params.get('fmt'))
    log.info('Using format %s' % format_)
    url = video.get_url(format_)
    raise webob.exc.HTTPMovedPermanently(location=url)

# ---------------------------------------------------------------

class WSGIApp(wsgi.WSGIApp):
    renderer_factory = xhtml5.Renderer

    def __init__(self):
        """Initialization
        """
        super(WSGIApp, self).__init__(None)

    def create_root(self, *args, **kw):
        """Create the application root component

        Return:
          - the root component
        """
        return component.Component(Podcaster())


app = WSGIApp()
