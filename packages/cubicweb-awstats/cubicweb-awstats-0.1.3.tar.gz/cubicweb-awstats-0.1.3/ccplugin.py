# -*- coding: utf-8 -*-
"""update-webstats cubicweb plugin

Usage: cubicweb-ctl update-webstats [options] <instance-name> startdate [stopdate]

This command will generate webstats objects for all linked document types.
"""

import os.path as osp
from datetime import datetime, timedelta

from logilab.common.date import first_day, last_day, date_range, ONEDAY
from logilab.common.shellutils import ProgressBar

from cubicweb import cwconfig, UnknownEid
from cubicweb import AuthenticationError
from cubicweb.dbapi import in_memory_repo_cnx

from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

from utils import SECTIONSPEC, extract_stats_dict, eid_from_url, \
     get_or_create_statperiod, compress_old_hits


def url_count_from_stats(cnx, stats_dict):
    '''
    parse most visited urls in stats_dict generated from awstats txt file

    returns two dictionnaries with eid as key and sequence of values as value
    one for normal navigation, the other for rdf navigation
    '''
    if 'SIDER' not in stats_dict:
        return {}, {}
    visit_count_dict = {}
    visit_count_rdf_dict = {}
    for item in stats_dict['SIDER'].values():
        url = item[SECTIONSPEC['SIDER'][0]]
        hits = int(item[SECTIONSPEC['SIDER'][1]])
        req = cnx.request()
        eid = eid_from_url(req, url)
        if not eid:
            continue
        if 'rdf' in url:
            visit_count_rdf_dict.setdefault(eid, [])
            visit_count_rdf_dict[eid].append((hits, url))
        else:
            visit_count_dict.setdefault(eid, [])
            visit_count_dict[eid].append((hits, url))
    return visit_count_dict, visit_count_rdf_dict


def parse_input_date(date, periodicity):
    input_formats = {'month':'%m/%Y',
                     'day': '%d/%m/%Y',
                     'hour': '%d/%m/%Y-%Hh'}
    try:
        return datetime.strptime(date, input_formats[periodicity])
    except ValueError:
        print 'Error : %s not a proper date' % date
        return None


def track_progress(iterable, nb_ops=None, pb_size=20, pb_title=''):
    # nb_ops must be set is iterable doesn't support length protocol
    if nb_ops is None:
        nb_ops = len(iterable)
    pb = ProgressBar(nb_ops, size=pb_size, title=pb_title)
    for item in iterable:
        pb.update()
        yield item
    pb.finish()


class StatsUpdater(object):
    def __init__(self, session, cnx, start, stop):
        self.session = session
        self.cnx = cnx
        self.config = session.vreg.config
        self.start = start
        self.stop = stop
        self.allowed_etypes = frozenset(eschema.type for eschema in
                                        session.vreg.schema.rschema('stats_about').objects())
        self.all_hits = {}
        hits_rset = session.execute('Any H,HC,HT,E,P,PSA,PSO WHERE '
                                    'H is Hits, H count HC, H hit_type HT, '
                                    'H stats_about E, H period P, P start PSA, P stop PSO '
                                    'HAVING (PSA >= %(start)s, PSO <= %(stop)s) ',
                                    {'start':start,
                                     'stop':stop})
        for hit in track_progress(hits_rset.entities(), nb_ops=len(hits_rset),
                                  pb_size=62, pb_title='Building cache'):
            hit_key = (hit.stats_about[0].eid, hit.period[0].eid, hit.hit_type)
            self.all_hits[hit_key] = hit

    ## internal utilities #####################################################
    def awstats_filepath(self, date):
        config = self.config
        date_formats = {'month': '%m%Y',
                        'day': '%m%Y%d',
                        'hour':'%m%Y%d%H'}
        domain = config['awstats-domain']
        if config['awstats-domain']:
            domain_ext = '.' + config['awstats-domain']
        else:
            domain_ext = ''
        filename = 'awstats%s%s.txt' % (
            date.strftime(date_formats[config['awstats-periodicity']]),
            domain_ext)
        return osp.join(config['awstats-dir'], filename)

    def stats_period_for_date(self, chosendate, stats_report):
        """ return a statperiod for the current month, if it doesn't exist, create it """
        periodicity = self.config['awstats-periodicity']
        if periodicity == 'month':
            start = first_day(chosendate)
            stop = last_day(start)
        elif periodicity == 'day':
            start = datetime(chosendate.year, chosendate.month, chosendate.day)
            stop = datetime(chosendate.year, chosendate.month, chosendate.day, 23, 59, 59)
        elif periodicity == 'hour':
            start = datetime(chosendate.year, chosendate.month, chosendate.day, chosendate.hour)
            stop = datetime(chosendate.year, chosendate.month, chosendate.day, chosendate.hour, 59, 59)
        return get_or_create_statperiod(self.session, start, stop, stats_report)

    ## update API #############################################################
    def update_stats(self, skip_compress=False):
        ''' parses awstats and creates or updates the corresponding
        data in the cubicweb instance

        :param start: period start (included)
        :param stop: period stop (excluded)
        '''
        stats_report = dict.fromkeys(('updated', 'created', 'exists no change',
                                      'skipped', 'periods', 'compressed'), 0)
        for chosendate in track_progress(date_range(self.start, self.stop),
                                         (self.stop-self.start).days,
                                         pb_size=70, pb_title='Import'):
            self._update_stats_for_date(chosendate, stats_report)
        if not skip_compress:
            compress_old_hits(self.session, stats_report)
        self.session.commit()
        self.session.set_cnxset()
        return stats_report

    def _update_stats_for_date(self, chosendate, stats_report):
        stats_dict = extract_stats_dict(self.awstats_filepath(chosendate))
        stats_period = self.stats_period_for_date(chosendate, stats_report)
        normal_dict, rdf_dict = url_count_from_stats(self.cnx, stats_dict)
        for count_dict, hit_type in ((normal_dict, u'normal'),
                                     (rdf_dict, u'rdf')):
            for eid, values in count_dict.items():
                status = self._update_hits_for_eid(eid, values,
                                                   stats_period, hit_type)
                stats_report[status] += 1

    def _update_hits_for_eid(self, eid, values, stats_period, hit_type):
        self.session.commit()
        self.session.set_cnxset()
        visit_count = visit_count_rdf = 0
        total_hits = sum([item[0] for item in values])
        try:
            entity = self.session.entity_from_eid(eid)
        except UnknownEid:
            return 'skipped'
        if entity.__regid__ not in self.allowed_etypes:
            return 'skipped'
        try:
            hit = self.all_hits[(eid, stats_period.eid, hit_type)]
        except KeyError: # no hit yet, create one
            status = 'created'
            req = self.cnx.request()
            hit = req.create_entity('Hits', count=total_hits, hit_type=hit_type,
                                             period=stats_period, stats_about=entity)
            # append it to the cache
            self.all_hits[(eid, stats_period.eid, hit_type)] = hit
        else:
            if hit.count != total_hits:
                status = 'updated'
                hit.set_attributes(count=total_hits)
            else:
                status = 'exists no change'
        return status


class UpdateWebstatsCommand(Command):
    """ Update cubicweb web stats from awstats processed files.

    If startdate is not entered, the update will be done on the previous
    day or the previous month. If only startdate is enterred, the day or
    month will be processed. If both dates are enterred, all the dates
    between these two dates will be processed.

    According to periodicity setting the input format for the date is
    different :

      * month 05/2011
      * day   15/05/2011
      * hour  15/05/2011-13h (not implemented yet)
    """

    arguments = '<instance> [startdate [stopdate]]'
    name = 'update-webstats'
    min_args = 1
    max_args = 3
    options = [
        ("skip-compress", {"action": 'store_true',
                           'help' : u'Skip the compression of old daily hits into month stats'}),
        ("today", {"action": 'store_true',
                   'help' : u'Process stats for the current day (for testing)'}),
        ]

    ## command / initial setup API ############################################
    def _init_cw_connection(self, appid):
        config = cwconfig.instance_configuration(appid)
        sourcescfg = config.sources()
        config.set_sources_mode(('system',))
        cnx = repo = None
        while cnx is None:
            try:
                login = sourcescfg['admin']['login']
                pwd = sourcescfg['admin']['password']
            except KeyError:
                login, pwd = manager_userpasswd()
            try:
                repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
            except AuthenticationError:
                print 'wrong user/password'
            else:
                break
        session = repo._get_session(cnx.sessionid)
        # XXX keep reference on cnx otherwise cnx.__del__ will cause trouble
        cnx.use_web_compatible_requests(session.vreg.config['base-url'])
        return cnx, session

    def run(self, args):
        # args = (appid, start[, stop])
        appid = args.pop(0)
        cw_cnx, session = self._init_cw_connection(appid)
        session.set_cnxset()
        periodicity = session.vreg.config['awstats-periodicity']
        start = stop = None
        if len(args) > 0:
            start = parse_input_date(args[0], periodicity)
        if start is None:
            if self.config.today:
                chosendate = datetime.now()
            else:
                chosendate = datetime.now()-timedelta(1)
            start = datetime(chosendate.year, chosendate.month, chosendate.day)
        if len(args) > 1:
            stop = parse_input_date(args[1], periodicity)
        if stop is None:
            stop = start
        if start is None or stop is None:
            sys.exit(1) # parse_input_date failed to parse date
        stop += ONEDAY # date_range() excludes stop boundary
        stats_updater = StatsUpdater(session, cw_cnx, start, stop)
        stats_report = stats_updater.update_stats(self.config.skip_compress)
        print '''=== Update Report ===
Number of periods imported :             %(periods)s
Number of stat objects created :         %(created)s
Number of stat objects updated :         %(updated)s
Number of stat objects already existed : %(exists no change)s
Number of stat objects skipped :         %(skipped)s
Number of stat objects compressed :      %(compressed)s
        ''' % stats_report

CWCTL.register(UpdateWebstatsCommand)
