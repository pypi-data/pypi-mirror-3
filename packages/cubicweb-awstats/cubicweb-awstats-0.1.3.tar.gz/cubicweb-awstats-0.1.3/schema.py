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

"""cubicweb-awstats schema"""

from yams.buildobjs import (EntityType, String, Int, BigInt, Date, Datetime, Boolean,
                            SubjectRelation, RelationDefinition, RelationType)
_ = unicode

MANAGER_PERMISSIONS = {
     'read': ('managers', ),
     'update': ('managers', 'owners',),
     'delete': ('managers', 'owners'),
     'add': ('managers',)
     }

class StatPeriod(EntityType):
    __permissions__ = MANAGER_PERMISSIONS
    # XXX periodicity for hour cannot work with Date, when it is implemented switch to DateTime
    start = Date(indexed=True)
    stop = Date(indexed=True)

class Hits(EntityType):
    __permissions__ = MANAGER_PERMISSIONS
    hit_type = String(maxsize=128, indexed=True)
    count = Int() #BigInt()

class period(RelationType):
    subject = 'Hits'
    object = 'StatPeriod'
    cardinality = '1*'
    composite = 'object'
    inlined = True

class stats_about(RelationType):
    inlined = True
    cardinality = '?*'



