"""Various blog boxes: archive, per author, etc...

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.selectors import (none_rset, one_line_rset, is_instance,
                                has_related_entities, match_view)
from cubicweb.web import component


class BlogArchivesBox(component.CtxComponent):
    """blog side box displaying a Blog Archive"""
    __regid__ = 'blog.archives_by_date'
    __select__ = (component.CtxComponent.__select__
                  & is_instance('Blog', 'MicroBlog')
                  & has_related_entities('entry_of', 'object'))
    title = _('blog.archives_by_date')
    order = 35
    context = 'left'

    def render_body(self, w):
        #FIXME doesn't handle (yet) multiple blogs
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        rset = entity.related('entry_of', 'object')
        self._cw.view('cw.archive.by_date', rset, maxentries=6,
                      basepath=entity.rest_path() + '/blogentries',
                      w=w)


class BlogEntryArchivesBox(BlogArchivesBox):
    __regid__ = 'blog.entry_archives_by_date'
    __select__ = (component.CtxComponent.__select__
                  & is_instance('BlogEntry', 'MicroBlogEntry')
                  & has_related_entities('entry_of', 'subject'))

    def render_body(self, w):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        box = self._cw.vreg['ctxcomponents'].select('blog.archives_by_date', self._cw, w=w,
                                                    rset=entity.related('entry_of', 'subject'))
        box.render_body(w)

class BlogByAuthorBox(component.CtxComponent):
    __regid__ = 'blog.archives_by_author'
    __select__ = (component.CtxComponent.__select__
                  & is_instance('Blog', 'MicroBlog')
                  & has_related_entities('entry_of', 'object'))
    title = _('blog.archives_by_author')
    order = 36
    context = 'left'

    def render_body(self, w):
        #FIXME doesn't handle (yet) multiple blogs
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        rset = entity.related('entry_of', 'object')
        self._cw.view('cw.archive.by_author', rset,
                      basepath=entity.rest_path() + '/blogentries',
                      w=w)


class BlogEntryByAuthorBox(BlogByAuthorBox):
    __regid__ = 'blog.entry_archives_by_author'
    __select__ = (component.CtxComponent.__select__
                  & is_instance('BlogEntry', 'MicroBlogEntry')
                  & has_related_entities('entry_of', 'subject'))

    def render_body(self, w):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        box = self._cw.vreg['ctxcomponents'].select('blog.archives_by_author', self._cw, w=w,
                                                    rset=entity.related('entry_of', 'subject'))
        box.render_body(w)

class LatestBlogsBox(component.CtxComponent):
    """display a box with latest blogs and rss"""
    __regid__ = 'blog.latest_blogs'
    __select__ = (component.CtxComponent.__select__
                  & none_rset() & match_view('index'))
    title = _('blog.latest_blogs')
    order = 34
    display_see_more_link = True
    contextual = False

    def latest_blogs_rset(self):
        return self._cw.execute(
            'Any X,T,CD ORDERBY CD DESC LIMIT 5 WHERE X is IN (MicroBlogEntry, BlogEntry), '
            'X title T, X creation_date CD')

    def render_body(self, w):
        # XXX turn into a selector
        rset = self.latest_blogs_rset()
        if not rset:
            return
        w(u'<ul class="boxListing">')
        for entity in rset.entities():
            w(u'<li>%s</li>\n' %
              tags.a(entity.dc_title(), href=entity.absolute_url()))
        rqlst = rset.syntax_tree()
        rqlst.set_limit(None)
        rql = rqlst.as_string(kwargs=rset.args)
        if self.display_see_more_link:
            url = self._cw.build_url('view', rql=rql, page_size=10)
            w(u'<li>%s</li>\n' %
              tags.a(u'[%s]' % self._cw._(u'see more'), href=url))
        rss_icon = self._cw.uiprops['RSS_LOGO_16']
        # FIXME - could use rss_url defined as a property if available
        rss_label = u'%s <img src="%s" alt="%s"/>' % (
            self._cw._(u'subscribe'), rss_icon, self._cw._('rss icon'))
        blogs = self._cw.execute('Any B,RSS WHERE B is Blog, B rss_url RSS')
        if len(blogs) == 1:
            rss_url = blogs[0][1]
        else:
            rss_url = self._cw.build_url('view', vid='rss', rql=rql)
        w(u'<li>%s</li>\n' %
          tags.a(rss_label, href=rss_url, escapecontent=False))
        w(u'</ul>\n')


class LatestBlogsBlogBox(LatestBlogsBox):
    """display a box with latest blogs and rss, filtered for a particular blog
    """
    __select__ = (component.CtxComponent.__select__
                  & one_line_rset() & is_instance('Blog'))
    display_see_more_link = False
    contextual = True

    def latest_blogs_rset(self):
        blog = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return self._cw.execute(
            'Any X,T,CD ORDERBY CD DESC LIMIT 5 WHERE '
            'X title T, X creation_date CD, X entry_of B, B eid %(b)s',
            {'b': blog.eid})

class LatestBlogsBlogEntryBox(LatestBlogsBox):
    """display a box with latest blogs and rss, filtered for a particular blog
    """
    __select__ = (component.CtxComponent.__select__
                  & is_instance('BlogEntry')
                  & has_related_entities('entry_of', 'subject'))
    display_see_more_link = False
    contextual = True

    def latest_blogs_rset(self):
        blogentry = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        #FIXME doesn't handle (yet) multiple blogs
        blog = blogentry.related('entry_of', 'subject').get_entity(0,0)
        return self._cw.execute(
            'Any X,T,CD ORDERBY CD DESC LIMIT 5 WHERE '
            'X title T, X creation_date CD, X entry_of B, B eid %(b)s',
            {'b': blog.eid})

