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

"""cubicweb-awstats views/forms/actions/components for web ui"""

from cubicweb.utils import RepeatList
from cubicweb.view import EntityView
from cubicweb.web.views import primary, navigation
from cubicweb.selectors import is_instance

class StatPeriodPrimaryView(primary.PrimaryView):
    """

    `column_types_aggr` enables you to combine results by type
    For example BlogEntry and MicroBlogEntries in one table and Cards in separate table :

    column_types_aggr = (('MicroBlogEntry', 'BlogEntry'),
                        ('Card'))
    """
    __select__ = is_instance('StatPeriod')
    column_types_aggr = None #tuple of tuples of types

    def cell_call(self, row, col):
        _ = self._cw._
        req = self._cw
        self.w(u'<div id="primarystatperiod">')
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h1>%s %s - %s (%s %s)</h1>' % (_('Statistics for period :'),
                                              entity.printable_value('start'),
                                              entity.printable_value('stop'),
                                              (entity.stop - entity.start).days,
                                              _('days')) )
        rset = self._cw.execute('DISTINCT Any C WHERE X is Hits, X hit_type C')
        self.w(u'<a href="%s">%s</a>' % (entity.absolute_url(showall=1),
                                         _('show all results')))
        for (hit_type,) in rset:
            self.w(u'<h3>%s</h3>' % hit_type)
            rql = 'Any X, C ORDERBY C DESC %(limit)s WHERE H stats_about X, H hit_type "%(type)s",'\
                  'H count C, H period P, P eid %%(e)s' % {'type': hit_type,
                                                           'limit': req.form.get('showall') and ' ' or 'LIMIT 20' }
            if self.column_types_aggr:
                self.w(u'<table><tr>')
                for types in self.column_types_aggr:
                    self.w(u'<td>')
                    typedrql = rql + ', X is in (%s)' % ','.join(types)
                    rset = self._cw.execute(typedrql, {'e':entity.eid})
                    self.wview('table', rset, 'null')
                    # cf rql/editextensions.py unset_limit
                    nolimit_rql = typedrql.replace('LIMIT 20', '')
                    self.w(u'<a href="%s">Export CSV</a>' % self._cw.build_url('', rql=nolimit_rql % {'e':entity.eid},
                                                                                vid='csvexport'))
                    #FIXME TODO not working right now
                    self.wview('piechart', rset, 'null')
                    self.w(u'</td>')
                self.w(u'</tr></table>')
            else:
                rset = self._cw.execute(rql, {'e':entity.eid})
                self.wview('table', rset, 'null')
                nolimit_rql = rql.replace('LIMIT 20', '')
                self.w(u'<a href="%s">Export CSV</a>' % self._cw.build_url('', rql=nolimit_rql % {'e':entity.eid},
                                                                           vid='csvexport'))
        self.w(u'</div>')


class StatPeriodIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('StatPeriod')

    def previous_entity(self):
        entity = self.entity
        execute = self._cw.execute
        rset = execute("StatPeriod P ORDERBY S DESC LIMIT 1  WHERE P start S, P2 start S2, P2 eid %(e)s HAVING S < S2",
                       {'e':entity.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        entity = self.entity
        execute = self._cw.execute
        rset = execute("StatPeriod P ORDERBY S LIMIT 1  WHERE P start S, P2 start S2, P2 eid %(e)s HAVING S > S2",
                       {'e':entity.eid})
        if rset:
            return rset.get_entity(0, 0)


class StatGraph(EntityView):
    __regid__ = 'webstatsgraph'
    # select only instances with stats_about relation

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h1>%s %s</h1>' % (_('Graph of hits for'),
                                    entity.dc_title()))
        self.w(u'<div id="webstats">')
        rql = ('DISTINCT Any S, HITS ORDERBY S WITH S, HITS BEING ('
              '(Any START, HITS WHERE H count HITS, H hit_type "normal", H period P, P start START, P stop STOP, H stats_about E, E eid %%(e)s %s)'
              ' UNION '
              '(Any START, 0 WHERE P is StatPeriod, P start START, P stop STOP, NOT EXISTS(H period P, H stats_about E, E eid %%(e)s) %s))')
        plot_displayed = False
        for constraint, label in ((' HAVING STOP-START <= 20', _('Daily')),
                                  (' HAVING STOP-START >= 20', _('Monthly'))):
            rset = self._cw.execute(rql % (constraint, constraint), {'e':entity.eid})
            if rset:
                self.w(u'<h2>%s</h2>' % label)
                self.w(self._cw.view('plot', rset, 'null'))
                plot_displayed = True
        if not plot_displayed:
            self.w(u'<h2>%s<h2>' % _('No stats yet'))
        self.w(u'</div>')
