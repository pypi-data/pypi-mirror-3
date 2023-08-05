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

import re
import os.path as osp
from datetime import datetime, date

from logilab.common.date import previous_month, first_day, date_range, last_day
from logilab.common.shellutils import ProgressBar

from cubicweb.req import FindEntityError
from cubicweb.web import NotFound

from psycopg2 import DataError

SECTIONSPEC = {
# commented sections are not usefull to view
#    'MAP' : ['section', 'offset'],
#    'GENERAL': ['key', None],
    'TIME': ['hour', 'pages', 'hits', 'bandwidth', 'not viewed pages', 'not viewed hits', 'not viewed bandwidth'],
    'VISITOR': ['host', 'pages', 'hits', 'bandwidth', 'last visit date', 'start date of last visit', 'last page of last visit'],
    'DAY': ['date', 'pages', 'hits', 'bandwidth', 'visits'],
    'DOMAIN': ['domain', 'pages', 'hits', 'bandwidth'],
    'LOGIN': ['cluster id', 'pages', 'hits', 'bandwidth', 'last visit date'],
    'ROBOT': ['most visiting robots', 'hits', 'bandwidth', 'last visit', 'hits on robots.txt'],
    'WORMS': ['worm id', 'hits', 'bandwidth', 'last visit'],
    'EMAILSENDER': ['email', 'hits', 'bandwidth', 'last visit'],
    'EMAILRECEIVER': ['email', 'hits', 'bandwidth', 'last visit'],
    'SESSION': ['session range', 'hits'],
    'SIDER': ['most visited URLs', 'hits', 'bandwidth', 'entry', 'exit'],
    'FILETYPES': ['served files type', 'hits', 'bandwidth', 'bandwidth without compression', 'bandwidth after compression'],
    'OS': ['operating systems', 'hits'],
    'BROWSER': ['browser id', 'hits'],
    'SCREENSIZE': ['screen size', 'hits'],
    'UNKNOWNREFERER': ['unknown referer os', 'last visit date'],
    'UNKNOWNREFERERBROWSER': ['unknown referer browser', 'last visit date'],
    'ORIGIN': ['origin', 'pages', 'hits'],
    'SEREFERRALS': ['search engine referers id', 'pages', 'hits'],
    'PAGEREFS': ['external page referers', 'pages', 'hits'],
    'SEARCHWORDS': ['main search keyphrases', 'hits'],
    'KEYWORDS': ['main search keyword', 'hits'],
     #'MISC': ['misc id', 'pages', 'hits', 'bandwidth'],
    'ERRORS': ['errors', 'hits', 'bandwidth'],
    'CLUSTER': ['cluster id', 'pages', 'hits', 'bandwidth'],
    'SIDER_404': ['urls with 404 errors', 'hits', 'last url referer'],
}


SECTIONLABELS = {
    'TIME': _('Visits by hour'),
    'VISITOR': _('Top visitors (by host)'),
    'DAY': _('Visits by days of the month'),
    'DOMAIN': _('Visitors domains/countries'),
    'LOGIN': _('logged in users'),
    'ROBOT': _('Robots/Spiders visitors'),
    'WORMS': _('Worm visits'),
    'EMAILSENDER': _('email sender'),
    'EMAILRECEIVER': _('email receiver'),
    'SESSION': _('Visits duration'),
    'SIDER': _('Most visited URLs'),
    'FILETYPES': _('Visited file types'),
    'OS': _('Visiting operating systems'),
    'BROWSER': _('Visiting browsers'),
    'SCREENSIZE': _('Hits by Screen size'),
    'UNKNOWNREFERER': _('Unknown referer os'),
    'UNKNOWNREFERERBROWSER': _('Unknown referer browser'),
    'ORIGIN': _('Origin of hits'),
    'SEREFERRALS': _('Search engine referers hits'),
    'PAGEREFS': _('Main external page referers'),
    'SEARCHWORDS': _('Hits from search keyphrases'),
    'KEYWORDS': _('Hits from search keywords'),
     #'MISC': ['misc id'), 'pages'), 'hits'), 'bandwidth'],
    'ERRORS': _('HTTP Status codes'),
    'CLUSTER': _('Visits by cluster id'),
    'SIDER_404': _('Hits with 404 errors'),
}

ORIGIN_LABELS = {
    'From0':'Direct address / Bookmark / Link in email...',
    'From1':'Unknown Origin',
    'From2':'Links from an Internet Search Engine',
    'From3':'Links from an external page (other web sites except search engines)',
    'From4':'Internal Link',
    }


def extract_stats_dict(filepath):
    ''' from an awstats file extract structured data into a dict

    returns a dictionnary like this :

    {'SIDER':  {
        '/someurl': {
            'most visisted url':'/someurl',
            'hits' : '1234',
            'bandwidth' : '4321',
            'entry' : '12',
            'exit' : '8'
            }
        ...
        }
    }
    '''
    if not osp.isfile(filepath):
        return {}
    section_name = None
    parsed_countdown = 0
    stats_dict = {}
    for line in file(filepath):
        if line.startswith('BEGIN_'):
            section_name, nb_of_lines = line.split('_', 1)[1].split()
            if section_name in SECTIONSPEC:
                stats_dict.setdefault(section_name, {})
                parsed_countdown = int(nb_of_lines)-1 if int(nb_of_lines) else 0
        elif section_name and parsed_countdown:
            for index, value in enumerate(line.split()):
                key = line.split()[0]
                stats_dict[section_name].setdefault(key, {})
                try:
                    stats_dict[section_name][key][SECTIONSPEC[section_name][index]] = value
                except IndexError:
                    print index, value, line
            parsed_countdown -= 1
        elif section_name and parsed_countdown == 0:
            section_name = None
    return stats_dict

def eid_from_url(req, value):
    ''' return an eid from an url '''
    url_resolver = req.vreg['components'].select('urlpublisher',
                                                     vreg=req.vreg)
    req.url = lambda includeparams: value
    req.relative_path = lambda includeparams: value[1:]
    try:
        pmid, rset = url_resolver.process(req, value)
        if rset and len(rset) == 1:
            return rset[0][0]
        elif req.form.get('rql'):
            rset = req.execute(req.form.get('rql'))
            if rset and len(rset) == 1:
                return rset[0][0]
    except (NotFound, DataError):
        pass

def get_or_create_statperiod(session, start, stop, stats_report={}):
    rql = 'Any P WHERE P is StatPeriod, P start "%(start_date)s", P stop "%(end_date)s"'
    rset = session.execute(rql %
                           {'start_date':start,
                            'end_date':stop})
    if rset:
        return rset.get_entity(0, 0)
    else:
        stats_report.setdefault('periods', 0)
        stats_report['periods'] += 1
        return session.create_entity('StatPeriod', start=start, stop=stop)

def time_params(req):
    params = []
    rset = req.execute('Any START ORDERBY START LIMIT 1 WHERE P is StatPeriod, P start START, P stop STOP HAVING STOP-START <= 2')
    for (item,) in rset:
        for first_day in date_range(previous_month(item), previous_month(datetime.now(), 5), incmonth=True):
            delta = 2
            params.append((first_day, last_day(first_day), delta))
    # TODO - roll complete 12 months into a year
    return params


def compress_old_hits(req, update_stats={}, progressbar=True):
    tp = time_params(req)
    if progressbar:
        pb = ProgressBar(len(tp), 55, title='Compressing old stats')
    for start, stop, delta in tp:
        if progressbar:
            pb.update()
        rql = 'DISTINCT Any E,SUM(C) GROUPBY E WHERE H is Hits, H count C, H hit_type %(hit_type)s,'\
              'H period P, P start >= %(start)s, P stop <= %(stop)s, H stats_about E,'\
              'P start START, P stop STOP  HAVING STOP-START <= %(timedelta)s'
        results = {}
        type_rset = req.execute('DISTINCT Any C WHERE X is Hits, X hit_type C')
        for (hit_type,) in type_rset:
            results[hit_type] = req.execute(rql,
                                            {'start': start,
                                             'stop': stop,
                                             'hit_type':hit_type,
                                             'timedelta': delta})
        if not any(results.values()):
            continue
        # deleting statperiod deletes all associated hits
        drset = req.execute('DELETE StatPeriod P WHERE P start >= %(start)s, P stop <= %(stop)s',
                            {'start': start,
                             'stop': stop,})
        update_stats['compressed'] += len(drset)
        stp = get_or_create_statperiod(req, start, stop)
        for hit_type, rset in results.items():
            for eid, count in rset:
                content_entity = req.entity_from_eid(eid)
                # FIXME if Hits for period and content exist, update it ?
                req.create_entity('Hits', hit_type=hit_type, period=stp, count=count,
                                  stats_about=content_entity)
    if progressbar:
        pb.finish()
