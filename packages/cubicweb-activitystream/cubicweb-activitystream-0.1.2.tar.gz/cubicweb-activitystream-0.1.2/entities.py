# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-activitystream adapters"""

from cubicweb.selectors import is_instance, adaptable
from cubicweb.view import EntityAdapter
from cubicweb.appobject import AppObject

class IActivityStreamAdapter(EntityAdapter):
    __regid__ = 'IActivityStream'
    __abstract__ = True

    @property
    def astream_rql(self):
        """return a RQL query to get the whole activity stream of the adapted
        entity.

        In this query, %(x)s will refer to the eid of the adapted entity. The
        returned query is expected to select:

        1. the eid of the activity
        2. its date
        3. the actor of the activity
        4. some content.

        and to be ordered on date (descending)
        """
        rqls = []
        for part in self._cw.vreg['astream'].possible_objects(
            self._cw, entity=self.entity):
            rqls += part.rql_parts
        assert rqls, 'no activity stream for %s' % self.entity
        if len(rqls) > 1:
            rql =  ' UNION '.join('(%s)' % rql for rql in rqls)
        else:
            rql = rqls[0]
        return 'Any X,XD,XA,XC ORDERBY XD DESC WITH X,XD,XA,XC BEING (%s)' % rql


class ActivityStreamPart(AppObject):
    __registry__ = 'astream'

    @property
    def rql_parts(self):
        """return a list of RQL queries to get some path of the activity stream
        of the adapted entity.

        In each query, %(x)s will refer to the eid of the adapted entity. The
        returned query is expected to select:

        1. the eid of the activity
        2. its date
        3. the actor of the activity
        4. some content.

        and should not be ordered.
        """
        raise NotImplementedError


class StatefulAStreamPart(ActivityStreamPart):
    __select__ = adaptable('IWorkflowable')
    __regid__ = 'stateful'
    rql_parts = (
        'Any TI,TICD,U,TIC WHERE TI is TrInfo, TI wf_info_for X, X eid %(x)s,'
        'TI creation_date TICD, TI created_by U?, TI comment TIC',)


class IActivityStreamItemAdapter(EntityAdapter):
    __regid__ = 'IActivityStreamItem'
    __select__ = is_instance('Any')

    @property
    def content(self):
        return u'%s %s added' % (self.entity.e_schema, self.entity.dc_title())

    @property
    def date(self):
        return self.entity.creation_date

    @property
    def actor(self):
        return self.entity.dc_creator()


class TrinfoAStreamItemAdapter(IActivityStreamItemAdapter):
    __select__ = is_instance('TrInfo')

    @property
    def content(self):
        return (u'%s %s transition from state %s to state %s with comment %s'
                % (self.entity.wf_info_for[0].e_schema,
                   self.entity.wf_info_for[0].dc_title(),
                   self.entity.from_state[0].name,
                   self.entity.to_state[0].name,
                   self.entity.printable_value('comment'),
                   ))
