# -*- coding:utf-8 -*-
from nagare.namespaces import xml
from nagare.namespaces.xml import TagProp


# Using recipe found at http://www.nagare.org/trac/blog/namespaces-and-rss-feed

class RssRenderer(xml.XmlRenderer):
    """RSS renderer"""
    # RSS tags
    # ------------

    rss = TagProp('rss', set(('version',)))

    channel = TagProp('channel', set())
    title = TagProp('title', set())
    link = TagProp('link', set())
    description = TagProp('description', set())
    language = TagProp('language', set())
    copyright = TagProp('copyright', set())
    managingEditor = TagProp('managingEditor', set())
    webMaster = TagProp('webMaster', set())
    pubDate = TagProp('pubDate', set())
    lastBuildDate = TagProp('lastBuildDate', set())
    category = TagProp('category', set())
    generator = TagProp('generator', set())
    docs = TagProp('docs', set())
    cloud = TagProp('cloud', set(('domain', 'port',
        'path', 'registerProcedure', 'protocol')))
    ttl = TagProp('ttl', set())

    image = TagProp('image', set())
    url = TagProp('url', set())
    width = TagProp('width', set())
    height = TagProp('height', set())

    rating = TagProp('rating', set())

    textInput = TagProp('textInput', set())
    name = TagProp('name', set())

    skipHours = TagProp('skipHours', set())
    skipDays = TagProp('skipDays', set())

    item = TagProp('item', set())
    title = TagProp('title', set())
    link = TagProp('link', set())
    description = TagProp('description', set())
    author = TagProp('author', set())
    category = TagProp('category', set(('domain',)))
    comments = TagProp('comments', set())
    enclosure = TagProp('enclosure', set(('url', 'length', 'type')))
    guid = TagProp('guid', set(('isPermaLink',)))
    pubDate = TagProp('pubDate', set())
    source = TagProp('source', set(('url',)))


class ItunesRenderer(xml.XmlRenderer):
    """iTunes specific tags"""

    author = TagProp('author', set())
    block = TagProp('block', set())
    category = TagProp('category', set())
    image = TagProp('image', set())
    duration = TagProp('duration', set())
    explicit = TagProp('explicit', set())
    keywords = TagProp('keywords', set())
    new_feed_url = TagProp('new-feed-url', set())
    owner = TagProp('owner', set())
    subtitle = TagProp('subtitle', set())
    summary = TagProp('summary', set())
