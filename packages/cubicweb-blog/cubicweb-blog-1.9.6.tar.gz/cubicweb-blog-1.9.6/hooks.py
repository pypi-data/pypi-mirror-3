from cubicweb.selectors import is_instance, is_in_state
from cubicweb.sobjects.notification import NotificationView, StatusChangeMixIn

class BlogEntryPublishedView(StatusChangeMixIn, NotificationView):
    """get notified from published blogs"""
    __select__ = is_instance('BlogEntry',) & is_in_state('published')
    content_attr = 'content'

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return '[%s] %s' % (self._cw.vreg.config.appid, entity.dc_title())
