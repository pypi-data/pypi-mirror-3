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

"""cubicweb-awstats entity's classes"""

from cubicweb.entities import AnyEntity

class StatPeriod(AnyEntity):
    __regid__ = 'StatPeriod'

    def dc_title(self):
        _ = self._cw._
        return u'%s : %s - %s' % (_('Stat period'),
                                  self.printable_value('start'),
                                  self.printable_value('stop'))
