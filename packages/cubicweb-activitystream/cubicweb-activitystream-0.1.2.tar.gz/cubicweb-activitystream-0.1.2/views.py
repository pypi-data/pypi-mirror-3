from logilab.mtconverter import xml_escape
from cubicweb.selectors import is_instance, adaptable
from cubicweb.view import EntityView

class AStreamView(EntityView):
    __regid__ = 'activitystream'
    __select__ = EntityView.__select__ & adaptable('IActivityStream')
    title = _('activitystream')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(entity.cw_adapt_to('IActivityStream').astream_rql,
                                dict(x=entity.eid))
        self.paginate(rset=rset)
        self.wview('activitystream_item', rset, 'null')


class AStreamItemView(EntityView):
    __regid__ = 'activitystream_item'
    __select__ = EntityView.__select__ & adaptable('IActivityStreamItem')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.activitystream.css')
        entity = self.cw_rset.get_entity(row, col)
        activity = entity.cw_adapt_to('IActivityStreamItem')
        self.w(u'<div class="activitystream">'
               u'<span class="author">%s</span>'
               u'<span class="msgtxt">%s</span>'
               u'<span class="meta"><a href="%s">%s</a></span>'
               u'</div>' % (xml_escape(activity.actor),
                            xml_escape(activity.content),
                            xml_escape(entity.absolute_url()),
                            self._cw.format_date(activity.date, time=True)))
