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

from cubicweb.web import action
from cubicweb.selectors import match_user_groups

class AwstatsAccessAction(action.Action):
    __regid__ = 'awstats-action'
    __select__ = match_user_groups('managers')
    title = _('awstats statistics')
    order = 11
    category = 'manage'

    def url(self):
        return self._cw.build_url('view', vid='awstats')


class WebStatsAccessAction(action.Action):
    __regid__ = 'webstats-action'
    __select__ = match_user_groups('managers')
    title = _('webstats statistics')
    order = 12
    category = 'manage'

    def url(self):
        return self._cw.build_url('view', vid='webstats')

