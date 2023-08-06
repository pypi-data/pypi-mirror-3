"""Secondary views for blogs

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import re

from calendar import monthrange
from datetime import datetime

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.view import EntityView
from cubicweb.selectors import paginated_rset, sorted_rset, is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import primary, baseviews, calendar, navigation, workflow
from cubicweb.web.views.xmlrss import RSSItemView

_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('BlogEntry', 'title'), 'hidden')
_pvs.tag_subject_of(('BlogEntry', 'entry_of', '*'), 'relations')
_afs = uicfg.autoform_section
_afs.tag_subject_of(('BlogEntry', 'entry_of', 'Blog'), 'main', 'attributes')

# blog entries #################################################################

def render_blogentry_title(req, w, entity):
    w(u'<h1>%s</h1>' % entity.view('incontext'))
    w(u'<div class="author_date"><div>%s' %
      req.format_date(entity.creation_date))
    rql = None
    if entity.has_creator:
        creator = entity.has_creator[0]
        name = creator.name
        rql = 'Any X ORDERBY D DESC WHERE X is BlogEntry, X has_creator Y, '\
              'Y eid %s, X creation_date D' % creator.eid
    elif entity.creator:
        creator = entity.creator
        name = creator.name()
        rql = 'Any X ORDERBY D DESC WHERE X is BlogEntry, X created_by Y, '\
              'Y eid %s, X creation_date D' % creator.eid
    if rql:
        vtitle = _('blog entries created by %s') % name
        url = req.build_url('view', rql=rql, vtitle=vtitle, page_size=10)
        w(u' %s <a title="%s" href="%s">%s</a>' % (
            _('by'), xml_escape(vtitle), xml_escape(url), xml_escape(name)))
    w(u'</div></div>')


class BlogEntryPrimaryView(primary.PrimaryView):
    __select__ = is_instance('BlogEntry')
    show_attr_label = False

    def render_entity_attributes(self, entity):
        self.w(u'<div class="blogwrapper">')
        super(BlogEntryPrimaryView, self).render_entity_attributes(entity)
        self.w(u'</div>')

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.blog.css')
        w = self.w
        w(u'<div class="blogentry_title">')
        render_blogentry_title(self._cw, w, entity)
        w(u'</div>')
        w(u'<br class="clear"/>')


# don't show workflow history for blog entry
class BlogEntryWFHistoryVComponent(workflow.WFHistoryVComponent):
    __select__ = workflow.WFHistoryVComponent.__select__ & is_instance('BlogEntry')

    def render(self, w, **kwargs):
        pass

class BlogEntrySameETypeListView(baseviews.SameETypeListView):
    __select__ = baseviews.SameETypeListView.__select__ & is_instance('BlogEntry')
    countrql = ('Any COUNT(B) WHERE B is BlogEntry, '
                'B creation_date >= %(firstday)s, B creation_date <= %(lastday)s')
    item_vid = 'blog'

    def call(self, **kwargs):
        self._cw.add_css('cubes.blog.css')
        super(BlogEntrySameETypeListView, self).call(**kwargs)
        # XXX Iirk, IPrevNext
        if 'year' in self._cw.form and 'month' in self._cw.form:
            self.render_next_previous(int(self._cw.form['year']), int(self._cw.form['month']))

    def render_next_previous(self, year, month):
        if month == 12:
            nextmonth = 1
            year = year + 1
        else:
            nextmonth = month + 1
        if month == 1:
            previousmonth = 12
            year = year - 1
        else:
            previousmonth = month -1
        self.w(u'<div class="prevnext">')
        self.w(u'<span class="previousmonth">%s</span>' \
               % self.render_link(year, previousmonth,
                                  xml_escape(u'<< ' + self._cw._(u'previous month'))))
        self.w(u'<span class="nextmonth">%s</span>' \
               % self.render_link(year, nextmonth,
                                  xml_escape(self._cw._(u'next month') + u' >>')))
        self.w(u'</div>')

    def render_link(self, year, month, atitle):
        firstday = datetime(year, month, 1)
        lastday = datetime(year, month, monthrange(year, month)[1])
        args = {'firstday': firstday, 'lastday': lastday}
        nmb_entries = self._cw.execute(self.countrql, args)[0][0]
        if not nmb_entries:
            return
        rql = ('Any B, BD ORDERBY BD DESC '
               'WHERE B is BlogEntry, B creation_date BD, '
               'B creation_date >= "%s", B creation_date <= "%s"' %
                (firstday.strftime('%Y-%m-%d'), lastday.strftime('%Y-%m-%d')))
        label = u'%s %s [%s]' % (self._cw._(calendar.MONTHNAMES[month-1]), year,
                                 nmb_entries)
        vtitle = '%s %s' % (display_name(self._cw, 'BlogEntry', 'plural'), label)
        url = self._cw.build_url('view', rql=rql, vtitle=vtitle,
                                 month=month, year=year)
        return u'<a href="%s">%s</a>' % (xml_escape(url), atitle)

class BlogEntryBlogView(EntityView):
    __regid__ = 'blog'
    __select__ = is_instance('BlogEntry')

    toolbar_components = primary.PrimaryView.content_navigation_components.im_func

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        w = self.w
        _ = self._cw._
        w(u'<div class="post">')
        self.toolbar_components('ctxtoolbar')
        render_blogentry_title(self._cw, w, entity)
        w(u'<div class="entry">')
        body = entity.printable_value('content')
        w(body)
        w(u'</div>')
        w(u'<br class="clear"/>')
        w(u'<div class="postmetadata">%s</div>' % entity.view('post-reldata'))
        w(u'</div>')


class BlogEntryPostMetaData(EntityView):
    __regid__ = 'post-reldata'
    __select__ = is_instance('BlogEntry')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        _ = lambda ertype, form='': display_name(self._cw, ertype, form)
        reldata = []
        w = reldata.append
        schema = self._cw.vreg.schema
        if 'comments' in schema and \
               'BlogEntry' in schema.rschema('comments').objects():
            from cubes.comment.entities import subcomments_count
            count = subcomments_count(entity)
            if count:
                url = xml_escape(entity.absolute_url())
                if count > 1:
                    label = _('Comment', 'plural')
                else:
                    label = _('Comment')
                w(u'<a href="%s">%s %s</a>' % (url, count, label))
            else:
                w(u'%s %s' % (count, _('Comment')))
        if 'tags' in schema and 'BlogEntry' in schema.rschema('tags').objects():
            tag_rset = entity.related('tags', 'object')
            if tag_rset:
                w(u'%s %s' % (_('tags', 'object'), self._cw.view('csv', tag_rset)))
        rset = entity.related('entry_of', 'subject')
        if rset:
            w(u'%s %s' % (self._cw._('blogged in '),
                          self._cw.view('csv', rset, 'null')))
        self.w(u' | '.join(reldata))


class BlogNavigation(navigation.PageNavigation):
    __select__ = paginated_rset() & sorted_rset() & is_instance('BlogEntry')

    def index_display(self, start, stop):
        return unicode(int(start / self.page_size)+1)


# micro blog entries ###########################################################

def format_microblog(entity):
    if entity.has_creator:
        author = entity.has_creator[0]
        if author.has_avatar:
            imgurl = author.has_avatar[0].uri
            ablock = u'<a href="%s"><img src="%s" alt="avatar"/></a>' % (
                author.absolute_url(), xml_escape(imgurl))
        else:
            ablock = entity.has_creator[0].view('outofcontext')
    else:
        ablock = entity.dc_creator()
    if entity.content_format == 'text/html':
        content = entity.content
    else:
        words = []
        for word in entity.content.split():
            if word.startswith('http://'):
                word = u'<a href="%s">%s</a>' % (word, word)
            else:
                word = xml_escape(word)
            words.append(word)
        content = u' '.join(words)
    return (u'<div class="microblog">'
            u'<span class="author">%s</span>'
            u'<span class="msgtxt">%s</span>'
            u'<span class="meta"><a href="%s">%s</a></span>'
            u'</div>' % (ablock, content, entity.absolute_url(), entity.creation_date))

class MicroBlogEntryPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('MicroBlogEntry')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.blog.css')
        entity = self.cw_rset.get_entity(row, col)
        self.w(format_microblog(entity))

class MicroBlogEntrySameETypeListView(baseviews.SameETypeListView):
    __select__ = baseviews.SameETypeListView.__select__ & is_instance('MicroBlogEntry')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.blog.css')
        entity = self.cw_rset.get_entity(row, col)
        self.w(format_microblog(entity))

_CLEAN_STYLE_RE = re.compile(r'<style .*?</style>', re.MULTILINE | re.DOTALL)

class BlogEntryRSSItemView(RSSItemView):
    __select__ = is_instance('BlogEntry')

    def render_description(self, entity):
        """
        Make sure generated XML for RSS is "valid", ie. do not
        contains <style> tags

        Note that this *should* not happen (style tags there), but
        browser tolerate them.
        """
        htmlcontent = entity.dc_description(format='text/html')
        htmlcontent = _CLEAN_STYLE_RE.sub('', htmlcontent)
        self._marker('description', htmlcontent)
