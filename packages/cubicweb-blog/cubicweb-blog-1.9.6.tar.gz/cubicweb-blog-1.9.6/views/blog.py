"""Primary views for blogs

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.selectors import is_instance
from cubicweb.web import uicfg, component
from cubicweb.web.views import primary

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_abaa = uicfg.actionbox_appearsin_addmenu
for etype in ('Blog', 'MicroBlog'):
    _pvs.tag_attribute((etype, 'title'), 'hidden')
    _pvs.tag_object_of(('*', 'entry_of', etype), 'hidden')
    _pvdc.tag_attribute((etype, 'description'), {'showlabel': False})
    _abaa.tag_object_of(('*', 'entry_of', etype), True)
_pvs.tag_attribute(('Blog', 'rss_url'), 'hidden')

_pvs.tag_object_of(('*', 'has_creator', 'UserAccount'), 'relations')
_pvs.tag_attribute(('UserAccount', 'name'), 'hidden')


class BlogPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Blog', 'MicroBlog')

    def entity_call(self, entity):
        self.w(u'<div class="blogwrapper">')
        super(BlogPrimaryView, self).entity_call(entity)
        self.w(u'</div>')

    def render_entity_relations(self, entity):
        super(BlogPrimaryView, self).render_entity_relations(entity)
        rset = entity.related('entry_of', 'object')
        if rset:
            strio = UStringIO()
            self.paginate(self._cw, w=strio.write, page_size=10, rset=rset)
            self.w(strio.getvalue())
            self.wview('sameetypelist', rset, showtitle=False)
            self.w(strio.getvalue())


class SubscribeToBlogComponent(component.EntityCtxComponent):
    __regid__ = 'blogsubscribe'
    __select__ = component.EntityVComponent.__select__ & is_instance('Blog', 'MicroBlog')
    context = 'ctxtoolbar'

    def render_body(self, w):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        w('<a href="%s"><img src="%s" alt="%s"/></a>' % (
            xml_escape(entity.cw_adapt_to('IFeed').rss_feed_url()),
            self._cw.uiprops['RSS_LOGO_16'],
            self._cw._(u'subscribe to this blog')))

