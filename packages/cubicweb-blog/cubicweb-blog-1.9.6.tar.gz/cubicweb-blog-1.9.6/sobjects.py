# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime

from lxml.html import fromstring, tostring

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    import rdflib
except ImportError:
    rdflib = None
else:
    RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    SIOC = rdflib.Namespace('http://rdfs.org/sioc/ns#')
    DCTERMS = rdflib.Namespace('http://purl.org/dc/terms/')

try:
    from cubes.datafeed.sobjects import DataFeedParser
except ImportError:
    DataFeedParser = None

def get_subject(g, pred, obj):
    subjects = list(g.subjects(pred, obj))
    assert len(subjects) == 1
    return subjects[0]

def get_object(g, subj, pred):
    objects = list(g.objects(subj, pred))
    assert len(objects) == 1
    return objects[0]

def parse_blogpost_sioc(url):
    g = rdflib.ConjunctiveGraph()
    g.parse(url)
    for post, type_, blogpost_ in g.triples((None, RDF.type, SIOC.BlogPost)):
        item = {'uri': unicode(post)}
        item['title'] = unicode(get_object(g, post, DCTERMS.title))
        item['content'] = unicode(get_object(g, post, SIOC.content))
        yield item

format_map = {'application/xhtml+xml':u'text/html',
              'text/html':u'text/html',
              'text/plain':u'text/plain',
              }

IMG_SPIES = ['http://feeds.feedburner.com',
             'http://creatives.commindo-media',
             'http://imp.constantcontact.com',
             'https://blogger.googleusercontent.com/tracker',
             'http://stats.wordpress.com/',
             ]

def is_img_spy(node):
    if node.tag != 'img':
        return False
    for url in IMG_SPIES:
        if node.get('src').startswith(url):
            return True
    return False

def is_tweetmeme_spy(node):
    href = node.get('href')
    if href and href.startswith('http://api.tweetmeme.com/share'):
        return True
    return False

def remove_content_spies(content):
    root = fromstring(content)
    if is_img_spy(root):
        return u''
    for img in root.findall('.//img'):
        if is_img_spy(img):
            img.drop_tree()
        elif img.get('height') == '1' and img.get('width') == '1':
            print tostring(img), 'is probably a spy'
    for anchor in root.findall('.//a'):
        if is_tweetmeme_spy(anchor):
            anchor.drop_tree()
    return unicode(tostring(root))

def parse_blogpost_rss(url):
    data = feedparser.parse(url)
    feed = data.feed
    for entry in data.entries:
        item = {}
        if 'feedburner_origlink' in entry:
            item['uri'] = entry.feedburner_origlink
        else:
            item['uri'] = entry.link
        item['title'] = entry.title
        if hasattr(entry, 'content'):
            content = entry.content[0].value
            mimetype = entry.content[0].type
        elif hasattr(entry, 'summary_detail'):
            content = entry.summary_detail.value
            mimetype = entry.summary_detail.type
        else:
            content = u''#XXX entry.description?
            mimetype = u'text/plain'
        if mimetype == u'text/html':
            content = remove_content_spies(content)
        item['content'] = content
        item['content_format'] = format_map.get(mimetype, u'text/plain')
        if hasattr(entry, 'date_parsed'):
            item['creation_date'] = datetime(*entry.date_parsed[:6])
        if hasattr(entry, 'author_detail') and hasattr(entry.author_detail, 'href'):
            item['author'] = entry.author_detail.href
        elif hasattr(feed, 'author_detail') and hasattr(feed.author_detail, 'href'):
            item['author'] = feed.author_detail.href
        elif hasattr(feed, 'author'):
            item['author'] = feed.author
        elif hasattr(feed, 'image') and hasattr(feed.image, 'link'):
            item['author'] = feed.image.link
        else:
            item['author'] = url
        item['cwuri'] = feed.link
        yield item

def parse_microblogpost_rss(url):
    feed = feedparser.parse(url)
    for entry in feed.entries:
        item = {}
        item['uri'] = entry.id
        # fix weird parsing
        if hasattr(entry, 'content'):
            content = entry.content[0].value
            mimetype = entry.content[0].type
        else:
            content = entry.description
            mimetype = u'text/plain'
        if ': ' in content:
            author, text = content.split(': ', 1)
            if ' ' not in author:
                content = text
        item['content'] = content
        item['content_format'] = format_map.get(mimetype, u'text/plain')
        item['creation_date'] = datetime(*entry.date_parsed[:6])
        item['modification_date'] = datetime(*entry.date_parsed[:6])
        item['author'] = feed.channel.link # true for twitter
        item['cwuri'] = feed.channel.link
        for link in entry.links:
            if link.type.startswith('image/') and link.rel == 'image':
                item['avatar'] = link.href
                break
        else:
            screen_name = feed.channel.link.split('/')[-1]
            item['avatar'] = get_twitter_avatar(screen_name)
        yield item

def search_twitter(word):
    import urllib2
    from simplejson import loads
    data = urllib2.urlopen('http://search.twitter.com/search.json?q=%s&rpp=100' % word).read()
    results = loads(data)
    # process results
    # print results
    return []

AVATAR_CACHE = {}

def get_twitter_avatar(screen_name):
    if screen_name not in AVATAR_CACHE:
        from urllib2 import urlopen
        import simplejson
        data = urlopen('http://api.twitter.com/1/users/show.json?screen_name=%s' % screen_name).read()
        user = simplejson.loads(data)
        AVATAR_CACHE[screen_name] = user['profile_image_url']
    return AVATAR_CACHE[screen_name]

if DataFeedParser is not None:
    class BlogPostParser(DataFeedParser):
        __abstract__ = True
        entity_type = 'BlogEntry'

        def process(self, url):
            stats = {'update':0, 'creation':0}
            for item in self.parse(url):
                author = item.pop('author', None)
                avatar = item.pop('avatar', None)
                euri = self.sget_entity('ExternalUri', uri=item.pop('uri'))
                if euri.same_as:
                    #sys.stdout.write('.')
                    stats['update'] += 1
                    post = self.update_blogpost(euri.same_as[0], item)
                else:
                    #sys.stdout.write('+')
                    stats['creation'] += 1
                    post = self.create_blogpost(item, euri)
                if author:
                    account = self.sget_entity('UserAccount', name=author)
                    self.sget_relation(post.eid, 'has_creator', account.eid)
                    if avatar:
                        auri = self.sget_entity('ExternalUri', uri=avatar)
                        self.sget_relation(account.eid, 'has_avatar', auri.eid)
                #sys.stdout.flush()
            return stats

        def create_blogpost(self, item, uri):
            entity = self._cw.create_entity(self.entity_type, **item)
            entity.set_relations(same_as=uri)
            return entity

        def update_blogpost(self, entity, item):
            entity.set_attributes(**item)
            return entity

    if rdflib is not None:
        class BlogPostSiocParser(BlogPostParser):
            __regid__ = 'blogpost-sioc'
            parse = staticmethod(parse_blogpost_sioc)

    if feedparser is not None:
        class BlogPostRSSParser(BlogPostParser):
            __regid__ = 'blogpost-rss'
            parse = staticmethod(parse_blogpost_rss)

        class MicroBlogPostRSSParser(BlogPostParser):
            __regid__ = 'microblogpost-rss'
            entity_type = 'MicroBlogEntry'
            parse = staticmethod(parse_microblogpost_rss)


if __name__ == '__main__':
    import sys
    from pprint import pprint

    name = sys.argv[1]
    url = sys.argv[2]

    parser = globals()[name]
    pprint(list(parser(url)))
