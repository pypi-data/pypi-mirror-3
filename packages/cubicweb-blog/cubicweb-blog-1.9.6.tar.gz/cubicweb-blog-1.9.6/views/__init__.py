from cubicweb.selectors import is_instance
from cubicweb.view import EntityAdapter
from cubicweb.web.views import ibreadcrumbs
from cubicweb.web.views.autoform import AutomaticEntityForm

class BlogEntryIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('BlogEntry', 'MicroBlogEntry')
    def parent_entity(self):
        return self.entity.entry_of and self.entity.entry_of[0] or None


class BlogEntryIPrevNextAdapter(EntityAdapter):
    __regid__ = 'IPrevNext'
    __select__ = is_instance('BlogEntry', 'MicroBlogEntry')

    def next_entity(self):
        return self._sibling_entry('ASC', '>')

    def previous_entity(self):
        return self._sibling_entry('DESC', '<')

    def _sibling_entry(self, order, operator):
        if self.entity.entry_of:
            rql = ('Any B ORDERBY B %s LIMIT 1 '
                   'WHERE B entry_of BL, BL eid %%(blog)s, '
                   'B eid %s %%(eid)s')
            rset = self._cw.execute(rql % (order, operator),
                                    {'blog': self.entity.entry_of[0].eid,
                                     'eid': self.entity.eid})
        else:
            rql = ('Any B ORDERBY B %s LIMIT 1 '
                   'WHERE B eid %s %%(eid)s, NOT B entry_of BL')
            rset = self._cw.execute(rql % (order, operator),
                                    {'eid': self.entity.eid})
        if rset:
            return rset.get_entity(0,0)


def registration_callback(vreg):
    vreg.register(BlogEntryIBreadCrumbsAdapter)
    vreg.register(BlogEntryIPrevNextAdapter)
    if 'preview' in vreg.config.cubes():

        from cubes.preview.views.forms import PreviewFormMixin
        class PreviewAutomaticEntityForm(PreviewFormMixin, AutomaticEntityForm):
            preview_mode = 'inline'
            __select__ = AutomaticEntityForm.__select__ & is_instance('Blog', 'BlogEntry',
                                                                      'MicroBlog', 'MicroBlogEntry')
        vreg.register(PreviewAutomaticEntityForm)
